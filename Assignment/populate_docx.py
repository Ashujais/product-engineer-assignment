import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import shutil
import os

source_path = r'Assignment\Assignment\Assignment I - Product Engineer.docx'
backup_path = r'Assignment\Assignment\Assignment I - Product Engineer - Original.docx'
completed_path = r'Assignment\Assignment\Assignment I - Product Engineer - Completed.docx'

if not os.path.exists(backup_path):
    shutil.copy2(source_path, backup_path)
    print(f"Created backup at {backup_path}")

doc = docx.Document(source_path)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_styled_paragraph(cell, text, bold_prefix="", space_after=6, font_size=10, is_code=False):
    p = cell.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.bold = True
        r_bold.font.name = 'Calibri'
        r_bold.font.size = Pt(font_size)
        r_bold.font.color.rgb = RGBColor(30, 41, 59)
    if text:
        r_text = p.add_run(text)
        r_text.font.name = 'Consolas' if is_code else 'Calibri'
        r_text.font.size = Pt(font_size - 1 if is_code else font_size)
        r_text.font.color.rgb = RGBColor(15, 23, 42) if not is_code else RGBColor(51, 65, 85)
    return p

# 1. Update Candidate Details (Paragraphs 20-24)
candidate_info = {
    20: "Name: Ashutosh Kumar Jaiswal",
    21: "Phone: +91 6207151423",
    22: "Email: ashutoshhjp00567@gmail.com",
    23: "LinkedIn Profile URL: https://www.linkedin.com/in/ashutosh-kumar-jaiswal/",
    24: "Github (or any public Git repositories showing your work) URL: https://github.com/Ashujais"
}

for p_idx, text in candidate_info.items():
    p = doc.paragraphs[p_idx]
    p.text = text
    p.runs[0].font.name = 'Calibri'
    p.runs[0].font.size = Pt(11)
    p.runs[0].font.bold = True
    p.runs[0].font.color.rgb = RGBColor(15, 23, 42)

# 2. Table 0: Question 2 (Code Change)
cell_q2 = doc.tables[0].rows[0].cells[0]
cell_q2.text = ""  # clear
set_cell_margins(cell_q2)

add_styled_paragraph(cell_q2, "Git Commit Message:", "", space_after=4, font_size=11)
commit_msg = """fix(math): guard multiplyByFive against non-integer arguments

Add an explicit runtime check using is_int() to ensure $arg is an integer before computing the product. If a non-integer value is provided, return -1 as an error indicator to prevent unexpected type juggling or runtime type errors under strict typing."""
add_styled_paragraph(cell_q2, commit_msg, "", space_after=10, font_size=9.5, is_code=True)

add_styled_paragraph(cell_q2, "Bonus - Technical Concerns Regarding the Final Version:", "", space_after=4, font_size=11)

concerns = [
    ("1. Sentinel Value Anti-Pattern (-1): ", "Returning -1 creates ambiguity. If the function receives -0.2 (or negative numbers in extended logic), the mathematical result is -1. A caller checking if ($result === -1) cannot distinguish between an error condition and a legitimate calculation. Furthermore, in PHP, -1 evaluates to true in loose boolean conditionals (if (multiplyByFive('foo'))), causing silent downstream state corruption."),
    ("2. Bypassing PHP's Native Type System: ", "The function specifies a return type hint (: int), but leaves the parameter $arg untyped, relying on manual runtime inspection (!is_int($arg)). In modern PHP (7.0+ / 8.x), the idiomatic and performant approach is declaring the parameter type directly: function multiplyByFive(int $arg): int with declare(strict_types=1);. The PHP engine will natively enforce type contracts at call time, eliminating manual boilerplate."),
    ("3. Violation of Fail-Fast Principle (Exceptions vs Error Codes): ", "Silently returning an arbitrary number forces every downstream consumer to write defensive checks. Modern software engineering best practice requires failing fast by throwing an InvalidArgumentException or TypeError when invalid data is supplied."),
    ("4. Float Multiplication Rejection: ", "If a numeric float (e.g. 2.5) is passed, is_int(2.5) evaluates to false, returning -1 instead of 12.5. If decimal operations are valid, union types (int|float) or float casting should be supported."),
    ("5. Integer Overflow: ", "In PHP, if $arg * 5 exceeds PHP_INT_MAX (9,223,372,036,854,775,807 on 64-bit systems), PHP automatically promotes the result to a float. Because the return type hint is strictly : int, this will throw an unhandled fatal TypeError: Return value of multiplyByFive() must be of the type int, float returned.")
]

