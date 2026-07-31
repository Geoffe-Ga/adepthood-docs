# domain/practice_modes — the engine-mode discriminator

`backend/src/domain/practice_modes.py` (32 lines). A practice's *mode*
selects which engine drives the session and which config fields the
catalog row carries. The enum values are the wire format — stored as
plain strings in `practice.mode` and emitted verbatim in API responses so
the frontend can branch on them without a translation table
(`practice_modes.py:1-8`).

The closed enumeration (`backend/src/domain/practice_modes.py:15-28`),
all 11 modes:

```python
class PracticeMode(StrEnum):
    """Closed enumeration of ritual modes supported by the engine."""

    MEDITATION_TIMER = "meditation_timer"
    COUNT_UP = "count_up"
    METRONOME = "metronome"
    INTERVAL_BELL = "interval_bell"
    REP_COUNTER = "rep_counter"
    SENSE_GROUNDING = "sense_grounding"
    TAROT = "tarot"
    TALLIED_GROUNDING = "tallied_grounding"
    MINDFUL_ANCHOR = "mindful_anchor"
    CARD_MEDITATION = "card_meditation"
    RANDOM_INTERVAL_BELL = "random_interval_bell"
```

`ALL_MODES` is the ordered tuple of wire values "suitable for CHECK
constraints and docs" (`practice_modes.py:31-32`). Consumers:

- `models/practice.py` generates `ck_practice_mode_valid` from
  `ALL_MODES` so the DB set cannot drift
  (`backend/src/models/practice.py:9-17`).
- `models/practice_recipe.py` restricts recipes to the
  `sense_grounding` / `tallied_grounding` subset (`RECIPE_MODES`,
  `backend/src/models/practice_recipe.py:49-52`).
- `schemas/practice_mode_config.py` keys its discriminated-union config
  validation on the same values (referenced from
  `backend/src/models/practice.py:53-56`).
- `models/practice_session.py` denormalizes the resolved mode into each
  session row (`backend/src/models/practice_session.py:43-47`).

Per-mode default config payloads are defined in the practice seed data —
see [infrastructure](../infrastructure.md#seeding) — and per-mode
metadata schemas in `backend/src/schemas/practice_session_metadata.py`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
