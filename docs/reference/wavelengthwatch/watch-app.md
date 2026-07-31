# WavelengthWatch — watch app

The watchOS SwiftUI application under
`frontend/WavelengthWatch/WavelengthWatch Watch App/`. This page enumerates
its screens and explains the navigation model; the offline journaling and
sync machinery is covered in
[Offline sync and flows](offline-sync-and-flows.md).

## Composition root

`ContentView` is deliberately a "thin shell that names the app's root view.
All composition lives in `RootShellView`; ObservableObject dependencies are
read from the environment (injected at the App layer in
`WavelengthWatchApp`)" (`ContentView.swift:3-17`). The live object graph —
`ContentViewModel`, `FlowCoordinator`, `SyncSettingsViewModel`,
`NetworkMonitor`, `JournalQueue`, `JournalSyncService`,
`NavigationViewModel`, `NotificationDelegate` — is built by
`ContentViewDependencies.live()` (`App/ContentViewDependencies.swift`,
visible in the preview wiring at `ContentView.swift:20-35`).

## Screen inventory (complete — 56 view files)

| Group | Files | Role |
| --- | --- | --- |
| `Views/Navigation/` (14) | `RootShellView`, `RootPresentationHost`, `MainContentStates`, `MainContentDialogsModifier`, `MainContentLifecycleModifier`, `MainNavigationToolbar`, `JournalFlowAlertsModifier`, `LayerScrollView`, `LayerView`, `LayerCardView`, `LayerSideIndicator`, `PhasePageView`, `PhaseCrystalCard`, `DetailDestinationView` | The main surface: a vertical **layer** axis crossed with a horizontal **phase** axis, plus root presentation/alert plumbing |
| `Views/Curriculum/` (6) | `CurriculumDetailView`, `CurriculumCard`, `ClearLightEmotionCard`, `LayeredEmotion`, `StrategyCard`, `StrategyListView` | Rendering one layer-phase cell: medicinal/toxic emotion expressions and self-care strategies |
| `Views/Journal/` (4) | `FlowReviewSheet`, `FlowConfirmationAlertsModifier`, `JournalFeedbackAlert`, `SubmitTimeout` | The emotion-logging flow's sheets/alerts |
| `Views/Analytics/` (11) | `AnalyticsView`, `AnalyticsViewSections`, `AnalyticsDetailHubView`, `DosageDeepDiveView`, `GrowthIndicatorsView`, `ModeDistributionView`, `PhaseJourneyView`, `StrategyUsageView`, `TemporalPatternsView`, `JournalEntryListView`, `JournalEntryRowView` | The analytics hub and its six drill-down screens |
| `Views/Components/` (11) | `AnalyticsEmptyView`, `AnalyticsErrorView`, `AnalyticsLoadingView`, `CircularProgressView`, `EmotionExpressionCard`, `EmotionSummaryCard`, `StrategyExpressionCard`, `StrategySummaryCard`, `HorizontalBarChart`, `StreakDisplayView`, `MysticalJournalIcon` | Shared chart/card primitives |
| `Views/Schedule/` (3) + `ScheduleSettingsView` | `ScheduleEditView`, `ScheduleRow`, `TimePickerView`, `ScheduleSettingsView` | Scheduled journal prompt editing |
| Sync & settings (3) | `SyncSettingsView`, `SyncStatusView`, `MenuView` | Cloud-sync toggle, queue status, app menu |
| Content & onboarding (3) | `OnboardingView`, `MarkdownContentView`, `About/ConceptExplainerView` | First-run and the About/concept reader (renders `Resources/about-content.md` via `WatchOSMarkdownParser`) |

## The dual-axis navigation model

The home surface is a grid: vertical scrolling moves between **layers**
(Beige → Ultraviolet, i.e. developmental stages), horizontal swiping moves
between the six **phases** of the wavelength. Two pieces make this work:

**Circular phase paging.** The phase axis is an "infinite" TabView: an extra
sentinel page is rendered on each end so the user can swipe from the first
phase to the last without interruption
(`PhaseNavigator.swift:3-13`). The bookkeeping is two pure functions:

