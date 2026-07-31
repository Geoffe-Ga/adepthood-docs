# API — practices router

`backend/src/routers/practices.py` (121 lines).
`APIRouter(prefix="/practices", tags=["practices"])`
(`practices.py:25`). Browsing the practice catalog and submitting new
practices. (Share-link routes live in the separate
[practice-share](practice-share.md) router.)

| Method | Path | Rate limit | Auth | Request | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GET | `/practices/?stage_number=N` | — | JWT | query: `stage_number`, `PaginationParams`, `include_mine` | `Page[PracticeResponse]` or bare `list[PracticeResponse]` | 200 | — |
| GET | `/practices/{practice_id}` | — | JWT | — | `PracticeResponse` | 200 | 404 `practice_not_found`; 403 `forbidden` (unapproved draft, not the submitter) |
| POST | `/practices/` | 5/minute **per user** | JWT | `PracticeCreate` | `PracticeResponse` | **201** | 422 (invalid mode/mode_config from schema validation) |

Notes:

- **Dual response shape** (BUG-INFRA-012): `?paginate=true` returns the
  `Page` envelope; otherwise "the legacy bare list is returned for one
  release while the frontend migrates" (`practices.py:38-41,60-64`;
  envelope in `backend/src/schemas/pagination.py`).
- **`include_mine`** (custom-practices-07): adds the caller's own
  unapproved drafts to the approved listing, "without leaking other
  users' submissions" (`practices.py:42-59`).
- **Detail visibility** is approved-OR-submitter (BUG-PRACTICE-001) via
  `require_visible_practice`
  (`backend/src/dependencies/ownership.py:205-218`).
- **Submission trust boundary** (BUG-PRACTICE-002): the ORM row is
  constructed with explicit kwargs, never `**payload.model_dump()`, so a
  future `PracticeCreate` field overlapping a server-controlled column
  (`approved`, `submitted_by_user_id`) cannot "let a client mint
  pre-approved rows or impersonate another submitter" — submissions are
  always `approved=False` with `submitted_by_user_id=current_user`
  (`practices.py:88-113`). The per-user rate-limit key
  (`rate_limit_keys.per_user_rate_limit_key`) scopes the 5/minute cap to
  the submitter rather than the IP (`practices.py:81`).
- `PracticeCreate` resolves `mode`/`mode_config` during validation
  (`practices.py:99-102`); the mode vocabulary is
  [domain/practice-modes](../domain/practice-modes.md).

Model: [data-model/practice](../data-model/practice.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
