# Backend infrastructure

App assembly, database plumbing, startup seeding, error handling,
auth/JWT mechanics, and the test harness. Source modules:
`backend/src/main.py` (704 lines), `database.py` (51), `errors.py`
(188), the seeders (`seed_stages.py`, `seed_practices.py`,
`seed_practice_recipes.py`, `seed_content.py`, `seed_practice_copy.py`,
`seed_helpers.py`), `content_config.py`, `rate_limit.py`,
`observability.py`, `middleware/`, `dependencies/`, and
`backend/conftest.py` (374).

## App assembly (`backend/src/main.py`)

### Lifespan (`main.py:470-537`)

On startup, in order:

1. `configure_logging()` — the root logger gets a real handler first;
   uvicorn only configures its own loggers, so "without this every app
   record below WARNING — including every `seed_complete` line this very
   function emits — is silently dropped" (`main.py:472-478`).
2. Lazy imports register every SQLModel table with the metadata exactly
   once (`import models`), deliberately at lifespan time
   (`main.py:479-487`).
3. **Fail-fast validations**: `_get_secret_key()` runs once so "a
   misconfigured deployment fails the orchestrator's health probe
   immediately rather than silently serving traffic and crashing on the
   first auth request" (BUG-AUTH-011, `main.py:492-498`);
   `validate_gumroad_config()` is all-or-nothing — a *half*-wired
   `GUMROAD_API_TOKEN`/`GUMROAD_WEBHOOK_SECRET` pair fails the boot,
   while a wholly unset pair only warns (pre-adoption state,
   `main.py:500-503,244`); proxy-allowlist and IPv6-throttle-prefix
   misconfigurations are warned loudly at boot (`main.py:504-512`).
4. **Startup seeding** unless `SKIP_STARTUP_SEED=1`; a seeder failure is
   logged and swallowed — "the orchestrator should still be able to take
   the pod live so an operator can SSH in and run `alembic upgrade
   head`" (`main.py:513-525`).