```swift
static func adjustedSelection(_ selection: Int, phaseCount: Int) -> Int {
  if selection == 0 {
    phaseCount
  } else if selection == phaseCount + 1 {
    1
  } else {
    selection
  }
}

static func normalizedIndex(_ selection: Int, phaseCount: Int) -> Int {
  (selection - 1 + phaseCount) % phaseCount
}
```

(`PhaseNavigator.swift:23-39`.) Worked example with `phaseCount = 6`:
swiping left from page 1 (Rising) lands on sentinel page 0;
`adjustedSelection(0, 6)` snaps the selection to page 6 (Restoration), and
`normalizedIndex(6, 6) = 5` indexes the last phase. Swiping right from
page 6 lands on sentinel 7 → snapped to page 1 → index 0.

**Selection reconciliation.** `NavigationViewModel` "owns the dual-axis
navigation selection and keeps it reconciled with `ContentViewModel`'s
ground-truth IDs and indices" (`ViewModels/NavigationViewModel.swift:4-11`).
`layerSelection` is a *filtered-array index* and `phaseSelection` an
infinite-scroll page; both are projections of the model's `selectedLayerId`
/ `selectedPhaseIndex`. View → model writes run in `didSet`s; model → view
writes run in four Combine subscriptions (`$phaseOrder`,
`$selectedLayerId`, `$layerFilterMode`, `$selectedPhaseIndex`,
`:66-89`), each dispatched onto a fresh main-actor `Task` and
equality-guarded so "the two representations converge instead of looping"
(`:18-20`). The doc comment explicitly notes the race window this design
accepts and why the guards make it safe (`:59-65`). This replaced a
six-observer view modifier (#329).

**Layer filtering.** During the logging flow the visible layers are filtered
by `ContentViewModel.layerFilterMode` (`all` / `emotionsOnly` /
`strategiesOnly` — `Models/LayerFilterMode.swift`), driven by the flow
coordinator (see the flow state machine in
[Offline sync and flows](offline-sync-and-flows.md)).

## API base URL resolution

`AppConfiguration` resolves the backend URL from three sources in priority
order, falling back to a loud placeholder
(`App/AppConfiguration.swift:38-60`):

1. `Info.plist` key `API_BASE_URL` (build-time configuration);
2. `APIConfiguration-Local.plist` (developer override, not committed);
3. `APIConfiguration.plist` (committed template value).

If none yields a URL the app uses
`https://api.not-configured.local` and logs a fault; if the resolved URL
*equals* the placeholder it warns "Configure a real backend before shipping"
(`App/AppConfiguration.swift:13`, `:26-33`). Because the catalog is cached
and journaling is queue-first, the app remains usable in this state — the
offline-first design doubles as a no-backend mode.

## Scheduled journal prompts

`JournalSchedule` is a Codable value: `id`, `time` (`DateComponents`),
`enabled`, and `repeatDays` as a `Set<Int>` with 0 = Sunday … 6 = Saturday,
validated by `isValid` (`Models/JournalSchedule.swift:4-28`).
`NotificationScheduler` exposes exactly three operations —
`requestPermission()`, `scheduleNotifications(for:)`,
`cancelAllNotifications()` (`Services/NotificationScheduler.swift:5-7`) —
and entries created from a notification are tagged
`initiated_by: "scheduled"` versus `"self"` for user-initiated ones
(backend enum at `backend/models.py:20-24`), which is how analytics can
distinguish prompted from spontaneous check-ins.

## Design system

`DesignSystem/` defines the `WL*` token set — `WLColorTokens`,
`WLSpacingTokens`, `WLTypographyTokens`, `WLTheme` — and six view modifiers
(`WLButtonStyle`, `WLCardModifier`, `WLGlassModifier`, `WLMotionModifier`,
`WLNavigationBarModifier`, `WLSurfaceModifier`) plus a
`DesignSystemPreview`. Stage colors map through `Extensions/Color+Stage.swift`
so every layer renders in its spiral color. Each token file has a matching
unit-test file (e.g. `WLColorTokensTests.swift`), keeping the token contract
pinned.

---

*Grounded in wavelengthwatch@d8342ad, 2026-07-31.*
