# High-Converting Newsletter Signup Platform & Lead Pipeline
### Reference Implementation for Product Engineer Assignment (Questions 3 & 4)

Built by **Ashutosh Kumar Jaiswal** (`Product Engineer`)  
GitHub: [https://github.com/Ashujais](https://github.com/Ashujais) | LinkedIn: [https://www.linkedin.com/in/ashutosh-kumar-jaiswal/](https://www.linkedin.com/in/ashutosh-kumar-jaiswal/) | Email: [ashutoshhjp00567@gmail.com](mailto:ashutoshhjp00567@gmail.com) | Phone: `+91 6207151423`

---

## 📌 1. Project Overview & Business Alignment

This project directly implements the end-to-end technical approach and system architecture formulated in **Question 3 (Task Approach)** and **Question 4 (Communication for Requirement Gathering)** of the Product Engineer Assignment.

When the Sales team requests a *"Newsletter Signup Page"*, a Product Engineer does not just throw together a static input field. Instead, they engineer a **conversion engine** that:
1. **Minimizes Donor / Prospect Drop-off**: Balances qualification data with low UX friction.
2. **Protects System Integrity**: Defends against bots via invisible honeypots and disallows disposable email domains.
3. **Decouples Third-Party Latency**: Syncs CRM leads (HubSpot/Salesforce) and dispatches transactional emails asynchronously via background workers so API responses stay `< 100ms`.
4. **Maintains Full Attribution**: Preserves UTM campaign tracking (`utm_source`, `utm_medium`, `utm_campaign`) for ROI attribution across marketing channels.
5. **Provides Sales Telemetry**: Features a live CRM Ingestion feed showing incoming leads, company badges, and webhook sync statuses.

---

## 🏗️ 2. Architectural Design

```text
[ Prospect / Visitor ]
         │
         ▼
[ Modern Responsive Landing Page (Tailwind CSS) ]
  ├── Real-time inline field validation
  ├── Anti-bot Honeypot trap (invisible to humans)
  └── Instant Lead Magnet (PDF Benchmark Whitepaper) download
         │  POST /api/subscribe (JSON)
         ▼
[ FastAPI High-Performance Backend ]
  ├── In-Memory Sliding-Window Rate Limiting (per client IP)
  ├── Disposable Domain Blacklist Filter (e.g. mailinator, tempmail)
  ├── SQLite Relational Store (ACID duplicate deduplication)
  └── BackgroundTasks Dispatcher
         │
         ├──► [ Background Worker 1 ]: Async CRM Webhook Sync (HubSpot / Salesforce)
         ├──► [ Background Worker 2 ]: Enterprise Hot-Lead Slack / Teams Notification
         └──► [ Background Worker 3 ]: Transactional Welcome Email + Asset Delivery
```

---

## 🚀 3. Key Technical Capabilities

| Feature | Engineering Implementation | Business Impact |
| :--- | :--- | :--- |
| **Instant Idempotent UX** | Returns clean success if an email is already subscribed without revealing database state. | Zero user confusion; prevents frustrated re-submits. |
| **Bot Honeypot Defense** | Hidden `website_hp` input traps automated scraping scripts silently. | Keeps CRM clean from spam leads without annoying CAPTCHAs. |
| **Disposable Email Filter** | Validates against a blocklist of temporary inbox providers. | Ensures SDRs only spend time reaching out to real corporate leads. |
| **Asynchronous Decoupling** | Heavy CRM API calls and email SMTP dispatch run in background workers. | Blazing-fast page experience (`< 100ms` response times). |
| **Live Sales Telemetry Feed** | Embedded UI drawer querying `/api/subscribers` and `/api/stats`. | Immediate visibility for sales reps to see incoming prospects in real time. |

---

## 🛠️ 4. Quickstart: Running Locally

### Prerequisites
- Python 3.10+ (Dependencies: `fastapi`, `uvicorn`, `pydantic`, `pytest`, `requests`)

### Step 1: Start the Server
```powershell
cd newsletter-signup-app
python main.py
```
*The server will start at: `http://127.0.0.1:8000`*

### Step 2: Open in Browser
- **Landing Page & Signup Form**: Open [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive OpenAPI Documentation**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Live CRM Ingestion Drawer**: Click **"Live CRM Activity"** in the top navigation to view the real-time subscriber ledger.

---

## 🧪 5. Automated Test Suite

To run the automated test suite with full coverage:
```powershell
python -m pytest tests/test_api.py -v
```

### Verified Test Cases:
- `test_subscribe_success`: Validates form submission, database insertion, and unique UUID generation.
- `test_duplicate_subscribe_idempotent`: Validates graceful duplicate handling.
- `test_disposable_email_rejected`: Validates HTTP 400 rejection for disposable email domains.
- `test_honeypot_traps_bot`: Validates that bots triggering the honeypot are rejected from the CRM database.
- `test_stats_and_subscribers_endpoint`: Validates sales analytics and listing queries.

---

## 📂 6. Repository Layout

```text
newsletter-signup-app/
├── main.py                     # FastAPI backend with async CRM dispatch & rate limiting
├── newsletter.db               # SQLite database file with subscribers schema
├── static/
│   ├── index.html              # Modern, responsive B2B landing page (Tailwind CSS)
│   └── whitepaper-mock.txt     # Downloadable engineering whitepaper asset
├── tests/
│   └── test_api.py             # Pytest automated test suite
└── README.md                   # Technical documentation
```

---
© 2026 Ashutosh Kumar Jaiswal. All rights reserved.
