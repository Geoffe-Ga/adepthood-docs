# API — habits router

`backend/src/routers/habits.py` (450 lines).
`APIRouter(prefix="/habits", tags=["habits"])` (`habits.py:36`).
Constants: `_MAX_HABITS_PER_USER = 100`, `_COMPLETIONS_WINDOW_DAYS = 90`
(the embedded-completions window) (`habits.py:39,47`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| POST | `/habits/` | JWT | `HabitCreate` | `HabitWithGoals` | 200 | 409 `habit_quota_exceeded` (`habits.py:164`), 409 `duplicate_habit_name` (pre-check *and* DB-race path, `habits.py:177,198`) |
| GET | `/habits/` | JWT | `PaginationParams` | `Page[HabitWithGoals]` or bare list | 200 | — |
| GET | `/habits/{habit_id}` | JWT + owned | — | `HabitWithGoals` | 200 | 404 / 403 |
| PUT | `/habits/{habit_id}` | JWT + owned | `HabitCreate` | `Habit` schema | 200 | 404 / 403; 409 `duplicate_habit_name` on rename collision (`habits.py:298`) |
| DELETE | `/habits/{habit_id}` | JWT + owned | — | — | **204** | 404 / 403 |
| DELETE | `/habits/{habit_id}/completions` | JWT + owned | — | — | **204** | 404 / 403 |
| PUT | `/habits/{habit_id}/goals/units` | JWT + owned | `GoalUnitsUpdate` | `list[Goal]` | 200 | 404 / 403 |
| GET | `/habits/{habit_id}/stats` | JWT | — | `HabitStats` | 200 | 404 `habit_not_found` / 403 `forbidden` (`habits.py:399-402`) |

Notes:

- **Create** provisions a habit **plus three default tier goals**
  (low/clear/stretch), enforcing the 100-habit quota and per-user
  case-insensitive name uniqueness — the latter is guaranteed at the DB
  level by migration `b5c6d7e8f9a0_habit_unique_user_lower_name`, so the
  race path also maps to 409 (`habits.py:164-228`).
- **Listing** sorts by `sort_order` and eager-loads goals with a bounded
  90-day completions window; `?paginate=true` opts into the envelope
  (`habits.py:242-266`).
- **Ownership** is `require_owned_habit`'s canonical 404 (missing) / 403
  (cross-user, audited) split
  (`backend/src/dependencies/ownership.py:75-87`).
- **Clear completions** bulk-deletes every completion for the habit's
  goals in one statement "so a start-date reset … leaves no stale rows
  behind", with a defense-in-depth `user_id` filter (`habits.py:324-338`).
- **Goal-units update** (issue #289) replaces the client's per-tier
  fan-out with one transaction: "either every goal moves to the new unit
  fields or none do. Tier identity and per-tier targets are deliberately
  untouched" (`habits.py:406-421`).
- **Stats** delegates to `domain.habit_stats.compute_habit_stats` in the
  caller's timezone, choosing the subtractive path per goal type — see
  [domain/habit-stats](../domain/habit-stats.md) and
  [domain/streaks](../domain/streaks.md) (`habits.py:439-450`).

DTOs: `backend/src/schemas/habit.py`, `schemas/habit_stats.py`. Model:
[data-model/habits-goals](../data-model/habits-goals.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
