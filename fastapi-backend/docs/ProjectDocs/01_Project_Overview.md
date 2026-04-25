# 01 — Project Overview

## 1.1 Project Title

**AI Powered Client Hunt & Outreach** — a system that discovers potential business clients, evaluates their websites, extracts contact channels, and generates personalized outreach emails.

## 1.2 Motivation

Many small and medium businesses have websites that are outdated, slow, inaccessible, missing search metadata, or misconfigured for security. Agencies and freelancers often spend time manually:

- searching for businesses in a location,
- collecting websites and emails,
- auditing pages (SEO/SSL/performance/mobile),
- crafting outreach messages.

This project automates most of the pipeline while still keeping a human-in-the-loop approach (the user can review results before sending).

## 1.3 Problem Statement

Given a business type and location, the system should:

1. Identify candidate businesses.
2. Retrieve business metadata (name, address, website, phone).
3. If a website exists, optionally crawl it for contact information.
4. Run a multi-module audit on the website.
5. Convert audit findings into actionable recommendations.
6. Generate a tailored outreach email emphasizing measurable impact.
7. Provide basic campaign and inbox management.

## 1.4 Objectives

### Functional objectives

- Business discovery using OpenStreetMap (OSM) data.
- Geocoding to a city center with country verification.
- Website crawling (HTTP + headless browser fallback) for emails, phones, and social links.
- Website audits with modular design:
  - SEO metadata
  - SSL certificate quality
  - Load speed
  - Mobile responsiveness
  - Social links
  - Image alt-text (accessibility/SEO)
- Outreach email generation via LLM-based agent prompts.
- SMTP sending (and optional inbox/thread management patterns).

### Non-functional objectives

- Reliability against unstable third-party APIs and slow sites.
- Reasonable performance (parallelism for audits and crawling).
- Security-conscious handling of secrets and outbound communication.
- Extensibility: easy to add new audit modules, new data sources, and new outreach strategies.

## 1.5 Scope

### Included

- FastAPI web + API server for user interaction.
- Modular services layer for discovery/audit/crawling/outreach.
- File-based persistence for demo mode (JSON files).

### Excluded or future work

- Full production database schema and migrations (the repository includes placeholder DB modules).
- Enterprise-scale campaign analytics (open/reply tracking requires pixel/tracking + mailbox integration).
- Full authentication/authorization hardening (an auth endpoint file exists, but security modules may be incomplete).

## 1.6 Stakeholders and Users

- **Primary user**: Outreach operator (student/researcher/agency).
- **Target audience**: Local businesses needing improved websites.
- **System stakeholders**: Developers/maintainers, project supervisor, evaluation committee.

## 1.7 Key Concepts (Definitions)

- **Lead / Prospect**: A candidate business that may be contacted for services.
- **Enrichment**: Adding more attributes to a record (emails, social links, scores).
- **Audit module**: A self-contained evaluation unit producing a score and flaws.
- **Score**: Numeric summary (e.g., 0–5) representing quality/completeness.
- **LLM**: Large Language Model used for text generation and extraction.
- **Deliverability**: Probability that an email reaches inbox rather than spam.

## 1.8 Typical End-to-End Use Case

1. User selects a business category (e.g., dentist) and location.
2. System queries OSM (via Overpass) to return businesses.
3. User saves selected businesses.
4. For businesses with websites:
   - crawl site to extract contact details,
   - run website audit.
5. User selects a business and generates outreach email.
6. User sends via SMTP or queues messages for a campaign.
7. User monitors threads/inbox.

## 1.9 Data Sources and External Dependencies

- **OpenStreetMap + Overpass API** for business discovery.
- **Nominatim** (geocoding servers) for resolving city coordinates.
- **Websites** (HTTP/HTTPS) as direct data source.
- **Playwright** as headless browser to render JavaScript-heavy pages.
- **LLM providers** (Groq/OpenAI/Grok keys appear in settings) for AI-generated content.

## 1.10 Why Modular Design Matters

A modular pipeline helps in both engineering and academic reporting:

- Each module can be tested independently.
- Scores can be weighted or swapped without rewriting the orchestrator.
- Researchers can evaluate module-level effectiveness (e.g., SEO scoring vs user conversion).
- Enhancements (e.g., adding accessibility audits) do not break existing features.

## 1.11 Research/Academic Relevance

This project spans multiple research areas:

- Information Retrieval (discovering leads from OSM)
- Web Mining / Web Scraping (contact extraction)
- Software Quality Metrics (web audit scoring)
- Natural Language Generation (personalized outreach emails)
- Systems Engineering (API design, orchestration, concurrency)
- Security and Privacy (handling personal data, SMTP credentials)

## 1.12 Success Criteria

A deployment is considered successful if:

- business discovery returns usable results for common categories and locations,
- crawling finds contact channels on a significant fraction of websites,
- audits complete with meaningful findings and stable performance,
- generated emails are coherent, specific, non-spammy, and aligned with audit findings,
- the UI/API provides a usable workflow for end-to-end outreach.

## 1.13 Assumptions

- OSM data is reasonably complete for the selected location.
- Businesses maintain at least one public webpage containing contact information.
- The user has permission to send outreach emails (compliance depends on jurisdiction).
- SMTP credentials are valid and configured.

## 1.14 Constraints

- Third-party API rate limiting and downtime.
- Websites may block bots, require JavaScript, or contain obfuscated contact info.
- Email deliverability varies by domain reputation and content.

## 1.15 Document Structure

The rest of the documentation proceeds from architecture to modules:

- System architecture and data flow
- FastAPI API layer
- OSM discovery and enrichment
- Crawling and contact extraction
- Website audit system + module details
- Scoring, summaries, recommendations
- AI agents and outreach composition
- Campaigns and inbox features
- Data storage and future DB design
- Security/privacy/compliance
- Testing and deployment
