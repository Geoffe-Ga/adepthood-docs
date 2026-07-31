# domain/depth_preferences — race-safe preference provisioning

`backend/src/domain/depth_preferences.py` (46 lines). Provisioning and
reading the per-user `UserDepthPreferences` row (see
[data-model](../data-model/preferences-invitations.md)).

## `ensure_depth_preferences(session, user_id) -> UserDepthPreferences`

Returns the user's depth preferences, provisioning an **all-true** row on
first access — a fresh user starts fully opted-in to every ring, per the
model defaults (`backend/src/models/user_depth_preferences.py:11-15`).

The implementation (`backend/src/domain/depth_preferences.py:22-46`) is
byte-for-byte the same race-safe SAVEPOINT pattern as
[ui-flags](ui-flags.md), with the docstring noting it "Mirrors
`ensure_user_progress` in `stage_progress.py`"
(`depth_preferences.py:28-29`):

1. Read the row by `user_id`; return if present
   (`depth_preferences.py:31-33`).
2. Insert `UserDepthPreferences(user_id=user_id)` inside
   `session.begin_nested()`, then `commit()` and `refresh()`
   (`depth_preferences.py:34-39`).
3. On `IntegrityError` (the `user_id` unique constraint,
   `backend/src/models/user_depth_preferences.py:50`), re-read and return
   the winner's committed row; raise `RuntimeError` if the winner's row
   is inexplicably missing (`depth_preferences.py:40-45`).

Why commit inside a helper: `get_session` does not auto-commit, and a
concurrent loser must be able to observe the winner's row — an uncommitted
insert would leave the loser's re-read empty
(`depth_preferences.py:25-27`).

Consumed by [api/depth-preferences](../api/depth-preferences.md), which
reads and updates the four `enable_*` toggles.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
