# domain/practice_resolution — collapsing catalog + override

`backend/src/domain/practice_resolution.py` (42 lines). Pure helpers that
collapse `(Practice, UserPractice)` into the *effective* values the
frontend reads. Keeping them pure (no DB access) makes them trivially
testable and lets endpoints reuse them without round-tripping through the
ORM (`practice_resolution.py:1-8`).

## `effective_name(practice, user_practice) -> str`

The user's `custom_name` if set (non-empty), else the catalog `name`
(`practice_resolution.py:17-21`).

## `effective_config(practice, user_practice) -> ModeConfig`

The override-resolution rule, verbatim
(`backend/src/domain/practice_resolution.py:24-42`):

```python
def effective_config(practice: Practice, user_practice: UserPractice | None) -> ModeConfig:
    """Return the user's override if set, else the catalog ``mode_config``.

    Validates the resolved payload through :class:`ModeConfigAdapter` so a
    structurally invalid override surfaces as a domain error rather than
    leaking into engine code. Raises ``ValueError("mode_mismatch")`` when
    the override's ``mode`` discriminator doesn't agree with the catalog
    mode — the override may only swap fields *within* a mode.
    """
    payload = (
        user_practice.mode_config_override
        if user_practice is not None and user_practice.mode_config_override is not None
        else practice.mode_config
    )
    cfg = ModeConfigAdapter.validate_python(payload)
    if cfg.mode != practice.mode:
        msg = "mode_mismatch"
        raise ValueError(msg)
    return cfg
```

Rules:

1. Payload selection: `user_practice.mode_config_override` when present,
   else `practice.mode_config`.
2. The payload is validated through the
   `schemas.practice_mode_config.ModeConfigAdapter` discriminated union —
   a structurally invalid override is a domain error, not an engine crash.
3. Cross-mode swaps are refused: `ValueError("mode_mismatch")` when the
   resolved config's `mode` differs from the catalog row's `mode`. This
   enforces the model-layer contract that `mode` itself is not
   overridable (`backend/src/models/user_practice.py:51-53`).

## Worked example

Catalog `Practice(mode="interval_bell", mode_config={...bell fields...})`;
`UserPractice(mode_config_override=None)` → the catalog config, validated.
Same catalog with
`override={"mode": "interval_bell", "interval_seconds": 90}` → the
override wins. `override={"mode": "metronome", ...}` →
`ValueError("mode_mismatch")` (the API layer maps this to a 4xx — see
[api/user-practices](../api/user-practices.md)).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
