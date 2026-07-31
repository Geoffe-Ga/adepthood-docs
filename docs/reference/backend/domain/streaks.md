# domain/streaks — streak math

`backend/src/domain/streaks.py` (152 lines). The canonical streak
implementations for additive (do-more) and subtractive (abstain) habits.
Both `GET /habits` (`services.streaks`) and `GET /habits/{id}/stats`
(`domain.habit_stats`) delegate here "so the same goal can never report
two different streak counts" (`streaks.py:72-75`).

## `is_scheduled_on(notification_days, weekday_name) -> bool`

Whether a weekday is in a habit's cadence. `None`/empty cadence means
every day; a misspelled weekday raises `ValueError` (valid names are
`WEEKDAY_ABBREVIATIONS = ("Mon", ..., "Sun")`, mirroring
`date.strftime("%a")`) (`streaks.py:16-30`).

## `sum_units_by_user_day(completions, user_timezone) -> dict[date, float]`

The single owner of the day-bucketing loop keyed on
`to_user_date_bucket`. Deliberately applies **no** `> 0` filter:
"subtractive habits treat the absence of a row as perfect abstention, so
zero-sum days stay addressable via `get(day, 0.0)`"
(`streaks.py:49-66`).

## `current_consecutive_streak(sorted_days_desc, today) -> int`

The one canonical additive streak — mirrored by the frontend's
`streakFromCompletions` (`streaks.py:69-75`). Verbatim
(`backend/src/domain/streaks.py:91-100`):

```python
    if not sorted_days_desc:
        return 0
    if sorted_days_desc[0] < today - timedelta(days=1):
        return 0
    streak = 1
    for i in range(1, len(sorted_days_desc)):
        if (sorted_days_desc[i - 1] - sorted_days_desc[i]).days != 1:
            break
        streak += 1
    return streak
```

Two rules (`streaks.py:80-88`):

- **Recency grace gate** — a most-recent day older than *yesterday*
  zeroes the streak. "The one-day grace prevents the UI flashing 'streak
  lost' between local midnight and the user's first completion of the
  day; one stale day is forgiven, two is not."
- **Backward walk** — count while each step back is exactly one calendar
  day; the first gap > 1 ends the streak.

Input must be distinct user-local days sorted descending.

## Subtractive streaks

`SubtractiveContext` bundles `clear_threshold` (day sum > threshold =
transgression) and `start_date` (the habit's birth, so the walk cannot
accrue days before the habit existed) — one kwarg to stay under the
project's PLR0913 max-5-args bar (`streaks.py:33-46`).

- `subtractive_current_streak(day_totals, tz, ctx)` — walks backwards
  from `today_in_tz`; a day counts when its total ≤ `clear_threshold`
  (trivially true with no row); stops on a transgression or when the
  cursor crosses `start_date`; 0 if the habit hasn't begun
  (`streaks.py:103-125`).
- `subtractive_longest_streak(day_totals, tz, ctx)` — forward scan of
  every calendar day in `[start_date, today]`, tracking the longest
  no-transgression run; a transgression resets the run
  (`streaks.py:128-152`).

## Worked example

Additive, today = 2026-07-31, completion days (desc)
`[07-30, 07-29, 07-27]`: gate passes (07-30 ≥ yesterday), walk counts
07-30→07-29 (gap 1, streak 2), 07-29→07-27 (gap 2, stop) → **2**. If the
latest day were 07-28, the gate zeroes it → **0**.

Subtractive, `clear_threshold=0`, `start_date=07-27`, one transgression
row on 07-29 (`total=1.0`): current walk from 07-31: 07-31 ok, 07-30 ok,
07-29 breaks → **2**; longest scan 07-27..07-31: runs `2` (27-28) then
`2` (30-31) → **2**.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