for prefix, text in concerns:
    add_styled_paragraph(cell_q2, text, prefix, space_after=6, font_size=10)

add_styled_paragraph(cell_q2, "What I Would Do Differently (Production-Grade Implementation):", "", space_after=4, font_size=11)
code_diff = """<?php
declare(strict_types=1);

namespace App\Math;

use InvalidArgumentException;
use TypeError;

/**
 * Multiplies an integer by five.
 *
 * @param int $arg The integer to multiply.
 * @return int The product of $arg and 5.
 * @throws TypeError If a non-integer is passed in strict typing mode.
 */
function multiplyByFive(int $arg): int {
    return $arg * 5;
}

// Alternatively, if defensive handling of mixed untyped inputs is required:
function multiplyByFiveDefensive(mixed $arg): int {
    if (!is_int($arg)) {
        throw new InvalidArgumentException(
            sprintf('Argument must be an integer, %s given.', get_debug_type($arg))
        );
    }
    return $arg * 5;
}"""
add_styled_paragraph(cell_q2, code_diff, "", space_after=4, font_size=9, is_code=True)


# 3. Table 1: Question 3 (Task Approach)
cell_q3 = doc.tables[1].rows[0].cells[0]
cell_q3.text = ""
set_cell_margins(cell_q3)

intro_q3 = "As a Product Engineer, building features without context often leads to wasted engineering cycles, poor conversion rates, or misaligned lead qualification. An underspecified request requires a structured, consultative approach that balances commercial sales objectives, UX friction, data privacy, and scalable technical architecture."
add_styled_paragraph(cell_q3, intro_q3, "", space_after=8, font_size=10)

q3_steps = [
    ("Step 1: Context Gathering & Commercial Alignment (Discovery)", 
     "• Understand the Core Objective: Clarify why Sales needs this page (e.g. B2B enterprise pipeline acceleration, webinar/event registrations, product launch updates, or general lead generation).\n"
     "• Target Audience & Channels: Determine whether traffic comes from outbound cold outreach (SDRs), paid performance ads, organic blog traffic, or offline conference QR codes.\n"
     "• Define Success Metrics: Align on target conversion rate (e.g., 3-5%), projected weekly subscriber volume, and qualification criteria for Marketing Qualified Leads (MQLs) vs. Sales Qualified Leads (SQLs)."),
    
    ("Step 2: Define Requirements & Scope Boundaries (Functional & Non-Functional)",
     "• Form Field Strategy: Balance lead qualification against conversion friction. Minimal MVP: Work Email. B2B Tier: First Name, Work Email, Company Name, and Job Role/Size.\n"
     "• Integrations & Lead Handoff: Connect submissions directly to Sales CRM (HubSpot, Salesforce, Marketo), internal PostgreSQL backup table, and Slack alerts for enterprise domains.\n"
     "• Post-Signup Journey: Immediate on-page confirmation UI, redirect to high-value lead magnet (e.g., Whitepaper/Report download), and automated welcome email with double opt-in.\n"
     "• Compliance & Privacy: Implement strict GDPR, CAN-SPAM, and CCPA compliance (explicit opt-in consent checkbox, privacy policy link, 1-click unsubscribe mechanism, audit trail).\n"
     "• Security & Anti-Abuse: Cloudflare Turnstile / reCAPTCHA v3 bot protection, honeypot fields, rate limiting per IP (max 5/min), and MX record validation to disallow disposable email domains."),
    
    ("Step 3: Rapid Prototyping & Wireframing",
     "• Create a mobile-first, low-fidelity wireframe in Figma or interactive mockup showcasing headline, value proposition, form fields, social proof metrics, and confirmation states.\n"
     "• Draft the technical API contract (POST /api/v1/newsletter/subscribe) and data schema."),
    
    ("Step 4: Stakeholder Alignment & Sign-Off",
     "• Present the wireframe and proposed scope to the Sales lead in a 15-minute alignment sync.\n"
     "• Establish agreement on MVP deliverables (launch within 5 days) vs. Phase 2 enhancements (A/B testing, personalized email drip flows)."),
    
    ("Step 5: Technical Implementation (Iterative Engineering Sprint)",
     "• Frontend: Semantic, accessible (WCAG 2.1 AA) responsive landing page built with modern framework (React/Next.js/Tailwind). Features instant client-side validation and responsive layout.\n"
     "• Backend API & Async Queue: Express/FastAPI endpoint with rate limiting and payload validation. Asynchronous task queue (Redis/BullMQ) to sync CRM leads in background without blocking user response times (<200ms).\n"
     "• Analytics & Telemetry: Instrument Segment/PostHog/GA4 event tracking (Pageview, Form Focus, Submit Attempt, Success, Error)."),
    
    ("Step 6: QA, Cross-Browser Testing & Security Verification",
     "• Test validation edge cases: duplicate submissions, malformed emails, uppercase strings, XSS/SQLi injection vectors, and slow 3G mobile networks.\n"
     "• End-to-end integration test: Verify that submitted leads correctly populate in the Sales CRM with all attribution parameters (UTM source, medium, campaign) intact."),
    
    ("Step 7: Deployment & Staging Review",
     "• Deploy to a staging environment for Sales team preview and acceptance sign-off.\n"
     "• Production release via zero-downtime CI/CD deployment with Datadog/Sentry monitoring."),
    
    ("Step 8: Post-Launch Review & Iteration",
     "• Monitor error rates, bounce rates, and funnel conversion metrics in real time.\n"
     "• Conduct a 7-day post-launch review with the Sales team to assess lead volume and lead quality, followed by A/B copy tests on headlines and CTA buttons.")
]

