# domain/course — content drip-feed gating

`backend/src/domain/course.py` (104 lines). Pure logic for the course
ring's proportional drip-feed: how many chapters of a stage are open, how
locked items are masked, and when the next chapter opens.

## `compute_days_elapsed(stage_started_at) -> int`

Whole days since the stage started; a *future* `stage_started_at` is
clamped to 0 with a `stage_started_at_in_future` WARNING log
(`course.py:15-28`). Naive datetimes are coerced to UTC first because
"SQLite drops tzinfo on round-trip" under the test fixture
(`course.py:18-20`).

## `unlocked_chapter_count(*, total, duration_days, day_in_stage) -> int`

The core drip rule (`backend/src/domain/course.py:31-48`):

```python
    The proportional drip spreads a stage's ``total`` chapters evenly
    across its ``duration_days``, so by the 1-based ``day_in_stage`` the
    user has earned ``ceil(total * day / duration)`` of them, clamped to
    ``[0, total]``.  ``ceil`` rounds up, so any open day (``day >= 1``) of
    a seeded stage (``total >= 1``) yields at least one chapter — the
    guarantee that keeps an unlocked, non-empty stage from ever rendering
    "No Content Yet".  A stage the user has moved past supplies
    ``day_in_stage >= duration_days`` and unlocks everything.
    """
    if total <= 0 or duration_days <= 0 or day_in_stage <= 0:
        return 0
    if day_in_stage >= duration_days:
        return total
    earned = math.ceil(total * day_in_stage / duration_days)
    return max(0, min(earned, total))
```

## `enrich_content_item(item, *, is_locked, read_content_ids) -> dict`

Attaches `is_locked` / `is_read`, and sets a locked item's `url` to
`None` "so a client cannot fetch — or spoil — a chapter ahead of its drip
release" (`course.py:51-64`).

## `filter_content_for_user(items, *, unlocked_count, read_content_ids)`

Gating is by **ordinal position**, not `release_day`
(`course.py:67-87`): items must already be in release order; the first
`unlocked_count` are open and the rest locked. "Gating on position is
what lets a non-dense `release_day` sequence (stage 1 skips day 11) still
drip exactly `unlocked_count` chapters — `release_day` is only the sort
key now, never the gate" (`course.py:76-81`).

## `next_unlock_day(*, total, duration_days, day_in_stage) -> int | None`

Inverts the drip: with `k` chapters open, the `(k+1)`-th opens on
`floor(k * duration / total) + 1`; `None` once everything is unlocked,
including the empty-stage case (`course.py:90-105`).

## Worked example

Stage with `total=7` chapters, `duration_days=21`:

| `day_in_stage` | `unlocked_chapter_count` | `next_unlock_day` |
| --- | --- | --- |
| 1 | `ceil(7·1/21)` = 1 | `floor(1·21/7)+1` = 4 |
| 4 | `ceil(28/21)` = 2 | `floor(2·21/7)+1` = 7 |
| 20 | `ceil(140/21)` = 7 | `None` |
| 21+ | 7 (full unlock) | `None` |

Day-in-stage comes from the program calendar
([domain/program-calendar](program-calendar.md)); the endpoint wiring is
in [api/course](../api/course.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
