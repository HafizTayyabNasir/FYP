# 05 — Website Crawling & Contact Extraction (Theory)

## 5.1 Purpose

After businesses are discovered, the system needs contact channels to enable outreach.

Because OSM records often lack emails, the system crawls a business website to extract:

- email addresses
- phone numbers
- social media profiles (Facebook, Instagram, X/Twitter, LinkedIn, etc.)

## 5.2 Web Crawling vs Web Scraping

- **Crawling**: navigating multiple pages and collecting content.
- **Scraping**: extracting structured signals from content.

The project combines both:

- a limited crawl across likely contact pages,
- extraction logic based on regex + heuristics.

## 5.3 Constraints of Real-World Websites

### 5.3.1 Anti-bot defenses
- rate limiting
- bot detection
- JavaScript rendering requirements

### 5.3.2 Content variability
- contact pages may be named differently ("Reach us", "Find us")
- emails may be obfuscated
- contact forms may replace visible emails

### 5.3.3 Internationalization
- non-English keywords
- phone number formats differ

These constraints justify fallback strategies and heuristic design.

## 5.4 Crawl Strategy (Theory)

### 5.4.1 Seed URL
The homepage is the starting point.

### 5.4.2 Candidate contact pages
A fixed list of common paths:

- `/contact`, `/contact-us`, `/about`, `/locations`, `/visit`, `/hours`, ...

This increases probability of finding contact info without full site crawling.

### 5.4.3 Dynamic link discovery
From the homepage, parse `<a>` links with contact-related keywords:

- “contact”, “about”, “reach”, “visit”, “location”, etc.

This handles websites whose contact pages do not match standard paths.

### 5.4.4 Depth and page limits
A production crawler must limit depth/pages to avoid:

- long runtimes
- excessive traffic (ethical concern)
- duplicate content

The project uses `max_pages` as a practical bound.

## 5.5 Rendering Model: Requests vs Headless Browser

### 5.5.1 HTTP fetch
Simple approach:

- `GET URL` and parse HTML.

Advantages:

- fast
- low resource usage

Disadvantages:

- fails on JS-rendered content
- fails if site uses client-side routing

### 5.5.2 Headless browser (Playwright)
A browser engine renders JavaScript, providing final DOM.

Advantages:

- works on SPA/React websites
- captures dynamic content

Disadvantages:

- heavier CPU/memory
- slower
- can be blocked by anti-bot scripts

The ideal system uses a hybrid approach:

- try requests-first
- fallback to headless when blocked or empty

## 5.6 Contact Extraction: Email Addresses

### 5.6.1 Regex extraction
Common regex:

- `[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}`

Limitations:

- matches junk strings inside scripts,
- may match image filenames (e.g., `sprite@2x.png`).

### 5.6.2 mailto links
Many sites include:

- `<a href="mailto:info@example.com">...`.

Extracting from mailto is often high precision.

### 5.6.3 Structured data (JSON-LD)
Modern sites embed schema.org markup:

- `<script type="application/ld+json">{ "email": "..." }</script>`

Extracting from JSON-LD improves recall.

### 5.6.4 URL-encoded emails
Some pages encode `@` as `%40`.

### 5.6.5 Filtering junk emails
Production crawlers must filter:

- sentry/analytics emails
- placeholders (`example.com`, `domain.com`)
- `noreply@` / `mailer-daemon@`
- platform/vendor emails unrelated to the business

Filtering reduces false positives, which is crucial because sending outreach to wrong addresses damages reputation.

### 5.6.6 Choosing the “best” email
Heuristic ranking:

- prefer `info@`, `contact@`, `hello@`, `support@`
- prefer non-free email domains when available

This is explainable and works well for outreach.

## 5.7 Contact Extraction: Phone Numbers

### 5.7.1 Regex challenges
Phone numbers appear in many formats:

- `(123) 456-7890`
- `+92 300 1234567`
- `020 1234 5678`

Regex should handle:

- optional country code
- optional separators
- parentheses

### 5.7.2 Normalization
Normalize extracted phones into a canonical format:

- remove spaces and punctuation
- store original + normalized

Advanced approach:

- use `phonenumbers` library to parse by region.

## 5.8 Social Media Link Extraction

### 5.8.1 Motivation
Even without email, social profiles can be used for outreach.

### 5.8.2 Profile link patterns
Use regex patterns for:

- Facebook pages
- Instagram profiles
- X/Twitter handles
- LinkedIn company pages
- YouTube channels

### 5.8.3 Avoiding false positives
Social domains contain non-profile URLs:

- Facebook plugins
- Twitter share intents
- YouTube watch URLs

Rules:

- skip known non-profile paths
- validate that a username/path exists

## 5.9 Crawl Quality and Performance

### 5.9.1 Timeouts
Use sensible timeouts:

- connect timeout (fail fast)
- read timeout (wait for page content)

### 5.9.2 Concurrency
Crawling multiple sites should be concurrent, but bounded.

Risks of unbounded concurrency:

- memory spikes
- overwhelming target sites
- unstable results

### 5.9.3 Idempotency
Repeated crawling should be safe:

- do not repeatedly crawl the same pages if data already known
- cache results by domain

## 5.10 Security Considerations

Crawling arbitrary URLs introduces risks:

- SSRF (server-side request forgery) where attacker forces backend to fetch internal IPs
- large downloads (resource exhaustion)
- malicious HTML designed to exploit parsers

Mitigations:

- allowlist schemes (http/https only)
- block private IP ranges
- enforce max response size
- avoid executing untrusted scripts (headless browsers still execute JS — caution)

## 5.11 Evaluation and Measurement

Metrics:

- precision of extracted emails (manual validation)
- recall (how often a business has an email and the system finds it)
- time per website
- average pages crawled per site

## 5.12 Failure Modes

- websites block headless browsers
- emails only present behind forms
- content is rendered after long async calls

Possible improvements:

- screenshot/DOM heuristics
- OCR for image-based emails (ethically questionable)
- use contact form analysis and provide “contact form link” as fallback

## 5.13 Summary

Website crawling + contact extraction converts raw discovery results into actionable prospects. A hybrid fetch strategy (requests + Playwright) and robust filtering are essential to minimize false positives and support ethical, reliable outreach.
