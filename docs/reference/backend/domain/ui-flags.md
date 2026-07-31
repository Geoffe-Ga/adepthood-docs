# domain/ui_flags — race-safe flag provisioning

`backend/src/domain/ui_flags.py` (42 lines). Provisioning and reading the
per-user `UserUiFlags` row (see
[data-model](../data-model/preferences-invitations.md)).

## `ensure_ui_flags(session, user_id) -> UserUiFlags`

Returns the user's UI flags, provisioning an all-false row on first
access. The concurrency handling is the point
(`backend/src/domain/ui_flags.py:18-42`):

```python
async def ensure_ui_flags(session: AsyncSession, user_id: int) -> UserUiFlags:
    """Return the user's UI flags, provisioning an all-false row on first access.

    Commits the new row before returning: a concurrent caller that loses the
    SAVEPOINT race must re-read the winner's committed row, and ``get_session``
    does not auto-commit. Because ``user_id`` is unique, a racing auto-provision
    hits an ``IntegrityError`` and re-reads the winner's row. Mirrors
    ``ensure_depth_preferences`` in ``depth_preferences.py``.
    """
    flags = await _get_ui_flags(session, user_id)
    if flags is not None:
        return flags
    flags = UserUiFlags(user_id=user_id)
    try:
        async with session.begin_nested():
            session.add(flags)
        await session.commit()
        await session.refresh(flags)
    except IntegrityError as exc:
        existing = await _get_ui_flags(session, user_id)
        if existing is None:
            msg = "UserUiFlags creation lost the race but the winner's row is missing"
            raise RuntimeError(msg) from exc
        return existing
    return flags
```

The pattern, step by step:

1. Read; if a row exists, return it (`ui_flags.py:27-29`).
2. Otherwise insert inside a SAVEPOINT (`begin_nested`) and **commit**
   before returning — `get_session` does not auto-commit, and the loser
   of a race must be able to re-read the winner's *committed* row
   (`ui_flags.py:30-35`).
3. The `user_id` unique constraint
   (`backend/src/models/user_ui_flags.py:37`) turns the race into an
   `IntegrityError`; the loser re-reads and returns the winner's row
   (`ui_flags.py:36-41`).
4. If the re-read finds nothing, that is an invariant violation and a
   `RuntimeError` — the code refuses to guess (`ui_flags.py:38-40`).

The identical pattern appears in
[depth-preferences](depth-preferences.md) and `ensure_user_progress` in
[stage-progress](stage-progress.md); consumed by
[api/ui-flags](../api/ui-flags.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
