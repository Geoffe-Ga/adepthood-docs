# API — stages router

`backend/src/routers/stages.py` (463 lines).
`APIRouter(prefix="/stages", tags=["stages"])` (`stages.py:54`). Stage
listing with progress overlay, the program calendar, the wheel, and the
two progression mutations.

| Method | Path | Auth | Request | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/stages` | JWT | `PaginationParams` | `Page[StageResponse]` or bare list | 200 | — |
| GET | `/stages/program-calendar` | JWT | — | `ProgramCalendarResponse` | 200 | — |
| GET | `/stages/wheel` | JWT | — | `WheelBalanceResponse` | 200 | — |
| GET | `/stages/{stage_number}/progress` | JWT | — | `StageProgressResponse` | 200 | 404 `stage_not_found` (`stages.py:220`) |
| GET | `/stages/{stage_number}/history` | JWT | — | `StageHistoryResponse` | 200 | 404 `stage_not_found`, 403 `stage_locked` (`stages.py:235-239`) |
| PUT | `/stages/progress` | JWT | `StageProgressUpdate` | `StageProgressRecord` | 200 | 400 `must_start_at_stage_one` / `stage_advance_mismatch`; 409 `all_stages_completed` / `stage_progress_race_unrecoverable` (`stages.py:284-323`) |
| POST | `/stages/begin-again` | JWT | — | `StageProgressRecord` | 200 | 404 `stage_progress_not_found`, 409 `cycle_not_complete` (`stages.py:394-396`) |

Notes:

- **Listing** overlays per-user progress from
  `compute_stage_progress_batch` — "three grouped queries for the whole
  list regardless of stage count" (issue #473); only unlocked stages
  feed the batch, locked stages report `0.0` (`stages.py:142-153`;
  [domain/stage-progress](../domain/stage-progress.md)).
- **`/program-calendar`** is the server's date-derived calendar (issue
  #386), registered *above* `/{stage_number}` so the static path wins
  route matching; a user with no progress row sees the day-zero shape
  (`stages.py:164-173`; [domain/program-calendar](../domain/program-calendar.md)).
- **`/wheel`**: "a connected, capable vault's own reading of the user's
  corpus wins; otherwise the balance is computed locally" via
  [domain/wheel](../domain/wheel.md) (`stages.py:194-207`;
  [domain/creek-vault](../domain/creek-vault.md)).
- **History** is gated on stage unlock (403 `stage_locked`) and
  aggregates via `get_stage_practice_history` /
  `get_stage_habit_history`.

## `PUT /stages/progress` — assertion, not authority

The request body "is treated as an **assertion** of what the client
expects the new `current_stage` to be, not an authoritative write"
(`stages.py:415-433`): on create, the stage is forced to 1 (payload must
assert 1 or 400 `must_start_at_stage_one`); on update, the server marks
the current stage complete and derives the sole legal next stage via
`next_stage_for` (curriculum end → 409 `all_stages_completed`); any other
asserted value — skip, rewind, stale client — is 400
`stage_advance_mismatch`. `completed_stages` is never read from the
payload (`extra='forbid'` would 422 it), "so the client cannot mint
credit for stages it hasn't actually completed." A `SELECT … FOR UPDATE`
row-lock closes the two-concurrent-advances TOCTOU (`stages.py:435-437`);
BUG-STAGE-003's racing-first-advance bootstrap idempotency and its one
deliberate non-idempotent edge (stale assertion vs a winner that advanced
twice → 400) are documented at `stages.py:439-457`.

## `POST /stages/begin-again`

An explicit, user-driven loop for someone at the final stage:
`current_stage` resets to 1, `completed_stages` clears, `cycle_number`
increments — on the same row, under `FOR UPDATE`. "Journal, habit
streaks, goal completions, practice sessions, and energy are all
untouched: the carry-over is automatic and there is no penalty."
Mid-cycle users get 409 `cycle_not_complete`; no progress row is never
created as a side effect (`stages.py:372-396`). `highest_stage_reached`
is deliberately not reset (its monotonicity keeps Return eligibility —
[domain/metta-return](../domain/metta-return.md)).

DTOs: `backend/src/schemas/stage.py`, `schemas/wheel.py`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
