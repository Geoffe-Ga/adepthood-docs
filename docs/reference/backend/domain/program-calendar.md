# domain/program_calendar — the date-derived program clock

`backend/src/domain/program_calendar.py` (110 lines). The backend mirror
of the frontend's single program-start anchor (issue #386 / PR #384).
Before it, the server gated weeks by prompt-completion counts and stages
by the advancement chain, so it "could 403 a week or stage the calendar
says is open". These helpers compute the same calendar server-side, and
gating call sites combine them with the existing models via `max(...)` —
"so time can OPEN access but never revoke what advancement already
granted — and never let a client skip past the calendar"
(`program_calendar.py:1-13`).

## `elapsed_days(anchor, now, *, tz=None) -> int`

Whole **calendar** days between the anchor's local date and `now`'s local
date, counted in `tz` (UTC when `None`) and floored at zero for clock
skew (`backend/src/domain/program_calendar.py:30-48`):

```python
    delta = to_user_date(tz, ensure_aware(now)) - to_user_date(tz, ensure_aware(anchor))
    return max(0, delta.days)
```

The result is "the number of midnights crossed in the user's zone —
matching the frontend's local-midnight convention — rather than a UTC
timedelta anchored to the anchor's wall-clock time-of-day"
(`program_calendar.py:33-38`). Both operands pass through `ensure_aware`
because SQLite reads anchors back naive (`program_calendar.py:43-45`).
Shared by this module and `domain.reflection_hierarchy`'s due-date ladder
so the normalization and skew floor live in exactly one place
(`program_calendar.py:40-43`).

## `calendar_week(anchor, now=None, *, tz=None) -> int`

1-based program week, clamped to the curriculum:
`elapsed_days // 7 + 1`, capped at `TOTAL_WEEKS` (36)
(`program_calendar.py:51-59`).

## `calendar_stage(anchor, now=None, *, tz=None) -> int`

1-based stage, walking `STAGE_DURATIONS_DAYS`
(`(21,)*8 + (42, 42)` — see [constants](constants.md)) until the elapsed
days fall inside a window; past the end returns `TOTAL_STAGES`
(`program_calendar.py:62-74`).

## `calendar_day_in_stage(anchor, stage_number, now=None, *, tz=None) -> int`

The 1-based day within `stage_number`'s window — the input to the
[course drip](course.md). `stage_number` is clamped to `1..TOTAL_STAGES`;
`day = elapsed_days - window_start + 1`, capped at the stage duration.
Values before the window opens are non-positive (deliberately not
floored). "Independent of advancement — callers combine it with
`current_stage` so time can only widen access"
(`program_calendar.py:77-98`).

## `resolve_program_anchor(progress) -> datetime`

`progress.program_started_at or progress.stage_started_at`
(`program_calendar.py:101-110`): prefers the stored program anchor
(backfilled by migration `18c9d0e1f2a3` from the earliest habit start
date); legacy rows fall back to the per-stage anchor, which is
"conservative (later) for anyone past stage 1, which only makes the time
gate stricter, never looser" (`program_calendar.py:104-108`).

## Worked example

Anchor 2026-01-05, tz `America/Los_Angeles`, now 2026-03-10 (local):
`elapsed_days = 64`. `calendar_week = 64 // 7 + 1 = 10`.
`calendar_stage`: 64 − 21 − 21 − 21 = 1 remaining after three stages →
stage 4. `calendar_day_in_stage(anchor, 4)` = 64 − 63 + 1 = 2 — day 2 of
stage 4, so with 7 chapters `unlocked_chapter_count(7, 21, 2) = 1`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
