# Data model — Metta Return

Models: `MettaReturnArc`, `MettaReturnHabitRelease`,
`MettaReturnOfferDismissal` — the persisted state of the Return, a
declinable five-week Metta rest. The tables encode the never-shaming
contract structurally: nothing here gates or mutates stage progress, and
every action (pause, resume, leave, release, dismiss) is first-class
(`metta_return_arc.py:5-8`, `metta_return_habit_release.py:9-10`). The
rules live in [domain/metta-return](../domain/metta-return.md).

## `MettaReturnArc` (`backend/src/models/metta_return_arc.py`)

Records that a user accepted the five-week Return: when it started,
whether it is currently paused, and when — if ever — the user left it
(`metta_return_arc.py:3-8`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `id` | `int \| None` | primary key | `None` | Arc id (`metta_return_arc.py:51`) |
| `user_id` | `int` | FK `user.id`, `ondelete="CASCADE"`, indexed | — | Arc owner (`metta_return_arc.py:52`) |
| `started_at` | `datetime` | `DateTime(timezone=True)`, not null | — | Acceptance instant (`metta_return_arc.py:53-55`) |
| `paused_at` | `datetime \| None` | nullable | `None` | Set while paused (`metta_return_arc.py:56-59`) |
| `left_at` | `datetime \| None` | nullable | `None` | Set on leaving; frees the active slot (`metta_return_arc.py:60-63`) |

At most one *active* arc (`left_at IS NULL`) per user, enforced by the
partial unique index `ix_metta_return_arc_user_active` on `user_id` WHERE
`left_at IS NULL` — any number of previously-left arcs may accumulate, so
leaving and restarting is always allowed (`metta_return_arc.py:31-49`).
Declared with both `postgresql_where` and `sqlite_where` so the SQLite
test DB gets the same constraint via `metadata.create_all` and
`alembic check` sees no drift (`metta_return_arc.py:21-25,34-37`).
Migration: `c9d0e1f2a3b4_add_metta_return_arc`
(`backend/migrations/versions/`).

## `MettaReturnHabitRelease` (`backend/src/models/metta_return_habit_release.py`)

Remembers that, within one arc, the user chose to *release* a habit — a
soft pause that flips `Habit.revealed` to `False`. Releasing deletes
nothing: goals and logged completions live on the habit's goals, so a
released habit keeps its whole history for when the user re-commits
(`metta_return_habit_release.py:3-9`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `id` | `int \| None` | primary key | `None` | Row id (`metta_return_habit_release.py:45`) |
| `user_id` | `int` | FK `user.id`, `ondelete="CASCADE"` | — | Releasing user (`metta_return_habit_release.py:46`) |
| `arc_id` | `int` | FK `mettareturnarc.id`, `ondelete="CASCADE"`, indexed | — | Scoping arc (`metta_return_habit_release.py:47`) |
| `habit_id` | `int` | FK `habit.id`, `ondelete="CASCADE"` | — | Released habit (`metta_return_habit_release.py:48`) |
| `released_at` | `datetime` | `DateTime(timezone=True)`, not null | — | Release instant (`metta_return_habit_release.py:49-51`) |
| `recommitted_at` | `datetime \| None` | nullable | `None` | `None` while live; stamped on re-commit (`metta_return_habit_release.py:52-55`) |

`UNIQUE (arc_id, habit_id)` (`uq_metta_return_habit_release_arc_habit`,
`metta_return_habit_release.py:36-43`) makes a release idempotent within
its arc while allowing the same habit to be released again in a later
arc; an arc's live releases are exactly the rows with a null
`recommitted_at` (`metta_return_habit_release.py:27-33`).

## `MettaReturnOfferDismissal` (`backend/src/models/metta_return_offer_dismissal.py`)

Records that a user waved away the Return invitation for one specific
offer *episode*. An episode is keyed by the user's current cycle and
stage, so any stage or cycle advance opens a fresh episode whose offer
surfaces again — a past dismissal never silences a future invitation
(`metta_return_offer_dismissal.py:3-7`).

| Field | Type | Constraints / column | Default | Purpose |
| --- | --- | --- | --- | --- |
| `id` | `int \| None` | primary key | `None` | Row id (`metta_return_offer_dismissal.py:39`) |
| `user_id` | `int` | FK `user.id`, `ondelete="CASCADE"`, indexed | — | Dismissing user (`metta_return_offer_dismissal.py:40`) |
| `episode_key` | `str` | not null; unique with `user_id` | — | Cycle+stage episode key (`metta_return_offer_dismissal.py:41`) |
| `dismissed_at` | `datetime` | `DateTime(timezone=True)`, not null | — | Dismissal instant (`metta_return_offer_dismissal.py:42-44`) |

The unique index `ix_metta_return_offer_dismissal_user_episode` on
`(user_id, episode_key)` makes re-dismissing the same episode a no-op
(`metta_return_offer_dismissal.py:29-37`). Migration:
`a7b8c9d0e1f2_add_metta_return_offer_dismissal`
(`backend/migrations/versions/`).

## Related

- [api/metta-return](../api/metta-return.md) — the endpoints
- [domain/metta-return](../domain/metta-return.md) — eligibility,
  episode keys, and the arc timeline math

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