for title, body in q3_steps:
    add_styled_paragraph(cell_q3, body, title + "\n", space_after=6, font_size=9.5)


# 4. Table 2: Question 4 (Communication For Requirement Gathering)
cell_q4 = doc.tables[2].rows[0].cells[0]
cell_q4.text = ""
set_cell_margins(cell_q4)

email_content = """Subject: [Kickoff] Newsletter Signup Page – Requirements & Proposed 5-Day Launch Plan

Hi Sales Team,

Thanks for reaching out! A dedicated Newsletter Signup page is an excellent initiative to accelerate our inbound lead pipeline and engage prospective customers.

To ensure we build an experience that maximizes conversion while capturing the exact data your team needs for sales workflows, I’ve put together a recommended baseline along with a few key questions.

Rather than starting from a blank slate, here is our recommended MVP (Phase 1) Proposal:
• Form Fields: Work Email + First Name (keeps form friction low while enabling personalized SDR outreach).
• CRM & Routing: Real-time webhook sync into your CRM (HubSpot/Salesforce) tagged with "Source: Newsletter", plus automated Slack notifications for high-value enterprise domain signups.
• User Experience: Instant on-page confirmation UI + automated transactional welcome email delivering our latest industry benchmark whitepaper.
• Compliance & Security: Bot protection via Cloudflare Turnstile, honeypot fields, and strict GDPR / CAN-SPAM compliance.

Key Inputs Needed From Your Side:
1. Target Audience & Traffic Source: Who is the primary persona (e.g., Enterprise CTOs, Mid-market VP Sales, or general consumers), and where will visitors arrive from (cold outbound campaigns, paid LinkedIn ads, or social media)?
2. Required Lead Fields: Are Work Email and First Name sufficient for MVP, or do you strictly require Company Name, Job Title, or Team Size upfront? (Note: Each additional field typically reduces conversion rates by 5–10%.)
3. CRM Properties & Lead Assignment: Which CRM list or pipeline stage should these contacts be mapped to, and which sales rep / team should be assigned ownership?
4. Incentive / Copy: Do you have specific headlines or a lead magnet ready (e.g., "Get our 2026 Industry Report"), or would you like engineering/marketing to provide placeholder copy for your review?

Proposed Timeline & Milestones (5-Day Delivery):
• Day 1 (Tomorrow, 2:00 PM): Consolidate feedback and lock in requirements.
• Day 2: Share interactive wireframe and API schema for your sign-off.
• Day 3–4: Engineering sprint (frontend landing page, backend API, CRM sync, and analytics tracking).
• Day 5: Staging walkthrough with the Sales team, QA verification, and Production Launch.

Could you share your thoughts by tomorrow at 12:00 PM? Alternatively, I am happy to hop on a quick 15-minute sync—feel free to grab time on my calendar [Calendar Link] or reply directly here.

Looking forward to launching this together!

Best regards,
Ashutosh Kumar Jaiswal
Product Engineer
ashutoshhjp00567@gmail.com | +91 6207151423"""

