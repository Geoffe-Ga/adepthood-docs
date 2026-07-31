# WavelengthWatch — module map

Deep reference for the
[WavelengthWatch](https://github.com/Geoffe-Ga/WavelengthWatch) repository,
generated from source. For the product-level story see
[the product page](../../products/wavelengthwatch.md).

Two applications share the repo: a **FastAPI + SQLModel backend**
(`backend/`) and a **watchOS SwiftUI app**
(`frontend/WavelengthWatch/WavelengthWatch Watch App/`). The watch is
offline-first: it renders the Archetypal Wavelength curriculum from a cached
catalog and queues journal entries locally, syncing when a network appears.

## Backend module map (complete)

All 16 backend Python modules (excluding `__init__.py` files):

| Module | Purpose | Key exports / notes |
| --- | --- | --- |
| `backend/app.py` | App factory: CORS policy, lifespan (create tables → rewrite legacy rest entries → seed → idempotency cleanup), router mounting under `/api/v1`, `/health` (`backend/app.py:53-98`) | `create_application`; production **requires** `CORS_ALLOWED_ORIGINS` or startup fails (`:43-48`) |
| `backend/database.py` | Engine config; normalizes Railway's bare `postgres://` URL to `postgresql+psycopg://`, enables SQLite `PRAGMA foreign_keys=ON` (`backend/database.py:26-57`) | `engine`, `get_session`, `configure_engine`; default URL `sqlite:///./app.db` (`:60-62`) |
| `backend/models.py` | 6 SQLModel tables + 3 enums (see [Backend API](backend-api.md)) | `Layer`, `Phase`, `Curriculum`, `Strategy`, `Journal`, `IdempotencyRecord`; `Dosage`, `InitiatedBy`, `EntryType` |
| `backend/schemas.py` | Request/response DTOs: Create/Update/Read triples per entity + 12 analytics response models (`backend/schemas.py:25-267`) | `JournalCreate`, `AnalyticsOverview`, `EmotionalLandscape`, … |
| `backend/schemas_catalog.py` | Nested catalog DTOs (`backend/schemas_catalog.py:10-59`) | `CatalogResponse` → `CatalogLayer` → `CatalogPhase` → entries/strategies |
| `backend/cache.py` | Thread-safe in-memory TTL cache for analytics — "in-memory … rather than Redis to avoid infrastructure complexity" (`backend/cache.py:1-12`) | `AnalyticsCache` (TTL 300 s, `:23`), `analytics_cache`, `make_cache_key` |
| `backend/logging_config.py` | Logging setup (privacy-tested by `tests/backend/test_logging_privacy.py`) | `configure_logging` |
| `backend/routers/analytics.py` | 5 read-only analytics endpoints + streak/ratio/trend algorithms | see [Offline sync and flows](offline-sync-and-flows.md) |
| `backend/routers/catalog.py` | The aggregated read-only catalog endpoint, `Cache-Control: public, max-age=3600` (`backend/routers/catalog.py:70`) | `GET /api/v1/catalog` |
| `backend/routers/curriculum.py`, `layer.py`, `phase.py`, `strategy.py` | CRUD for the four reference tables | 5 endpoints each |
| `backend/routers/journal.py` | Journal CRUD + idempotent create (`X-Idempotency-Key`) | see [Offline sync and flows](offline-sync-and-flows.md) |
| `backend/services/catalog.py` | `build_catalog`: aggregates layers × phases × dosage entries × strategies (`backend/services/catalog.py:34-138`; graph node `workspace_wavelengthwatch_backend_services_catalog_build_catalog`, `source_location` `backend/services/catalog.py` L34) | `build_catalog`, `CatalogDataError` |
| `backend/tools/seed_data.py` | Seeds empty tables from CSVs in `backend/tools/data/` (`layer.csv`, `phase.csv`, `curriculum.csv`, `strategy.csv`, `journal.csv`); skips any table that already has rows (`backend/tools/seed_data.py:31-32`) | `seed_database` |
| `backend/tools/csv_to_json.py` | Converts the source `backend/data/a-w-*.csv` sheets to seed data | — |

`backend/data/` holds the curriculum source sheets:
`a-w-curriculum.csv` (`dosage,stage,rising,peaking,withdrawal,diminishing,
bottoming out,restoration` — Medicine/Toxic rows per stage),
`a-w-strategies.csv` (`strategy,stage,phase`), and `a-w-headers.csv`
(`level,title,subtitle`, e.g. `Beige,INHABIT,(Do)`) — the same
mode/phase/dosage ontology as aptitude-course's curriculum database and
wavelength-demo's mode files.

## Watch app layer map (complete at directory level)

All Swift sources live under
`frontend/WavelengthWatch/WavelengthWatch Watch App/`:

| Group | Files | Contents |
| --- | --- | --- |
| `App/` | 3 | `AppConfiguration` (API base URL resolution), `AppStorageKeys`, `ContentViewDependencies` (live dependency wiring) |
| `Constants/` | 1 | `UIConstants` |
| `ContentView.swift`, `WavelengthWatchApp.swift`, `PhaseNavigator.swift` | 3 | App entry, root shell host, circular-paging math |
| `DesignSystem/` | 11 | `WL*` theme tokens (color/spacing/typography), modifiers (button/card/glass/motion/navigation-bar/surface), preview |
| `Extensions/` | 3 | `Color+Stage`, `Comparable+Clamped`, `EnvironmentValues+DetailView` |
| `Models/` | 11 | Catalog/analytics DTO models, `LocalJournalEntry`, `JournalQueueModels`, `JournalSchedule`, `SyncSettings`, drill-down filters, `DetailDestination`, `HourFormatter`, `LayerFilterMode` |
| `Services/` | 14 | `APIClient`, `AnalyticsService`, `CatalogRepository`, `JournalClient`, `JournalDatabase`, `JournalQueue`, `JournalRepository`, `JournalSyncService`, `LocalAnalyticsCalculator`, `MarkdownContentLoader`, `NetworkMonitor`, `NotificationCenterProtocol`, `NotificationScheduler`, `WatchOSMarkdownParser` |
| `ViewModels/` | 14 | `ContentViewModel`, `NavigationViewModel`, `FlowCoordinator`, `FlowStepReactionPolicy`, `FlowSubmissionPresenter`, `PresentationCoordinator`, `AnalyticsViewModel`, `EmotionalLandscapeViewModel`, `GrowthIndicatorsViewModel`, `TemporalPatternsViewModel`, `SelfCareViewModel`, `ScheduleViewModel`, `SyncSettingsViewModel`, `LogConfirmation` |
| `Views/` | 56 | Screen and component views — enumerated in [Watch app](watch-app.md) |
| `Resources/` | 3 | `APIConfiguration.plist` (+ template), `about-content.md` |

Tests: 68 unit-test files in `WavelengthWatch Watch AppTests/` plus 3 UI-test
files; backend tests in `tests/backend/` (16 files).

## Repo-level surfaces

| Item | Detail |
| --- | --- |
| `railway.toml` | Backend deploy config (Railway) |
| `pyproject.toml`, `ruff.toml`, `mypy.ini`, `pytest.ini` | Python toolchain, strict lint/type gates |
| `.swiftformat`, `scripts/swiftformat_lint.sh` | Swift formatting gate |
| `dev-setup.sh`, `scripts/setup-local-api.sh`, `scripts/check-backend.sh` | Local development bootstrap |
| `frontend/WavelengthWatch/run-tests-individually.sh` | watchOS test runner |
| `scripts/convert_csv_to_json.sh`, `scripts/add_files_to_xcode.py`, `scripts/pr-status.sh` | Utilities |

## Relationship to the rest of the ecosystem

- **Shared ontology, no shared code.** The six phases
  (Rising … Restoration), the layer colors (Beige … Ultraviolet), the
  Mode/orientation headers, and the Medicinal/Toxic dosage split all trace to
  the same curriculum spreadsheet as aptitude-course's
  `google_docs/database_of_course_curriculum/` CSVs; here they are seeded
  into relational tables (`backend/tools/seed_data.py`).
- **wavelength-demo links here.** Its "Get the App" buttons point at this
  repo (`src/components/MobileAppCta.tsx:1` in wavelength-demo).
- **adepthood parallels.** The watch's journal-first, offline-first design
  (local queue + idempotent replay) is the same pattern adepthood's journal
  uses server-side; the two apps share vocabulary (phases, stages,
  medicinal/toxic) but have independent backends and data models.

---

*Grounded in wavelengthwatch@d8342ad, 2026-07-31.*
