# Backend domain logic

One page per module in `backend/src/domain/`. **Covers all 28 domain
modules** (29 files minus `__init__.py`, which only sets the package
docstring), enumerated from the directory listing — none sampled.

| Page | Module | Concern |
| --- | --- | --- |
| [constants](constants.md) | `constants.py` | Curriculum shape: `TOTAL_STAGES`, `STAGE_DURATIONS_DAYS` |
| [care](care.md) | `care.py` | Care surface + the medication guardrail |
| [contraction](contraction.md) | `contraction.py` | Naming a natural ebb; ease-off vs Return offer |
| [course](course.md) | `course.py` | Content drip-feed gating |
| [creek-vault](creek-vault.md) | `creek_vault.py` | Vault seam: capabilities, tiers, graceful degradation |
| [dates](dates.md) | `dates.py` | User-local day math (the timezone bug family's fix) |
| [depth-preferences](depth-preferences.md) | `depth_preferences.py` | Race-safe preference provisioning |
| [detection](detection.md) | `detection.py` | Completion detection over journal entries |
| [energy](energy.md) | `energy.py` | 21-day energy plan generation |
| [entitlements](entitlements.md) | `entitlements.py` | Gumroad classification + course access |
| [habit-stats](habit-stats.md) | `habit_stats.py` | Habit stats rollup (additive & subtractive) |
| [invitations](invitations.md) | `invitations.py` | Readiness signals for resonant invitations |
| [marginalia-anchoring](marginalia-anchoring.md) | `marginalia_anchoring.py` | Re-anchoring notes after edits |
| [metta-return](metta-return.md) | `metta_return.py` | The five-week Return arc |
| [practice-insights](practice-insights.md) | `practice_insights.py` | Practice insights rollup |
| [practice-modes](practice-modes.md) | `practice_modes.py` | The 11-mode engine discriminator |
| [practice-resolution](practice-resolution.md) | `practice_resolution.py` | Effective name/config from catalog + override |
| [program-calendar](program-calendar.md) | `program_calendar.py` | The date-derived program clock |
| [reflection-hierarchy](reflection-hierarchy.md) | `reflection_hierarchy.py` | Nested reflection calendar + source resolution |
| [resonance](resonance.md) | `resonance.py` | Anchored margin notes from an LLM |
| [safety](safety.md) | `safety.py` | Acute-distress screening |
| [stage-progress](stage-progress.md) | `stage_progress.py` | Progress %, unlocking, history |
| [streaks](streaks.md) | `streaks.py` | Additive & subtractive streak math |
| [timezone](timezone.md) | `timezone.py` | IANA timezone validation at trust boundaries |
| [transcription](transcription.md) | `transcription.py` | Journal Photographer prompt |
| [ui-flags](ui-flags.md) | `ui_flags.py` | Race-safe UI-flag provisioning |
| [weekly-prompts](weekly-prompts.md) | `weekly_prompts.py` | The 36 weekly prompts + titles |
| [wheel](wheel.md) | `wheel.py` | Wheel of Wholeness balance |

## Layer conventions

- **Purity as a design rule.** Most modules are pure functions over value
  objects — no DB, no clock, no network (`contraction.py:17-21`,
  `invitations.py:24-28`, `safety.py:69`, `resonance.py:1-7`,
  `reflection_hierarchy.py:13-14`). Where DB access is needed
  (`stage_progress`, `wheel`, `ui_flags`, `depth_preferences`,
  `entitlements`), queries are deliberately batched and the
  provisioning helpers share one race-safe SAVEPOINT pattern.
- **LLM trust model.** Modules that consume model output (`resonance`,
  `detection`) never trust model-supplied ids or offsets: the server
  anchors verbatim quotes itself and drops anything that does not
  resolve (`resonance.py:1-7`, `detection.py:6-11`). Every LLM prompt
  leads with the shared `MEDICATION_GUARDRAIL` (`care.py:109-122`).
- **DB-import-free vocabularies.** Domain modules re-declare enum value
  sets as literals (`resonance.VALID_KINDS`,
  `detection.VALID_TARGET_TYPES`,
  `creek_vault.TIER_CEILING_BY_CLASSIFICATION`) with drift-guard tests
  asserting they match the model enums.
- **The product ethic is encoded.** `contraction`, `invitations`,
  `metta_return`, and `wheel` all state — in code comments that this
  reference quotes — that they never shame, rank, or gamify; silence is
  the default and thresholds are deliberately conservative
  (ADR [0006 — graduated engagement](../../../decisions/0006-graduated-engagement.md)).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
