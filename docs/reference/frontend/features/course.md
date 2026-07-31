# Course

`frontend/src/features/Course/` — the course-reading ring: stage-gated
content lists, an in-app chapter reader, stage intros, and the
always-available Site Resources.

## Screen

`CourseScreen` (`Course` tab) composes `StageSelector`, `StageIntroCard`,
`ContentCard` rows in a FlatList, `ContentViewer` / `ChapterReader` for
bodies, `SiteResourcesPanel`, a `CourseDrawer`, and a `Celebration`
(`CourseScreen.tsx:1-49`).

## Notable behavior

- **Stage selection precedence** (`useStagesLoader`,
  `CourseScreen.tsx:53-100`): a route param wins; otherwise the
  date-derived stage from the program anchor
  (`programStage(programAnchor)`), falling back to the server-owned,
  count-based progression — deliberately *not* "max unlocked", which
  "would visually reward skip-ahead attempts whenever `is_unlocked` ran
  ahead of completion" (`CourseScreen.tsx:69-77`).
- **Deep-link follow**: the warm tab stays mounted, so a later Map→Course
  navigation changes only the route param; an effect follows a changed
  non-null `stageNumber` (`CourseScreen.tsx:92-100`). The reader restores
  `contentId` + `scrollOffset` when returning from a "write a note"
  excursion into the Journal (`frontend/src/navigation/BottomTabs.tsx:33-34`,
  `RootStack.tsx:64-68`).
- **Error surfacing**: stage-load failure is tracked explicitly so the
  screen shows error + `RetryButton` instead of an empty course
  (audit-ux-04, `CourseScreen.tsx:78-85`).
- **Reader → Journal**: `ChapterReader` exposes `WriteNotePassage` so a
  selected passage folds into a new `JournalEntry` as a blockquote prefill
  (`CourseScreen.tsx:35`, `RootStack.tsx:62-63`).
- `chapterNav.ts` derives previous/next chapter neighbors;
  `stageDisplay.ts` and `stripLeadingTitleHeading.ts` normalize display;
  stage colors resolve through the shared `resolveStageColor`
  (`CourseScreen.tsx:28`).

## Stores and API

Stores: `useProgramStore` (+ `programStage`), `useDepthPreferencesStore`
(ring visibility). API: `course` (all 8 wrappers) and `stages.listAll`
(`CourseScreen.tsx:7-14,67`). The domain helper `deriveCurrentStage` comes
from `frontend/src/domain/stageProgression.ts` (`CourseScreen.tsx:29`).

*Grounded in adepthood@55eef11, 2026-07-31.*
