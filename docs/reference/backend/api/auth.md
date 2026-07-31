# API — auth router

`backend/src/routers/auth.py` (2234 lines) — the largest router.
`APIRouter(prefix="/auth", tags=["auth"])` (`auth.py:70`). Request/response
DTOs live in `backend/src/schemas/` (`AuthRequest`, `SignupRequest`,
`AuthResponse`; password-reset shapes in `schemas/password_reset.py`).
See also ADR [0004 — JWT auth](../../../decisions/0004-jwt-auth.md) and
[data-model/identity-auth](../data-model/identity-auth.md).

## Endpoint table (all 8 routes)

| Method | Path | Rate limit | Auth | Request DTO | Response | Success | Error paths |
| --- | --- | --- | --- | --- | --- | --- | --- |
| POST | `/auth/signup` | 3/minute | none | `SignupRequest` | `AuthResponse` | 200 | 400 `invalid_license` / `license_required` / `password_too_long`, 429 `too_many_license_attempts`, 503 `license_verification_unavailable` (`auth.py:695-736`) |
| POST | `/auth/login` | 5/minute | none | `AuthRequest` | `AuthResponse` | 200 | 401 `invalid_credentials` (wrong password, unknown email, locked, or gated account — one detail for all) (`auth.py:769-820`) |
| POST | `/auth/refresh` | 1/minute | JWT | — | `AuthResponse` | 200 | 401 `unauthorized` (`auth.py:1057-1091`) |
| POST | `/auth/password-reset/request` | 3/hour | none | `PasswordResetRequest` | `PasswordResetAccepted` | **202** always (`auth.py:1379-1413`) | — (anti-enumeration: no error path reveals registration) |
| POST | `/auth/password-reset/confirm` | 5/hour | token possession | `PasswordResetConfirm` | `AuthResponse` | 200 | 400 `invalid_or_expired_token` / `password_unchanged` / `password_too_long` (`auth.py:1500-1590`) |
| POST | `/auth/password-reset/cancel` | 10/hour | token possession | `PasswordResetCancel` | — | **204** on hit *and* miss (`auth.py:1601-1633`) | — |
| POST | `/auth/oauth/google` | 5/minute | Google `id_token` | `GoogleOAuthRequest` | `AuthResponse` | 200 | 401 `invalid_oauth_token`, 409 `needs_license`, 429 `too_many_license_attempts`, 503 `license_verification_unavailable` (`auth.py:2169-2206`) |
| POST | `/auth/oauth/apple` | 5/minute | Apple `id_token` | `AppleOAuthRequest` | `AuthResponse` | 200 | same as Google (`auth.py:2208-2234`) |

## JWT mechanics

Tokens are HS256 (`_JWT_ALGORITHM`, `auth.py:73`) with a 1-hour TTL
(`_TOKEN_TTL`, `auth.py:78`), carrying `sub` (user id), `iat`, `exp`, and
a random `jti` (`_create_token`, `auth.py:313-359`). `SECRET_KEY` comes
from the environment; the placeholder value `replace-me` is rejected by
`_get_secret_key` (`auth.py:72,171-183`).

`get_current_user` (`auth.py:999-1025`) is the dependency every
authenticated route hangs off. It 401s (`detail="unauthorized"`) when the
header is missing/malformed, the signature or `exp` fails
(`_decode_token_payload`, `auth.py:824-846`), `sub` is not coercible
(`auth.py:848-866`), the `jti` appears in `revokedtoken`
(`_check_token_not_revoked`, `auth.py:883-898`), the token's `iat`
predates `User.password_changed_at` (the "log out everywhere" gate,
`_token_predates_password_reset`, `auth.py:931-996`), or the user row is
inactive/soft-deleted (`_check_user_active`, `auth.py:961-996`).
Legacy tokens without a `jti` remain valid for their original TTL
(`backend/src/models/revoked_token.py:24-29`).

`/auth/refresh` revokes the old token's `jti` **before** minting
(BUG-AUTH-013) and re-asserts the stored timezone "so a frontend that
hot-reloads … receives the correct user-local zone after a refresh, not a
stale `"UTC"` default" (`auth.py:1057-1091`).

## Signup — verify-then-create

