# API — goals router

`backend/src/routers/goals.py` (49 lines).
`APIRouter(prefix="/goals", tags=["goals"])` (`goals.py:27`). Exists to
fill a gap: the habits PUT endpoint's `HabitCreate` carries no goal
fields, so target/unit/frequency/`is_additive` could not be edited from
the client (`goals.py:1-8`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| PUT | `/goals/{goal_id}` | JWT + owned goal | `GoalUpdate` (`backend/src/schemas/goal.py`) | `Goal` schema | 200 | 404 `goal_not_found` (missing, orphaned, **or not yours** — collapsed for enumeration safety) |

Ownership rides on the parent habit via the `require_owned_goal`
dependency (`backend/src/dependencies/ownership.py:118-130`), which
collapses "missing goal" and "not yours" into a single 404
(`ownership.py:93-115`). `habit_id` is deliberately absent from
`GoalUpdate` "so the parent habit cannot be swapped via this endpoint —
a goal is bound to its habit for life" (`goals.py:37-42`). The update
applies every field of the payload, commits, and logs `goal_updated`
(`goals.py:43-49`).

Model reference: [data-model/habits-goals](../data-model/habits-goals.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
