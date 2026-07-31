# domain/contraction — naming a natural ebb

`backend/src/domain/contraction.py` (177 lines). Pure contraction
detection: given a snapshot of how a user's habit *foundation* behaved
over a recent window, decide whether the moment warrants a warm,
declinable Higher Self reflection that names a contraction — and, for
someone who has travelled far, offers the optional five-week Return
(`contraction.py:1-6`).

The module's ethics are explicit
(`backend/src/domain/contraction.py:8-15`):

```text
This module encodes NO shaming and NO gamification. It never counts a "broken
streak", never compares the user to anyone, never demotes, and stays silent by
default. An absent signal is the expected, healthy case — not a deficiency. A
contraction is framed exactly as the product philosophy frames it: *Contraction
follows Expansion; it is ok to need a break from progress.*
```

Pure by design — no session, no I/O, no clock; the caller gathers
aggregates and hands them in (`contraction.py:17-21`).

## Thresholds

| Constant | Value | Meaning |
| --- | --- | --- |
| `FOUNDATION_UNMET_CONSECUTIVE_DAYS` | `14` | Consecutive days a scheduled goal is *logged-but-unmet* (checked in at zero units) before naming — "long enough that this reads as a genuine season, not a bad day or a busy week" (`contraction.py:30-35`) |
| `FOUNDATION_UNCHECKED_CONSECUTIVE_DAYS` | `14` | Consecutive days entirely *unchecked*; held equal so "silence and zero-effort days are treated with the same patience" (`contraction.py:37-41`) |
| `RETURN_MIN_HIGHEST_STAGE` | `RETURN_MINIMUM_STAGE` (= 5, sourced from `domain.metta_return`) | Highest stage reached before the Return variant is offered — one canonical constant, never re-declared (`contraction.py:43-49`) |

## Types

`HabitFoundationSignal(habit_id, consecutive_unmet_days,
consecutive_unchecked_days)`; `ContractionAggregates(habits: tuple)` — a
tuple, not a list, so the value object is "immutable by content, not just
by attribute binding" (`contraction.py:104-114`);
`ContractionSignal(flagged_habit_ids)`;
`ContractionInvitation(variant, message)` with
`ContractionVariant` ∈ {`simple_ease_off`, `return_offer`}
(`contraction.py:77-135`).

## `detect_contraction(aggregates) -> ContractionSignal | None`

Silent by default. A single habit crossing **either** window flags —
"a thinning foundation is worth naming even when only one thread has
gone quiet. The boundary is exact — one day short of a window never
flags" (`contraction.py:146-157`). `_habit_crosses_window` is a `>=`
test on either counter (`contraction.py:138-143`).

## `build_contraction_invitation(highest_stage_reached) -> ContractionInvitation`

Precondition: a contraction was already detected — the copy depends only
on furthest reach, so the signal is not an input (`contraction.py:160-167`).
`highest_stage_reached >= 5` → `RETURN_OFFER` with the Return message;
otherwise `SIMPLE_EASE_OFF` (`contraction.py:169-177`). The ease-off copy
"deliberately avoids the word 'return' so the five-week Return remains
the higher-stage variant's distinct offer" (`contraction.py:51-55`); both
messages hand back agency and promise nothing is lost
(`contraction.py:56-74`).

## Worked example

Habits A (`unmet=14, unchecked=0`) and B (`unmet=3, unchecked=13`):
A crosses the unmet window, B crosses nothing →
`ContractionSignal(flagged_habit_ids=(A,))`. With
`highest_stage_reached=4` → `SIMPLE_EASE_OFF`; with `5` → `RETURN_OFFER`.
Both counters at 13 → `None` (exact boundary).

Related: [metta-return](metta-return.md) (the Return itself),
[stage-progress](stage-progress.md) (`highest_stage_reached`'s
monotonicity).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
