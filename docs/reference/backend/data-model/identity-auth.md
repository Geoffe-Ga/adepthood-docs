# Data model — identity & auth

Models: `User`, `AuthIdentity`, `RevokedToken`, `LoginAttempt`,
`PasswordResetToken` — the five tables that decide who a request belongs
to and whether its credentials still count. All file references are
repo-relative to the adepthood monorepo.

## `User` (`backend/src/models/user.py`)

The account row. One row per person; almost every other table hangs off
`user.id`. Beyond credentials it carries the AI-resonance wallet
(two-bucket: free monthly allocation + purchased offering balance,
`backend/src/models/user.py:42-48`), the IANA timezone that anchors all
streak/daily-completion math (`backend/src/models/user.py:50-56`), and the
account-state flags added by BUG-MODEL-001
(`backend/src/models/user.py:96-117`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `id` | `int \| None` | primary key | `None` (autoincrement) | Account id (`user.py:59`) |
| `is_admin` | `bool` | `nullable=False` | `False` | Gates the `/admin` router (`user.py:60`) |
| `offering_balance` | `int` | — | `0` | Purchased/gifted BotMason credits; never expire (`user.py:61`) |
| `monthly_messages_used` | `int` | — | `0` | Free-bucket usage this month (`user.py:62`) |
| `monthly_reset_date` | `datetime` | `DateTime(timezone=True)`, not null | first-of-next-month UTC via `_default_reset_date` (`user.py:18-20`) | When the free bucket next resets (`user.py:63-66`) |
| `email` | `str` | `unique`, `index`, `max_length=254` | — | Login identifier (`user.py:67`) |
| `password_hash` | `str` | `min_length=1` | — (required) | bcrypt digest; no default so a blank-password row is impossible at the schema level (BUG-AUTH-018, `user.py:68-75`) |
| `display_name` | `str \| None` | `max_length=120` (`DISPLAY_NAME_MAX_LENGTH`, `user.py:28-33`) | `None` | Written once at account creation from a social provider's name claim; password signups leave it `None` (`user.py:76-83`) |
| `timezone` | `str` | `String(64)`, not null, `server_default="UTC"` | `"UTC"` (`DEFAULT_USER_TIMEZONE`, `user.py:23-26`) | IANA zone read by `domain/dates.py` for local-day math (`user.py:84-91`) |
| `created_at` | `datetime` | `DateTime(timezone=True)`, not null | `datetime.now(UTC)` | Signup instant (`user.py:92-95`) |
| `is_active` | `bool` | not null, `server_default="1"` | `True` | Soft-disable switch; auth rejects login when false (`user.py:101-103,118-121`) |
| `email_verified` | `bool` | not null, `server_default="0"` | `False` | Reserved for the verification-flow phase; no auth helper currently reads it (`user.py:105-110,122-125`) |
| `deleted_at` | `datetime \| None` | `DateTime(timezone=True)`, nullable | `None` | Soft-delete timestamp; login fails and lookups filter when set (`user.py:112-117,126-129`) |
| `password_changed_at` | `datetime \| None` | `DateTime(timezone=True)`, nullable | `None` | "Log out everywhere" lever — see excerpt below (`user.py:139-142`) |

The `password_changed_at` column is load-bearing for token revocation
(`backend/src/models/user.py:130-138`):

```python
# Password recovery (SPEC §R7 option a): a successful
# ``/auth/password-reset/confirm`` advances this timestamp so every
# token minted before the reset is rejected by
# ``_decode_token_payload``'s ``iat`` check.  This is the
# "log out everywhere" lever -- one column update revokes the
# entire outstanding-JWT fleet without having to enumerate
# individual ``jti`` rows.  ``NULL`` means "no reset has happened",
```

**Relationships** (`backend/src/models/user.py:143-154`): `habits`
(list, back-populates `Habit.user`), `journals` (list, `JournalEntry.user`),
`responses` (list, `PromptResponse.user`), `stage_progress` (one,
`StageProgress.user`), `depth_preferences` (one, passive-deletes),
`ui_flags` (one, passive-deletes).

**Lifecycle.** Created by `/auth/signup` and by the social sign-in path on
first login (see [api/auth](../api/auth.md)); wallet columns mutated by the
BotMason spend path and Gumroad credit path; `password_changed_at` written
only by password-reset confirm.

**Migrations.** Shaped after `145d340640ce_initial_schema` by
`b9c0d1e2f3a4_add_user_is_admin`, `d1e2f3a4b5c6_add_user_timezone`,
`a4b5c6d7e8f9_add_user_state_flags` (`is_active`/`email_verified`/`deleted_at`),
`c6d7e8f9a0b1_add_password_reset_token_and_password_changed_at`,
`b0c1d2e3f4a5_add_user_display_name` (all in `backend/migrations/versions/`).

## `AuthIdentity` (`backend/src/models/auth_identity.py`)

Social sign-in link table: one row per `(provider, subject)` pair pointing
at the account it unlocks. A separate table (not columns on `User`) because
one account may carry several links and because link provenance is audit
data (`auth_identity.py:1-8`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `id` | `int \| None` | primary key | `None` | Row id (`auth_identity.py:80`) |
| `user_id` | `int` | FK `user.id`, `ondelete="CASCADE"`, index | — | Account the link signs into (`auth_identity.py:81`) |
| `provider` | `str` | `max_length=16` | — | `"google"` or `"apple"` per `AuthProvider` StrEnum (`auth_identity.py:44-52`) |
| `subject` | `str` | `max_length=255` | — | Provider's stable per-app user id — the only sign-in key (`auth_identity.py:64-66,83`) |
| `email_at_link_time` | `str` | `max_length=254`, NOT NULL | — | Snapshot of the provider-verified address; audit-only, never a lookup key (`auth_identity.py:68-73,84`) |
| `created_at` | `datetime` | `DateTime(timezone=True)`, not null | `datetime.now(UTC)` | Link instant (`auth_identity.py:85-88`) |

Two table constraints carry the security of the table
(`backend/src/models/auth_identity.py:75-78`):

```python
    __table_args__ = (
        _provider_check(),
        UniqueConstraint("provider", "subject", name="uq_authidentity_provider_subject"),
    )
```

`uq_authidentity_provider_subject` prevents one Google account forking
across two Adepthood accounts (`auth_identity.py:11-14`);
`ck_authidentity_provider_valid` is a CHECK generated from the
`AuthProvider` enum so the DB set cannot drift from the Python enum
(`auth_identity.py:55-58`). A plain `UniqueConstraint` (not a partial
index) is deliberate so SQLite `metadata.create_all` and the PostgreSQL
migration render identical DDL (`auth_identity.py:19-22`).

## `RevokedToken` (`backend/src/models/revoked_token.py`)

Denylist of JWT ids. BUG-AUTH-013: `/auth/refresh` used to mint a new
token without invalidating the old one; every refresh now inserts the old
`jti` here and `get_current_user` rejects any token whose `jti` is present
(`revoked_token.py:3-7`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `jti` | `str` | primary key, `max_length=64` | — | The revoked JWT id (`revoked_token.py:31`) |
| `expires_at` | `datetime` | `DateTime(timezone=True)`, not null, index | — | Same instant as the revoked token's `exp`; rows expire naturally (`revoked_token.py:9-12,32-34`) |
| `revoked_at` | `datetime` | `DateTime(timezone=True)`, not null | `datetime.now(UTC)` | Audit timestamp (`revoked_token.py:35-37`) |

Tokens minted before the `jti` claim existed are treated as
legacy-but-valid for their original 1-hour TTL, so existing sessions do
not all 401 at once on deploy (`revoked_token.py:24-29`).

## `LoginAttempt` (`backend/src/models/login_attempt.py`)

Per-attempt audit rows powering brute-force lockout: failed attempts
accumulate per email; after `MAX_FAILED_ATTEMPTS` consecutive failures the
account locks for `LOCKOUT_DURATION`; a success resets the counter
(`login_attempt.py:10-15` — the constants live in `backend/src/routers/auth.py`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `id` | `int \| None` | primary key | `None` | Row id (`login_attempt.py:17`) |
| `email` | `str` | index | — | Attempted identifier (`login_attempt.py:18`) |
| `ip_address` | `str` | — | `""` | Source address for audit (`login_attempt.py:19`) |
| `success` | `bool` | — | `False` | Outcome flag (`login_attempt.py:20`) |
| `created_at` | `datetime` | `DateTime(timezone=True)`, not null | `datetime.now(UTC)` | Attempt instant (`login_attempt.py:21-24`) |

## `PasswordResetToken` (`backend/src/models/password_reset_token.py`)

Single-use, time-limited reset tokens. The plaintext token is emailed and
never stored; the row keeps a bcrypt digest (cost 10 — the tokens are
256-bit randoms, not human input) plus a non-secret SHA-256-prefix
`lookup_key` used as an indexed SQL pre-filter so confirm/cancel do a
point query instead of bcrypt-scanning every active token
(`password_reset_token.py:1-9,46-57`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `id` | `int \| None` | primary key | `None` | Row id (`password_reset_token.py:39`) |
| `user_id` | `int` | FK `user.id`, not null, index, `ondelete="CASCADE"` | — | Owning account (`password_reset_token.py:40-45`) |
| `lookup_key` | `str` | not null, `max_length=32`, index | — | First 16 hex chars of `sha256(plaintext)`; fast pre-filter, not a security gate (`password_reset_token.py:46-57`) |
| `token_hash` | `str` | not null, `max_length=128` | — | bcrypt digest of the plaintext token (`password_reset_token.py:58`) |
| `requested_ip` | `str` | `max_length=64` | `""` | Audit: requesting IP (`password_reset_token.py:59`) |
| `requested_user_agent` | `str` | `max_length=256` | `""` | Audit: requesting UA (`password_reset_token.py:60`) |
| `expires_at` | `datetime` | `DateTime(timezone=True)`, not null, index | — | TTL boundary (`password_reset_token.py:61-63`) |
| `used_at` | `datetime \| None` | nullable | `None` | Set on successful confirm (`password_reset_token.py:64-67`) |
| `cancelled_at` | `datetime \| None` | nullable | `None` | Set by the "this wasn't me" cancel link (`password_reset_token.py:68-71`) |
| `created_at` | `datetime` | `DateTime(timezone=True)`, not null | `datetime.now(UTC)` | Mint instant (`password_reset_token.py:72-75`) |

State machine (`password_reset_token.py:25-36`): *created* (`used_at` and
`cancelled_at` both `NULL`) → *confirmed* (`used_at` set) or *cancelled*
(`cancelled_at` set). Either terminal state rejects later confirms with
the same generic 400 so an attacker cannot distinguish "already used"
from "wrong token". Rows outlive the TTL by a 7-day audit tail
(`password_reset_token.py:6-9`).

**Migrations.** `c6d7e8f9a0b1_add_password_reset_token_and_password_changed_at`
created the table; `d7e8f9a0b1c2_add_passwordresettoken_lookup_key` added
the pre-filter column (`backend/migrations/versions/`).

## Related

- [api/auth](../api/auth.md) — the endpoints that create and consume these rows
- [infrastructure](../infrastructure.md) — JWT mechanics in `dependencies/auth.py`
- ADR [0004 — JWT auth](../../../decisions/0004-jwt-auth.md)

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
