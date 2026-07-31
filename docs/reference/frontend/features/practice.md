# Practice

`frontend/src/features/Practice/` — the practice ramp: a full-bleed dark
"player" tab, a catalog, a creation wizard, per-mode ritual engines, recipes,
tags, and share links. Second-largest module (77 non-test files).

## Screens

| Screen | Route | Responsibility |
| --- | --- | --- |
| `PracticeScreen` | `Practice` tab | "the full-bleed dark 'player'" — one deep-umber `showcase.canvas` card: `Practice \| Catalog` switcher, centered session, weekly-progress footer; the Catalog tab embeds the shared list in place, and the switcher hides while a session runs (`PracticeScreen.tsx:1-27`) |
| `PracticeCatalogScreen` | `Catalog` | stage catalog over `PracticeCatalogList` (with `includeMine` drafts section) |
| `PracticeDetailScreen` | `PracticeDetail` | one practice's detail + assignment (`assignError` param surfaces a failed assign, `RootStack.tsx:39`) |
| `CreatePracticeWizard` | `CreatePractice` | authoring flow for custom practices (custom-practices-07); accepts a `prefill` config (`RootStack.tsx:23-30,40`) |
| `SharePreviewScreen` | `SharePreview` | recipient landing for `adepthood://practices/share/<token>` — preview + import, then forwards back into the Practice tab (`RootStack.tsx:38,82-93`) |

## Composition of the player

Stated layering (`PracticeScreen.tsx:13-24`): `useActivePractice` resolves
the active practice + effective config from the stage catalogue and
per-user overrides; `useWeeklyProgress` reads
`practice-sessions/insights` with a fallback to the legacy `week-count`
route; `ActiveRitualSession` owns the engine, mode dispatch, configurator
sheet, and the ritual-12 insight capture modal; `PracticeIdentityHeader`
pins identity and collapses while a session runs. The screen re-fetches the
active practice on tab refocus (silently, skipping first focus) so a
selection made in the catalog is live on return
(`PracticeScreen.tsx:89-100`).

## The ritual engine

`engine/types.ts` mirrors the backend `ModeConfig` Pydantic discriminated
union (ritual-01, `engine/types.ts:1-2`). Eleven modes are implemented —
each with a config form under `configurator/forms/` and a session view under
`views/`:

`meditation_timer`, `count_up`, `metronome`, `interval_bell`,
`random_interval_bell`, `rep_counter`, `sense_grounding`,
`tallied_grounding`, `tarot`, `card_meditation`, `mindful_anchor`
(config shapes at `engine/types.ts:16-80` and onward; view files
`views/*View.tsx`; forms `configurator/forms/*Form.tsx`).

Engine internals: `useRitualEngine` + a pure `reducer.ts` over
`EngineStatus = 'idle' | 'running' | 'paused' | 'complete'`
(`engine/types.ts:4`), cue scheduling in `cues.ts` with audio/haptics
adapters (`engine/adapters/`), config validation in `validation.ts`, and
`harvestMetadata.ts` producing the per-mode `SessionMetadata` the session
POST carries — whose discriminator must match the practice mode or the
server rejects with `400 mode_metadata_mismatch`
(`frontend/src/api/index.ts:2067-2073`).

Session logging sends wall-clock `started_at`/`ended_at`; the server derives
duration "so a backgrounded `setInterval` can't under-report and a tampered
client can't inflate" (`frontend/src/api/index.ts:2162-2176`).

## Recipes, tags, data, sharing

- `recipes/` — `RecipePickerModal` / `RecipeEditorModal` / `TagPicker` over
  the `practiceRecipes` + `practiceTags` namespaces; applying a recipe
  materialises it into the user practice's `mode_config_override`
  (`frontend/src/api/index.ts:2459-2470`).
- `data/` — tarot/card-deck catalogs (`decks/rws.ts`, `tarot.ts`,
  `resolveCard.ts`, `groundingCatalog.ts`, `colorPalette.ts` — the
  black/white-on-fill decision `readableGlyphOn` generalises).
- `ShareSheet` + the `practiceShare` namespace mint/revoke share links
  (issue #348); `SharePreviewScreen` imports into the recipient's catalog
  as a private draft.
- `useRecentPractices` snapshots display fields into
  `recentPracticesStorage` (max 6) so "Recently used" renders across
  stages (`frontend/src/storage/recentPracticesStorage.ts:1-13`).
- `useFrequency` renders the server-assembled `banner_text` verbatim —
  never client-assembled copy (ritual-05,
  `frontend/src/api/index.ts:2473-2490`).

## Stores and API

Stores: `useStageStore` (+ `stageService` from the Map module for stage
data), `useProgramStore` / `useDerivedCurrentStage`,
`useDepthPreferencesStore`. API: `practices`, `userPractices`,
`practiceSessions`, `practiceTags`, `practiceRecipes`, `frequency`,
`practiceShare`.

*Grounded in adepthood@55eef11, 2026-07-31.*
