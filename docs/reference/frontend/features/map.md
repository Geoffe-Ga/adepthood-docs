# Map

`frontend/src/features/Map/` — the stage map: the ten-stage arc rendered
over artwork, per-stage detail (expressions, history), the
wheel-of-wholeness balance overlay, and the declinable "begin again"
end-of-cycle affordance.

## Screen

`MapScreen` (`Map` tab) renders a responsive row grid (one flex row
`[LeftCell | CenterCell | RightCell]` per stage as the single source of
vertical truth), the `WaveOverlay`, a `MagnifierLens`, a `MapDrawer`, a
journey-summary narrative, and a `Celebration` (`MapScreen.tsx:1-100`).
Layout metrics and label fitting live in `mapLayout.ts`; geometry in
`waveGeometry.ts` / `magnifierGeometry.ts`.

## Service layer

`services/stageService.ts` "orchestrates API calls for stages and writes the
result into `useStageStore`", keeping API access out of the pure store
(`stageService.ts:1-8`). Key logic, verbatim where load-bearing:

- `clampProgress` pins backend progress into `[0, 1]`, coercing
  NaN/Infinity/missing to 0 — "without this guard a bad payload renders as
  'NaN%' or overflows the progress bar (width: 110%)"
  (BUG-FE-MAP-003, `stageService.ts:18-28,38-41`).
- `toStageData` maps the wire `Stage` onto `StageData`, resolving the color
  from `STAGE_ORDER`/`STAGE_COLORS` (`stageService.ts:31-54`).
- Unlock semantics unify server flag and calendar:

```ts
export const isStageUnlocked = (
  stage: Pick<StageData, 'isUnlocked' | 'stageNumber'>,
  currentStage: number | null,
): boolean => stage.isUnlocked || (currentStage !== null && stage.stageNumber <= currentStage);
```

  "so the padlock matches the Practice/Course stage"
  (`stageService.ts:56-60`).

- `highestCompletedStage` is the baseline the completion celebration
  watches; `isEndOfCycle` gates the declinable "begin again" affordance
  (`stageService.ts:62-70`).

## Hooks

| Hook | Responsibility |
| --- | --- |
| `useStageAnchors` | measured row anchors for the lens/overlay |
| `useWheelBalance` | loads `wheel.get` (`/stages/wheel`) fullness per Aspect; `wheelBalance.ts` holds the math; absent stages read thin (`MapScreen.tsx:91-93`) |
| `useJourneySummary` | stage history → narrative (`journeyNarrative.ts`: `progressionSentence`, `rankedStats`, `unlockTimeline`) |
| `useBeginAgainGuard` | confirms before `stages.beginAgain` opens a fresh cycle (`beginAgain.ts` copy) |

## Stores and API

Stores: `useStageStore` (six selectors incl. `selectCycleNumber`,
`MapScreen.tsx:25-33`), `useDaysUntilStage` / `useDerivedCurrentStage`
(calendar unlocks), `useDepthPreferencesStore`. API: `stages`
(`listAll`, `history`, `beginAgain`, `programCalendar`) and `wheel`.
Per-stage expression detail renders `manifestations` via
`StageExpressionsSection` (`MapScreen.tsx:73`).

*Grounded in adepthood@55eef11, 2026-07-31.*
