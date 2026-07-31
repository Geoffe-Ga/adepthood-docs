# domain/wheel — the Wheel of Wholeness balance view

`backend/src/domain/wheel.py` (141 lines). Per-Aspect *fullness*: for
each of the ten stages, how engaged the user is (habits, practice,
course), blended with a capped chord-tag signal from journal tagging.
Items are always returned in canonical stage order 1..10, "never sorted
by fullness, so the frontend can lay them out on a fixed wheel"
(`wheel.py:1-7`) — balance, never altitude.

## Constants (`wheel.py:37-43`)

| Constant | Value | Meaning |
| --- | --- | --- |
| `WHEEL_PRIMARY_TAG_WEIGHT` | `1.0` | Weight of a primary Aspect tag |
| `WHEEL_SECONDARY_TAG_WEIGHT` | `0.5` | Weight of a secondary tag |
| `WHEEL_CHORD_SIGNAL_CAP` | `0.2` | Max fullness lift chord tags can add |
| `WHEEL_CHORD_SATURATION_TAGS` | `10.0` | Weighted count at which the cap is reached |

## The formula (`wheel.py:9-20,102-104`)

```text
weighted      = 1.0 * n_primary + 0.5 * n_secondary          (per stage)
chord_signal  = 0.2 * min(weighted / 10.0, 1.0)
fullness      = min(overall_progress + chord_signal, 1.0)
```

Only non-deleted entries count, across **all** classifications — "the
wheel is the user's own private aggregate". With no tagged entries
`chord_signal` is exactly `0.0`, so fullness equals `overall_progress`
(`wheel.py:17-20`).

## `compute_wheel_balance(session, user_id) -> list[WheelItem]`

Returns ten `{"stage_number", "aspect", "fullness"}` items
(`WheelItem` TypedDict, `wheel.py:46-51`). Query shape is deliberately
batched — no N+1 (`wheel.py:107-141`):

1. `compute_stage_progress_batch` supplies `overall_progress` for all ten
   stages in one batched pass (`wheel.py:126-127`; see
   [stage-progress](stage-progress.md)).
2. One query fetches `{stage_number: aspect}` labels from `CourseStage`
   (`_aspect_labels_by_stage`, `wheel.py:54-63`).
3. Two constant grouped-count queries — one per aspect column — count
   non-deleted tagged entries per stage
   (`_aspect_counts` / `_chord_tag_weighted_counts`, `wheel.py:66-99`).

`aspect` falls back to `""` only if a `CourseStage` row is absent for a
stage in 1..10 — "a misconfigured-seed sentinel; the seeder guarantees
all ten" (`wheel.py:123-124`).

## Worked example

Stage 3 has `overall_progress = 0.4`; the user has 6 entries with
`primary_aspect=3` and 4 with `secondary_aspect=3`:
`weighted = 6·1.0 + 4·0.5 = 8.0`;
`chord_signal = 0.2 · min(8/10, 1) = 0.16`;
`fullness = min(0.4 + 0.16, 1.0) = 0.56`. With 20 primary tags instead,
`chord_signal` saturates at `0.2`.

Endpoint: the Map screen's wheel — see [api/stages](../api/stages.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
