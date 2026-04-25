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
