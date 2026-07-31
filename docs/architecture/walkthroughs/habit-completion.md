# Walkthrough: completing a habit

One tap on a habit tile in the Habits screen, traced through the Zustand
store, the API client, the FastAPI check-in route, the streak/milestone
domain math, the PostgreSQL write, and back to the celebration toast. All
paths are repo-relative to `Geoffe-Ga/adepthood`.

The UI is optimistic: the store is updated **before** the network call,
and rolled back if the server rejects it. The server is the source of
truth for streaks; the client never computes the authoritative streak for
the response.

## The happy path, hop by hop

1. **The tap.** In quick-log mode, pressing a habit tile calls
   `logUnit(itemId, 1)` — one unit against the habit
   (`frontend/src/features/Habits/HabitsScreen.tsx:79`):

    ```typescript
    else if (mode === 'quickLog') logUnit(itemId, 1);
    ```

2. **Snapshot preparation.** `useLogUnitMutation` builds a
   `LogUnitContext` via `habitManager.prepareLogUnit(habitId, amount, tz,
   date)` (`frontend/src/features/Habits/hooks/useHabitActions.ts:117`,
   `frontend/src/features/Habits/services/habitManager.ts:993-1030`). The
   context captures `prev` (the pre-tap habit list) and `next` (the
   post-tap list) **by value**, so a concurrent second tap rolls back to
   the right baseline (`habitManager.ts:365-370`). `completed_on` is set
   only for a genuine backfill — "a date that resolves to today is left
   undefined so the server stamps the completion with the real wall-clock
   time" (`habitManager.ts:1016-1020`).

3. **Optimistic apply.** The mutation hook
   (`frontend/src/hooks/useOptimisticMutation.ts:52`) runs
   `habitManager.applyLogUnitContext(ctx)`, which writes `next` into the
   Zustand store **and** persists it to disk
   (`frontend/src/features/Habits/services/habitManager.ts:1037-1040`):

    ```typescript
    applyLogUnitContext: (ctx: LogUnitContext): void => {
      setHabits(ctx.next);
      void persistHabits(ctx.next);
    },
    ```

4. **The network commit.** `commitLogUnitContext` POSTs the completion
   for the habit's current-tier goal
   (`frontend/src/features/Habits/services/habitManager.ts:1048-1055`),
   through the API client's `goalCompletions.create`
   (`frontend/src/api/index.ts:1147-1155`), which issues
   `POST /goal_completions/` with this payload shape
   (`frontend/src/api/index.ts:1117-1125`):

    ```json
    { "goal_id": 42, "did_complete": true, "completed_on": "2026-07-30" }
    ```

    An optional deterministic `Idempotency-Key` header
    (`frontend/src/api/index.ts:249`, `1136-1146`) guards against a
    double-send from a network blip mid-tap (BUG-API-008).

5. **Bearer attach.** The shared `request` core resolves the JWT from
   the registered token getter and attaches
   `Authorization: Bearer <token>`
   (`frontend/src/api/index.ts:330-347`) — see the
   [sign-in walkthrough](sign-in.md) for how that getter is wired.

6. **The route.** FastAPI dispatches to `create_goal_completion`
   (`backend/src/routers/goal_completions.py:35-56`). The request DTO
   rejects unknown fields (`extra="forbid"`) and a `completed_on` older
   than today backfills that day
   (`backend/src/routers/goal_completions.py:22-32`). The route resolves
   three dependencies: the authenticated user (`get_current_user`,
   `backend/src/routers/auth.py:999`), ownership of the goal and its
   parent habit (`resolve_owned_goal_and_habit`,
   `backend/src/dependencies/ownership.py:90`), and the user's IANA
   timezone (`current_user_timezone`,
   `backend/src/dependencies/timezone.py:30`).

