# API — metta-return router

`backend/src/routers/metta_return.py` (553 lines).
`APIRouter(prefix="/metta-return", tags=["metta-return"])`
(`metta_return.py:54`). The Return arc lifecycle. "Every action is scoped
to the caller resolved from the JWT — no `user_id` is ever accepted from
the body or path, nor returned — and none of the lifecycle actions
mutate `StageProgress`" (`metta_return.py:1-8`). Write handlers select
the caller's active arc `FOR UPDATE`; an arc the caller does not own is
indistinguishable from a missing one (`metta_return.py:10-14`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/metta-return` | JWT | — | `MettaReturnStateResponse` | 200 | — |
| POST | `/metta-return/arc` | JWT | — | `ReturnArcResponse` | **201** | 409 `return_not_eligible` / `return_arc_already_active` (`metta_return.py:331-341`) |
| POST | `/metta-return/arc/pause` | JWT | — | `ReturnArcResponse` | 200 (idempotent) | 404 `return_arc_not_found` |
| POST | `/metta-return/arc/resume` | JWT | — | `ReturnArcResponse` | 200 (idempotent) | 404 `return_arc_not_found` |
| POST | `/metta-return/arc/leave` | JWT | — | `ReturnArcResponse` | 200 | 404 `return_arc_not_found` |
| POST | `/metta-return/arc/release` | JWT | `ReleaseHabitsRequest` | `list[ReleasedHabitResponse]` | 200 | 404 `return_arc_not_found` |
| POST | `/metta-return/arc/recommit` | JWT | `ReleaseHabitsRequest` | `list[ReleasedHabitResponse]` | 200 (idempotent) | 404 `return_arc_not_found` |
| POST | `/metta-return/offer/dismiss` | JWT | — | `MettaReturnStateResponse` | 200 (idempotent) | 409 `return_not_eligible` |

Behavior:

- **GET** is strictly read-only — stage progress is fetched, never
  provisioned, "so a brand-new user's row is not created as a side
  effect"; it reports eligibility, the five-week sequence, the active
  arc projected to its current week, and whether the current offer
  episode was dismissed (`metta_return.py:294-305`).
- **Start** (`metta_return.py:314-341`): 409 unless eligible
  (`highest_stage_reached >= 5`) and no active arc. Two truly concurrent
  starts both clear the pre-check (no row to lock yet), so "the
  partial-unique active-arc index is the real guard: the loser's insert
  raises `IntegrityError`, which is caught and collapsed to the same
  409."
- **Pause / resume** freeze and restore the arc week: pause keeps the
  original pause instant on repeat "so the frozen week does not drift";
  resume shifts `started_at` forward by the paused duration "so no
  elapsed weeks are lost" (`metta_return.py:346-382`;
  [domain/metta-return](../domain/metta-return.md)).
- **Leave** sets `left_at`, freeing the partial-unique slot so a fresh
  arc can be started later (`metta_return.py:393-403`).
- **Release** softly pauses named habits (`revealed → False`, history
  preserved) and records them per-arc; unowned/unknown/already-locked
  ids are skipped silently. The `FOR UPDATE` arc lock fully serializes
  concurrent releases, so the `(arc_id, habit_id)` unique constraint "is
  never provoked here, and no `IntegrityError` catch is needed"
  (`metta_return.py:466-491`).
- **Recommit** re-unlocks habits released in this arc, stamping
  `recommitted_at`; ids never released here are ignored; "works while
  the arc is time-complete but not yet left" (`metta_return.py:499-516`).
- **Dismiss offer** is per-episode (`{cycle}:{stage}` key): a repeat
  collapses onto the same row, and "any stage or cycle advance opens a
  fresh episode whose offer surfaces again" (`metta_return.py:528-544`).

DTOs: `backend/src/schemas/metta_return.py`. Model:
[data-model/metta-return](../data-model/metta-return.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