add_styled_paragraph(cell_q4, email_content, "", space_after=4, font_size=9.5)


# 5. Table 3: Question 5 (Exercise: UI/UX Assessment)
table_q5 = doc.tables[3]
# Ensure table has header + rows
table_q5.autofit = False

q5_data = [
    ("1", "Geolocation-First Funnel Gating", 
     "The donation journey begins by detecting or asking for the user's location/pin code before asking for item details. This is an excellent usability pattern because it prevents users from going through a multi-step cataloging process only to discover at the end that their area is unserviceable.", 
     "Good"),
    
    ("2", "Multi-Fulfillment Options (Doorstep / Drop / Campaigns)", 
     "Offering three distinct pathways ('Pickup from Doorstep', 'Live Campaigns', and 'Drop yourself') caters effectively to diverse donor personas—from busy professionals willing to pay for convenience to budget-conscious donors who prefer free drop-offs.", 
     "Good"),
    
    ("3", "Clear Item Condition & Age Tagging", 
     "Allowing donors to specify item state ('Brand New', 'Barely Used', 'Well Used') and age brackets gives valuable operational data to sorting teams and partner NGOs, ensuring dignity for recipients and reducing logistics rejection.", 
     "Good"),
    
    ("4", "Late Fee Disclosure / Price Shock at Checkout", 
     "The platform communicates 'Donate' as a charitable act, but surprises the user with a mandatory convenience/pickup logistics fee only at the very final checkout step. This late pricing shock causes friction, drops trust, and triggers cart abandonment. Displaying transparent copy upfront (e.g., 'Doorstep pickup supported by a small ₹199 logistics contribution') would drastically reduce drop-offs.", 
     "Bad"),
    
    ("5", "Mandatory Mobile OTP Barrier at Final Step", 
     "Requiring users to enter their mobile number and wait for an SMS OTP right before placing the order introduces unnecessary drop-off friction. If SMS delivery is delayed or signal is weak, the entire donation flow fails. Implementing 1-click social login (Google OAuth) or delayed verification post-booking would improve checkout completion.", 
     "Bad"),
    
    ("6", "Repetitive Modal Dialogs for Multi-Category Donors", 
     "Adding multiple distinct items (e.g., clothes, books, and electronics) forces the user to navigate through repetitive modal overlays to input condition, brand, and age for each item individually. For a household decluttering session with 10+ items, this creates high cognitive fatigue.", 
     "Bad"),
    
    ("7", "Opaque NGO / Cause Allocation During Booking", 
     "The donor is not shown which specific NGO, orphanage, or community organization will receive their items during the booking flow. Showing paired NGO cards or impact stories during checkout would create an emotional bond and boost repeat donations.", 
     "Neutral"),
    
    ("8", "Feature Suggestion: AI-Powered Photo Donation Estimation", 
     "Instead of manually browsing categories and item dropdowns, allow donors to snap a picture of their donation box/bag. Computer vision can automatically estimate volume, category breakdown, and assign the appropriate vehicle/bag size for pickup.", 
     "Neutral"),
    
    ("9", "Feature Suggestion: Instant Environmental & Social Impact Counter", 
     "Integrate dynamic impact metrics during item selection (e.g., 'Donating 10 clothes saves ~7,000 liters of water and provides warmth to 2 school children'). Gamifying and quantifying social/environmental impact in real time significantly increases motivation to finish the flow.", 
     "Neutral")
]

# Adjust rows in table 3
# currently table_q5 has 4 rows: row 0 is header, rows 1-3 are empty
while len(table_q5.rows) > 1:
    # remove existing empty rows
    tr = table_q5.rows[-1]._tr
    tr.getparent().remove(tr)

# Now append all 9 rows
for item_num, summary, desc, item_type in q5_data:
    row = table_q5.add_row()
    cells = row.cells
    cells[0].text = item_num
    cells[1].text = summary
    cells[2].text = desc
    cells[3].text = item_type
    
    for c_idx, cell in enumerate(cells):
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r = p.runs[0]
        r.font.name = 'Calibri'
        r.font.size = Pt(9.5)
        if c_idx == 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r.bold = True
        elif c_idx == 1:
            r.bold = True
            r.font.color.rgb = RGBColor(15, 23, 42)
        elif c_idx == 3:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r.bold = True
            if item_type == "Good":
                r.font.color.rgb = RGBColor(22, 101, 52)
            elif item_type == "Bad":
                r.font.color.rgb = RGBColor(153, 27, 27)
            else:
                r.font.color.rgb = RGBColor(133, 77, 14)