7. **Recording is centralized.** The route delegates to
   `record_goal_completion` in `backend/src/services/checkin.py:285-330`
   — deliberately shared so the journal suggestion accept flow (issue
   #818) "records through the identical path"
   (`backend/src/services/checkin.py:1-7`).

8. **Target-day resolution.** `_resolve_target_day` defaults to the
   user's today (in their timezone), rejects a future date, and rejects
   a backfill older than 30 days
   (`backend/src/services/checkin.py:163-175`):

    ```python
    _MAX_BACKFILL_DAYS = 30
    ...
    if target_day > today:
        raise bad_request("completion_date_in_future")
    if target_day < today - timedelta(days=_MAX_BACKFILL_DAYS):
        raise bad_request("completion_date_too_old")
    ```

    The 30-day cap exists because "beyond this window a user could
    manufacture an arbitrarily long streak by logging one consecutive
    past day at a time" (`backend/src/services/checkin.py:42-45`).

9. **Polarity check.** `_subtractive_context_for_goal` decides whether
   this is an additive habit ("do the thing") or a subtractive one
   ("abstain from sugar") by querying the habit's clear-tier sibling
   goal; additive habits get `None` and take the legacy path
   (`backend/src/services/checkin.py:108-152`).

10. **Idempotency gate.** `_already_logged_on` checks for an existing
    completion in the user-local day bounds; if one exists the service
    returns the current streak with
    `reason_code: "already_logged_today"` and writes nothing
    (`backend/src/services/checkin.py:71-95` and `304-308`).

11. **Unscheduled-miss hold.** Logging a *miss* (`did_complete: false`)
    on a day outside the habit's `notification_days` cadence holds the
    streak without inserting a row — `reason_code: "streak_held"`
    (`backend/src/services/checkin.py:309-317`, `154-160`); the cadence
    check itself is `is_scheduled_on`
    (`backend/src/domain/streaks.py:22-30`), where an empty cadence
    means every day is scheduled.

12. **Streak math, one history read.** `compute_streak_before_and_after`
    fetches the goal's completions once, buckets units per user-local
    calendar day, computes the pre-insert streak, folds the pending
    completion in, and recomputes
    (`backend/src/services/streaks.py:135-152`). The additive rules are
    owned by `current_consecutive_streak`
    (`backend/src/domain/streaks.py:69-100`):

    ```python
    if sorted_days_desc[0] < today - timedelta(days=1):
        return 0
    streak = 1
    for i in range(1, len(sorted_days_desc)):
        if (sorted_days_desc[i - 1] - sorted_days_desc[i]).days != 1:
            break
        streak += 1
    ```

    Two exact rules: a **recency grace gate** — a most-recent completion
    older than *yesterday* zeroes the streak ("one stale day is
    forgiven, two is not", `backend/src/domain/streaks.py:80-84`) — and
    a **backward walk** that ends at the first gap greater than one
    calendar day. Days are bucketed in the *user's* timezone, not the
    server's (BUG-STREAK-002, `backend/src/services/streaks.py:9-14`).
    For subtractive habits the polarity flips:
    `subtractive_current_streak` walks back from today counting days
    whose logged total is at most the clear-tier threshold — a day with
    no row at all is perfect abstention — stopping at a transgression or
    the habit's `start_date` (`backend/src/domain/streaks.py:103-125`).

13. **The write.** `_persist_and_build_response` inserts a
    `GoalCompletion` row carrying `local_day` (the user-local calendar
    day) and `completed_units`, inside a savepoint, then commits
    (`backend/src/services/checkin.py:208-236`). One-per-day is
    guaranteed by a migration-owned unique index over
    `(goal_id, user_id, local_day)`
    (`backend/src/models/goal_completion.py:22-24`). A backfilled day's
    timestamp is anchored mid-day in the user's zone so it "lands
    unambiguously inside that local calendar day regardless of DST
    shoulder days" (`backend/src/services/checkin.py:178-190`).

14. **Milestones and reason code.** `check_milestones` returns only the
    thresholds *newly crossed* between old and new streak — thresholds
    are `[1, 3, 7, 14, 30]` (`backend/src/services/checkin.py:40`) —
    "preventing duplicate milestone toasts on retries" (BUG-HABITS-008,
    `backend/src/services/streaks.py:203-214`). The reason code is
    derived from the actual streak transition so "the flag never
    contradicts the number it ships with"
    (`backend/src/services/checkin.py:192-206`).

15. **The response.** The route returns a `CheckInResult`
    (`backend/src/schemas/checkin.py:24-32`), with `reason_code` pinned
    to a `Literal` of exactly four values (BUG-SCHEMA-003,
    `backend/src/schemas/checkin.py:12-21`):

    ```json
    {
      "streak": 7,
      "milestones": [{ "threshold": 7 }],
      "reason_code": "streak_incremented"
    }
    ```

16. **The toast.** Back in the hook, only `onSuccess` fires the toast —
    via `habitManager.buildLogUnitToast`
    (`frontend/src/features/Habits/hooks/useHabitActions.ts:107-111`,
    `frontend/src/features/Habits/services/habitManager.ts:1075`) — "so
    a server-rejected check-in never flashes a celebration the user
    didn't earn"
    (`frontend/src/features/Habits/hooks/useHabitActions.ts:40-45`).

## Where "energy" fits (and doesn't)

The check-in path computes streaks and milestones only. The energy
domain module is a separate, pure 21-day plan generator
(`generate_plan`, `backend/src/domain/energy.py:45-62`, with
`PLAN_DURATION_DAYS = 21` at `backend/src/domain/energy.py:41`) served
by its own `/energy` router (`backend/src/routers/energy.py`); nothing
in `services/checkin.py` or `services/streaks.py` calls it. A habit
completion does not recompute any energy plan.

## Failure modes

- **Future or too-old date** — `_resolve_target_day` raises
  `400 completion_date_in_future` / `400 completion_date_too_old`
  (`backend/src/services/checkin.py:170-175`). The client rolls back
  the optimistic write and shows the error toast.
- **Stale goal id (404 `goal_not_found`)** — after onboarding, the
  store may hold ids the server never issued (issue #282). The failure
  handler detects exactly this case, rolls back, background-refreshes
  the habits list, and asks the user to tap again
  (`frontend/src/features/Habits/hooks/useHabitActions.ts:36-37` and
  `76-90`).
- **Offline** — a non-server error (no HTTP response) keeps the
  optimistic state and queues the check-in via `savePendingCheckIn` for
  replay on the next `loadHabits`, with an explicit "saved on this
  device" toast
  (`frontend/src/features/Habits/hooks/useHabitActions.ts:58-75`). The
  request core also fast-fails GETs when the network layer already
  knows it is offline (`frontend/src/api/index.ts:840-845`).
- **Any other server rejection** — `rollbackLogUnitContext` restores
  **both** the store and the on-disk snapshot — before that fix, a cold
  start would rehydrate the optimistic state and desync from the server
  (BUG-FE-HABIT-001,
  `frontend/src/features/Habits/services/habitManager.ts:1057-1066`).
- **Two devices race the same day** — the second insert trips the
  unique index; `_try_persist_or_idempotent` catches `IntegrityError`,
  rolls back, and returns the idempotent `already_logged_today`
  response instead of a 500
  (`backend/src/services/checkin.py:239-254`).
- **Corrupt data: duplicate clear-tier goals** — the subtractive
  context builder surfaces `MultipleResultsFound` as a stable
  `500 duplicate_clear_tier_goals` rather than guessing which threshold
  applies (`backend/src/services/checkin.py:140-148`).

*Grounded in Geoffe-Ga/adepthood@55eef11, 2026-07-31.*
