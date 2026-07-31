# API — prompts router

`backend/src/routers/prompts.py` (334 lines).
`APIRouter(prefix="/prompts", tags=["prompts"])` (`prompts.py:40`).
Serves the 36 weekly reflection prompts
([domain/weekly-prompts](../domain/weekly-prompts.md)) and stores
responses (`PromptResponse` rows,
[data-model/course-content](../data-model/course-content.md)).

| Method | Path | Auth | Request | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/prompts/current` | JWT | — | `PromptDetail` | 200 | 404 `prompt_not_found` (past the curriculum) |
| GET | `/prompts/history` | JWT | filter/pagination query params | `PromptListResponse` | 200 | — |
| GET | `/prompts/{week_number}` | JWT | — | `PromptDetail` | 200 | 404 `prompt_not_found` (unknown week), 403 `week_locked` (future week) |
| POST | `/prompts/{week_number}/respond` | JWT | `PromptSubmit` | `PromptDetail` | **201** | 404, 403 `week_locked`, 409 `already_responded`, 422 `title_too_long` / `response_too_long` |

Notes:

- **Week gating** (`prompts.py:198-204`): a specific week is served only
  up to the user's current week — "without this check a fresh (week-1)
  user could enumerate `/prompts/1` … `/prompts/36` and lift every
  future question." 404 precedes 403 "so unknown weeks (outside
  1..`TOTAL_WEEKS`) don't get re-interpreted as 'locked'."
- **Anti-leapfrog on submit** (`prompts.py:258-264`): `week_number >
  user_week` is refused, so "a single POST cannot leapfrog the weekly
  pacing by driving `max(week_number)` up in one request" — the
  server-derived week is "a monotone function of *contiguous*
  completion, not the highest value the client has ever submitted."
- **Duplicate handling** (BUG-PROMPT-004, `prompts.py:266-272,319`):
  duplicates are caught *exclusively* by the DB constraint
  `uq_promptresponse_user_week` and surfaced as 409 — the earlier
  400-precheck/409-race split exposed two status codes for one
  condition; "the constraint is the only observer that sees both rows
  in a TOCTOU race anyway."
- **History pagination** (`prompts.py:153-167`): `include_total=true`
  (default) runs a count subquery; `include_total=false` uses a
  fetch-`limit+1` peek so cursor pagination stays accurate "without
  paying for `COUNT(*)`."
- The user's week derives from timezone-aware calendar math
  (`current_user_timezone` dependency + the count-plus-one contiguity
  rule referenced above); prompt titles default to the band-based
  pattern from `domain.weekly_prompts.prompt_title_for_week`.

DTOs: `backend/src/schemas/prompt.py`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
