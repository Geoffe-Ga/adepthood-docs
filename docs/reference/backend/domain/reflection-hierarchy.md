# domain/reflection_hierarchy — the nested reflection calendar

`backend/src/domain/reflection_hierarchy.py` (447 lines). When a
reflection falls due and what feeds it. The APTITUDE curriculum is a
nested calendar: ten stages pair into five *components* (stages `2n-1`
and `2n`), components split into two *tiers* (first six stages, then
four), and every layer closes with an invitation to reflect. "The
precedence is fixed: **program beats tier beats component beats stage
beats a plain week.** A user who reaches day seven of week eighteen is
not asked for four reflections; they are offered the single tier
reflection that subsumes the rest" (`reflection_hierarchy.py:1-11`).
Pure — no database (`reflection_hierarchy.py:13-14`).

Two driving ideas (`reflection_hierarchy.py:16-34`): everything derives
from `STAGE_DURATIONS_DAYS` (so `_WEEKS_PER_STAGE = (3,)*8 + (6, 6)` and
`TOTAL_PROGRAM_WEEKS = 36` are computed, not hand-written,
`reflection_hierarchy.py:56-63`) — except the six-then-four tier split,
which "is a curriculum design decision — it is NOT derivable from
STAGE_DURATIONS_DAYS", hence the named constant
`_TIER_ONE_LAST_STAGE = 6` (`reflection_hierarchy.py:75-80`); and uniform
recursion in source resolution with no boundary special-cases.

## Keys and levels

Scope keys are `"c{cycle}:{token}"` with token ∈ `prog`, `w<week>`,
`s<stage>`, `p<component>`, `t<tier>`; the cycle prefix "isolates repeat
runs of the program: a reflection from cycle one never satisfies a
cycle-two lookup" (`reflection_hierarchy.py:36-39,86`).
`ReflectionLevel` = `week < stage < component < tier < program`
(`reflection_hierarchy.py:89-101`); `_parse_key` validates shape and
range (a stray `s11` or `t3` is rejected, `reflection_hierarchy.py:124-131,285-298`).

## `due_reflection(anchor, now=None, cycle=1) -> DueReflection | None`

(`backend/src/domain/reflection_hierarchy.py:247-267`):

```python
    reference = now if now is not None else datetime.now(UTC)
    elapsed = elapsed_days(anchor, reference)
    if elapsed % _DAYS_PER_WEEK + 1 != _DAYS_PER_WEEK:
        return None
    week = elapsed // _DAYS_PER_WEEK + 1
    if week > TOTAL_PROGRAM_WEEKS:
        return None
    level, token = _closing_level(week)
    return DueReflection(level=level, key=f"c{cycle}:{token}", week=week)
```

Reflections come due **only on the seventh day of a program week**;
other days, clock skew, and weeks past 36 yield `None`. `_closing_level`
picks the widest closing layer: week 36 → `PROGRAM`; a week that ends no
stage → plain `WEEK`; a stage end escalates to `TIER` if the stage is 6
or 10, else `COMPONENT` if the stage is even, else `STAGE`
(`reflection_hierarchy.py:219-244`).

Worked precedence table (cycle 1):

| Week | Closes | Due | Key |
| --- | --- | --- | --- |
| 2 | nothing | `week` | `c1:w2` |
| 3 | stage 1 (odd) | `stage` | `c1:s1` |
| 6 | stage 2 (even → component 1) | `component` | `c1:p1` |
| 18 | stage 6 (tier-one cap) | `tier` | `c1:t1` |
| 36 | everything | `program` | `c1:prog` |

## `scope_weeks(level, key) -> range`

The inclusive program-week span a reflection covers, as
`range(start, end+1)`; the `level` argument must agree with the key's
token "so callers cannot silently scope the wrong span"
(`reflection_hierarchy.py:314-325`). Spans: week `w5` → weeks 5..5;
stage `s9` → 25..30; component `p1` → 1..6; tier `t2` → 19..36; `prog`
→ 1..36 (`reflection_hierarchy.py:177-200,301-311`).

## `resolve_sources(level, key, existing, entries) -> list[SourceItem]`

"What raw material feeds this reflection?" — a top-down walk: an
existing child reflection stands in for its whole span; otherwise recurse
(program → tiers → components → stage pairs → weeks); a `WEEK` bottoms
out in its own weekly reflection or that week's raw daily entries sorted
by `(date, id)` (`reflection_hierarchy.py:341-447`). The uniformity
argument (`reflection_hierarchy.py:29-34`): a stage's *final* week can
never carry its own weekly reflection — that day resolved to the STAGE
(or higher) layer instead — so the final week "simply recurses to its
dailies like any other gap" and no boundary special-casing is needed;
ascending child order yields chronological output with each reflection
ahead of the raw entries it summarizes. Reflections match by full
`c{cycle}:` key; entries carry no cycle, so the caller must pass only
this cycle's entries (`reflection_hierarchy.py:437-440`).

Example: resolving `c1:p1` (component 1, weeks 1-6) where `c1:s1`
exists but stage 2 has no reflections and weeks 4-6 have only dailies →
`[reflection(c1:s1)] + entries(week 4) + entries(week 5) + entries(week 6)`.

## Consumers

The journal reflections endpoints persist due reflections as
`JournalEntry` rows tagged `hierarchical_reflection` with the
`(reflection_level, reflection_scope_key)` pair and a per-(user, scope)
live-row uniqueness — see [api/reflections](../api/reflections.md) and
[data-model/journal-reflection](../data-model/journal-reflection.md).
`models/journal_entry.py` derives its `reflection_level` CHECK from this
module's `ReflectionLevel` (`backend/src/models/journal_entry.py:92-98`).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
