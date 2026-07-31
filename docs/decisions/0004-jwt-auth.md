# 0004. JWT-based authentication with server-side revocation state

## Status

Accepted (backfilled 2026-07-31; introduced with roadmap issue
"phase-1-03 Auth router → DB + JWT" and extended by phase-4 hardening).

## Context

A mobile client needs stateless request authentication that survives app
restarts without a session store round-trip on every call, while the
product's privacy posture demands the ability to revoke access and resist
credential abuse.

## Decision

Authenticate with JWTs issued by the backend auth router
(`backend/src/routers/auth.py`) and managed on the client by an
`AuthContext` (`frontend/src/context/` — token storage and attachment to API
calls). Keep the security-relevant state server-side in dedicated tables:
`revoked_token.py`, `login_attempt.py`, `password_reset_token.py`, and
`auth_identity.py` under `backend/src/models/`, with rate limiting (slowapi)
and security-header middleware wired in `backend/src/main.py`.

## Consequences

- API requests are self-authenticating; the client persists the token and
  the auth context rehydrates it on launch.
- Statelessness is deliberately compromised where it matters: token
  revocation and login-attempt throttling require DB lookups, trading pure
  JWT purity for the ability to lock out a compromised credential.
- Password-reset and multi-identity flows have first-class storage rather
  than ad-hoc token columns.
- Future auth changes (new identity providers, token rotation) must extend
  the models above rather than bypass them.
