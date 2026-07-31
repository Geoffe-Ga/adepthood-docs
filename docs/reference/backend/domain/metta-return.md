# domain/metta_return — the five-week Return

`backend/src/domain/metta_return.py` (196 lines). The Return is an
optional, self-chosen depth offered once a user has EVER passed Blue —
read from the persisted lifetime high-water mark. "Nothing here ranks,
shames, or penalizes: eligibility is a lifetime property the user already
earned, and the week the arc sits in is a gentle pacing hint, never a
deadline" (`metta_return.py:1-10`). All helpers are pure: they read
`StageProgress` and datetimes and never mutate stage progress
(`metta_return.py:12-15`).

## Constants (`metta_return.py:30-36`)

| Constant | Value | Meaning |
| --- | --- | --- |
| `RETURN_WEEK_COUNT` | `5` | One week per focus of loving-kindness |
| `RETURN_MINIMUM_STAGE` | `5` | "Blue is stage 4; reaching stage 5 (Orange) means Blue was passed to get there" |
| `DAYS_PER_WEEK` | `7` | — |
| `RETURN_TOTAL_DAYS` | `35` | "Living all of them is completion" |

## The sequence

`RETURN_SEQUENCE` is a tuple of five immutable `ReturnWeek(week_number,
focus, title, framing)` values (`metta_return.py:53-121`), widening the
circle of care (`MettaFocus`, `metta_return.py:39-50`):

| Week | Focus | Title |
| --- | --- | --- |
| 1 | `self` | "Coming home to steady ground" |
| 2 | `benefactor` | "Someone who has held you" |
| 3 | `stranger` | "A face you barely know" |
| 4 | `antagonist` | "Meeting a hard heart with softness" |
| 5 | `all_beings` | "The circle without an edge" |

The copy is "held to a strictly non-shaming standard — a Return is a
skillful rest, never a shortfall" (`metta_return.py:57-59`).

## Eligibility and episodes

`is_return_eligible(progress)` — verbatim rule
(`backend/src/domain/metta_return.py:124-137`):

```python
    Eligibility is the persisted lifetime high-water mark alone: a user with no
    :class:`StageProgress` row has never advanced and is ineligible; otherwise
    it holds when ``highest_stage_reached`` is at least
    :data:`RETURN_MINIMUM_STAGE`. ... which is why the
    offer holds from any current stage — Beige, Purple, or Red included — on any
    run, with no runtime max needed.
    """
    return progress is not None and progress.highest_stage_reached >= RETURN_MINIMUM_STAGE
```

`current_offer_episode(progress)` returns
`f"{cycle_number}:{current_stage}"` (or `None` if ineligible) — the
episode key persisted by `MettaReturnOfferDismissal`, so "any stage/cycle
advance is a fresh episode" and a past dismissal never silences a future
offer (`metta_return.py:140-144`;
[data-model/metta-return](../data-model/metta-return.md)).

## Arc timeline math

- `resumed_start(started_at, paused_at, now)` — resuming pushes the
  pause duration onto the start "so elapsed-since-start once again
  matches the pre-pause elapsed"; both operands are UTC-coerced before
  subtraction so SQLite-naive and Postgres-aware values never mix
  (`metta_return.py:153-166`).
- `active_return_week(started_at, paused_at, now)` — elapsed days are
  measured to `paused_at` when paused (a paused arc reports a *frozen*
  week), else to `now`; `week = days // 7 + 1`, clamped to `[1, 5]`
  (`metta_return.py:169-180`).
- `is_return_complete(started_at, paused_at, now)` — pure time-derived
  predicate: complete once ≥ 35 days have elapsed (frozen identically
  when paused) — "a reflective close rather than a reward"
  (`metta_return.py:183-196`).

## Worked example

Arc started 2026-06-20, paused 2026-07-05, resumed (`resumed_start`)
2026-07-12: new start = 06-20 + 7 days = 06-27. On 2026-07-31:
elapsed = 34 days → `active_return_week = 34 // 7 + 1 = 5`,
`is_return_complete = False` (34 < 35); one day later it completes.
While paused on 07-05 the arc reported week `15 // 7 + 1 = 3` no matter
how much later you asked.

Endpoints: [api/metta-return](../api/metta-return.md). The Return offer
copy on contraction lives in [contraction](contraction.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
