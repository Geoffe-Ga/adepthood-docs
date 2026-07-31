# domain/practice_insights — the practice insights rollup

`backend/src/domain/practice_insights.py` (207 lines). Pure-Python rollup
over a user's recent `PracticeSession` rows: the router fetches the last
60 days in a single query and hands them to `build_insights`. "Keeping
the aggregator DB-free keeps it cheap to test (no fixtures), and forces
the SQL layer to stay a thin 'select by user and date window'"
(`practice_insights.py:1-6`). All week math runs in the user's timezone
so a Pacific user doesn't see a week-boundary jump at 5 PM Sunday
(`practice_insights.py:8-12`).

## Constants (`practice_insights.py:25-36`)

| Constant | Value | Meaning |
| --- | --- | --- |
| `WEEKLY_TARGET_SESSIONS` | `4` | The spec's "meeting the practice goal" cadence (≥4 sessions per local calendar week) |
| `WEEKLY_HISTORY_WEEKS` | `8` | Rolling window for the weekly bar chart — "enough to spot a 6-week streak with a soft on-ramp" |
| `ROLLING_30D_WINDOW_DAYS` | `30` | Window for total/average/per-mode rollups; named so the router's SQL window stays in lock-step |

## Output

`PracticeInsights(weekly_counts, streak_weeks, total_minutes_30d,
avg_duration_minutes_30d, per_mode_counts, last_insight)` — mirrors
`schemas.practice.PracticeInsightsResponse` "so the router can re-shape
with a single `model_validate` call" (`practice_insights.py:47-61`).

## Rules

- **Week bucketing** — ISO weeks (Monday-start, `_monday_of`), matching
  the practice-cadence rule elsewhere in the app
  (`practice_insights.py:64-71`); the 8 week-start dates are ordered
  oldest-first so the chart reads left-to-right
  (`practice_insights.py:74-81`).
- **Zero-duration guard** — sessions with `duration_minutes <= 0` are
  skipped everywhere: "partial sessions count toward weekly totals *iff*
  duration > 0. Zero-duration aborts don't move the cadence needle"
  (`practice_insights.py:92-95`), mirrored in the 30-day stats so "a
  quick-cancel session never inflates `per_mode_counts` or drags the
  average toward zero" (`practice_insights.py:138-140`).
- **Streak weeks** — consecutive weeks ending *now* with
  `count >= 4`, scanning the weekly buckets from the newest backwards.
  "The current week counts even if it's still in progress — the spec's
  '4 x/week for 3 weeks running' UX shows users their momentum as it
  accrues" (`practice_insights.py:101-118`).
- **30-day window** — strict lower bound
  `today - 30 < local_day <= today` "so the span is exactly 30 distinct
  calendar days (today-29 .. today); an inclusive lower bound would
  count 31" (`practice_insights.py:121-128`).
- **Last insight** — the most recent non-null `insight` across the full
  **60-day** fetch window, deliberately wider than the 30-day rollup: "a
  user who took a multi-week pause should still see their last takeaway
  when they return rather than a blank card"
  (`practice_insights.py:156-174`).
- `avg_duration_minutes_30d` is `None` (not 0) with no qualifying
  sessions (`practice_insights.py:151-153`).

## Worked example

Today = Thu 2026-07-30 (Monday 07-27); sessions this week: 4×15 min →
current week bucket = 4; previous week = 5; two weeks ago = 2. Then
`streak_weeks = 2` (this week and last hit 4; the 2-count week breaks
the scan). `total_minutes_30d` sums all positive-duration sessions in
07-01..07-30; a 0-minute abort on 07-29 affects nothing.

Endpoint: `GET` practice insights — see
[api/practice-sessions](../api/practice-sessions.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
