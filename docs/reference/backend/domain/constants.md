# domain/constants — curriculum-shape constants

`backend/src/domain/constants.py` (26 lines). Shared domain constants
with **no further domain imports** — split from `domain.stage_progress`
so Pydantic schemas can pull the curriculum length without triggering a
`schemas <-> domain` import cycle (`constants.py:1-5`).

| Constant | Value | Meaning |
| --- | --- | --- |
| `TOTAL_STAGES` | `10` | Stages in the APTITUDE curriculum, matching the rows seeded by `seed_stages` (stages 1..10). Router-level stage mutations clamp inputs to this range; re-exported by `domain.stage_progress` and aliased `MAX_STAGE_NUMBER` by schemas (`constants.py:9-16`) |
| `STAGE_DURATIONS_DAYS` | `(21, 21, 21, 21, 21, 21, 21, 21, 42, 42)` | Days each stage lasts — eight 3-week stages, then two 6-week integration stages (`constants.py:18-23`) |
| `TOTAL_PROGRAM_DAYS` | `sum(...)` = 252 | Exactly the 36-week curriculum (`constants.py:25-26`) |

Two decisions are encoded here:

- Issue #386 fixed `TOTAL_STAGES`: "the previous value, 36, conflated the
  36-week calendar with the 10-stage curriculum" (`constants.py:14-15`).
- `STAGE_DURATIONS_DAYS` is a **cross-stack contract**
  (`backend/src/domain/constants.py:19-22`):

```python
# two 6-week integration stages.  CROSS-STACK CONTRACT (issue #386): this
# tuple mirrors ``STAGE_DURATIONS_DAYS`` in
# ``frontend/src/constants/program.ts`` literal-for-literal; both stacks
# pin it with tests, so a schedule change must touch both files together.
```

Consumers: [program-calendar](program-calendar.md) derives every
stage/week boundary from these; `models/journal_entry.py` derives Aspect
CHECK ranges from `TOTAL_STAGES`
(`backend/src/models/journal_entry.py:110-118`).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
