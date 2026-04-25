# Module 3: Business Data Crawling & Collection (Website Scraping + Contact Extraction)

## AI‑Powered Client Hunt & Outreach — Final Year Project (FYP) Documentation

---

## Purpose of this module

OSM and other data sources often provide incomplete contact details:

- many businesses have no email address in OSM
- many businesses have no website URL
- phone and social links are inconsistent

This module fills the gap by **crawling websites** (when available) and extracting:

- emails
- phone numbers
- social media profile URLs

It is used in two places:

1) **During OSM search enrichment** (optional) — fast enrichment for websites already present in OSM
2) **For saved businesses** — a deeper crawl triggered on demand via API

---

# Table of Contents

1. System role and scope
2. Design goals
3. Code map (where each part lives)
4. Data structures (ScrapedContacts)
5. Crawl strategy: page selection and link discovery
6. Extraction pipelines
   - email extraction
   - phone extraction
   - social profile extraction
7. Anti-noise filtering (junk emails)
8. Concurrency model and performance
9. API endpoints for crawling
10. Persistence model (updating business records)
11. Playwright vs httpx fallback
12. Next.js integration guide
13. Operational notes and deployment
14. Security, ethics, and safe crawling
15. Testing strategy
16. Limitations and future enhancements

---

# 1. System role and scope

## 1.1 Where crawling fits in your product

Your overall product is a lead generation + outreach automation system.

A high-level pipeline is:

1) Find businesses by location/type (OSM)
2) Save businesses locally
3) Crawl websites for contacts
4) Run website audit
5) Generate outreach email and optionally send

This module covers step 3: turning a business website into structured “contact signals”.

## 1.2 What this module does not do

- It does not send emails.
- It does not generate AI content.
- It does not evaluate SEO/SSL/speed (handled by Website Audit module).

---

# 2. Design goals

## 2.1 Accuracy and practicality

The extraction is designed to work on real websites that:

- use JavaScript rendering
- include emails in JSON-LD blocks
- hide contact information on secondary pages

## 2.2 Safety and performance

To stay safe and practical:

- limit total pages crawled per site
- use timeouts
- filter junk emails (analytics, placeholders)
- do not brute force deep crawling

---

# 3. Code map

Key implementation locations:

- Scraper implementation:
  - `app/services/scraping/website_scraper.py`
  - exported via `app/services/scraping/__init__.py`
- Crawl endpoints:
  - `app/api/v1/endpoints/businesses.py`:
    - `POST /api/v1/businesses/{business_id}/crawl`
    - `POST /api/v1/businesses/crawl-url`
- OSM enrichment crawler (simple crawler inside OSM Overpass client):
  - `app/services/osm/overpass_client.py` includes HTML extraction helpers and enrichment functions

---

# 4. Data structures

## 4.1 `ScrapedContacts`

The scraper returns a structured container with:

- `emails: List[str]`
- `phones: List[str]`
- social profile URLs: `facebook`, `instagram`, `twitter`, `linkedin`, `youtube`, `tiktok`
- `pages_crawled: List[str]`
- `best_email`, `best_phone`

This structure supports both UI display (show all emails found) and automation (use best email as primary contact).

---

# 5. Crawl strategy

## 5.1 Page selection: why “contact pages” matter

Most sites keep contact info on predictable paths:

- `/contact`, `/contact-us`
- `/about`, `/about-us`
- `/locations`, `/find-us`
- `/support`, `/help`

The scraper keeps a curated list of “high-value paths” and checks them.

## 5.2 Dynamic contact link discovery

Many websites don’t use standard URL paths. For this reason, the scraper:

- loads the homepage
- scans `<a>` elements
- detects keywords like `contact`, `about`, `location`, `email`
- adds those internal links to `pages_to_check`

This avoids a full crawl while still finding hidden contact pages.

---

# 6. Extraction pipelines

## 6.1 Email extraction

The code applies multiple strategies:

1) standard regex email pattern
2) `mailto:` link extraction
3) JSON-LD parsing (`application/ld+json`)
4) attribute patterns (`data-email=...`)
5) URL-encoded emails (`%40`)