# 6. Table 4: Question 6 (Exercise: Backend Design)
cell_q6 = doc.tables[4].rows[0].cells[0]
cell_q6.text = ""
set_cell_margins(cell_q6)

q6_intro = """1. ARCHITECTURAL CONTEXT & MODELING STRATEGY:
• Platform: Milaap (Online crowdfunding platform primarily for medical emergencies, personal causes, education, and memorials).
• Database Choice: Relational DBMS (PostgreSQL) is strictly recommended due to ACID transactional consistency required for monetary donations, strict audit trails, multi-currency processing, and tax exemption (80G) reporting.
• Data Modeling Approach: Highly normalized 3NF schema for transactional integrity, paired with strategic denormalization (cached aggregate counters raised_amount and donors_count on the campaigns table) to support sub-10ms query times on the high-traffic /crowdfunding/fundraisers listing page.

2. ENTITY RELATIONSHIP OVERVIEW:
[users] 1 ──── N [campaigns] (as campaigner/organizer)
[categories] 1 ──── N [campaigns]
[campaigns] 1 ──── 1 [beneficiaries]
[campaigns] 1 ──── N [campaign_media]
[campaigns] 1 ──── N [donations]
[users] 1 ──── N [donations] (as donor, optional/guest)
[campaigns] 1 ──── N [campaign_updates]
[campaigns] N ──── M [tags] (via campaign_tags)"""

add_styled_paragraph(cell_q6, q6_intro, "", space_after=8, font_size=9.5)

q6_sql = """-- 1. USERS TABLE (Campaigners, Donors, Administrators)
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255),
    profile_image_url TEXT,
    kyc_status VARCHAR(30) DEFAULT 'PENDING' CHECK (kyc_status IN ('PENDING', 'VERIFIED', 'REJECTED')),
    role VARCHAR(30) DEFAULT 'USER' CHECK (role IN ('USER', 'CAMPAIGNER', 'DONOR', 'ADMIN', 'VERIFIER')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. CATEGORIES TABLE (Medical, Memorials, Education, Emergency, etc.)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE,
    tag_line TEXT,
    icon_url TEXT,
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. BENEFICIARIES TABLE (The patient or recipient of funds)
CREATE TABLE beneficiaries (
    id BIGSERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    relationship_to_campaigner VARCHAR(50) NOT NULL, -- 'myself', 'family_member', 'friend', 'organisation'
    age INT,
    gender VARCHAR(20),
    medical_condition TEXT,
    hospital_name VARCHAR(200),
    treating_doctor VARCHAR(150),
    hospital_city VARCHAR(100),
    verification_documents_url TEXT[],
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. CAMPAIGNS TABLE (Fundraisers - Powers the listing page cards)
CREATE TABLE campaigns (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    story_summary TEXT NOT NULL,
    story_html TEXT,
    campaigner_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    beneficiary_id BIGINT REFERENCES beneficiaries(id) ON DELETE SET NULL,
    category_id INT NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    
    -- Financial metrics
    currency CHAR(3) DEFAULT 'INR' NOT NULL,
    goal_amount NUMERIC(14, 2) NOT NULL CHECK (goal_amount > 0),
    raised_amount NUMERIC(14, 2) DEFAULT 0.00 NOT NULL CHECK (raised_amount >= 0),
    donors_count INT DEFAULT 0 NOT NULL CHECK (donors_count >= 0),
    shares_count INT DEFAULT 0 NOT NULL CHECK (shares_count >= 0),
    
    -- Visuals & badges
    cover_image_url TEXT NOT NULL,
    video_url TEXT,
    tax_exemption_eligible BOOLEAN DEFAULT FALSE, -- 80G tax benefit tag
    is_emergency BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE, -- Milaap Verified badge
    featured_rank INT DEFAULT 0, -- Higher rank for promoted fundraisers
    
    -- Status & Lifecycle
    status VARCHAR(30) DEFAULT 'ACTIVE' CHECK (status IN ('DRAFT', 'UNDER_REVIEW', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CLOSED', 'REJECTED')),
    start_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. CAMPAIGN MEDIA TABLE (Gallery, hospital receipts, videos)
CREATE TABLE campaign_media (
    id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    media_type VARCHAR(20) NOT NULL CHECK (media_type IN ('IMAGE', 'VIDEO', 'DOCUMENT')),
    media_url TEXT NOT NULL,
    caption VARCHAR(255),
    display_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. DONATIONS TABLE (Financial transaction ledger)
CREATE TABLE donations (
    id BIGSERIAL PRIMARY KEY,
    transaction_uuid UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    campaign_id BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    donor_id BIGINT REFERENCES users(id) ON DELETE SET NULL, -- Nullable for guest donors
    
    -- Donor display attributes
    donor_name VARCHAR(150) NOT NULL DEFAULT 'Anonymous',
    donor_email VARCHAR(255),
    donor_phone VARCHAR(20),
    is_anonymous BOOLEAN DEFAULT FALSE,
    
    -- Transaction breakdown
    currency CHAR(3) DEFAULT 'INR' NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    tip_to_milaap NUMERIC(10, 2) DEFAULT 0.00 CHECK (tip_to_milaap >= 0),
    gateway_fee NUMERIC(10, 2) DEFAULT 0.00,
    net_campaign_amount NUMERIC(12, 2) GENERATED ALWAYS AS (amount) STORED,
    
    -- Payment gateway integration
    payment_gateway VARCHAR(50) NOT NULL, -- 'RAZORPAY', 'STRIPE', 'PAYU', 'UPI'
    gateway_transaction_id VARCHAR(150) UNIQUE,
    payment_status VARCHAR(30) DEFAULT 'INITIATED' CHECK (payment_status IN ('INITIATED', 'SUCCESS', 'FAILED', 'REFUNDED')),
    
    -- Tax exemption
    wants_80g_receipt BOOLEAN DEFAULT FALSE,
    pan_number_encrypted TEXT,
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. CAMPAIGN UPDATES TABLE (Hospital progress, updates to backers)
CREATE TABLE campaign_updates (
    id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    author_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title VARCHAR(200) NOT NULL,
    content_html TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8. TAGS & CAMPAIGN_TAGS (Tax Benefit, Urgent, Milaap Assured)
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(60) UNIQUE NOT NULL,
    badge_color VARCHAR(20)
);

CREATE TABLE campaign_tags (
    campaign_id BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    tag_id INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (campaign_id, tag_id)
);"""

