# Feature modules

`frontend/src/features/` contains **10 modules** (enumerated from the
directory listing at the commit in the footer). One page per module; each
records its screens, key components and hooks, the stores and API namespaces
it touches, and notable behavior implemented in code.

| Module | Surface | Stores touched | API namespaces touched |
| --- | --- | --- | --- |
| [Auth](auth.md) | 7 screens on the AuthStack + the ReauthSheet overlay | `useWelcomeStore` | `auth` |
| [Course](course.md) | Course tab | `useDepthPreferencesStore`, `useProgramStore` | `course`, `stages` |
| [Habits](habits.md) | Habits tab | `useHabitStore`, `useProgramStore`, `useDepthPreferencesStore` | `habits`, `goalCompletions`, `goals`, `goalGroups`, `uiFlags` |
| [Invitations](invitations.md) | `InvitationStack` band on the Journal shelf | — | `invitations` |
| [Journal](journal.md) | Journal tab (shelf) + `JournalEntry` / `JournalPhotograph` stack routes | `useContractionSignalStore`, `useHabitStore`, `useProgramStore`, `useDepthPreferencesStore`, derived program hooks | `journal`, `prompts`, `promotions`, `reflections`, `resonance`, `completionSuggestions`, `stages` |
| [Map](map.md) | Map tab | `useStageStore`, `useDepthPreferencesStore`, derived program hooks | `stages`, `wheel` (via `useWheelBalance`) |
| [Practice](practice.md) | Practice tab + `Catalog` / `PracticeDetail` / `CreatePractice` / `SharePreview` stack routes | `useStageStore`, `useProgramStore`, `useDepthPreferencesStore`, derived program hooks | `practices`, `userPractices`, `practiceSessions`, `practiceTags`, `practiceRecipes`, `frequency`, `practiceShare` |
| [Return](return.md) | `ReturnStack` band on the Journal shelf | `useContractionSignalStore` | `mettaReturn`, `habits` |
| [Settings](settings.md) | `Settings` hub + 3 sub-screens on the RootStack | `useDepthPreferencesStore` | `users` |
| [Welcome](welcome.md) | First-run editorial intro above the shell | `useWelcomeStore` (via `useFirstRun` in App.tsx) | — |

The stores/API columns were enumerated by grepping each module's non-test
imports of `@/api` and `store/use*`. Note the Today tab named in older docs
does not exist in source; the Journal shelf is the home surface
(`frontend/src/navigation/BottomTabs.tsx:81,209`).

*Grounded in adepthood@55eef11, 2026-07-31.*
