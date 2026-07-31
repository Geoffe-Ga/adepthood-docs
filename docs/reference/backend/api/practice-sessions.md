# API — practice-sessions router

`backend/src/routers/practice_sessions.py` (463 lines).
`APIRouter(prefix="/practice-sessions", tags=["practice-sessions"])`
(`practice_sessions.py:50`).

| Method | Path | Auth | Request | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| POST | `/practice-sessions/` | JWT | `PracticeSessionCreate` + optional `Idempotency-Key` header | `PracticeSessionResponse` | **201** | 404 `user_practice_not_found` / 403 `forbidden` (inline split, `practice_sessions.py:73-75`); 403 `stage_locked` (`:94`); 400 `chosen_option_key_required` / `chosen_option_key_not_in_catalog` / `mode_metadata_mismatch` (`:102,117,160`); 404 `practice_not_found` / `practice_session_not_found` (`:184,199`); 409 `idempotency_in_flight` (`:223`) |
| GET | `/practice-sessions/?user_practice_id=` | JWT + owned selection | `PaginationParams` | `Page[PracticeSessionResponse]` or bare list | 200 | 404 / 403 |
| GET | `/practice-sessions/insights` | JWT | — | `PracticeInsightsResponse` | 200 (with `Cache-Control: private, max-age=60`) | — |
| GET | `/practice-sessions/week-count` | JWT | — | `WeekCountResponse` | 200 | — |

Notes on create (`practice_sessions.py:307-341`):

- The ownership split is inlined (same order/exceptions as
  `require_owned_user_practice`) because `user_practice_id` arrives in
  the **body** — "FastAPI's DI cannot extract body fields into
  sub-dependencies … the IDOR matrix test sees the same 403 for
  cross-user calls" (`practice_sessions.py:321-325`).
- **Stage gating**: assigning a practice to a future stage is allowed
  for planning, but logging a real session there is 403 `stage_locked`,
  evaluated in the caller's timezone, "before any row or idempotency
  spend is written" (`practice_sessions.py:327-330`).
- **Idempotency** (BUG-PRACTICE-007): with an `Idempotency-Key`, a
  replay of the same `(user_id, key)` returns the recorded session
  without duplicating — backed by `practicesessionspend`'s
  `UNIQUE(user_id, idem_key)`, "so it holds across process restarts and
  workers — the database serialises the check-then-insert race"
  (`practice_sessions.py:332-338`;
  [data-model/practice](../data-model/practice.md)).
- **Mode metadata validation**: the session's `mode_metadata` must match
  the resolved mode's discriminated-union schema and, for option-choice
  modes, name a `chosen_option_key` present in the catalog config
  (`practice_sessions.py:102-160`).

Other endpoints:

- **List** runs the canonical 404→403 split before touching the sessions
  table — cross-user calls "used to return an empty list (the `user_id`
  filter silently masked them)" (`practice_sessions.py:350-359`;
  envelope per BUG-INFRA-014).
- **Insights**: one query fetches the last 60 days
  (`_INSIGHTS_LOOKBACK_DAYS`, `practice_sessions.py:40`), then
  `domain.practice_insights.build_insights` buckets in memory; the
  private one-minute `Cache-Control` lets the frontend poll "without
  thrashing the DB" (`practice_sessions.py:376-392`;
  [domain/practice-insights](../domain/practice-insights.md)).
- **Week-count** (BUG-PRACTICE-009): the week boundary derives from
  `User.timezone`, "not the UTC equivalent"
  (`practice_sessions.py:444-455`).

DTOs: `backend/src/schemas/practice.py`,
`schemas/practice_session_metadata.py`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
