import os
import sys
import uuid
import sqlite3
import pytest

TEST_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_newsletter.db"))
os.environ["NEWSLETTER_DB"] = TEST_DB
os.environ["TESTING"] = "1"

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app, init_db
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    yield
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass

def test_subscribe_success():
    unique_email = f"ashutosh.{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "first_name": "Ashutosh",
        "email": unique_email,
        "company": "Tech Innovators",
        "utm_source": "linkedin_ad",
        "utm_medium": "paid",
        "utm_campaign": "q4_pipeline"
    }
    response = client.post("/api/subscribe", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "Thank you for subscribing" in data["message"]
    assert "subscriber_id" in data

def test_duplicate_subscribe_idempotent():
    unique_email = f"ashutosh.{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "first_name": "Ashutosh",
        "email": unique_email,
        "company": "Tech Innovators"
    }
    # First submission -> 201 Created
    resp1 = client.post("/api/subscribe", json=payload)
    assert resp1.status_code == 201
    
    # Second submission with same email -> 200 OK (idempotent duplicate)
    resp2 = client.post("/api/subscribe", json=payload)
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["status"] == "success"
    assert data["is_existing"] is True

def test_disposable_email_rejected():
    payload = {
        "first_name": "Bot",
        "email": "spammer@mailinator.com"
    }
    response = client.post("/api/subscribe", json=payload)
    assert response.status_code == 400
    assert "Temporary or disposable email" in response.json()["detail"]

def test_honeypot_traps_bot():
    payload = {
        "first_name": "SneakyBot",
        "email": f"sneaky.{uuid.uuid4().hex[:6]}@botnet.org",
        "website_hp": "http://spamsite.xyz" # Honeypot triggered
    }
    response = client.post("/api/subscribe", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify the bot was NOT saved into the database
    subs_resp = client.get("/api/subscribers")
    emails = [s["email"] for s in subs_resp.json()]
    assert payload["email"] not in emails

def test_stats_and_subscribers_endpoint():
    stats_resp = client.get("/api/stats")
    assert stats_resp.status_code == 200
    data = stats_resp.json()
    assert "total_subscribers" in data
    assert "crm_synced_count" in data
