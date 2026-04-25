# Module 2: Website Audit (SEO + SSL + Speed + Responsiveness + Social Links + Image ALT)

## AI‑Powered Client Hunt & Outreach — Final Year Project (FYP) Documentation

**Department of Software Engineering**

---

## Why this module exists

The purpose of the Website Audit module is to automatically analyze a business website and convert technical website quality signals into:

1) **Structured scores** (0–5) per category
2) **Readable flaws** (what is wrong)
3) A **single overall score** (0–5)
4) A **summary + recommendations** usable by the Outreach Email Agent

This module is a “diagnostic engine” for the overall system. The lead pipeline is:

- Discover businesses (OSM)
- Identify/confirm website URLs (OSM + discovery)
- **Audit websites** (this module)
- Generate outreach email using the audit findings (Email Agent)

---

# Table of Contents

1. Introduction and scope
2. Architecture overview
3. Backend code map (where each feature lives)
4. API layer (FastAPI endpoints)
5. Orchestrator design (`WebsiteAuditOrchestrator`)
6. Scoring system (0–5)
7. SEO audit module
8. SSL audit module
9. Load speed audit module
10. Responsiveness audit module
11. Social links audit module
12. Image ALT tags audit module
13. Concurrency + timeouts + reliability
14. Data model (Pydantic schemas)
15. Integration with Business module
16. Integration with Outreach pipeline
17. Next.js frontend integration guide
18. Operational notes (Playwright, headless browsing)
19. Security, privacy, and compliance considerations
20. Testing strategy
21. Limitations and future work

---

# 1. Introduction and scope

## 1.1 What is a “Website Audit” in this project?

In this FYP, a “website audit” means an automated set of checks that estimate how well a website supports:

- **Discovery** (SEO basics)
- **Trust** (HTTPS/SSL correctness)
- **Performance** (load time)
- **Mobile UX** (responsiveness)
- **Brand proof** (social presence)
- **Accessibility & SEO richness** (image alt text)

The audit is not intended to fully replace professional tools (e.g., full Lighthouse), but to provide **fast, consistent**, and **actionable** results that can:

- prioritize leads (“low-score websites need help”) and
- produce personalization details for outreach.

## 1.2 Inputs and outputs

**Input:** `website_url` (string)

**Outputs:** A structured response with:

- `overall_score` (0–5)
- six optional section results:
  - SEO (`seo`)
  - SSL (`ssl`)
  - load speed (`load_speed`)
  - responsiveness (`responsiveness`)
  - social links (`social_links`)
  - image ALT (`image_alt`)
- `summary` and `recommendations`

---

# 2. Architecture overview

## 2.1 Main design idea

The module is built around an **orchestrator** that:

- normalizes the input URL
- runs independent audit checks in parallel
- aggregates results into a single response

This design is a classic **fan‑out / fan‑in** pattern:

- Fan‑out: launch tasks concurrently
- Fan‑in: collect results and build a final report

## 2.2 Why concurrency matters

Auditing is I/O-bound:

- HTTP requests (requests library)
- TCP/TLS handshakes (socket/ssl)
- headless browser rendering (Playwright)

Without concurrency, audits would feel slow and reduce throughput. Using parallel tasks keeps response time closer to the slowest module rather than the sum of all module times.

---

# 3. Backend code map

These are the primary implementation locations in your backend:

- Orchestrator: `app/services/website_audit/orchestrator.py`
- Audit modules:
  - SEO: `app/services/website_audit/modules/seo_metadata.py`
  - SSL: `app/services/website_audit/modules/ssl_certificate.py`
  - Speed: `app/services/website_audit/modules/load_speed.py` (script‑style checker)
  - Responsiveness: `app/services/website_audit/modules/responsiveness.py`
  - Social links: `app/services/website_audit/modules/social_links.py`
  - Image ALT: `app/services/website_audit/modules/image_alt_tags.py`
- API endpoints:
  - Dedicated audit endpoints: `app/api/v1/endpoints/audits.py`
  - Business-specific audit route: `app/api/v1/endpoints/businesses.py` (`/{business_id}/audit`)

---

# 4. API layer (FastAPI)

## 4.1 Endpoint: Run a full audit

**Route:** `POST /api/v1/audits/run`

**Request body:** `AuditRequest`

Fields:

- `website_url: str`
- boolean flags: `include_seo`, `include_ssl`, `include_speed`, `include_responsiveness`, `include_social_links`, `include_image_alt`

**Response:** `WebsiteAuditResponse`

## 4.2 Endpoint: Bulk audit

**Route:** `POST /api/v1/audits/bulk`

Supports up to 50 websites per request.

## 4.3 Endpoint: Quick audit

**Route:** `GET /api/v1/audits/quick/{url:path}`

This endpoint builds a simplified response for HTML templates (and can also be used by Next.js). It converts nested schema objects into the shape expected by older template pages.

### Implementation detail

The audit itself is synchronous (uses threads + sync libraries). The endpoints run it safely using:

- `asyncio.get_event_loop().run_in_executor(...)`

This avoids blocking the FastAPI event loop.

---

# 5. Orchestrator design (`WebsiteAuditOrchestrator`)

## 5.1 Responsibilities

`WebsiteAuditOrchestrator` is responsible for:

- input URL normalization
- launching audit modules concurrently
- collecting results with timeouts
- computing `overall_score`
- building `summary` + `recommendations`

## 5.2 URL normalization

The orchestrator normalizes the URL so `example.com` becomes `https://example.com`.

### Why?

- reduces failure due to missing scheme
- avoids duplicate handling across modules

## 5.3 Parallel execution

The orchestrator uses a thread pool:

- `ThreadPoolExecutor(max_workers=6)`

Each audit is launched using `executor.submit(...)`.

### Timeout policy

When collecting results, each future uses `timeout=120`. If a module fails or times out, it returns:

- `{ "error": "...", "score": 0 }`

This prevents one slow module from breaking the entire response.

---

# 6. Scoring system (0–5)

## 6.1 Why a 0–5 scale?

A 0–5 score is:

- simple for UI
- easy to average
- consistent across modules

In this project:

- **0** = critical failure / missing / cannot load
- **1** = very weak
- **2** = below average
- **3** = acceptable but improvable
- **4** = strong
- **5** = excellent

## 6.2 Overall score calculation

Overall score is a simple mean of included module scores:

$$\text{overall} = \frac{\sum_i s_i}{n}$$

Rounded to 2 decimals.

---

# 7. SEO audit module

## 7.1 Goal

The SEO module checks the presence of basic on-page metadata that influences:

- Google snippet quality
- social link previews
- canonical URL handling

## 7.2 Core steps

1) Fetch HTML (requests)
2) If blocked, fallback to Playwright
3) Parse HTML using BeautifulSoup
4) Extract tags:
   - `<title>`
   - `<meta name="description">`
   - `<meta name="keywords">`
   - Open Graph (og:title, og:description, og:image, og:url)
   - Twitter cards (twitter:title, twitter:description, twitter:image)
   - canonical link
   - first `<h1>`

## 7.3 Rating

Each missing element adds a flaw and reduces score. The module awards partial points per tag and returns a score in 0–5.

---

# 8. SSL audit module

## 8.1 Goal

SSL checks build trust signals:

- Is HTTPS accessible?
- Is the certificate valid?
- Does HTTP redirect to HTTPS?
- Is HSTS enabled?

## 8.2 Certificate verification

The SSL module uses:

- `ssl.create_default_context()`
- socket TLS wrap with SNI

This helps classify:

- self-signed certificates
- hostname mismatch
- expired certificates
- general verification failures

## 8.3 Rating logic

Scoring is deterministic:

- 0: HTTPS not accessible
- 1: HTTPS works but certificate invalid
- 2: cert ok but no HTTP→HTTPS redirect
- 3–5: depends on HSTS and days until expiry

---

# 9. Load speed audit module

## 9.1 Two approaches in codebase

There are two speed-related implementations in the repo:

1) Orchestrator’s built-in speed check uses `requests.get(...)` and measures elapsed time.
2) `modules/load_speed.py` is a script-style checker that uses Playwright and browser performance timing.

## 9.2 What the API currently uses

`WebsiteAuditOrchestrator._audit_speed()` uses the **requests-based** approach for fast scoring.

Measured:

- response time (ms)
- page size (bytes)

---

# 10. Responsiveness audit module

## 10.1 Goal

Estimate whether a website provides a usable mobile experience.

Checks include:

- viewport meta presence
- horizontal overflow
- whether a responsive media query matches as expected