add_styled_paragraph(cell_q6, q6_sql, "", space_after=8, font_size=8.5, is_code=True)

q6_perf = """3. STRATEGIC INDEXING & PERFORMANCE OPTIMIZATIONS:
-- Ultra-fast card listing query (ACTIVE campaigns ordered by featured rank & recency)
CREATE INDEX idx_campaigns_status_created ON campaigns (status, featured_rank DESC, created_at DESC) 
    WHERE status = 'ACTIVE';

-- Category filter index
CREATE INDEX idx_campaigns_category_status ON campaigns (category_id, status) 
    WHERE status = 'ACTIVE';

-- Unique index for instant SEO slug lookups
CREATE UNIQUE INDEX idx_campaigns_slug ON campaigns (slug);

-- Full-text search index for live title/summary search bar
CREATE INDEX idx_campaigns_fts ON campaigns USING GIN (to_tsvector('english', title || ' ' || story_summary));

-- Fast donation lookup index
CREATE INDEX idx_donations_campaign_status ON donations (campaign_id, payment_status) 
    WHERE payment_status = 'SUCCESS';

4. CONCURRENCY & DATA CONSISTENCY STRATEGY:
• Atomic Aggregate Increments: Rather than executing expensive SELECT SUM(amount), COUNT(*) FROM donations queries across hundreds of active campaigns on every page load, successful payment gateway webhooks trigger atomic increments:
    UPDATE campaigns 
    SET raised_amount = raised_amount + NEW.amount, 
        donors_count = donors_count + 1, 
        updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.campaign_id;
• Edge Caching Layer: High-throughput listing endpoints (/crowdfunding/fundraisers) are cached in Redis with a 30-60 second TTL, combined with HTTP Cache-Control: public, s-maxage=60, stale-while-revalidate=30 headers."""

add_styled_paragraph(cell_q6, q6_perf, "", space_after=4, font_size=9.5)

# Save both to Completed and original
doc.save(completed_path)
print(f"Saved completed docx to {completed_path}")

doc.save(source_path)
print(f"Updated original docx at {source_path}")
