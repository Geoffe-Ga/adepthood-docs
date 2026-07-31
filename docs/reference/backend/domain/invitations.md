# domain/invitations — readiness-signal computation

`backend/src/domain/invitations.py` (185 lines). Pure computation of
*invitation coordinates*: given a snapshot of cross-feature engagement
(habit streaks, sustained practice weeks, active days in a rolling
window) plus optional Creek Vault corpus-theme readings, decide which
deeper depths the moment invites the user to *consider*. A later
persistence pass turns the coordinates into `InvitationSignal` rows
(`invitations.py:1-8`).

Ethics, stated in code (`backend/src/domain/invitations.py:17-22`):

```text
This module encodes NO shaming and NO FOMO: it never counts what the user
*failed* to do, never compares them to anyone, and stays silent by default.
An absent signal is the norm, not a deficiency. The thresholds below are
deliberately conservative so an invitation only appears once a rhythm is
genuinely established — the "you choose your depth" principle honoured before a
single row is written.
```

Pure by design: no session, no I/O, no clock (`invitations.py:24-28`).

## Thresholds

| Constant | Value | Rationale |
| --- | --- | --- |
| `SUSTAINED_HABIT_STREAK_DAYS` | `21` | "Three unbroken weeks … an integrated habit rather than a burst of early enthusiasm" (`invitations.py:36-39`) |
| `SUSTAINED_PRACTICE_WEEKS` | `4` | Four consecutive weeks meeting the ≥4-sessions/week cadence = "depth already reached" (`invitations.py:41-44`) |
| `HIGH_ENGAGEMENT_ACTIVE_DAYS` | `25` | Active 25 of the last 30 days before the embodied-community invitation — "never a nudge to do more" (`invitations.py:46-49`) |
| `ENGAGEMENT_WINDOW_DAYS` | `30` | The rolling window (`invitations.py:51-54`) |
| `CORPUS_THEME_FULLNESS_THRESHOLD` | `0.75` | A corpus theme this full is "a genuinely lived Aspect, not a passing mention" (`invitations.py:56-59`) |

Target/kind strings are referenced from the model enums' *values* (not
literals) "so the candidate coordinates can never drift from the
persisted vocabulary — the drift-guard test asserts exactly this
coupling" (`invitations.py:61-70`).

## Inputs and output

`ReadinessAggregates(habits: list[HabitSignal], practices:
list[PracticeSignal], active_days_in_window: int, corpus_themes:
list[CorpusThemeSignal] = [])` — `corpus_themes` was appended last with a
default "so every existing positional construction (behavioral-only)
stays valid" (`invitations.py:110-122`). Output:
`InvitationCandidate(target_type, target_id, kind)`; `target_id` is
`None` for ring-level invitations (`invitations.py:73-83`).

## `compute_invitation_candidates(aggregates)`

Each source contributes independently (`invitations.py:169-185`):

| Source | Rule | Emitted candidate |
| --- | --- | --- |
| Habits | each habit with `streak_days >= 21` | `(habit, habit_id, consistency)` (`invitations.py:125-131`) |
| Practices | each practice with `sustained_weeks >= 4` | `(practice, practice_id, mastery)` (`invitations.py:134-140`) |
| Engagement | `active_days_in_window >= 25` | at most one `(embodied_community, None, readiness)` (`invitations.py:143-149`) |
| Corpus themes | filter to `fullness >= 0.75`; strongest wins — highest fullness, lowest `stage_number` breaking ties | at most one `(course, stage_number, readiness)` (`invitations.py:152-166`) |

## Worked example

`habits=[(id=1, streak=25), (id=2, streak=20)]`,
`practices=[(id=7, weeks=4)]`, `active_days=26`,
`corpus_themes=[(stage=3, 0.8), (stage=6, 0.8), (stage=2, 0.5)]` →
four candidates: `(habit, 1, consistency)`, `(practice, 7, mastery)`,
`(embodied_community, None, readiness)`, and `(course, 3, readiness)` —
stage 3 beats stage 6 on the tie-break. Habit 2 (20 < 21) and stage 2
(0.5 < 0.75) stay silent.

Persistence dedupe (a declined invitation is never recreated) is
DB-level — see
[data-model/preferences-invitations](../data-model/preferences-invitations.md);
endpoints in [api/invitations](../api/invitations.md); the vault reading
in [creek-vault](creek-vault.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
