# 07 — Audit Modules Detail (Theory)

## 7.1 Module: SEO Metadata

### 7.1.1 Objective
Evaluate whether a page provides baseline metadata required for search engines and social previews.

### 7.1.2 What is SEO metadata
Key signals include:

- `<title>` tag
- `<meta name="description">`
- `<meta name="keywords">` (less important today, but still seen)
- canonical link (`<link rel="canonical">`)

Social preview metadata:

- Open Graph (`og:title`, `og:description`, `og:image`, `og:url`)
- Twitter Cards (`twitter:title`, `twitter:description`, `twitter:image`)

### 7.1.3 Why it matters (business impact)
- missing title/description reduces click-through rate from search
- missing OG/Twitter tags causes poor link previews
- missing canonical can create duplicate content issues

### 7.1.4 Typical checks
- existence of each tag
- non-empty content
- reasonable length heuristics:
  - title ~ 30–60 chars
  - description ~ 120–160 chars

### 7.1.5 Scoring rubric (example)
- 5: title + description + canonical + OG/Twitter + H1 present
- 3–4: core tags present but missing some social/secondary tags
- 1–2: title present but missing description/canonical
- 0: cannot fetch page or no metadata

### 7.1.6 Limitations
- true SEO requires content quality, backlinks, internal linking
- metadata presence is only a baseline

## 7.2 Module: SSL & HTTPS

### 7.2.1 Objective
Check whether the site uses HTTPS correctly and provides a trusted certificate.

### 7.2.2 Theory: TLS and certificates
TLS provides:

- encryption (confidentiality)
- integrity (tamper resistance)
- authentication (certificate binds domain to key)

Certificates have:

- issuer
- validity window
- domain names (SAN)

### 7.2.3 Typical checks
- HTTPS reachable
- certificate is verifiable (not self-signed)
- certificate validity dates
- redirects from HTTP → HTTPS
- HSTS header presence

### 7.2.4 Why it matters
- browsers show “Not Secure” warnings
- HTTPS is a ranking signal
- user trust and conversion impact

### 7.2.5 Scoring rubric
- 5: valid cert, redirects ok, HSTS present, expiry ≥30 days
- 4: valid cert + redirect ok but no HSTS (or near expiry)
- 3: valid cert but weak redirect configuration
- 1: HTTPS works but certificate invalid
- 0: HTTPS not accessible

### 7.2.6 Limitations
- deeper security requires header scan, TLS config scan, vulnerability checks

## 7.3 Module: Load Speed (Basic Performance)

### 7.3.1 Objective
Estimate responsiveness and page weight.

### 7.3.2 Theory: performance metrics
Common metrics:

- TTFB (time to first byte)
- DOMContentLoaded
- LCP (Largest Contentful Paint)
- Total Blocking Time

This project uses a simplified approach:

- measure total response time
- approximate load time
- inspect page size

### 7.3.3 Why it matters
- speed is correlated with conversion
- slow pages increase bounce rate

### 7.3.4 Scoring rubric (example)
- 5: <1s
- 4: 1–2s
- 3: 2–3s
- 2: 3–5s
- 1: 5–8s
- 0: >8s or failure

### 7.3.5 Limitations
- one request does not represent user experience
- geographic distance affects latency

### 7.3.6 Future enhancement
Integrate PageSpeed API (Lighthouse) for real UX metrics.

## 7.4 Module: Responsiveness / Mobile-Friendly

### 7.4.1 Objective
Check for basic signals that the website supports mobile devices.

### 7.4.2 Theory
Mobile-friendly sites:

- include viewport meta tag
- use responsive CSS (media queries)
- use fluid layouts

### 7.4.3 Checks
- `meta name="viewport"`
- content includes `width=device-width`
- presence of media queries or responsive framework classes

### 7.4.4 Business impact
- most local businesses get significant traffic from mobile
- poor mobile UX reduces calls/bookings

### 7.4.5 Limitations
- true responsiveness requires layout testing in real viewports

## 7.5 Module: Social Links

### 7.5.1 Objective
Detect whether site links to social profiles.

### 7.5.2 Why it matters
- social proof and trust
- alternative contact channels
- cross-platform brand consistency

### 7.5.3 Checks
- extract links to known social domains
- check accessibility and broken links

### 7.5.4 Limitations
- link presence doesn’t mean active engagement

## 7.6 Module: Image Alt Tags

### 7.6.1 Objective
Assess whether images include alt attributes.

### 7.6.2 Theory
Alt text supports:

- accessibility for screen readers
- SEO for image search
- content comprehension

### 7.6.3 Checks
- count images
- count images missing `alt` or with empty alt
- compute coverage percentage

### 7.6.4 Business impact
- accessibility compliance and user inclusivity
- improved SEO signals

### 7.6.5 Limitations
- alt quality is hard to evaluate automatically

## 7.7 Error Handling in Audit Modules

Audit modules should classify errors:

- DNS failure
- timeout
- SSL error
- blocked by bot protection

For reporting, store:

- error type
- error message
- module score set to 0

This makes results explainable.

## 7.8 Cross-Module Consistency

To keep the audit meaningful:

- use consistent score ranges (0–5)
- keep flaw descriptions human-friendly
- avoid overly technical jargon when possible

A recommended practice is to map flaws to:

- “user impact” statement
- “fix recommendation” statement

## 7.9 Summary

This chapter details the theory and evaluation rationale for each website audit module. These modules produce explainable results suitable for outreach and academic reporting.