5. Content-pin and LLM-provider status are logged (issues #397, #402) —
   loud log rather than crash (`main.py:527-534`).

### Middleware order (`main.py:550-590`)

Starlette's `add_middleware` is LIFO (BUG-APP-001), so the declared
order produces this request path: `ForwardedProtoMiddleware` (outermost —
the scheme must be settled "before anything routes" so trailing-slash
307 `Location`s carry the client-facing scheme, `main.py:565-570`) →
`RequestLoggingMiddleware` → `CorrelationIdMiddleware` →
`SecurityHeadersMiddleware` → `CORSMiddleware` → `SlowAPIMiddleware`.
CORS sits inside SecurityHeaders so "even preflight responses echo
`X-Request-ID`" (`main.py:558-564`).

### CORS (`main.py:82-243`)

Environment-derived origin list (`get_cors_origins`): dev loopback
origins in development; production origins parsed from config and
validated — HTTPS-only, hostname checks (BUG-APP-003), and a hard
assertion that the list never contains `*` (`_assert_credentials_safe`,
`main.py:226-238`). `allow_credentials=False` because the API uses
Bearer tokens and sets no cookies — "disabling it shrinks the CORS
attack surface" (`main.py:578-583`). Only served methods and named
headers are allowed; `X-Request-ID` is the sole exposed header
(`main.py:94-110`).

### Router mounting

All **27** routers are mounted flat on the app
(`main.py:592-618`) — see the [API index](api/index.md) for the roster.

### Health probes (`main.py:620-704`)

BUG-APP-004 splits liveness from readiness:

| Path | Depends on DB | Purpose |
| --- | --- | --- |
| `GET /health/live` | no | "process is responsive"; a DB outage must NOT trip it (`main.py:653-663`) |
| `GET /health/ready` | yes | bounded `SELECT 1` (2 s timeout); 503 `not_ready` drops the pod from rotation without restarting it (`main.py:666-686`) |
| `GET /health` | yes | legacy combined probe; adds `content_version` (the live content pin) for dashboards (`main.py:689-704`) |

The shared `_probe_db` helper owns the timeout window, exception tuple,
and 503 contract in one place (`main.py:632-651`).

## Database (`backend/src/database.py`)

`normalize_database_url` rewrites PaaS-style `postgres://` /
`postgresql://` URLs to `postgresql+asyncpg://`, leaving other schemes
(e.g. `sqlite+aiosqlite://`) untouched (`database.py:9-23`). One async
engine + `async_sessionmaker(expire_on_commit=False)`
(`database.py:26-35`). The FastAPI dependency
(`backend/src/database.py:38-51`):

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    BUG-INFRA-021: wrap the yield in ``try/except Exception`` so a failed
    handler rolls back its transaction and re-raises.  The outer
    ``async with`` is what releases the connection (it guarantees
    ``close()``); the explicit rollback prevents an in-flight ``BEGIN``
    from being silently committed by the connection pool when reused.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

Note: `get_session` does **not** auto-commit — which is why the
provisioning helpers in the domain layer commit explicitly (see
[domain/ui-flags](domain/ui-flags.md)). Migrations live in
`backend/migrations/versions/` (70 revisions;
`backend/alembic.ini:8` sets `script_location = %(here)s/migrations`).

## Seeding

`_seed_startup_data` (`main.py:391-425`) runs the idempotent seeders
with isolation and a prerequisite: `seed_stages` must succeed first
(every dependent reads the seeded `CourseStage` rows — a stages failure
short-circuits to avoid "a misleading `seed_complete inserted=0`"),
then `seed_practices`, `seed_practice_recipes`, `seed_content`, and
`seed_goal_group_templates` each run in their own try/except so one
failure "must not starve the others."

- `seed_stages.py` (139 lines) — the 10 `CourseStage` rows.
- `seed_practices.py` (502) — the practice presets per stage;
  `seed_practice_copy.py` (1280) holds the copy. The preset-uniqueness
  functional index (migration `d2e3f4a5b6c7`) closes the two-worker
  seeder race.
- `seed_practice_recipes.py` (405) — system recipes + tags.
- `seed_content.py` (443) — reconciles `StageContent` from the vendored
  content manifest: fields come from `manifest.json` verbatim, `url`
  carries a local `content://<chapter-id>` reference, manifest-claimed
  rows update in place, unclaimed rows in reconciled stages are pruned
  with `ContentCompletion` read-marks repointed to a surviving
  `(stage, title)` row or dropped. "Seeding is resilient, never
  all-or-nothing": a manifest stage with no `CourseStage` row is skipped
  with a `content_seed_partial` WARNING (`seed_content.py:1-26`).
- `content_config.py` (100) — the vendored-content pin
  (`content_version_info`) surfaced in `/health` and the boot log.
- Goal-group templates: `seed_goal_group_templates` in
  `routers/goal_groups.py:48-69`.

## Error helpers (`backend/src/errors.py`)

Per-route errors are `HTTPException`s with stable snake_case details in
the legacy `{"detail": ...}` shape, built by one helper per status:
`not_found` (404, `<resource>_not_found`), `forbidden` (403),
`bad_request` (400), `conflict` (409), `payment_required` (402),
`unprocessable` (422 — for post-Pydantic domain/security failures),
`bad_gateway` (502 — upstream provider failures), `service_unavailable`
(503 — fail-closed dependencies) (`errors.py:34-88`).

Unhandled exceptions get the sanitized envelope (BUG-OBS-002/-003):
`{"error": "internal_error", "request_id": "..."}` plus the trace-id
header — "the client sees only … a stable token they can show the user"
while the full traceback goes to logs and Sentry (`errors.py:91-157`).
Journal encrypt/decrypt failures get their own handler and error code
`decryption_failure` so "a key misconfiguration … would [not] be
indistinguishable from any other 500" (`errors.py:28-31,160-170`).
`install_exception_handlers` registers the specific handler before the
catch-all (`errors.py:173-188`).

## Auth mechanics

JWT creation/validation and the account-security machinery live in the
auth router and are documented in depth in [api/auth](api/auth.md):
HS256, 1-hour TTL, `jti` revocation via `RevokedToken`,
`password_changed_at` fleet revocation, per-email login serialization,
and lockout (5 failures / 15 minutes). Shared dependencies:
`dependencies/auth.py` (`get_current_user_model`, `require_admin`),
`dependencies/ownership.py` (per-resource ownership with the 404→403
split and enumeration-safe collapses), `dependencies/timezone.py`
(request-scoped timezone resolution). Rate limiting is slowapi
(`rate_limit.py`, 199 lines) with client-IP resolution hardened in
`client_ip.py` (354) behind the validated trusted-proxy config;
observability (`observability.py`, 249) supplies the correlation-id
middleware and trace headers used by the error envelope.

## Test harness (`backend/conftest.py`)

- Environment first: `SECRET_KEY` is set and `SKIP_STARTUP_SEED=1`
  before any app import, so tests mount a clean schema and the lifespan
  seeder stays off (`conftest.py:8-14`).
- **In-memory SQLite** (`sqlite+aiosqlite:///:memory:`) with
  `_replace_array_columns()` swapping PostgreSQL `ARRAY` columns to
  `JSON` (`conftest.py:55-66`).
- **Constraint parity**: production-only functional/partial unique
  indexes that `metadata.create_all` cannot express are mirrored as
  SQLite `CREATE UNIQUE INDEX IF NOT EXISTS` statements
  (`_SQLITE_ALWAYS_INDEXES`, `conftest.py:78-113`): habit
  per-user lowercase-name uniqueness, practice preset uniqueness,
  `coursestage.stage_number` uniqueness, and the `content://` reference
  uniqueness. The per-day `GoalCompletion` unique index is
  **concurrency-only** (`_SQLITE_CONCURRENT_ONLY_INDEXES`,
  `conftest.py:115-129`): the regular fixture omits it because streak
  tests intentionally insert multiple rows per day.
- **Fixtures**: `db_session` (fresh schema per test,
  `conftest.py:149-175`); `async_client` (overrides `get_session`,
  clears `app.dependency_overrides` in `finally` and asserts no leak —
  BUG-INFRA-026, `conftest.py:178-198`); autouse `_reset_rate_limiter`
  (limiter state cannot leak between tests, `conftest.py:201-219`);
  autouse `_stub_signup_license_gate` (replaces
  `verify_aptitude_license` so ordinary tests sign up without Gumroad,
  `conftest.py:225-256`); opt-in `disable_rate_limit`,
  `zero_monthly_cap` (`conftest.py:259-276`); and
  `concurrent_async_client` — a file-backed SQLite DB with per-request
  sessions and the full unique-index set, for tests that exercise the
  `IntegrityError → idempotent/409` races (`conftest.py:279-310`).

## Ambiguity noted

`backend/src/main.py` mounts 27 routers and this page plus the API
section document all of them; `backend/src/load_options.py`,
`backend/src/sentry.py` (a no-op stub until a DSN lands,
`errors.py:101-104`), and `backend/src/rate_limit_keys.py` are small
supporting modules referenced where they matter rather than given their
own pages.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
