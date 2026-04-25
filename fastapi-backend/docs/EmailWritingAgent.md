# Module 4: Email Writing Agent (AI‑Generated Outreach Emails)

## AI‑Powered Client Hunt & Outreach — Final Year Project (FYP) Documentation

---

## Module purpose

The Email Writing Agent is responsible for producing **personalized outreach emails** for each target business.

This module converts technical findings (audit scores + flaws) into **human-language business impact** and an **actionable solution pitch**.

In your system architecture:

- Business discovery finds leads
- Website audit diagnoses weaknesses
- **Email Agent writes the outreach message**
- SMTP module sends the message (optional)

---

# Table of Contents

1. Why outreach needs an AI agent
2. Requirements and success criteria
3. Code map
4. API endpoints (generate email, extract business data, full pipeline)
5. Input contract (Pydantic schema)
6. Agent prompt engineering
7. Score → impact translation rules
8. Output format rules (subjects + body + personalization note)
9. Deliverability rules (anti-spam constraints)
10. Provider configuration (Groq/OpenAI keys)
11. Integration with Website Audit module
12. Integration with Business Data Extractor
13. Next.js integration guide
14. Operational safety (prompt safety, non-fabrication)
15. Testing strategy
16. Limitations and future work

---

# 1. Why outreach needs an AI agent

## 1.1 Outreach is “context + persuasion”

Cold outreach is not just sending templates. Effective outreach requires:

- understanding what the prospect likely cares about (calls, bookings, orders)
- connecting website issues to measurable impact
- proposing a credible fix plan
- writing naturally to avoid spam filters

## 1.2 Automation challenge

Manually writing a personalized email per lead does not scale. This module solves that by generating high-quality drafts that still feel human.

---

# 2. Requirements and success criteria

A generated outreach email in this FYP must:

- sound human (non-robotic)
- mention the business (name or domain) and industry
- highlight 2–3 major website problems in plain language
- propose a clear solution (repair/rebuild/optimize)
- end with a low-friction CTA
- avoid spam signals and exaggerated claims

---

# 3. Code map

Key locations:

- Outreach API endpoints:
  - `app/api/v1/endpoints/outreach.py`
- Email agent implementation:
  - `app/services/agents/email_writing_service.py` (class `EmailWritingAgent`)
  - Additional prompt rules reference: `app/services/agents/Email_Writing Agent.py`
- Business data extractor agent:
  - `app/services/agents/business_Data_Extractor_Agent.py`

Note: In this workspace snapshot, some agent files can be difficult to open via the editor file API on Windows. The behaviors documented here are anchored to the public API layer (`outreach.py`) and the request/response contracts (`schemas/outreach.py`).

---

# 4. API endpoints

## 4.1 Generate email

**Route:** `POST /api/v1/outreach/generate-email`

The endpoint:

- receives `EmailGenerationRequest`
- runs `EmailWritingAgent.generate_email(...)` in a thread pool (`ThreadPoolExecutor`)
- returns a plain `dict` (not a strict `GeneratedEmail` model)

Implementation detail (important): the request schema includes `competitor_examples`, but the endpoint does not pass it into `generate_email(...)` in the current code.

## 4.2 Extract business data

**Route:** `POST /api/v1/outreach/extract-business-data`

This endpoint uses an AI agent to extract:

- industry
- target customers
- unique selling points
- location
- core offer

This improves personalization without manual research.

## 4.3 Full pipeline

**Route:** `POST /api/v1/outreach/full-pipeline`

This endpoint demonstrates end-to-end orchestration and returns a combined payload.

Important: in the current implementation, inputs are **query parameters** (not a JSON body):

- `website_url` (required)
- `business_name` (optional)
- `to_email` (optional; if provided, response marks `ready_to_send: true` but does not send automatically)

Pipeline steps:

1) website audit
2) AI business data extraction
3) email generation
4) (optional) return info needed to send

The response includes:

- `audit`: overall score + per-category scores + summary + recommendations
- `business_data`: extracted fields from the extractor agent
- `generated_email`: the email draft object returned by the email agent

Note: sending is a separate endpoint (`/send-email`).

## 4.4 Send email

**Route:** `POST /api/v1/outreach/send-email`

Sends via SMTP using environment configuration (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, etc.).

This is a key “capstone workflow” for your FYP.

---

# 5. Input contract (schemas)

The request schemas are in `app/schemas/outreach.py`:

## 5.1 Required fields

- `business_name`
- `website_url`
- six audit scores (0–5):
  - `seo_score`
  - `ssl_score`
  - `load_speed_score`
  - `responsiveness_score`
  - `social_links_score`
  - `image_alt_score`

## 5.2 Optional fields (high impact personalization)

- `industry`
- `location`
- `target_audience`
- `business_goal`
- `specific_issues` (list)
- `competitor_examples` (list)
- `additional_notes`

These optional fields allow the agent to sound genuinely researched.

Note: `competitor_examples` is currently part of the schema but is not forwarded to the agent by `POST /generate-email`.

---

# 6. Agent prompt engineering

