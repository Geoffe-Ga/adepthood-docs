# Habits

`frontend/src/features/Habits/` — the habit-scaffolding ring: tiles, goals
in three tiers (low / clear / stretch), check-ins with offline replay, and
stats.

## Screen and layering

`HabitsScreen` (`Habits` tab) renders the paged tile grid
(`HABITS_PER_PAGE = MAX_HABITS`, 1-up on mobile / 2×5 landscape) with a
mode bar (Stats / Edit / Quick Log) and a drawer
(`HabitsScreen.tsx:45-81`). The module is deliberately layered:

- **`useHabits`** is composition-only: store reads + UI state + delegated
  actions, "deliberately contains no business logic"
  (`hooks/useHabits.ts:31-65`).
- **`services/habitManager.ts`** is the service layer — "a plain object
  with async methods that mutate the Zustand `useHabitStore`, persist to
  AsyncStorage, and sync with the backend", hook-free so it unit-tests in
  isolation (`habitManager.ts:1-8`). It imports the `habits`,
  `goalCompletions`, `goalGroups`, and `goals` API namespaces plus
  `toLocalHabit` (`habitManager.ts:13-19`).
- **`useHabitStore`** holds normalized state only (see
  [State](../state.md)).

## Notable behavior

- **Bootstrap runs twice on purpose**: once with the UTC default and again
  when the auth-hydrated timezone lands, because day buckets and queued
  check-in replay days both depend on the zone (#269,
  `hooks/useHabits.ts:13-19`).
- **Offline resilience**: pending check-ins queue in
  `@adepthood/pending_checkins` under a serialized write lane and replay
  with partial-success handling (`frontend/src/storage/habitStorage.ts:48-104`);
  when the server is unreachable and no cache exists, a demo seed renders
  with tiles revealed "so the offline experience is explorable rather than
  a wall of locked tiles" (`habitManager.ts:54-60`).
- **Notifications**: `useHabitNotifications` registers for push and
  reconciles per-habit scheduled notification ids (AbortController-guarded
  on unmount, `hooks/useHabits.ts:20-28`), persisted via
  `notificationStorage`.
- **Tiers and stars**: goal tiers render via `TierMarkerOverlay`,
  `TierStar`, `starFill.ts`/`useStarFill`, and `goalMarker.ts`; gestures in
  `markerGesture.ts` / `longPressGestureStyle.ts`.
- **Modals** are coordinated by `useModalCoordinator`; the set is
  `AddHabitModal`, `GoalModal`, `HabitSettingsModal`, `StatsModal`,
  `MissedDaysModal`, `OnboardingModal`, `ReorderHabitsModal`,
  `HabitEmojiPicker`, `ConfirmDialog`, plus `HabitsDrawer` /
  `HabitsEmptyState`. Missed-day computation is gated on modal-open because
  it scans every completion (`HabitsScreen.tsx:92-100`).
- **Pagination bar visibility** persists globally via
  `paginationVisibilityStorage` through `usePaginationBarVisibility`.
- **Energy scaffolding**: `EnergyCostReturnEditor` / `EnergyTextInput` and
  `parseEnergyValue` edit per-habit energy cost/return; the archived flag
  is device-scoped storage (`frontend/src/storage/energyScaffoldingStorage.ts:7`).

## Stores and API

Stores: `useHabitStore`, `useProgramStore` (stage-at-index for paging),
`useDepthPreferencesStore`. API: `habits`, `goalCompletions`, `goals`,
`goalGroups`, `uiFlags`. Check-ins use deterministic idempotency keys so a
mid-tap network blip can't double-log
(`frontend/src/api/index.ts:1133-1156`).

*Grounded in adepthood@55eef11, 2026-07-31.*
