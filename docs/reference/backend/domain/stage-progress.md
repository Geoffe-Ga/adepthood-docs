# domain/stage_progress — progress, unlocking, and history

`backend/src/domain/stage_progress.py` (560 lines). Computes stage
progress percentages, decides stage unlocking, provisions the per-user
`StageProgress` row, and aggregates per-stage habit/practice history. The
largest domain module; re-exports `TOTAL_STAGES` from
[constants](constants.md) (`stage_progress.py:13,30-43`).

## Row access and provisioning

- `get_user_progress` — plain fetch by user (`stage_progress.py:56-59`).
- `get_user_progress_for_update` — the same fetch `WITH FOR UPDATE`, for
  mutation endpoints "to prevent TOCTOU races (e.g. two concurrent
  advance requests both reading the same current_stage)"
  (`stage_progress.py:62-72`).
- `ensure_user_progress` — provision a stage-1 row on first access using
  the same race-safe SAVEPOINT/commit/IntegrityError-re-read pattern as
  [ui-flags](ui-flags.md) (`stage_progress.py:75-98`).
- `AllStagesCompletedError` — a plain domain exception (not
  `HTTPException`) "so non-HTTP callers (admin tooling, async tasks,
  tests) use the helper without pulling in FastAPI's transport layer"
  (`stage_progress.py:46-53`); raised by `next_stage_for` when
  `current_stage >= TOTAL_STAGES` (`stage_progress.py:152-158`).

## Invariant math

`expected_completed_stages(current_stage)` = `{1..current_stage-1}`;
`completed_stage_gap(completed, current_stage)` returns
`(missing, extra)` — "the invariant every stage mutation must preserve is
`set(completed) == {1..current_stage-1}`. … the canonical owner of the
gap math the admin router used to inline twice"
(`stage_progress.py:101-119`).

## `is_stage_unlocked` — advancement OR calendar

The unlock rule, verbatim
(`backend/src/domain/stage_progress.py:122-149`):

```python
    if stage_number == _STAGE_1:
        return True
    if progress is None:
        return False
    unlocked_through = max(
        progress.current_stage,
        calendar_stage(resolve_program_anchor(progress), now, tz=tz),
    )
    return stage_number <= unlocked_through
```

Advancement moves only via the validated router path (advance must equal
`current + 1`); the calendar term is the same date-derived schedule the
frontend renders, evaluated in the caller's timezone "so the server …
never 403s a stage the user can see is open. `max` of the two means time
can OPEN stages but never revoke advancement-granted access — and the
calendar itself is server-computed, so a client cannot skip ahead"
(`stage_progress.py:129-139`). Stage 1 is always unlocked
(`stage_progress.py:27-28`).

## Progress computation

`compute_stage_progress(session, user_id, stage_number)` returns
`{"habits_progress", "practice_sessions_completed",
"course_items_completed", "overall_progress"}`
(`stage_progress.py:258-297`). Components:

- **Habits** — ratio of habits with ≥1 completion to total habits for
  the stage; a stage with no habits reports `(0.0, present=False)` "so
  it is excluded from the overall average rather than dragging it down
  as a 0% component" (`stage_progress.py:161-195`).
- **Practice** — binary `1.0` once any session is logged; *presence* is
  "the user selected a practice for this stage", so a selected-but-idle
  stage counts practice as 0% while an unselected one excludes it
  (`stage_progress.py:230-243,287`).
- **Course** — `completed_items / total_items` clamped to 1.0; presence
  is `total > 0` (`stage_progress.py:198-227,283`).
- **Overall** — `_average_present`: the mean of the *present* components
  only — "the divisor adapts instead of always being a hardcoded 2"
  (`stage_progress.py:246-255,284-290`). Both leaf values are rounded to
  2 decimals (`stage_progress.py:292-297`).

`compute_stage_progress_batch(session, user_id, stage_numbers)` is the
batched equivalent: "exactly three grouped queries (habits, practice
sessions, course items) regardless of stage count", eliminating the N+1
on `list_stages` (issue #473), with values identical to the per-stage
function (`stage_progress.py:408-436`). The helpers deliberately
`GROUP BY` the whole dataset with no `IN` filter — the curriculum is ≤36
stages, so "one grouped scan beats a parameterised per-stage filter"
(`stage_progress.py:421-424`; batch queries at
`stage_progress.py:300-378`, assembly parity at
`stage_progress.py:381-405`). Consumed by [wheel](wheel.md).

## Worked example

Stage 3: 2 habits (1 with a completion), a selected practice with 0
sessions, 4 of 8 course items read → habits `0.5` (present), practice
`0.0` (present — selected), course `0.5` (present) →
`overall = (0.5 + 0.0 + 0.5) / 3 ≈ 0.33`. Same stage with no practice
selected → `(0.5 + 0.5) / 2 = 0.5`.

## History aggregations

- `get_stage_practice_history` — one GROUP BY over sessions joined
  through `UserPractice` to `Practice`: per-practice
  `(name, sessions_completed, total_minutes, last_session)`
  (`stage_progress.py:447-479`).
- `get_stage_habit_history` — two queries regardless of habit/goal count
  (the previous implementation issued `1 + 2*habits + goals`, "26+
  queries for a typical stage"): fetch habits ordered by id, then one
  LEFT-OUTER-JOIN aggregate counting completions per `(habit, tier)`;
  the user filter sits on the join condition, not WHERE, so a goal with
  only other users' completions still surfaces with `count == 0`
  (`stage_progress.py:482-560`). Output `HabitHistoryItem` marks
  `goals_achieved[tier] = count > 0` and `best_streak` from the cached
  `Habit.streak` (`stage_progress.py:530-538`).

Consumers: [api/stages](../api/stages.md), [api/course](../api/course.md),
[domain/wheel](wheel.md), [domain/metta-return](metta-return.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
