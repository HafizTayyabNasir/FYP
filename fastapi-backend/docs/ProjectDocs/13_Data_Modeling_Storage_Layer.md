# 13 — Data Modeling & Advanced Storage Layer (PostgreSQL / Supabase)

## 13.1 Transition to Relational Database Management Systems (RDBMS)
Initially prototyped with JSON and SQLite, the final production architecture implements a highly scalable, fully relational PostgreSQL database hosted on Supabase. This evolution guarantees ACID (Atomicity, Consistency, Isolation, Durability) properties, which are critically mandatory for a multi-tenant SaaS handling sensitive OAuth tokens, billing, and user identities.

## 13.2 Asynchronous Database Connectivity (`asyncpg`)
To prevent the database from becoming a bottleneck during concurrent AI scraping operations, the system leverages `SQLAlchemy 2.0` in strictly asynchronous mode via the `asyncpg` driver. Furthermore, Supabase's transaction-mode connection pooler (listening on port 6543) acts as a reverse proxy, drastically reducing the memory overhead of maintaining thousands of idle PostgreSQL connections.

## 13.3 Core Entity-Relationship (ER) Models

### 13.3.1 User Entity (`users` table)
The foundational identity model. It utilizes cryptographic UUIDs (Universally Unique Identifiers) rather than sequential integers to prevent enumeration attacks.
- `id` (UUID): Primary Key.
- `email` (VARCHAR): Unique constraint, indexed for rapid authentication lookups.
- `hashed_password` (VARCHAR): Secured via `bcrypt` (v3.2.0 for `passlib` compatibility).
- `is_verified` (BOOLEAN): Gatekeeps access until Resend API email verification completes.
- `role` (VARCHAR): Facilitates Role-Based Access Control (RBAC), distinguishing `admin` from `user`.

### 13.3.2 Pricing Plan Entity (`pricing_plans` table)
Facilitates dynamic SaaS monetization.
- `slug` (VARCHAR): Unique identifier (e.g., 'individual', 'team').
- `price` (FLOAT): Billing amount.
- `features` (JSONB): A PostgreSQL binary JSON field storing the feature matrix, allowing for highly flexible, schema-less updates to plan capabilities without requiring complex database migrations.

### 13.3.3 Email Accounts Entity (`email_accounts` table)
Stores the credentials required for the Outreach Dispatcher.
- `provider` (VARCHAR): Enum identifying `google`, `microsoft`, or `smtp`.
- `access_token` & `refresh_token` (VARCHAR): Encrypted at rest using AES (Advanced Encryption Standard) via the `cryptography.fernet` library. This is a critical security compliance measure.
- `smtp_host` & `smtp_port`: For generic providers (GoDaddy, Hostinger).

## 13.4 Migration Strategy and Initialization
The database utilizes a declarative schema generation approach (`Base.metadata.create_all`). An asynchronous seeding script (`init_db.py`) automatically provisions the initial administrative user and constructs the default pricing plans upon the first deployment to the Render cloud infrastructure.