No `User` or `Entitlement` row is written until the Gumroad license
verifies (allowlist product, email match, unclaimed signup email); "every
rejection returns a generic detail with matched timing
(anti-enumeration), and a Gumroad outage fails closed with 503"
(`auth.py:697-713`). Order is deliberate — license first, duplicate-email
second, "so an attacker cannot infer account existence from which check
ran first" (`auth.py:715-718`); losing the unique-index race answers with
the same `invalid_license` and burns a real bcrypt hash so timing holds
(`auth.py:722-731`). After creation: entitlement grant + sweep of token
packs bought under the same email (`claim_token_pack_sales`,
`auth.py:733-735`). License verification is capped per-IP: 429 after too
many invalid attempts (`_reject_if_license_cap_exhausted`,
`auth.py:508-545`). Password bounds: min 8 chars, max 64 (bcrypt's
72-byte limit with headroom) (`auth.py:131-145`).

## Login — lockout and serialization

`MAX_FAILED_ATTEMPTS = 5` consecutive failures lock the account for
`LOCKOUT_DURATION = 15 min` (`auth.py:165-168`), tracked via
`LoginAttempt` rows. The check-verify-record sequence is serialized
per-email — an in-process TTL lock map plus a Postgres advisory lock —
"so concurrent failed attempts cannot all pass the threshold-1 check
before any of them inserts (BUG-AUTH-007)" (`auth.py:424-505,812-815`).
Every rejection (unknown email, bad password, locked, inactive/deleted)
is the same 401 `invalid_credentials` (`auth.py:769-796`).

## Password reset — anti-enumeration throughout

- **request**: always 202 with the same body; a miss burns one dummy
  bcrypt digest so response time matches the hit path "within the SPEC R4
  ~50 ms tolerance" (`auth.py:1385-1413`). Token: 32 random bytes,
  bcrypt-hashed at cost 10, 30-minute TTL, at most 3 outstanding per user
  (oldest auto-cancelled) (`auth.py:84-109,1205-1295`).
- **confirm**: matching token (via the indexed `lookup_key` pre-filter,
  then bcrypt verify) sets the new password, stamps
  `password_changed_at` (revoking the whole JWT fleet), clears recent
  failed attempts, and emails a change notification; reuse of the old
  password is 400 `password_unchanged`; any terminal/expired/unknown
  token is the same 400 `invalid_or_expired_token`
  (`auth.py:1414-1590`).
- **cancel**: possession-only auth, 204 on hit and miss "so the endpoint
  is safe to embed in an email link without leaking whether the link is
  live" (`auth.py:1601-1633`).

## Social sign-in — the four-rung ladder

Both OAuth routes share one resolution ladder with "exactly two possible
refusals" (`auth.py:2178-2194`): (1) token verified against the
provider's published keys — failure is the only 401 and writes nothing;
(2) a stored `(provider, subject)` link logs straight in; (3) a
*verified* provider email links onto the account owning it — "an
unverified email never links — that is the account-takeover vector";
(4) verified email + valid APTITUDE license creates the account exactly
as `/auth/signup` would. Everything else — no license, bad license,
unverified address, no email, disabled/deleted account — is **one 409
`needs_license` with identical bytes** (`_needs_license_conflict`,
`auth.py:1780-1808`); a gated account differs only in the operator log
(`_gated_account_conflict`, `auth.py:1811-1821`). Apple-specific: email
arrives only on first authorization (rung 2 keys on the stored subject)
and the name comes from the request's `full_name`, read only by the
account-creating rung (`auth.py:2216-2229`). `id_token` bodies are capped
at 4096 chars *before* any JWKS fetch "denying an attacker a free way to
drive outbound key fetches" (`auth.py:1643-1648`).

## Cross-cutting

`extract_user_id_from_authorization` (`auth.py:868-881`) is the
sync-context variant used by non-DB consumers. Emails only ever appear in
logs as a 12-char fingerprint (`_email_log_fingerprint`,
`auth.py:184-190`). Error helpers come from `backend/src/errors.py`
(`bad_request`, `conflict`, `service_unavailable` — see
[infrastructure](../infrastructure.md#error-helpers-backendsrcerrorspy)).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
