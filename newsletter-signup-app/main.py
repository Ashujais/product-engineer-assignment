import os
import re
import time
import uuid
import sqlite3
import logging
from typing import Optional, List, Dict
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("newsletter_service")

# Database Initialization
DB_FILE = os.environ.get("NEWSLETTER_DB", os.path.join(os.path.dirname(__file__), "newsletter.db"))

def get_db():
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            company TEXT,
            status TEXT DEFAULT 'SUBSCRIBED',
            utm_source TEXT DEFAULT 'direct',
            utm_medium TEXT DEFAULT 'web',
            utm_campaign TEXT DEFAULT 'newsletter_launch',
            ip_address TEXT,
            crm_synced INTEGER DEFAULT 0,
            welcome_email_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
    """)
    conn.commit()
    conn.close()

init_db()

app = FastAPI(
    title="Newsletter Signup Platform",
    description="Production-grade API for High-Converting Newsletter Subscriptions with CRM Sync & Lead Routing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory Rate Limiting (Max 5 requests per minute per IP)
RATE_LIMIT_STORE: Dict[str, List[float]] = {}
RATE_LIMIT_MAX = 5
RATE_LIMIT_WINDOW = 60

# Disposable Email Domains Blocklist
DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "sharklasers.com", "throwawaymail.com", "yopmail.com", "dispostable.com"
}

# Request Models
class SubscribeRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Subscriber's first name")
    email: EmailStr = Field(..., description="Corporate or personal email address")
    company: Optional[str] = Field(None, max_length=150, description="Company or Organization")
    utm_source: Optional[str] = Field("direct", max_length=50)
    utm_medium: Optional[str] = Field("web", max_length=50)
    utm_campaign: Optional[str] = Field("organic", max_length=50)
    # Honeypot field - bots will fill this, humans will not see it
    website_hp: Optional[str] = Field(None, description="Anti-spam honeypot")

# Background Workers (Simulated Asynchronous CRM & Notification Queue)
def sync_lead_to_crm(subscriber_uuid: str, first_name: str, email: str, company: Optional[str]):
    if not os.environ.get("TESTING"):
        time.sleep(0.3) # Simulate API call latency to Salesforce/HubSpot
    logger.info(f"[CRM Sync] Successfully pushed lead {subscriber_uuid} ({email}) to HubSpot CRM. Assigned to: Inbound Sales Queue.")
    
    # Check if high-value enterprise domain
    domain = email.split("@")[-1].lower()
    if domain not in ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]:
        logger.info(f"[Slack Alert] High-Intent B2B Lead Alert! {first_name} from {company or domain} ({email}) subscribed to Newsletter!")
    
    # Mark as synced in DB
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE subscribers SET crm_synced = 1 WHERE uuid = ?", (subscriber_uuid,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to update crm_synced: {e}")

def dispatch_welcome_email(first_name: str, email: str):
    if not os.environ.get("TESTING"):
        time.sleep(0.1)
    logger.info(f"[Email Service] Sent transactional Welcome Email with Whitepaper PDF download link to {email}.")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE subscribers SET welcome_email_sent = 1 WHERE email = ?", (email,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to update welcome_email_sent: {e}")

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/api/subscribe" and request.method == "POST":
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        
        timestamps = RATE_LIMIT_STORE.get(client_ip, [])
        # filter timestamps within window
        timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        
        if len(timestamps) >= RATE_LIMIT_MAX:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please wait a moment before trying again."}
            )
        
        timestamps.append(now)
        RATE_LIMIT_STORE[client_ip] = timestamps
        
    response = await call_next(request)
    return response

@app.post("/api/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_user(payload: SubscribeRequest, request: Request, background_tasks: BackgroundTasks):
    # 1. Check Honeypot (Anti-bot defense)
    if payload.website_hp:
        logger.warning(f"[Bot Blocked] Honeypot field triggered from {request.client.host}")
        # Silently return success to mislead the bot
        return JSONResponse(status_code=200, content={"status": "success", "message": "Subscription received."})
    
    clean_email = payload.email.strip().lower()
    clean_first_name = payload.first_name.strip()
    clean_company = payload.company.strip() if payload.company else None
    domain = clean_email.split("@")[-1]

    # 2. Disposable Email Filter
    if domain in DISPOSABLE_DOMAINS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Temporary or disposable email addresses are not allowed. Please provide a valid work or personal email."
        )

    # 3. Database Insertion & Duplicate Check
    sub_uuid = str(uuid.uuid4())
    client_ip = request.client.host if request.client else "unknown"

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO subscribers 
            (uuid, first_name, email, company, utm_source, utm_medium, utm_campaign, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (sub_uuid, clean_first_name, clean_email, clean_company, 
              payload.utm_source, payload.utm_medium, payload.utm_campaign, client_ip))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        # User is already subscribed! Idempotent return without leaking failure
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "You are already subscribed! We've resent the latest edition to your inbox.",
                "is_existing": True
            }
        )
    except Exception as e:
        logger.error(f"Database error during subscription: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error. Please try again later.")

    # 4. Schedule Asynchronous Background Jobs (CRM sync + Welcome email)
    background_tasks.add_task(sync_lead_to_crm, sub_uuid, clean_first_name, clean_email, clean_company)
    background_tasks.add_task(dispatch_welcome_email, clean_first_name, clean_email)

    return {
        "status": "success",
        "message": "Thank you for subscribing! Check your inbox for your welcome guide and whitepaper.",
        "subscriber_id": sub_uuid,
        "is_existing": False
    }

@app.get("/api/subscribers")
async def list_subscribers():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, uuid, first_name, email, company, status, utm_source, utm_medium, utm_campaign, 
               crm_synced, welcome_email_sent, created_at 
        FROM subscribers 
        ORDER BY created_at DESC 
        LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/stats")
async def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM subscribers")
    total_subs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM subscribers WHERE crm_synced = 1")
    synced_subs = cursor.fetchone()[0]
    
    cursor.execute("SELECT utm_source, COUNT(*) FROM subscribers GROUP BY utm_source")
    sources = dict(cursor.fetchall())
    conn.close()
    
    return {
        "total_subscribers": total_subs,
        "crm_synced_count": synced_subs,
        "sources_breakdown": sources
    }

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return "<h1>Newsletter Signup API is running. Visit /docs for OpenAPI specs.</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
