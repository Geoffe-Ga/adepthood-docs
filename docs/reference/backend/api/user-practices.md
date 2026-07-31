# API — user-practices router

`backend/src/routers/user_practices.py` (699 lines).
`APIRouter(prefix="/user-practices", tags=["user-practices"])`
(`user_practices.py:51`). Selecting a practice per stage and viewing
selections. All 5 routes:

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| POST | `/user-practices/` | JWT | `UserPracticeCreate` | `UserPracticeResponse` | **201** | 404 `practice_not_found`; 400 `practice_not_approved` / `stage_number_mismatch` (`user_practices.py:70-87`); 409 `active_practice_exists_for_stage` (racing replacement, `user_practices.py:179`) |
| GET | `/user-practices/` | JWT | `PaginationParams` | `Page[UserPracticeResponse]` or bare list (BUG-INFRA-017) | 200 | — |
| GET | `/user-practices/current/frequency?stage_number=` | JWT | optional `stage_number` (1..10) | `FrequencyResponse` | 200 | 404 `course_stage_not_found` / `preset_practice_not_found` / `practice_not_found` (`user_practices.py:370-469`) |
| GET | `/user-practices/{user_practice_id}?…embed…` | JWT + owned | `EmbeddedSessionsParams` | `UserPracticeDetail` | 200 | 404 / 403 |
| PATCH | `/user-practices/{user_practice_id}/customize` | JWT + owned | `UserPracticeCustomize` | `UserPracticeDetail` | 200 | 404 / 403; 422 (structured config errors); 400 `mode_mismatch` (`user_practices.py:645-650`) |

Notes:

- **Select/replace** (`user_practices.py:128-150`): the
  `ix_user_practice_active_stage` partial unique index enforces one open
  selection per `(user, stage)` (BUG-PRACTICE-005), so the route closes
  the prior open row and inserts the new one in one transaction rather
  than 409ing the user "out of ever switching" (BUG-PRACTICE-012). Under
  a race the index remains the single source of truth: exactly one new
  open row lands, the loser rolls back to a *transient* 409. Re-selecting
  the already-active practice is a no-op "so an accidental double-tap
  can't reset `start_date` … or the streak math that hangs off it."
- **Frequency banner** (ritual-05, `user_practices.py:502-546`):
  collapses four lookups (StageProgress → CourseStage → UserPractice →
  Practice) into one payload; the wording template lives server-side in
  `schemas.frequency`. Stage resolution: the query param wins (so the
  banner tracks the practice on screen), else
  `StageProgress.current_stage`, else stage 1. Practice slot: the active
  selection (honouring `custom_name` via
  `domain.practice_resolution.effective_name`), else the seeded preset
  with `user_practice_id: null` signalling "showing the unselected
  default."
- **Detail** embeds a capped newest-first `sessions[]`
  (`EMBEDDED_SESSIONS_DEFAULT_LIMIT = 50`) with
  `sessions_total`/`sessions_has_more` (issue #474,
  `user_practices.py:562,601-612`).
- **Customize** (`user_practices.py:653-666`): per-user override of
  name + `mode_config`; `None` clears the override back to the catalog value;
  "mode-shifting is rejected with 400 `mode_mismatch` because mode
  changes are conceptually a practice replacement, not a tweak" — the
  same invariant [domain/practice-resolution](../domain/practice-resolution.md)
  enforces and the recipe apply path re-uses.

DTOs: `backend/src/schemas/practice.py`, `schemas/frequency.py`. Model:
[data-model/practice](../data-model/practice.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
