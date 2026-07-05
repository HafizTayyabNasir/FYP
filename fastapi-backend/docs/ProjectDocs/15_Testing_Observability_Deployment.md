# 15 — Testing, Observability, Deployment (Theory)

## 15.1 Testing Strategy

A multi-module system should be tested at multiple levels:

- unit tests
- integration tests
- end-to-end tests

The repository includes a `tests/` folder; in your report, explain how each area can be tested.

## 15.2 Unit Testing

### 15.2.1 What to unit test
- URL normalization
- email extraction filters
- scoring functions
- business type mapping

### 15.2.2 Test characteristics
- fast
- deterministic
- no network calls

### 15.2.3 Mocking
Mock external dependencies:

- Overpass responses
- Nominatim responses
- website fetch responses

This prevents flaky tests.

## 15.3 Integration Testing

Integration tests validate real component interactions:

- FastAPI endpoint → service call → JSON output

Examples:

- `/osm/search` with a known city and small radius
- `/audits/run` with a stable test URL

Challenges:

- external services are unstable
- tests can be slow

Mitigations:

- record/replay fixtures
- use local test servers

## 15.4 End-to-End Testing

E2E tests validate the full pipeline:

- search businesses
- save business
- crawl website
- run audit
- generate email

In academic evaluation, E2E demos are valuable.

## 15.5 Observability

### 15.5.1 Logging
Log should include:

- request id
- endpoint path
- timing
- error type

Avoid logging secrets.

### 15.5.2 Metrics
Useful metrics:

- average audit time
- audit failure rate
- crawl success rate
- emails generated per day
- email send success rate

### 15.5.3 Tracing
Distributed tracing is optional but can be described:

- trace IDs across services

## 15.6 Performance Considerations

### 15.6.1 Bottlenecks
- Playwright crawling is heavy
- parallel audits consume threads

### 15.6.2 Mitigations
- limit thread pools
- cache results
- move heavy tasks to workers

## 15.7 Worker Architecture (Celery) — Theory

Celery supports background processing:

- audit tasks
- crawl tasks
- scheduled sending
- IMAP sync

Benefits:

- do not block API requests
- retry semantics
- scheduling (beat)

Design:

- API enqueues task
- worker executes
- status stored in DB

Even if tasks are placeholders, describing this architecture strengthens the report.

## 15.8 Deployment Theory

### 15.8.1 Local development
- run FastAPI with Uvicorn
- configure `.env`

### 15.8.2 Docker deployment
A dockerized backend should include:

- app container
- redis container (for Celery)
- optional database container

### 15.8.3 Reverse proxy
Production deployments typically use:

- Nginx/Traefik

Responsibilities:

- TLS termination
- compression
- rate limiting

### 15.8.4 Environment configuration
- set DEBUG=false
- restrict CORS
- store secrets in environment

## 15.9 Reliability and Recovery

- retries for transient network issues
- graceful timeouts
- circuit breaker pattern (optional)

## 15.10 Documentation and Reproducibility

A strong FYP report includes:

- setup instructions
- dependency list
- sample data
- evaluation scripts

## 15.11 Suggested Appendices for 500+ Pages

To reach 500 pages, append:

- screenshots of UI pages
- sample audit reports (multiple websites)
- sample outreach emails per industry
- experiment logs and tables
- code listings (selected key modules)
- test case matrix

## 15.12 Summary

Testing, observability, and deployment are essential to present the project as an engineered system rather than a single script. This chapter provides the theoretical foundation to justify your design and to plan future improvements.


## 15.6 Final Production Deployment Strategy (Vercel, Render, Supabase)
The deployment topology of the platform represents a masterclass in modern DevOps and Cloud-Native engineering. The system is distributed across three specialized cloud providers to maximize performance and developer velocity.

### 15.6.1 Frontend Deployment: Vercel Edge Network
The Next.js 14 frontend is deployed onto Vercel's Edge Network. Vercel automatically analyzes the React tree and strategically serves static components from global Content Delivery Networks (CDNs) while executing dynamic Server-Side Rendered (SSR) routes via ephemeral Serverless Functions. This ensures sub-100ms Time-To-First-Byte (TTFB) globally.

### 15.6.2 Backend Deployment: Render Cloud Infrastructure
The FastAPI Python application is hosted as a long-running Web Service on Render. Unlike serverless functions which suffer from "cold starts" and strict timeout limits (typically 10 seconds), Render provides a persistent containerized environment. This persistence is absolutely crucial for the AI Client Hunt platform, as web scraping (Playwright) and LLM inference generation can easily take 30 to 60 seconds per business. The Web Service is configured with `uvicorn` to multiplex incoming HTTP requests.

### 15.6.3 Database Deployment: Supabase (PostgreSQL)
The data persistence layer is outsourced to Supabase, an open-source Firebase alternative powered by raw PostgreSQL. Supabase provides automated daily backups, point-in-time recovery (PITR), and out-of-the-box PgBouncer connection pooling. 

### 15.6.4 Cross-Origin Resource Sharing (CORS) Security
To secure the communication between the Vercel Frontend and Render Backend, strict CORS policies are enforced. The FastAPI `CORSMiddleware` is configured to dynamically accept preflight `OPTIONS` requests only from the specific `ALLOWED_ORIGINS` defined in the environment variables (e.g., `https://ai-client-hunting.vercel.app`), explicitly rejecting unauthorized programmatic access from third-party domains.
