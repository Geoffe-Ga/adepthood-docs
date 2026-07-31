# Data model — depth preferences, UI flags, invitations

Models: `UserDepthPreferences`, `UserUiFlags`, `InvitationSignal` — the
tables that record which self-chosen depths a user has enabled, one-time
interface state, and detected invitations toward deeper rings. Together
they are the data layer of the "you choose your depth" principle
(ADR [0006 — graduated engagement](../../../decisions/0006-graduated-engagement.md)).

## `UserDepthPreferences` (`backend/src/models/user_depth_preferences.py`)

One row per user recording which optional program rings — habit
scaffolding, the practice ramp, the course reading, the Digital Sangha —
the user has enabled. Nothing is gated; the toggles simply quiet rings
the user has not chosen (`user_depth_preferences.py:19-27`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `id` | `int \| None` | primary key | `None` | Row id (`user_depth_preferences.py:29`) |
| `enable_habits` | `bool` | not null, `server_default="1"` | `True` | Habit-scaffolding ring offered (`user_depth_preferences.py:30-34`) |
| `enable_practices` | `bool` | not null, `server_default="1"` | `True` | Practice-ramp ring offered (`user_depth_preferences.py:35-39`) |
| `enable_course` | `bool` | not null, `server_default="1"` | `True` | Course-reading ring offered (`user_depth_preferences.py:40-44`) |
| `enable_sangha` | `bool` | not null, `server_default="1"` | `True` | Digital Sangha ring offered (`user_depth_preferences.py:45-49`) |
| `user_id` | `int` | FK `user.id`, `unique`, `ondelete="CASCADE"` | — | One row per user (`user_depth_preferences.py:50`) |

All flags default to enabled so a fresh user — and every legacy row the
migration backfilled — starts fully opted-in and can decline depths later
(`user_depth_preferences.py:11-15`). Relationship: `user`
back-populates `User.depth_preferences` (`user_depth_preferences.py:51`).

## `UserUiFlags` (`backend/src/models/user_ui_flags.py`)

One row per user of lightweight one-time interface state. Both flags
default to `False`; rows are created on first access rather than
backfilled (`user_ui_flags.py:18-24`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `id` | `int \| None` | primary key | `None` | Row id (`user_ui_flags.py:26`) |
| `has_seen_welcome` | `bool` | not null, `server_default="0"` | `False` | Welcome flow seen (`user_ui_flags.py:27-31`) |
| `energy_scaffolding_archived` | `bool` | not null, `server_default="0"` | `False` | Energy-scaffolding surface archived (`user_ui_flags.py:32-36`) |
| `user_id` | `int` | FK `user.id`, `unique`, `ondelete="CASCADE"` | — | One row per user (`user_ui_flags.py:37`) |

Relationship: `user` back-populates `User.ui_flags`
(`user_ui_flags.py:38`). Migration:
`b4c5d6e7f8a1_add_user_ui_flags` (`backend/migrations/versions/`).

## `InvitationSignal` (`backend/src/models/invitation_signal.py`)

Records that the system observed a resonant moment to *offer* a deeper
depth — never to gate or pressure. Each row pins one
`(user_id, target_type, target_id, kind)` coordinate; a row is created
once and either lives or is dismissed (`invitation_signal.py:1-11`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `id` | `int \| None` | primary key | `None` | Row id (`invitation_signal.py:115`) |
| `user_id` | `int` | FK `user.id`, `ondelete="CASCADE"` | — | Invited user (`invitation_signal.py:116`) |
| `target_type` | `str` | `max_length=32`, CHECK `ck_invitation_signal_target_type_valid` | — | Ring pointed at: `habit`, `practice`, `course`, `sangha`, `embodied_community` (`InvitationTargetType`, `invitation_signal.py:33-40`) |
| `target_id` | `int \| None` | nullable | `None` | Optional concrete target inside the ring (`invitation_signal.py:118`) |
| `kind` | `str` | `max_length=32`, CHECK `ck_invitation_signal_kind_valid` | — | Why the moment qualifies: `readiness`, `consistency`, `mastery` (`InvitationKind`, `invitation_signal.py:43-52`) |
| `created_at` | `datetime` | `DateTime(timezone=True)`, not null | `datetime.now(UTC)` | Detection instant (`invitation_signal.py:120-123`) |
| `dismissed_at` | `datetime \| None` | nullable | `None` | Records a decline (`invitation_signal.py:124-127`) |

The uniqueness contract is the load-bearing piece: it spans *all* rows,
dismissed included, so a declined invitation is never silently recreated
(`invitation_signal.py:8-10`). Because SQL treats two `NULL`s as distinct
in an ordinary UNIQUE, the constraint is split into two partial unique
indexes (`backend/src/models/invitation_signal.py:90-113`):

```python
    __table_args__ = (
        Index(
            "ix_invitation_signal_user_target",
            "user_id",
            "target_type",
            "target_id",
            "kind",
            unique=True,
            postgresql_where=_TARGET_ID_COLUMN.is_not(None),
            sqlite_where=_TARGET_ID_COLUMN.is_not(None),
        ),
        Index(
            "ix_invitation_signal_user_target_null",
            "user_id",
            "target_type",
            "kind",
            unique=True,
            postgresql_where=_TARGET_ID_COLUMN.is_(None),
            sqlite_where=_TARGET_ID_COLUMN.is_(None),
        ),
        Index("ix_invitation_signal_user_id", "user_id"),
        _target_type_check(),
        _kind_check(),
    )
```

Declaring both `postgresql_where` and `sqlite_where` keeps the metadata
aligned with the migration (`alembic check` sees no drift) and installs
the same constraints on the SQLite test DB via `metadata.create_all`
(`invitation_signal.py:82-88`). Both CHECK constraints are generated from
the StrEnums so the stored set cannot drift from Python
(`invitation_signal.py:55-70`). Migration:
`b3c4d5e6f7a8_add_invitation_signal` (`backend/migrations/versions/`).

## Related

- [api/depth-preferences](../api/depth-preferences.md),
  [api/ui-flags](../api/ui-flags.md),
  [api/invitations](../api/invitations.md) — the routers over these tables
- [domain/invitations](../domain/invitations.md) and
  [domain/depth-preferences](../domain/depth-preferences.md) — the rules
  that read/write them

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
