# API — goal-completions router

`backend/src/routers/goal_completions.py` (56 lines).
`APIRouter(prefix="/goal_completions", tags=["goals"])`
(`goal_completions.py:19`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| POST | `/goal_completions/` | JWT + owned goal | `GoalCompletionRequest` (defined in-router, `extra="forbid"`) | `CheckInResult` (`backend/src/schemas/checkin.py`) | 200 | 404 `goal_not_found` (missing / orphaned / not yours — enumeration-safe), 400 (future `completed_on`, from the service) |

The request DTO (`goal_completions.py:22-32`):

```python
class GoalCompletionRequest(BaseModel):
    """Payload for recording a goal completion or miss; rejects unknown fields."""

    model_config = ConfigDict(extra="forbid")

    goal_id: int
    did_complete: bool = True
    # Calendar day the check-in is for, in the user's timezone. Omit to log
    # today; supply a past ``YYYY-MM-DD`` to backfill a missed day. A future
    # date is rejected by the route.
    completed_on: date | None = None
```

Behavior (`goal_completions.py:35-56`): resolves `(goal, habit)` through
the enumeration-safe ownership helper
(`backend/src/dependencies/ownership.py:90-115`), builds a
`CheckInContext` with the per-request-cached user timezone
(`backend/src/dependencies/timezone.py:30-40`), and delegates to
`services.checkin.record_goal_completion`. Recording is **idempotent on
the same (user, goal, local day)** — backed by the DB unique index over
`(goal_id, user_id, local_day)`
([data-model/habits-goals](../data-model/habits-goals.md)) — and the
service layer is shared deliberately: "the journal accept flow (#818)
records through the identical path" (`goal_completions.py:42-48`).
`did_complete=false` persists a real zero-unit row (the additive-parity
rule documented in [domain/habit-stats](../domain/habit-stats.md)). The
response carries updated streak and milestone data.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
