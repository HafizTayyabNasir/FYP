# 03 — FastAPI API Layer (Theory + Implementation Mapping)

## 3.1 Role of the API Layer

The API layer exposes system capabilities to the web UI and external clients.

In a layered architecture, the API layer should:

- validate input,
- enforce authentication/authorization (if enabled),
- call domain services,
- translate service output into HTTP responses,
- apply consistent error handling.

## 3.2 Why FastAPI

FastAPI is commonly used because:

- **type hints** + Pydantic schemas improve correctness,
- automatic OpenAPI docs enable easy testing,
- async support fits I/O-heavy workloads,
- dependency injection mechanisms encourage clean design.

## 3.3 Application Entry Point

The project initializes the application with:

- `FastAPI(title, version, description, docs_url, redoc_url)`
- CORS middleware
- static file mounting
- Jinja template rendering

Conceptually:

- **API endpoints** live under `/api/v1/...`
- **web pages** render HTML templates at `/`, `/businesses`, etc.

This dual mode is a practical approach for FYP demos:

- UI can be shown without a separate frontend build tool.
- API endpoints remain accessible for Postman testing.

## 3.4 Router Composition

Routers provide modular API design:

- Each feature area has its own router file.
- A top-level router includes each router with prefix and tags.

Benefits:

- avoids a single huge `main.py`,
- makes it easier to assign tasks in a team,
- improves documentation organization via tags.

## 3.5 Request/Response Models (Pydantic)

Pydantic schemas define:

- field types,
- default values,
- constraints (e.g., min/max sizes),
- JSON schema examples.

Advantages:

- better validation than ad-hoc `dict` parsing,
- clear API contracts,
- easier to generate frontend clients.

### 3.5.1 Example: Website audit schema patterns
A typical module schema includes:

- a numeric score in range 0–5,
- a list of flaws (human-readable issue descriptions),
- optional structured fields (timing details, metadata).

This pattern is very report-friendly because it supports both:

- quantitative evaluation (scores), and
- qualitative explanation (flaws + recommendations).

## 3.6 Endpoint Design Principles

### 3.6.1 REST-style resources
Where possible, endpoints follow REST conventions:

- `GET /businesses` list
- `GET /businesses/{id}` retrieve
- `PUT /businesses/{id}` update
- `DELETE /businesses/{id}` delete

### 3.6.2 Task endpoints
Some endpoints represent operations:

- `/audits/run` (run an audit)
- `/businesses/{id}/crawl` (crawl website)

This is acceptable when the operation is not a simple CRUD resource.

### 3.6.3 Bulk endpoints
Bulk operations reduce client overhead:

- `/audits/bulk` audits multiple websites.

In production, bulk tasks often move to background workers.

## 3.7 Async Boundaries and Thread Executors

FastAPI endpoints are async, but many libraries used are synchronous:

- `requests`
- sync Playwright
- some SSL socket operations

If we call these directly inside an async endpoint, the event loop is blocked.

The project uses `ThreadPoolExecutor` + `loop.run_in_executor(...)`:

- the endpoint stays non-blocking,
- the work runs in threads.

Theoretical note:

- In high-scale production, you would use async HTTP clients (httpx async) and avoid thread pools where possible.
- For FYP, a thread pool is a pragmatic solution and easy to explain.

## 3.8 Error Handling Strategy

### 3.8.1 HTTPException
Endpoints raise `HTTPException(status_code, detail)` to:

- return correct HTTP codes,
- provide error details.

### 3.8.2 Graceful module errors
The audit orchestrator catches exceptions per module and returns:

- score 0,
- error text in flaws.

This avoids total failure on partial errors.

### 3.8.3 Input normalization
- URL normalization ensures consistent behavior.
- Geocode matching verifies that the resolved location corresponds to the requested country.

## 3.9 CORS and Frontend Integration

CORS allows browser-based clients to call the API.

In production:

- restrict allowed origins,
- do not set `"*"` when credentials are enabled.

In FYP demos:

- permissive CORS is common for quick testing.

## 3.10 Authentication and Authorization (Theory)

A robust system should include:

- user authentication (session/JWT),
- role-based access control,
- per-user workspaces.

Reasons:

- protect SMTP sending capability,
- protect stored business data,
- prevent abuse.

If auth is incomplete in the current codebase, document it as future work and explain the intended design.

## 3.11 Rate Limiting and Abuse Prevention (Theory)

Public endpoints that fetch URLs or send email are abuse targets.

Mitigations:

- per-IP rate limits,
- CAPTCHA or API key access,
- throttle outbound SMTP send rate,
- domain allow/deny lists.

The repo includes middleware placeholders for rate limiting and request IDs; the security chapter proposes an implementation.

## 3.12 API Endpoint Catalog (Conceptual)

### Health
- `GET /api/v1/health`
- `GET /api/v1/health/detailed`

### OSM
- `POST /api/v1/osm/search`
- `GET /api/v1/osm/business-types`
- `POST /api/v1/osm/geocode`

### Audits
- `POST /api/v1/audits/run`
- `POST /api/v1/audits/bulk`
- `GET /api/v1/audits/quick/{url}`

### Businesses
- `GET /api/v1/businesses`
- `POST /api/v1/businesses/save`
- `PUT /api/v1/businesses/{id}`
- `DELETE /api/v1/businesses/{id}`
- `POST /api/v1/businesses/{id}/audit`
- `POST /api/v1/businesses/{id}/crawl`

### Outreach
- `POST /api/v1/outreach/generate-email`
- `POST /api/v1/outreach/extract-business-data`
- `POST /api/v1/outreach/full-pipeline`
- `POST /api/v1/outreach/send-email`

### Campaigns
- `GET /api/v1/campaigns`
- `POST /api/v1/campaigns`
- `PUT /api/v1/campaigns/{id}`
- `POST /api/v1/campaigns/{id}/start`
- `POST /api/v1/campaigns/{id}/pause`
- `GET /api/v1/campaigns/{id}/stats`

### Mail & Chat
- `GET /api/v1/mail/threads`
- `GET /api/v1/mail/threads/{id}`
- `POST /api/v1/mail/send`
- `POST /api/v1/mail/threads/{id}/reply`
- `PUT /api/v1/mail/threads/{id}/status`
- `DELETE /api/v1/mail/threads/{id}`
- `GET /api/v1/mail/stats`

## 3.13 API Documentation and Testing

FastAPI provides interactive docs:

- Swagger UI
- ReDoc

For academic evaluation, recommend:

- test cases per endpoint,
- sample payloads and responses,
- error case demonstrations.

## 3.14 Summary

The API layer is the boundary between user interaction and domain services. FastAPI + Pydantic provides a strong foundation for typed, self-documenting APIs while still supporting a practical FYP demo through Jinja templates.
