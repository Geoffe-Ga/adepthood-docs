# API — goal-groups router

`backend/src/routers/goal_groups.py` (212 lines).
`APIRouter(prefix="/goal-groups", tags=["goal-groups"])`
(`goal_groups.py:24`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/goal-groups/` | JWT | `PaginationParams` | `Page[GoalGroupResponse]` or bare list | 200 | — |
| GET | `/goal-groups/{group_id}` | JWT | — | `GoalGroupResponse` | 200 | 404 `goal_group_not_found`; 403 `forbidden` (another user's private group) |
| POST | `/goal-groups/` | JWT | `GoalGroupCreate` | `GoalGroupResponse` | **201** | — |
| PUT | `/goal-groups/{group_id}` | JWT, owner-only | `GoalGroupCreate` | `GoalGroupResponse` | 200 | 404; 403 (incl. shared templates) |
| DELETE | `/goal-groups/{group_id}` | JWT, owner-only | — | — | **204** | 404; 403 |

Behavior:

- **Listing** returns the caller's groups plus all shared templates,
  eager-loading goals; `?paginate=true` opts into the envelope
  (BUG-INFRA-015, `goal_groups.py:72-98`).
- **Seed templates** (Meditation/Exercise/Nutrition,
  `goal_groups.py:26-45`) are provisioned idempotently at app startup by
  `seed_goal_group_templates` — keyed on name, "so `list_goal_groups`
  performs no write while users still get the defaults"
  (`goal_groups.py:48-69`; called from the lifespan hook, see
  [infrastructure](../infrastructure.md)).
- **Create** sources ownership from the JWT (BUG-GOAL-005 — the schema
  has no `user_id` field); `shared_template=true` flips the row to a
  public template with `user_id=NULL` per the DB CHECK
  (`goal_groups.py:116-133`;
  [data-model/habits-goals](../data-model/habits-goals.md)).
- **Read vs write access split**: reads allow owner OR shared template
  (`require_visible_goal_group`); mutations are strict owner-only
  (`require_owned_goal_group`) — shared templates have `user_id IS NULL`
  "so they can never match `current_user` and always 403", closing
  BUG-GOAL-006 where "shared templates were editable by any user"
  (`goal_groups.py:168-176`;
  `backend/src/dependencies/ownership.py:175-202`).
- **Delete unlinks, never cascades**: each goal's `goal_group_id` is set
  to `NULL` before the group row is deleted (`goal_groups.py:190-212`).
- All post-mutation reads go through `_refetch_goal_group_with_goals`,
  whose `.first()` + None-check "turns a concurrent delete into a 404
  rather than a `NoResultFound` 500" (BUG-INFRA-020,
  `goal_groups.py:147-158`).

DTOs: `backend/src/schemas/goal_group.py`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