## 10.2 How it works

Uses Playwright to render pages in two viewports:

- mobile viewport (phone-like)
- desktop viewport (laptop-like)

It crawls internal links (same domain), then checks up to `MAX_PAGES_TO_CHECK` pages.

## 10.3 Evidence via screenshots

The module is configured to always save screenshots.

This is valuable for FYP documentation because it creates objective proof.

---

# 11. Social links audit module

## 11.1 Goal

Check whether the website exposes real social media profiles and whether those links are accessible.

## 11.2 Extraction

- Requests homepage HTML
- Parses `<a href>` links using BeautifulSoup
- Detects known social domains

## 11.3 Accessibility verification

Some platforms block bots:

- LinkedIn/Facebook/TikTok may return 403/429/999

When this happens, the module verifies with Playwright:

- if the page opens in a browser, it is counted as accessible

---

# 12. Image ALT tags audit module

## 12.1 Goal

ALT text improves:

- accessibility (screen readers)
- SEO relevance
- image search visibility

## 12.2 Approach

- Use Playwright to crawl internal pages
- For each image: evaluate `alt` rules

Common flaws:

- missing alt
- empty alt
- generic alt ("image", "logo")
- alt too short/too long
- alt looks like filename

---

# 13. Concurrency + timeouts + reliability

## 13.1 Reliability philosophy

This project treats audits as best-effort:

- partial results are acceptable
- do not fail the whole response when one module fails

## 13.2 Practical timeouts

- per-module future timeout: 120s
- requests timeout: 15s for speed module
- Playwright timeouts vary by module (20–30s)

---

# 14. Data model (schemas)

The audit schemas are in `app/schemas/audit.py`.

Key design:

- Separate schema per module result
- Each contains `score` and `flaws`

This structure makes it easy for:

- Next.js to display module-by-module cards
- outreach to pick specific issues

---

# 15. Integration with the Business module

Your business API supports:

- auditing a saved business by `id`

Flow:

1) Business record includes `website`
2) Endpoint triggers orchestrator
3) Business JSON is updated with:
   - `audit_completed`
   - `audit_summary`
   - `audit_recommendations`
   - `overall_score`

---

# 16. Integration with the Outreach pipeline

The outreach pipeline uses the audit output in two ways:

1) Directly: `/outreach/full-pipeline` calls `WebsiteAuditOrchestrator`
2) Indirectly: email generation request takes the scores as inputs

Important: in the **Email Writing Agent** implementation, scores should be translated into plain language (do not show “3/5” to business owners).

---

# 17. Next.js frontend integration guide

This backend is FastAPI. In Next.js, treat it as a separate API server.

## 17.1 Recommended frontend architecture

- Next.js pages/components call FastAPI endpoints
- Use environment variable `NEXT_PUBLIC_API_BASE_URL`

Example:

- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`

## 17.2 Fetch example (client component)

```ts
const base = process.env.NEXT_PUBLIC_API_BASE_URL;
const res = await fetch(`${base}/api/v1/audits/run`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ website_url: 'https://example.com' })
});
const data = await res.json();
```

## 17.3 UI mapping

A clean Next.js UI typically uses:

- Summary header: overall score + summary text
- Module cards: SEO/SSL/Speed/Responsiveness/Social/Images
- Recommendation list

---

# 18. Operational notes (Playwright)

Because several checks rely on Playwright:

- you must install Playwright browsers in the deployment environment
- headless Chrome/Chromium must be permitted

In dev:

- `pip install playwright`
- `playwright install`

---

# 19. Security, privacy, and compliance

The module fetches public websites only, but still must be careful:

- Do not crawl authenticated pages
- Limit pages and timeouts
- Avoid storing sensitive HTML

---

# 20. Testing strategy

Recommended tests:

- unit tests for rating functions (pure logic)
- integration tests against known stable URLs
- contract tests for API response shape (Next.js depends on this)

---

# 21. Limitations and future work

- Replace requests speed check with full Navigation Timing measurement
- Add robots.txt compliance for deeper crawling
- Add caching for repeated audits
- Add language detection and content quality scoring

---

# 22. Conclusion

The Website Audit module provides the technical “evidence” and prioritization needed to run effective outreach. Its outputs feed directly into AI email generation, converting measurable website weaknesses into business outcomes and action plans.
