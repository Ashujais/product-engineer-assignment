# Product Engineer Take-Home Assignment & Full-Stack Reference System

**Candidate:** Ashutosh Kumar Jaiswal  
**Email:** [ashutoshhjp00567@gmail.com](mailto:ashutoshhjp00567@gmail.com)  
**GitHub:** [https://github.com/Ashujais](https://github.com/Ashujais)  
**Role:** Product Engineer  

---

## 📁 Submission Deliverables

| Deliverable | File Path | Description |
| :--- | :--- | :--- |
| **Submission PDF (Ready)** | [`Assignment/XXXX - Ashutosh Kumar Jaiswal - FirstAssignment - ProductEngineer.pdf`](file:///F:/Share_FullStack/Assignment/XXXX%20-%20Ashutosh%20Kumar%20Jaiswal%20-%20FirstAssignment%20-%20ProductEngineer.pdf) | Publication-grade 10-page PDF formatted strictly to submission instructions. *(Replace `XXXX` with your last 4 phone digits).* |
| **Submission PDF (Standard)** | [`Assignment/Assignment - Ashutosh Kumar Jaiswal - FirstAssignment - ProductEngineer.pdf`](file:///F:/Share_FullStack/Assignment/Assignment%20-%20Ashutosh%20Kumar%20Jaiswal%20-%20FirstAssignment%20-%20ProductEngineer.pdf) | Standard named publication PDF. |
| **Completed Word Document** | [`Assignment/Assignment/Assignment I - Product Engineer - Completed.docx`](file:///F:/Share_FullStack/Assignment/Assignment/Assignment%20I%20-%20Product%20Engineer%20-%20Completed.docx) | Fully populated Microsoft Word `.docx` file matching original template formatting. |
| **Updated Original Document** | [`Assignment/Assignment/Assignment I - Product Engineer.docx`](file:///F:/Share_FullStack/Assignment/Assignment/Assignment%20I%20-%20Product%20Engineer.docx) | Original document updated with all answers in place. |
| **Full-Stack Reference Demo** | [`newsletter-signup-app/`](file:///F:/Share_FullStack/newsletter-signup-app/) | Complete working full-stack implementation of the Newsletter Signup platform with FastAPI backend, Tailwind frontend, CRM webhook simulation, and automated test suite. |

---

## 📋 Comprehensive Assignment Solutions

### 1. Candidate Details
- **Name:** Ashutosh Kumar Jaiswal
- **Phone:** +91 [Your 10-Digit Mobile Number]
- **Email:** ashutoshhjp00567@gmail.com
- **LinkedIn Profile URL:** https://www.linkedin.com/in/[your-linkedin-handle]
- **GitHub URL:** https://github.com/Ashujais

---

### 2. Question: Code Change

#### Context & Code Examination
- **Before:**
  ```php
  <?php
  function multiplyByFive($arg): int {
      return $arg * 5;
  }
  ```
- **After:**
  ```php
  <?php
  function multiplyByFive($arg): int {
      return (!is_int($arg) ? -1 : $arg * 5);
  }
  ```

#### Recommended Git Commit Message
```text
fix(math): guard multiplyByFive against non-integer arguments

Add an explicit runtime check using is_int() to verify that $arg is an integer before computing the product. If a non-integer value is provided, return -1 as an error indicator to avoid unintended type coercion or runtime type errors under strict typing.
```

#### Bonus: Concerns Regarding the Final Version & Technical Critique
1. **Sentinel Value Anti-Pattern (`-1`)**: Returning `-1` conflates legitimate computational outputs with error states. If `$arg = -0.2`, the mathematical result is `-1`. A caller checking `if ($result === -1)` cannot distinguish whether an error occurred or if `-1` was a valid calculation. Furthermore, `-1` evaluates to `true` in loose boolean conditionals (`if (multiplyByFive("abc"))`), allowing failures to pass through truthy checks silently and corrupt downstream business logic.
2. **Bypassing PHP's Native Type System**: The function specifies a return type hint (`: int`), but leaves parameter `$arg` untyped, relying on manual runtime inspection (`!is_int($arg)`). In modern PHP (7.0+ / 8.x), the idiomatic and performant approach is declaring the parameter type directly: `function multiplyByFive(int $arg): int` with `declare(strict_types=1);`. The Zend Engine natively enforces type contracts at call time without manual boilerplate.
3. **Violation of Fail-Fast Principle (Exceptions vs Error Codes)**: Silently returning an arbitrary number forces every downstream consumer to write defensive checks. Modern engineering best practice requires failing fast by throwing an `InvalidArgumentException` or `TypeError` when invalid data is supplied.
4. **Numeric Float Inflexibility**: If a numeric float (e.g. `2.5`) is passed, `is_int(2.5)` evaluates to false, returning `-1` instead of `12.5`. If decimal operations are valid, union types (`int|float`) or float casting should be supported.
5. **Integer Overflow**: In PHP, if `$arg * 5` exceeds `PHP_INT_MAX` (`9,223,372,036,854,775,807` on 64-bit systems), PHP automatically promotes the result to a float. Because the return type hint is strictly `: int`, this triggers a fatal `TypeError: Return value of multiplyByFive() must be of the type int, float returned`.

#### What I Would Do Differently (Production-Grade Code)
```php
<?php
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
}
```

---

### 3. Question: Task Approach (Newsletter Signup Page)

**Strategic Overview:** An underspecified request requires a structured, consultative approach balancing commercial sales objectives, UX friction, data privacy, and scalable technical architecture.

1. **Step 1: Context Gathering & Commercial Alignment (Discovery)**
   - Understand the core objective (enterprise pipeline acceleration vs. product announcements).
   - Target audience & acquisition channels (cold SDR emails, LinkedIn ads, blog organic search).
   - Success metrics (conversion targets, MQL vs. SQL criteria).
2. **Step 2: Define Requirements & Scope Boundaries (Functional & Non-Functional)**
   - Form field strategy (Work Email + First Name for low friction; optional Company/Role).
   - Downstream CRM integrations (HubSpot, Salesforce) + Slack alerts for enterprise domains.
   - Post-signup journey (on-page confirmation, lead magnet download, welcome email).
   - Privacy & security (GDPR / CAN-SPAM compliance, honeypots, disposable email filtering).
3. **Step 3: Rapid Prototyping & Wireframing**
   - Create mobile-first low-fidelity wireframe and draft technical API contracts (`POST /api/v1/newsletter/subscribe`).
4. **Step 4: Stakeholder Alignment & Sign-Off**
   - 15-minute sync with Sales lead to lock in MVP scope (5-day sprint) vs. Phase 2 enhancements.
5. **Step 5: Technical Implementation (Iterative Engineering Sprint)**
   - Frontend landing page with inline client-side validation and WCAG 2.1 AA accessibility.
   - Backend API with asynchronous background worker queues for CRM ingestion (`< 100ms` response times).
   - Telemetry instrumentation (GA4, PostHog, Segment).
6. **Step 6: QA, Cross-Browser Testing & Security Verification**
   - Edge case validation (duplicate submissions, SQLi/XSS prevention, slow networks, mobile viewports).
7. **Step 7: Deployment & Staging Review**
   - Staging sign-off, followed by zero-downtime production deployment.
8. **Step 8: Post-Launch Review & Iteration**
   - 7-day review with Sales on lead quality; execute A/B copy tests.

---

### 4. Question: Communication for Requirement Gathering

**Subject:** [Kickoff] Newsletter Signup Page – Requirements & Proposed 5-Day Launch Plan

**Hi Sales Team,**

Thanks for reaching out! A dedicated Newsletter Signup page is an excellent initiative to accelerate our inbound lead pipeline and engage prospective customers.

To ensure we build an experience that maximizes conversion while capturing the exact data your team needs for sales workflows, I’ve put together a recommended baseline along with a few key questions.

Rather than starting from a blank slate, here is our recommended **MVP (Phase 1) Proposal**:
- **Form Fields:** Work Email + First Name (keeps form friction low while enabling personalized SDR outreach).
- **CRM & Routing:** Real-time webhook sync into your CRM (HubSpot/Salesforce) tagged with *"Source: Newsletter"*, plus automated Slack notifications for high-value enterprise domain signups.
- **User Experience:** Instant on-page confirmation UI + automated transactional welcome email delivering our latest industry benchmark whitepaper.
- **Compliance & Security:** Bot protection via Cloudflare Turnstile, honeypot fields, and strict GDPR / CAN-SPAM compliance.

**Key Inputs Needed From Your Side:**
1. **Target Audience & Traffic Source:** Who is the primary persona (e.g., Enterprise CTOs, Mid-market VP Sales, or general consumers), and where will visitors arrive from (cold outbound campaigns, paid LinkedIn ads, or social media)?
2. **Required Lead Fields:** Are Work Email and First Name sufficient for MVP, or do you strictly require Company Name, Job Title, or Team Size upfront? *(Note: Each additional field typically reduces conversion rates by 5–10%.)*
3. **CRM Properties & Lead Assignment:** Which CRM list or pipeline stage should these contacts be mapped to, and which sales rep / team should be assigned ownership?
4. **Incentive / Copy:** Do you have specific headlines or a lead magnet ready (e.g., *"Get our 2026 Industry Report"*), or would you like engineering/marketing to provide placeholder copy for your review?

**Proposed Timeline & Milestones (5-Day Delivery):**
- **Day 1 (Tomorrow, 2:00 PM):** Consolidate feedback and lock in requirements.
- **Day 2:** Share interactive wireframe and API schema for your sign-off.
- **Day 3–4:** Engineering sprint (frontend landing page, backend API, CRM sync, and analytics tracking).
- **Day 5:** Staging walkthrough with the Sales team, QA verification, and Production Launch.

Could you share your thoughts by **tomorrow at 12:00 PM**? Alternatively, I am happy to hop on a quick 15-minute sync—feel free to grab time on my calendar [Calendar Link] or reply directly here.

Looking forward to launching this together!

Best regards,  
**Ashutosh Kumar Jaiswal**  
Product Engineer  
ashutoshhjp00567@gmail.com | +91 [Phone Number]

---

### 5. Exercise: UI/UX Assessment (ShareAtDoorStep)

Website: [https://shareatdoorstep.com/donate/](https://shareatdoorstep.com/donate/)

| # | Summary | Description | Type |
| :-: | :--- | :--- | :-: |
| **1** | **Geolocation-First Funnel Gating** | The donation journey begins by detecting or asking for the user's location/pin code before asking for item details. This is an excellent usability pattern because it prevents users from going through a multi-step cataloging process only to discover at the end that their area is unserviceable. | **Good** |
| **2** | **Multi-Fulfillment Options (Doorstep / Drop / Campaigns)** | Offering three distinct pathways ('Pickup from Doorstep', 'Live Campaigns', and 'Drop yourself') caters effectively to diverse donor personas—from busy professionals willing to pay for convenience to budget-conscious donors who prefer free drop-offs. | **Good** |
| **3** | **Clear Item Condition & Age Tagging** | Allowing donors to specify item state ('Brand New', 'Barely Used', 'Well Used') and age brackets gives valuable operational data to sorting teams and partner NGOs, ensuring dignity for recipients and reducing logistics rejection. | **Good** |
| **4** | **Late Fee Disclosure / Price Shock at Checkout** | The platform communicates 'Donate' as a charitable act, but surprises the user with a mandatory convenience/pickup logistics fee only at the very final checkout step. This late pricing shock causes friction, drops trust, and triggers cart abandonment. Displaying transparent copy upfront (e.g., 'Doorstep pickup supported by a small Rs. 199 logistics contribution') would drastically reduce drop-offs. | **Bad** |
| **5** | **Mandatory Mobile OTP Barrier at Final Step** | Requiring users to enter their mobile number and wait for an SMS OTP right before placing the order introduces unnecessary drop-off friction. If SMS delivery is delayed or signal is weak, the entire donation flow fails. Implementing 1-click social login (Google OAuth) or delayed verification post-booking would improve checkout completion. | **Bad** |
| **6** | **Repetitive Modal Dialogs for Multi-Category Donors** | Adding multiple distinct items (e.g., clothes, books, and electronics) forces the user to navigate through repetitive modal overlays to input condition, brand, and age for each item individually. For a household decluttering session with 10+ items, this creates high cognitive fatigue. | **Bad** |
| **7** | **Opaque NGO / Cause Allocation During Booking** | The donor is not shown which specific NGO, orphanage, or community organization will receive their items during the booking flow. Showing paired NGO cards or impact stories during checkout would create an emotional bond and boost repeat donations. | **Neutral** |
| **8** | **Feature Suggestion: AI-Powered Photo Donation Estimation** | Instead of manually browsing categories and item dropdowns, allow donors to snap a picture of their donation box/bag. Computer vision can automatically estimate volume, category breakdown, and assign the appropriate vehicle/bag size for pickup. | **Neutral (Feature)** |
| **9** | **Feature Suggestion: Instant Environmental & Social Impact Counter** | Integrate dynamic impact metrics during item selection (e.g., 'Donating 10 clothes saves ~7,000 liters of water and provides warmth to 2 school children'). Gamifying and quantifying social/environmental impact in real time significantly increases motivation to finish the flow. | **Neutral (Feature)** |

---

### 6. Exercise: Backend Design (Milaap Fundraisers)

Website: [https://milaap.org/crowdfunding/fundraisers](https://milaap.org/crowdfunding/fundraisers)

#### 1. System Architecture Context
- **Platform:** Milaap (Crowdfunding platform primarily for medical emergencies, personal causes, education, and memorials).
- **Database Engine:** Relational DBMS (**PostgreSQL**) is strictly recommended due to ACID transactional consistency required for monetary donations, audit trails, and 80G tax certificates.
- **Design Strategy:** Highly normalized 3NF core entities combined with strategic denormalization (cached aggregate counters `raised_amount` and `donors_count` on the `campaigns` table) to support sub-10ms query times on the high-traffic `/crowdfunding/fundraisers` listing page.

#### 2. Entity-Relationship Model
```text
[users] 1 ──── N [campaigns] (as campaigner)
[categories] 1 ──── N [campaigns]
[campaigns] 1 ──── 1 [beneficiaries]
[campaigns] 1 ──── N [campaign_media]
[campaigns] 1 ──── N [donations]
[users] 1 ──── N [donations] (as donor, optional/guest)
[campaigns] 1 ──── N [campaign_updates]
[campaigns] N ──── M [tags] (via campaign_tags)
```

#### 3. Core Database Tables (PostgreSQL DDL)
1. `users`: Campaigners, donors, verifiers, admins (UUID, contact, role, KYC status).
2. `categories`: Medical, Memorials, Education, Emergency, etc. (Display order, slug, tagline).
3. `beneficiaries`: Patient details, hospital, treating doctor, medical condition, verification docs.
4. `campaigns`: Fundraisers table powering listing cards (Goal, cached raised amount, donor count, slug, verification badge, tax exemption tag, cover image, status).
5. `campaign_media`: Gallery images, hospital invoices, videos.
6. `donations`: Financial ledger (UUID, transaction status, amount, tip, gateway reference, 80G tax receipt PAN details).
7. `campaign_updates`: Medical milestones and updates to backers.
8. `tags` & `campaign_tags`: M:N tagging for "Tax Benefit", "Urgent", "Milaap Assured".

#### 4. Performance, Indexing & Concurrency Strategy
- **Composite Listing Index:** `CREATE INDEX idx_campaigns_status_created ON campaigns (status, featured_rank DESC, created_at DESC) WHERE status = 'ACTIVE';`
- **Category Filter Index:** `CREATE INDEX idx_campaigns_category_status ON campaigns (category_id, status) WHERE status = 'ACTIVE';`
- **Full-Text Search:** `CREATE INDEX idx_campaigns_fts ON campaigns USING GIN (to_tsvector('english', title || ' ' || story_summary));`
- **Atomic Aggregate Increments:** Payment gateway webhooks atomically increment `raised_amount = raised_amount + NEW.amount` and `donors_count = donors_count + 1`, eliminating expensive `SUM()` queries across high-traffic listing views.
- **Edge Caching Layer:** Redis cache with 30-60 second TTL for the top fundraisers listing endpoint.

---

## 🏃‍♂️ How to Run the Included Full-Stack Demo

```powershell
cd newsletter-signup-app
python main.py
```
- Open [http://127.0.0.1:8000](http://127.0.0.1:8000) for the high-converting landing page.
- Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger OpenAPI specification.
- Run tests: `python -m pytest tests/test_api.py -v` (100% passing).

---
© 2026 Ashutosh Kumar Jaiswal. All rights reserved.