## 6.1 Two layers of instruction

Your repo contains two prompt sources:

1) A large “orchestrator instructions” file (`Email_Writing Agent.py`) describing:
   - required inputs
   - output structure
   - anti-spam rules
   - score interpretation

2) The production service instructions (`email_writing_service.py`) which adds a critical constraint:

**Never show numeric scores to the business owner.**

Instead, translate numeric scores into plain language.

## 6.2 Why hide the numeric scores?

Numeric scores are internal diagnostics. Prospects respond better to:

- “Visitors may leave before the page loads”
- “Some customers may see a ‘Not Secure’ warning”

…than to “your speed score is 2/5”.

This also reduces the “automated report” feel and improves deliverability.

---

# 7. Score → impact translation

The agent must map category weaknesses to business outcomes.

## 7.1 Mapping examples

- SEO low → fewer high-intent Google visitors
- Responsiveness low → high mobile bounce and fewer calls
- SSL low → trust loss and fewer form submissions
- Speed low → users abandon pages; wasted ad spend
- Social links low → weaker brand proof
- Image alt low → missed image-search visibility and accessibility issues

## 7.2 Industry specialization

The best email connects issues to the business model:

- restaurants: calls, reservations, WhatsApp orders
- clinics: appointment forms, trust, local SEO
- e-commerce: checkout, trust, conversion rate
- services: quote requests, lead forms

---

# 8. Output format rules

Every generation must output:

1) **Three subject lines**
   - personal/specific
   - benefit/outcome
   - short curiosity

2) **One final email**
   - professional, human, concise
   - clear CTA with two options

3) **Personalization note**
   - 1–2 lines for the operator

---

# 9. Deliverability rules

Your prompt includes explicit anti-spam constraints:

- avoid spam words (guarantee, urgent, free money, etc.)
- avoid repetitive patterns
- avoid ALL CAPS
- avoid excessive links
- vary openers and sentence structure

These are essential for Gmail deliverability.

---

# 10. Provider configuration (Groq/OpenAI)

Your settings file provides:

- `GROQ_API_KEY`
- `OPENAI_API_KEY`

The agent service chooses a provider depending on which key is configured.

Important engineering note:

- Keep provider calls behind a small abstraction so switching providers does not change business logic.

---

# 11. Integration with Website Audit

The full pipeline endpoint uses audit results to:

- compute category scores
- extract specific issues (top flaws)
- feed them into email generation

This creates a consistent narrative: “I checked your site and noticed…”.

---

# 12. Integration with Business Data Extractor

The pipeline also calls `BusinessDataExtractorAgent` to extract:

- industry
- location
- target audience

These fields increase personalization and reduce generic emails.

---

# 13. Next.js integration guide

## 13.1 Recommended UI flow

A clean Next.js workflow:

1) User selects a business
2) Frontend calls audit endpoint
3) Frontend calls extract-business-data endpoint
4) Frontend calls generate-email endpoint
5) User reviews/edits the email
6) Optional: send via SMTP

## 13.2 Generate email call example

```ts
const base = process.env.NEXT_PUBLIC_API_BASE_URL;

const payload = {
  business_name: 'Example Dental Clinic',
  website_url: 'https://example.com',
  seo_score: 2,
  ssl_score: 4,
  load_speed_score: 1,
  responsiveness_score: 2,
  social_links_score: 1,
  image_alt_score: 3,
  industry: 'Dental clinic',
  location: 'Lahore',
  business_goal: 'More appointment bookings',
  specific_issues: ['Missing meta description', 'Slow server response']
};

const res = await fetch(`${base}/api/v1/outreach/generate-email`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
});

const emailDraft = await res.json();
```

## 13.3 Full pipeline call example (query parameters)

```ts
const base = process.env.NEXT_PUBLIC_API_BASE_URL;
const url = new URL(`${base}/api/v1/outreach/full-pipeline`);
url.searchParams.set('website_url', 'https://example.com');
url.searchParams.set('business_name', 'Example Dental Clinic');

const res = await fetch(url.toString(), { method: 'POST' });
const pipeline = await res.json();
```

## 13.4 UI rendering

Render:

- subjects as selectable chips
- email body as editable textarea
- personalization note as helper text

---

# 14. Operational safety (non-fabrication)

The prompt explicitly prohibits:

- inventing awards, certifications, client lists
- claiming access to private analytics
- promising guaranteed ranking/sales

This is important for ethical compliance and reputational safety.

---

# 15. Testing strategy

- snapshot tests: verify output always contains 3 subjects + email body
- constraint tests: ensure no numeric score strings like `"3/5"` appear
- integration test: audit → generate email pipeline

---

# 16. Limitations and future work

- add campaign-level tone controls (formal vs casual)
- add multilingual generation (Urdu + English mix)
- add follow-up sequence generation (Follow-up #1/#2)
- add structured “offer library” per industry

---

# Conclusion

The Email Writing Agent is the “conversion layer” of the system: it transforms technical diagnostics into persuasive business communication while enforcing deliverability and non-fabrication rules.
