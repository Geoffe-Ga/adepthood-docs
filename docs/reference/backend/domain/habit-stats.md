# domain/habit_stats — the stats rollup

`backend/src/domain/habit_stats.py` (156 lines). Aggregates a habit's
`GoalCompletion` rows into the `HabitStats` DTO
(`backend/src/schemas/habit_stats.py`) using the user's local calendar.

## `compute_habit_stats(completions, user_timezone="UTC", subtractive=None)`

The entry point (`habit_stats.py:140-156`): with a
`SubtractiveContext` the subtractive variant runs; without it the
additive path preserves legacy behavior for every existing caller.

## Additive path (`_additive_stats`, `habit_stats.py:111-137`)

The parity rule with `GET /habits` comes first
(`backend/src/domain/habit_stats.py:113-120`):

```python
    Additive parity (#781): a "did not complete" check-in persists a real
    ``completed_units == 0`` row. ``GET /habits`` (services.streaks) excludes
    those via ``completed_units > 0``; the stats path must use the same rule or
    the two endpoints report different streaks. Filter once at the entry so the
    day buckets, streaks, rate, and total all describe actual completions.
    """
    completed = [c for c in completions if c.completed_units > 0]
```

Then: `_aggregate_by_day` buckets units and event counts per **JS-style
weekday index** (`(local_date.weekday() + 1) % 7`, Sun=0)
(`habit_stats.py:38-52`); `current_streak` delegates to
`domain.streaks.current_consecutive_streak`; `longest_streak` uses the
local `_longest_streak` forward scan over logged days only —
deliberately distinct from the subtractive scan, which "counts absent
days as abstention wins; this additive walk only ever sees days the user
actually logged, so the two cannot share an implementation"
(`habit_stats.py:55-70`).

## Subtractive path (`_subtractive_stats`, `habit_stats.py:83-108`)

Only the two streak fields flip polarity (delegating to
`subtractive_current_streak` / `subtractive_longest_streak`); day-of-week
buckets, completion rate, and total completions "stay rooted in the
additive bucketing because they describe 'what the user logged' —
pre-existing semantics this PR explicitly leaves unchanged. Only the two
streak fields flip polarity, which is the visible inconsistency that PR #379
review surfaced" (`habit_stats.py:88-95`).

## `_completion_rate` (`habit_stats.py:73-80`)

`len(distinct_days) / days_since_first_inclusive` in the user's calendar:
`span = (today - first).days + 1`; empty input → `0.0`.

## Output shape (`HabitStats`)

`day_labels` (`["Sun", ..., "Sat"]`), `values` (units per weekday),
`completions_by_day` (event counts per weekday), `longest_streak`,
`current_streak`, `total_completions`, `completion_rate`,
`completion_dates` (ISO strings, ascending) — empty stats are all-zeros
(`habit_stats.py:25-35`).

## Worked example

Additive habit, tz UTC, today 2026-07-31; rows: 3.0 units on Wed 07-29,
2.0 on Thu 07-30, and a 0-unit check-in on Fri 07-31. The zero row is
filtered (#781): `total_completions=2`, `completion_dates=[07-29,
07-30]`, `current_streak=2` (grace gate passes), `longest_streak=2`,
`completion_rate = 2 / 3 ≈ 0.667` (span 07-29..07-31),
`values[3]=3.0, values[4]=2.0` (Wed=idx 3, Thu=idx 4 in Sun-first
indexing).

Consumed by `GET /habits/{id}/stats` — see [api/habits](../api/habits.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
