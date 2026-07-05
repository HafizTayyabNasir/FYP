# 19 — Advanced Authentication & OAuth Architecture

## 19.1 JWT-Based Authentication Lifecycle
The system implements a robust, stateless authentication mechanism utilizing JSON Web Tokens (JWT).
- **Algorithm**: `HS256` hashing with a securely generated `SECRET_KEY`.
- **Token Claims**: Tokens encode the user's `sub` (UUID) and `exp` (expiration timestamp) to prevent replay attacks.
- **Password Security**: Passwords are mathematically hashed using `bcrypt` (v3.2.0 for `passlib` compatibility) with appropriate salt rounds before database persistence.

## 19.2 OAuth 2.0 Integration (Google Cloud)
To facilitate seamless outreach without requiring users to share raw SMTP credentials, the platform integrates Google OAuth.
- **Consent Flow**: The backend generates an authorization URL with scopes `gmail.send`, `gmail.readonly`, and `userinfo.profile`.
- **Token Exchange**: The `/google/callback` endpoint securely exchanges the authorization code for an `access_token` and `refresh_token`.
- **At-Rest Encryption**: OAuth tokens are encrypted using `cryptography.fernet` (AES) before being stored in the Supabase database to prevent credential leakage in the event of a data breach.

## 19.3 Email Verification Workflow
- **Resend API**: Upon registration, a unique, cryptographically secure token is generated and dispatched to the user's email via the Resend API.
- **Time-Bound Validity**: Verification tokens are strictly time-bound (e.g., 24 hours), utilizing timezone-aware `datetime.now(timezone.utc)` objects in PostgreSQL (`TIMESTAMP WITH TIME ZONE`).