### Why multiple strategies?

Different websites expose emails in different ways; using a single regex misses many cases or produces junk results.

## 6.2 Phone extraction

Phone extraction uses regex patterns and normalization.

Key engineering considerations:

- local formats vary by country
- numbers can contain spaces, hyphens, parentheses
- some numbers are tracking numbers

Your implementation chooses a “best phone” similarly to “best email”.

## 6.3 Social profile extraction

Social links are extracted from HTML content by matching known domain patterns:

- Facebook, Instagram, X/Twitter, LinkedIn, YouTube, TikTok

Skip rules avoid capturing non-profile pages:

- `/share`, `/login`, `/intent`, `/embed`

---

# 7. Anti-noise filtering

A major practical problem in scraping is **false positives**:

- analytics and error reporting emails (e.g., sentry)
- placeholder emails (`example.com`)
- asset filenames that match email regex (`sprite@2x.png`)

This project uses:

- domain blocklists
- pattern blocklists

This improves the quality of extracted leads.

---

# 8. Concurrency model and performance

## 8.1 Why Playwright is used

Many modern sites (React/Next.js) render content client-side. Requests-only scraping will see:

- minimal HTML
- missing footer contact info

Playwright loads the page in a real browser engine, making extraction more reliable.

## 8.2 Executor compatibility

The scraper contains a sync engine (`WebsiteScraperSync`) which can be run inside a thread executor for async compatibility.

---

# 9. Crawl API endpoints

## 9.1 Crawl a saved business

**Route:** `POST /api/v1/businesses/{business_id}/crawl`

Behavior:

- loads saved businesses from JSON
- finds business by `id`
- verifies `website` exists
- runs Playwright crawl (default)
- falls back to httpx if Playwright fails
- updates the business record with discovered fields

## 9.2 Crawl any URL (utility endpoint)

**Route:** `POST /api/v1/businesses/crawl-url`

**Body:**

- `url: string`
- `use_playwright: boolean`

Returns extraction results without modifying saved businesses.

---

# 10. Persistence model

Your project persists businesses in JSON (`app/data/businesses.json`).

When crawling finds data, the API updates fields:

- `email`
- `phone`
- `facebook`, `instagram`, ...

This is intentionally simple for an FYP: no DB migration complexity and easy to debug.

---

# 11. Playwright vs httpx fallback

## 11.1 Playwright path (primary)

Strengths:

- handles JS rendering
- finds dynamic content
- better at extracting data hidden in menus/footers

Costs:

- heavier CPU/memory
- requires browser installation

## 11.2 httpx fallback (secondary)

When Playwright is unavailable or fails:

- request a small list of contact pages
- parse HTML with BeautifulSoup
- run regex-based extraction

This is less accurate than Playwright but ensures the system still works.

---

# 12. Next.js integration guide

## 12.1 Common UI workflows

Recommended Next.js screens:

- Business list page: show “has email/has website” badges
- Business details page: button “Crawl website”
- Result panel: show extracted emails/phones/social links

## 12.2 Fetch example

```ts
const base = process.env.NEXT_PUBLIC_API_BASE_URL;

const res = await fetch(`${base}/api/v1/businesses/${businessId}/crawl`, {
  method: 'POST'
});

const data = await res.json();
```

---

# 13. Operational notes

To run Playwright-based crawling:

- install Playwright Python package
- install browsers: `playwright install`

In Docker, ensure the image has system dependencies for Chromium.

---

# 14. Security, ethics, and safe crawling

This FYP module crawls public websites. Still follow safe rules:

- respect timeouts and page limits
- avoid crawling login/checkout pages
- do not store full HTML unless needed

---

# 15. Testing strategy

- unit tests for extraction regex helpers
- integration tests against a local mock HTML server
- E2E test: crawl → store → verify business JSON updated

---

# 16. Limitations and future enhancements

- add robots.txt compliance
- add per-domain rate limiting
- support multilingual websites and non-Latin scripts
- add structured extraction for contact forms (not only emails)

---

# Conclusion

The Crawling module is a practical extraction engine that upgrades raw business listings into outreach-ready lead records with real contact channels.
