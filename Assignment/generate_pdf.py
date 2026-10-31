import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, Preformatted, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "First Assignment - Product Engineer | Ashutosh Kumar Jaiswal")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        
        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 28, page_str)
        self.drawString(54, 28, "CONFIDENTIAL - For Review Only")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 38, 8.5 * 72 - 54, 38)
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12
    )
    
    section_h1 = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=12,
        spaceAfter=5
    )
    
    section_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=7,
        spaceAfter=3
    )
    
    body = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=4
    )
    
    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=body,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#475569')
    )
    
    meta_val = ParagraphStyle(
        'MetaVal',
        parent=body,
        fontName='Helvetica',
        textColor=colors.HexColor('#0f172a')
    )
    
    instruction_style = ParagraphStyle(
        'InstText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#64748b')
    )
    
    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#0f172a')
    )
    
    code_dark = ParagraphStyle(
        'CodeDark',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=7.6,
        leading=9.8,
        textColor=colors.HexColor('#f8fafc')
    )
    
    def make_code_box(sql_text):
        p = Paragraph(sql_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>'), code_dark)
        t = Table([[p]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")),
            ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#334155")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    story = []
    
    # Title & Subtitle
    story.append(Paragraph("First Assignment", title_style))
    story.append(Paragraph("Role: Product Engineer", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=10))
    
    # Instructions Box
    inst_data = [[
        Paragraph(
            "<b>Instructions Summary:</b> Estimated completion time: 2 hours. All sections mandatory. "
            "Submission naming: <code>{Last4DigitsOfPhoneNumber} - {YourName} - FirstAssignment - ProductEngineer.pdf</code>. "
            "Contents confidential.", instruction_style
        )
    ]]
    t_inst = Table(inst_data, colWidths=[504])
    t_inst.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_inst)
    story.append(Spacer(1, 8))
    
    # 1. Candidate Details
    story.append(Paragraph("1. Candidate Details", section_h1))
    story.append(Paragraph("<i>Verified details matching application and public records:</i>", instruction_style))
    story.append(Spacer(1, 3))
    
    cand_data = [
        [Paragraph("<b>Name:</b>", meta_label), Paragraph("Ashutosh Kumar Jaiswal", meta_val)],
        [Paragraph("<b>Phone:</b>", meta_label), Paragraph("+91 6207151423", meta_val)],
        [Paragraph("<b>Email:</b>", meta_label), Paragraph("ashutoshhjp00567@gmail.com", meta_val)],
        [Paragraph("<b>LinkedIn Profile URL:</b>", meta_label), Paragraph("https://www.linkedin.com/in/ashutosh-kumar-jaiswal/", meta_val)],
        [Paragraph("<b>GitHub URL:</b>", meta_label), Paragraph("https://github.com/Ashujais", meta_val)]
    ]
    t_cand = Table(cand_data, colWidths=[140, 364])
    t_cand.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_cand)
    story.append(Spacer(1, 10))
    
    # 2. Question: Code Change
    story.append(Paragraph("2. Question: Code Change", section_h1))
    story.append(Paragraph("<b>Code Change Under Examination:</b>", section_h2))
    
    img_path = r'Assignment\word\media\image1.png'
    if os.path.exists(img_path):
        story.append(Image(img_path, width=480, height=125))
        story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Recommended Git Commit Message:</b>", section_h2))
    commit_block = [
        [Paragraph(
            "<b>fix(math): guard multiplyByFive against non-integer arguments</b><br/><br/>"
            "Add an explicit runtime check using <code>is_int()</code> to verify that <code>$arg</code> is an integer before computing the product. "
            "If a non-integer value is provided, return <code>-1</code> as an error indicator to avoid unintended type coercion or runtime type errors under strict typing.",
            code_style
        )]
    ]
    t_commit = Table(commit_block, colWidths=[504])
    t_commit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_commit)
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Bonus: Concerns Regarding the Final Version:</b>", section_h2))
    concerns = [
        "<b>1. Sentinel Value Anti-Pattern (-1):</b> Returning <code>-1</code> creates ambiguity between computational results and error states. If <code>$arg = -0.2</code>, mathematically <code>-0.2 * 5 = -1</code>. A caller checking <code>if ($result === -1)</code> cannot tell if an error occurred or if <code>-1</code> was the genuine result. Moreover, in PHP, <code>-1</code> evaluates to <code>true</code> in loose boolean checks (<code>if (multiplyByFive('abc'))</code>), allowing bad state to silently propagate.",
        "<b>2. Bypassing PHP's Native Type System:</b> The function specifies a return type hint (<code>: int</code>), but leaves the parameter <code>$arg</code> completely untyped, relying on manual runtime inspection (<code>!is_int($arg)</code>). In modern PHP (7.0+ / 8.x), the idiomatic and performant approach is declaring the parameter type directly: <code>function multiplyByFive(int $arg): int</code> with <code>declare(strict_types=1);</code>. The Zend Engine enforces type contracts natively with zero manual overhead.",
        "<b>3. Violation of Fail-Fast Principle (Exceptions vs Error Codes):</b> Silently returning an arbitrary number forces every downstream consumer to write defensive checks. Modern software engineering best practice requires failing fast by throwing an <code>InvalidArgumentException</code> or <code>TypeError</code> when invalid data is supplied.",
        "<b>4. Numeric Float Inflexibility:</b> If a numeric float (e.g. <code>2.5</code>) is passed, <code>is_int(2.5)</code> evaluates to false, returning <code>-1</code> instead of <code>12.5</code>. If decimal operations are valid, union types (<code>int|float</code>) should be supported.",
        "<b>5. Integer Overflow:</b> In PHP, if <code>$arg * 5</code> exceeds <code>PHP_INT_MAX</code> (<code>9,223,372,036,854,775,807</code> on 64-bit systems), PHP automatically promotes the result to a float. Because the return type hint is strictly <code>: int</code>, this triggers a fatal <code>TypeError: Return value of multiplyByFive() must be of the type int, float returned</code>."
    ]
    for c in concerns:
        story.append(Paragraph(f"• {c}", body))
    
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>What I Would Do Differently (Production-Grade Code):</b>", section_h2))
    
    code_diff = """&lt;?php
declare(strict_types=1);

namespace App\\Math;

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
    t_code = Table([[Paragraph(code_diff.replace('\n', '<br/>'), code_dark)]], colWidths=[504])
    t_code.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#334155")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_code)
    story.append(Spacer(1, 10))
    
    # 3. Question: Task Approach
    story.append(PageBreak())
    story.append(Paragraph("3. Question: Task Approach", section_h1))
    story.append(Paragraph(
        "<i>Scenario: You are asked to create a 'Newsletter Signup' page by your company's Sales team with no other inputs. "
        "What are your first steps to approach this work?</i>", instruction_style
    ))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "<b>Strategic Overview:</b> As a Product Engineer, building features without context often leads to wasted engineering cycles, poor conversion rates, or misaligned lead qualification. An underspecified request requires a structured, consultative approach that balances commercial sales objectives, UX friction, data privacy, and scalable technical architecture.",
        body
    ))
    story.append(Spacer(1, 3))
    
    q3_steps = [
        ("Step 1: Context Gathering & Commercial Alignment (Discovery)", [
            "<b>Understand the Core Objective:</b> Clarify why Sales needs this page (e.g. B2B enterprise pipeline acceleration, webinar/event registrations, product launch updates, or general lead generation).",
            "<b>Target Audience & Channels:</b> Determine whether traffic comes from outbound cold outreach (SDRs), paid performance ads, organic blog traffic, or offline conference QR codes.",
            "<b>Define Success Metrics:</b> Align on target conversion rate (e.g., 3-5%), projected weekly subscriber volume, and qualification criteria for Marketing Qualified Leads (MQLs) vs. Sales Qualified Leads (SQLs)."
        ]),
        ("Step 2: Define Requirements & Scope Boundaries (Functional & Non-Functional)", [
            "<b>Form Field Strategy:</b> Balance lead qualification against conversion friction. Minimal MVP: Work Email. B2B Tier: First Name, Work Email, Company Name, and Job Role/Size.",
            "<b>Integrations & Lead Handoff:</b> Connect submissions directly to Sales CRM (HubSpot, Salesforce, Marketo), internal PostgreSQL backup table, and Slack alerts for enterprise domains.",
            "<b>Post-Signup Journey:</b> Immediate on-page confirmation UI, redirect to high-value lead magnet (e.g., Whitepaper/Report download), and automated welcome email with double opt-in.",
            "<b>Compliance & Privacy:</b> Implement strict GDPR, CAN-SPAM, and CCPA compliance (explicit opt-in consent checkbox, privacy policy link, 1-click unsubscribe mechanism, audit trail).",
            "<b>Security & Anti-Abuse:</b> Cloudflare Turnstile / reCAPTCHA v3 bot protection, honeypot fields, rate limiting per IP (max 5/min), and MX record validation to disallow disposable email domains."
        ]),
        ("Step 3: Rapid Prototyping & Wireframing", [
            "Create a mobile-first, low-fidelity wireframe in Figma or interactive mockup showcasing headline, value proposition, form fields, social proof metrics, and confirmation states.",
            "Draft the technical API contract (<code>POST /api/v1/newsletter/subscribe</code>) and data schema."
        ]),
        ("Step 4: Stakeholder Alignment & Sign-Off", [
            "Present the wireframe and proposed scope to the Sales lead in a 15-minute alignment sync.",
            "Establish agreement on MVP deliverables (launch within 5 days) vs. Phase 2 enhancements (A/B testing, personalized email drip flows)."
        ]),
        ("Step 5: Technical Implementation (Iterative Engineering Sprint)", [
            "<b>Frontend:</b> Semantic, accessible (WCAG 2.1 AA) responsive landing page built with modern framework (React/Next.js/Tailwind). Features instant client-side validation and responsive layout.",
            "<b>Backend API & Async Queue:</b> Express/FastAPI endpoint with rate limiting and payload validation. Asynchronous task queue (Redis/BullMQ) to sync CRM leads in background without blocking user response times (<200ms).",
            "<b>Analytics & Telemetry:</b> Instrument Segment/PostHog/GA4 event tracking (Pageview, Form Focus, Submit Attempt, Success, Error)."
        ]),
        ("Step 6: QA, Cross-Browser Testing & Security Verification", [
            "Test validation edge cases: duplicate submissions, malformed emails, uppercase strings, XSS/SQLi injection vectors, and slow 3G mobile networks.",
            "End-to-end integration test: Verify that submitted leads correctly populate in the Sales CRM with all attribution parameters (UTM source, medium, campaign) intact."
        ]),
        ("Step 7: Deployment & Staging Review", [
            "Deploy to a staging environment for Sales team preview and acceptance sign-off.",
            "Production release via zero-downtime CI/CD deployment with Datadog/Sentry monitoring."
        ]),
        ("Step 8: Post-Launch Review & Iteration", [
            "Monitor error rates, bounce rates, and funnel conversion metrics in real time.",
            "Conduct a 7-day post-launch review with the Sales team to assess lead volume and lead quality, followed by A/B copy tests on headlines and CTA buttons."
        ])
    ]
    
    for title, points in q3_steps:
        story.append(Paragraph(f"<b>{title}</b>", section_h2))
        for pt in points:
            story.append(Paragraph(f"• {pt}", body))
    
    story.append(Spacer(1, 10))
    
    # 4. Question: Communication For Requirement Gathering
    story.append(PageBreak())
    story.append(Paragraph("4. Question: Communication For Requirement Gathering", section_h1))
    story.append(Paragraph(
        "<i>Write down your first communication (in email format) with the Sales team for their inputs, including timelines.</i>", instruction_style
    ))
    story.append(Spacer(1, 6))
    
    email_html = """<b>Subject: [Kickoff] Newsletter Signup Page – Requirements &amp; Proposed 5-Day Launch Plan</b><br/><br/>
