# 16 — Full Stack SaaS Implementation & Architecture

## 16.1 Transition to Production SaaS
The project has evolved from a local minimal viable product (MVP) into a production-grade Software-as-a-Service (SaaS) platform. This architectural shift separates concerns across distinct deployment environments:
- **Frontend Layer**: Deployed on Vercel utilizing the Next.js 14 App Router.
- **Backend API Layer**: Deployed on Render utilizing FastAPI.
- **Persistence Layer**: Managed via Supabase (PostgreSQL), utilizing connection pooling (pgbouncer) for high-concurrency requests.

## 16.2 Deployment Pipeline & CORS Strategy
### Cross-Origin Resource Sharing (CORS)
To securely facilitate communication between the Vercel frontend and Render backend, the backend is configured with dynamic CORS middleware:
- `ALLOWED_ORIGINS` strictly defines domains (e.g., `https://ai-client-hunting.vercel.app`) permitted to make API calls.
- Preflight requests (`OPTIONS`) are natively handled by FastAPI's `CORSMiddleware`.

### Environment Configuration Management
Strict separation of environment variables is maintained to ensure security and flexibility:
- **Backend (.env)**: Stores `DATABASE_URL`, `SECRET_KEY`, `GOOGLE_CLIENT_SECRET`, and `RESEND_API_KEY`.
- **Frontend (.env.local)**: Stores `NEXT_PUBLIC_API_URL` to route client-side fetch requests to the correct backend endpoint dynamically.

## 16.3 High Availability & Scaling
By deploying on Vercel and Render, the system leverages edge caching and horizontal scaling. The FastAPI backend utilizes `asyncpg` combined with Supabase's transaction pooler (port 6543) to prevent connection exhaustion during concurrent web crawling and auditing tasks.
