# domain/dates — user-local day math

`backend/src/domain/dates.py` (185 lines). The single source of truth for
"what day is it for this user?". Re-deriving from
`datetime.now(UTC).date()` is exactly the bug family this module closes
(BUG-STREAK-002, BUG-HABIT-006, BUG-GOAL-004): "a habit completed at
11:30 PM Pacific is recorded with a UTC timestamp that the naive
`.date()` call labels as the *next* day, so streaks tick over prematurely
on the West Coast and idempotency checks fail near midnight"
(`dates.py:1-9`). Intentionally narrow — no display formatting, no input
parsing; backend code deals only in `date` and timezone-aware `datetime`
(`dates.py:11-15`).

## Input shapes and fallback

Helpers accept a `User`-like object (structural `_HasTimezone` protocol,
`dates.py:34-44`), an IANA string, or `None`. `_resolve_zone` silently
falls back to UTC for unknown zones: "a single bad zone string should
never lock a user out of completing a habit" (`dates.py:63-75`).
`_FALLBACK_TZ = "UTC"` is duplicated from `User.DEFAULT_USER_TIMEZONE`
deliberately so this module has no import cycle on the model
(`dates.py:24-31`).

## Function reference

| Function | Contract |
| --- | --- |
| `ensure_aware(value)` | Tags naive datetimes as UTC; passes aware through. Correct (not a band-aid) because SQLite drops `tzinfo` on round-trip but the stored instant was written as UTC (`dates.py:78-87`) |
| `compute_next_reset(now)` | First moment of the next calendar month, UTC-aware — e.g. `2026-04-15T12:34:56Z → 2026-05-01T00:00:00Z`; feeds `User.monthly_reset_date` (`dates.py:90-101`) |
| `now_in_tz(user_or_tz)` | Aware "now" in the user's zone, for user-facing wall-clock fields; internal timestamps (JWT `iat`/`exp`, ops audit) keep `datetime.now(UTC)` so they correlate across users (`dates.py:104-114`) |
| `today_in_tz(user_or_tz)` | The date the user perceives as today — the funnel for streaks, daily-completion idempotency, and habit-start logic (`dates.py:117-126`) |
| `day_bounds_in_tz(user_or_tz, day)` | Half-open `[start, end)` UTC-normalized bounds for the user-local day — see below (`dates.py:129-152`) |
| `to_user_date(user_or_tz, moment)` | Stored timestamp → user-perceived date; **refuses naive datetimes** with `ValueError` ("callers passing one are bugs we want to surface fast") (`dates.py:155-170`) |
| `to_user_date_bucket(ts, user_or_tz)` | Storage-boundary variant: accepts `datetime` *or* ISO-8601 string (SQLite returns strings), coerces naive → UTC; "the single canonical owner of this coercion (was duplicated in the streak service and the subtractive domain)" (`dates.py:173-185`) |

## `day_bounds_in_tz` — the SQLite lexical-comparison subtlety

Bounds are computed at local midnight and then normalized to UTC (issue #412) (`backend/src/domain/dates.py:135-148`):

```text
Postgres ``timestamptz`` compares instants, so either representation
works there — but SQLite stores ``DateTime(timezone=True)`` as ISO
strings and compares **lexically**, ignoring the offset suffix, so
bounds pinned to a non-UTC zone mis-ordered against the UTC-rendered
stored values.  Normalizing both bounds to UTC makes every rendered
string share the ``+00:00`` offset, so the lexical comparison is also
the chronological one.
```

`end` is the start of the *next* local day, so `WHERE col >= start AND
col < end` groups a full local day even across a DST jump — the window
may be 23 or 25 hours, never assumed 24 (`dates.py:142-148`).

## Worked example

User in `America/Los_Angeles` completes a goal at
`2026-07-31T06:30:00Z` (= 23:30 on 07-30 Pacific):
`to_user_date_bucket` → `2026-07-30`, not 07-31.
`day_bounds_in_tz(user, date(2026, 7, 30))` →
`(2026-07-30T07:00:00Z, 2026-07-31T07:00:00Z)`.

Consumers: [streaks](streaks.md), [habit-stats](habit-stats.md),
[program-calendar](program-calendar.md), `models/user.py`'s
`monthly_reset_date` default (`backend/src/models/user.py:18-20`).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