<b>Hi Sales Team,</b><br/><br/>
Thanks for reaching out! A dedicated Newsletter Signup page is an excellent initiative to accelerate our inbound lead pipeline and engage prospective customers.<br/><br/>
To ensure we build an experience that maximizes conversion while capturing the exact data your team needs for sales workflows, I’ve put together a recommended baseline along with a few key questions.<br/><br/>
Rather than starting from a blank slate, here is our recommended <b>MVP (Phase 1) Proposal</b>:
<ul>
  <li><b>Form Fields:</b> Work Email + First Name (keeps form friction low while enabling personalized SDR outreach).</li>
  <li><b>CRM &amp; Routing:</b> Real-time webhook sync into your CRM (HubSpot/Salesforce) tagged with <i>"Source: Newsletter"</i>, plus automated Slack notifications for high-value enterprise domain signups.</li>
  <li><b>User Experience:</b> Instant on-page confirmation UI + automated transactional welcome email delivering our latest industry benchmark whitepaper.</li>
  <li><b>Compliance &amp; Security:</b> Bot protection via Cloudflare Turnstile, honeypot fields, and strict GDPR / CAN-SPAM compliance.</li>
</ul>
<br/>
<b>Key Inputs Needed From Your Side:</b>
<ol>
  <li><b>Target Audience &amp; Traffic Source:</b> Who is the primary persona (e.g., Enterprise CTOs, Mid-market VP Sales, or general consumers), and where will visitors arrive from (cold outbound campaigns, paid LinkedIn ads, or social media)?</li>
  <li><b>Required Lead Fields:</b> Are Work Email and First Name sufficient for MVP, or do you strictly require Company Name, Job Title, or Team Size upfront? <i>(Note: Each additional field typically reduces conversion rates by 5–10%.)</i></li>
  <li><b>CRM Properties &amp; Lead Assignment:</b> Which CRM list or pipeline stage should these contacts be mapped to, and which sales rep / team should be assigned ownership?</li>
  <li><b>Incentive / Copy:</b> Do you have specific headlines or a lead magnet ready (e.g., <i>"Get our 2026 Industry Report"</i>), or would you like engineering/marketing to provide placeholder copy for your review?</li>
</ol>
<br/>
<b>Proposed Timeline &amp; Milestones (5-Day Delivery):</b>
<ul>
  <li><b>Day 1 (Tomorrow, 2:00 PM):</b> Consolidate feedback and lock in requirements.</li>
  <li><b>Day 2:</b> Share interactive wireframe and API schema for your sign-off.</li>
  <li><b>Day 3–4:</b> Engineering sprint (frontend landing page, backend API, CRM sync, and analytics tracking).</li>
  <li><b>Day 5:</b> Staging walkthrough with the Sales team, QA verification, and Production Launch.</li>
</ul>
<br/>
Could you share your thoughts by <b>tomorrow at 12:00 PM</b>? Alternatively, I am happy to hop on a quick 15-minute sync—feel free to grab time on my calendar [Calendar Link] or reply directly here.<br/><br/>
Looking forward to launching this together!<br/><br/>
Best regards,<br/>
<b>Ashutosh Kumar Jaiswal</b><br/>
Product Engineer<br/>
ashutoshhjp00567@gmail.com | +91 6207151423"""

    t_email = Table([[Paragraph(email_html, body)]], colWidths=[504])
    t_email.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_email)
    story.append(Spacer(1, 10))
    
    # 5. Exercise: UI/UX Assessment
    story.append(PageBreak())
    story.append(Paragraph("5. Exercise: UI/UX Assessment", section_h1))
    story.append(Paragraph(
        "<i>Website: https://shareatdoorstep.com/donate/ | Task: Go through the donation flow and record observations categorized by Good, Bad, and Neutral with feature suggestions.</i>",
        instruction_style
    ))
    story.append(Spacer(1, 6))
    
    table_hdr = ParagraphStyle('THdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white, alignment=1)
    cell_p = ParagraphStyle('TCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.8, leading=10.5, textColor=colors.HexColor('#1e293b'))
    cell_p_b = ParagraphStyle('TCellB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=colors.HexColor('#0f172a'))
    
    good_tag = ParagraphStyle('GoodTag', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=1, textColor=colors.HexColor('#15803d'))
    bad_tag = ParagraphStyle('BadTag', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=1, textColor=colors.HexColor('#b91c1c'))
    neutral_tag = ParagraphStyle('NeutTag', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=1, textColor=colors.HexColor('#b45309'))
    
    ux_rows = [
        [Paragraph("<b>#</b>", table_hdr), Paragraph("<b>Summary</b>", table_hdr), Paragraph("<b>Description</b>", table_hdr), Paragraph("<b>Type</b>", table_hdr)],
        
        [Paragraph("1", cell_p_b), Paragraph("Geolocation-First Funnel Gating", cell_p_b),
         Paragraph("The donation journey begins by detecting or asking for the user's location/pin code before asking for item details. This is an excellent usability pattern because it prevents users from going through a multi-step cataloging process only to discover at the end that their area is unserviceable.", cell_p),
         Paragraph("<b>Good</b>", good_tag)],
        
        [Paragraph("2", cell_p_b), Paragraph("Multi-Fulfillment Options (Doorstep / Drop / Campaigns)", cell_p_b),
         Paragraph("Offering three distinct pathways ('Pickup from Doorstep', 'Live Campaigns', and 'Drop yourself') caters effectively to diverse donor personas—from busy professionals willing to pay for convenience to budget-conscious donors who prefer free drop-offs.", cell_p),
         Paragraph("<b>Good</b>", good_tag)],
        
        [Paragraph("3", cell_p_b), Paragraph("Clear Item Condition &amp; Age Tagging", cell_p_b),
         Paragraph("Allowing donors to specify item state ('Brand New', 'Barely Used', 'Well Used') and age brackets gives valuable operational data to sorting teams and partner NGOs, ensuring dignity for recipients and reducing logistics rejection.", cell_p),
         Paragraph("<b>Good</b>", good_tag)],
        
        [Paragraph("4", cell_p_b), Paragraph("Late Fee Disclosure / Price Shock at Checkout", cell_p_b),
         Paragraph("The platform communicates 'Donate' as a charitable act, but surprises the user with a mandatory convenience/pickup logistics fee only at the very final checkout step. This late pricing shock causes friction, drops trust, and triggers cart abandonment. Displaying transparent copy upfront (e.g., 'Doorstep pickup supported by a small Rs. 199 logistics contribution') would drastically reduce drop-offs.", cell_p),
         Paragraph("<b>Bad</b>", bad_tag)],
        
        [Paragraph("5", cell_p_b), Paragraph("Mandatory Mobile OTP Barrier at Final Step", cell_p_b),
         Paragraph("Requiring users to enter their mobile number and wait for an SMS OTP right before placing the order introduces unnecessary drop-off friction. If SMS delivery is delayed or signal is weak, the entire donation flow fails. Implementing 1-click social login (Google OAuth) or delayed verification post-booking would improve checkout completion.", cell_p),
         Paragraph("<b>Bad</b>", bad_tag)],
        
        [Paragraph("6", cell_p_b), Paragraph("Repetitive Modal Dialogs for Multi-Category Donors", cell_p_b),
         Paragraph("Adding multiple distinct items (e.g., clothes, books, and electronics) forces the user to navigate through repetitive modal overlays to input condition, brand, and age for each item individually. For a household decluttering session with 10+ items, this creates high cognitive fatigue.", cell_p),
         Paragraph("<b>Bad</b>", bad_tag)],
        
        [Paragraph("7", cell_p_b), Paragraph("Opaque NGO / Cause Allocation During Booking", cell_p_b),
         Paragraph("The donor is not shown which specific NGO, orphanage, or community organization will receive their items during the booking flow. Showing paired NGO cards or impact stories during checkout would create an emotional bond and boost repeat donations.", cell_p),
         Paragraph("<b>Neutral</b>", neutral_tag)],
        
        [Paragraph("8", cell_p_b), Paragraph("Feature Suggestion: AI-Powered Photo Donation Estimation", cell_p_b),
         Paragraph("Instead of manually browsing categories and item dropdowns, allow donors to snap a picture of their donation box/bag. Computer vision can automatically estimate volume, category breakdown, and assign the appropriate vehicle/bag size for pickup.", cell_p),
         Paragraph("<b>Neutral<br/>(Feature)</b>", neutral_tag)],
        
        [Paragraph("9", cell_p_b), Paragraph("Feature Suggestion: Instant Environmental &amp; Social Impact Counter", cell_p_b),
         Paragraph("Integrate dynamic impact metrics during item selection (e.g., 'Donating 10 clothes saves ~7,000 liters of water and provides warmth to 2 school children'). Gamifying and quantifying social/environmental impact in real time significantly increases motivation to finish the flow.", cell_p),
         Paragraph("<b>Neutral<br/>(Feature)</b>", neutral_tag)]
    ]
    
    t_ux = Table(ux_rows, colWidths=[18, 105, 321, 60], repeatRows=1)
    t_ux.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#ffffff")),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor("#ffffff")),
        ('BACKGROUND', (0,5), (-1,5), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0,6), (-1,6), colors.HexColor("#ffffff")),
        ('BACKGROUND', (0,7), (-1,7), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0,8), (-1,8), colors.HexColor("#ffffff")),
        ('BACKGROUND', (0,9), (-1,9), colors.HexColor("#f8fafc")),
    ]))
    story.append(t_ux)
    story.append(Spacer(1, 10))
    
    # 6. Exercise: Backend Design
    story.append(PageBreak())
    story.append(Paragraph("6. Exercise: Backend Design", section_h1))
    story.append(Paragraph(
        "<i>Website: https://milaap.org/crowdfunding/fundraisers | Task: Guess the database schema of this page and fundraisers' listings.</i>",
        instruction_style
    ))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph(
        "<b>1. Architectural Context &amp; Modeling Strategy:</b><br/>"
        "• <b>Platform:</b> Milaap (Online crowdfunding platform primarily for medical emergencies, personal causes, education, and memorials).<br/>"
        "• <b>Database Choice:</b> Relational DBMS (PostgreSQL) is strictly recommended due to ACID transactional consistency required for monetary donations, strict audit trails, multi-currency processing, and tax exemption (80G) reporting.<br/>"
        "• <b>Data Modeling Approach:</b> Highly normalized 3NF schema for transactional integrity, paired with strategic denormalization (cached aggregate counters <code>raised_amount</code> and <code>donors_count</code> on the <code>campaigns</code> table) to support sub-10ms query times on the high-traffic <code>/crowdfunding/fundraisers</code> listing page.",
        body
    ))
    story.append(Spacer(1, 4))
    
    story.append(Paragraph(
        "<b>2. Entity-Relationship Overview:</b><br/>"
        "<code>[users] 1 ──── N [campaigns] (as campaigner)</code><br/>"
        "<code>[categories] 1 ──── N [campaigns]</code><br/>"
        "<code>[campaigns] 1 ──── 1 [beneficiaries]</code><br/>"
        "<code>[campaigns] 1 ──── N [campaign_media]</code><br/>"
        "<code>[campaigns] 1 ──── N [donations]</code><br/>"
        "<code>[users] 1 ──── N [donations] (as donor, optional/guest)</code><br/>"
        "<code>[campaigns] 1 ──── N [campaign_updates]</code><br/>"
        "<code>[campaigns] N ──── M [tags] (via campaign_tags)</code>",
        body
    ))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph("<b>3. Production Relational Schema (PostgreSQL DDL):</b>", section_h2))
    
    # Split SQL into modular blocks that fit easily on pages
    sql_part1 = """-- 1. USERS TABLE (Campaigners, Donors, Administrators)
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
);"""
    story.append(make_code_box(sql_part1))
    story.append(Spacer(1, 5))

    sql_part2 = """-- 3. BENEFICIARIES TABLE (The patient or recipient of funds)
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
);"""
    story.append(make_code_box(sql_part2))
    story.append(Spacer(1, 5))

    sql_part3 = """-- 4. CAMPAIGNS TABLE (Fundraisers - Powers the listing page cards)
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
    currency CHAR(3) DEFAULT 'INR' NOT NULL,
    goal_amount NUMERIC(14, 2) NOT NULL CHECK (goal_amount > 0),
    raised_amount NUMERIC(14, 2) DEFAULT 0.00 NOT NULL CHECK (raised_amount >= 0),
    donors_count INT DEFAULT 0 NOT NULL CHECK (donors_count >= 0),
    shares_count INT DEFAULT 0 NOT NULL CHECK (shares_count >= 0),
    cover_image_url TEXT NOT NULL,
    video_url TEXT,
    tax_exemption_eligible BOOLEAN DEFAULT FALSE,
    is_emergency BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    featured_rank INT DEFAULT 0,
    status VARCHAR(30) DEFAULT 'ACTIVE' CHECK (status IN ('DRAFT', 'UNDER_REVIEW', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CLOSED', 'REJECTED')),
    start_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);"""
    story.append(make_code_box(sql_part3))
    story.append(Spacer(1, 5))

    sql_part4 = """-- 5. CAMPAIGN MEDIA TABLE (Gallery, hospital receipts, videos)
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
    donor_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    donor_name VARCHAR(150) NOT NULL DEFAULT 'Anonymous',
    donor_email VARCHAR(255),
    donor_phone VARCHAR(20),
    is_anonymous BOOLEAN DEFAULT FALSE,
    currency CHAR(3) DEFAULT 'INR' NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    tip_to_milaap NUMERIC(10, 2) DEFAULT 0.00 CHECK (tip_to_milaap >= 0),
    gateway_fee NUMERIC(10, 2) DEFAULT 0.00,
    net_campaign_amount NUMERIC(12, 2) GENERATED ALWAYS AS (amount) STORED,
    payment_gateway VARCHAR(50) NOT NULL,
    gateway_transaction_id VARCHAR(150) UNIQUE,
    payment_status VARCHAR(30) DEFAULT 'INITIATED' CHECK (payment_status IN ('INITIATED', 'SUCCESS', 'FAILED', 'REFUNDED')),
    wants_80g_receipt BOOLEAN DEFAULT FALSE,
    pan_number_encrypted TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);"""
    story.append(make_code_box(sql_part4))
    story.append(Spacer(1, 5))

    sql_part5 = """-- 7. CAMPAIGN UPDATES TABLE (Hospital progress, updates to backers)
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
    story.append(make_code_box(sql_part5))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "<b>4. Strategic Indexing &amp; Query Optimization for <code>/crowdfunding/fundraisers</code>:</b><br/>"
        "• <b>Composite Listing Index:</b> <code>CREATE INDEX idx_campaigns_status_created ON campaigns (status, featured_rank DESC, created_at DESC) WHERE status = 'ACTIVE';</code><br/>"
        "• <b>Category Filter Index:</b> <code>CREATE INDEX idx_campaigns_category_status ON campaigns (category_id, status) WHERE status = 'ACTIVE';</code><br/>"
        "• <b>Fast Slug Lookup:</b> <code>CREATE UNIQUE INDEX idx_campaigns_slug ON campaigns (slug);</code><br/>"
        "• <b>Full-Text Search Index:</b> <code>CREATE INDEX idx_campaigns_fts ON campaigns USING GIN (to_tsvector('english', title || ' ' || story_summary));</code><br/>"
        "• <b>Fast Donation Lookup:</b> <code>CREATE INDEX idx_donations_campaign_status ON donations (campaign_id, payment_status) WHERE payment_status = 'SUCCESS';</code>",
        body
    ))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph(
        "<b>5. Concurrency &amp; Data Consistency Strategy:</b><br/>"
        "• <b>Atomic Aggregate Increments:</b> The listing page displays cards with <i>'Rs. raised of Rs. goal'</i> and <i>'N supporters'</i>. Running <code>SELECT SUM(amount), COUNT(*) FROM donations WHERE campaign_id = X</code> across dozens of cards on every request would degrade database performance. Instead, successful payment gateway webhooks trigger atomic increments:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>UPDATE campaigns SET raised_amount = raised_amount + NEW.amount, donors_count = donors_count + 1, updated_at = CURRENT_TIMESTAMP WHERE id = NEW.campaign_id;</code><br/>"
        "• <b>Edge Caching Layer:</b> High-throughput listing endpoints (<code>/crowdfunding/fundraisers</code>) are cached in Redis with a 30-60 second TTL, combined with <code>Cache-Control: public, s-maxage=60, stale-while-revalidate=30</code> headers.",
        body
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>That’s all, folks!</b>", subtitle_style))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {filename}")

if __name__ == '__main__':
    target_pdf = r'Assignment\Assignment - Ashutosh Kumar Jaiswal - FirstAssignment - ProductEngineer.pdf'
    build_pdf(target_pdf)
    
    strict_pdf = r'Assignment\1423 - Ashutosh Kumar Jaiswal - FirstAssignment - ProductEngineer.pdf'
    build_pdf(strict_pdf)
