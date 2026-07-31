# WavelengthWatch

As of the 2026-07-31 baseline seed (issue #3).

A watchOS-only companion for the Archetypal Wavelength: browse every layer
and phase, see "medicinal" and "toxic" expressions side by side, and get
context-aware self-care strategies from the wrist. Not yet deployed to
production; an App Store launch is planned. Source: WavelengthWatch
`README.md` and `CLAUDE.md`.

## Stack

- **Frontend** — watchOS SwiftUI app
  (`frontend/WavelengthWatch/WavelengthWatch.xcodeproj`), built with Xcode
  26.3+ (16.4 still builds; Liquid Glass APIs need the watchOS 26 SDK).
- **Backend** — FastAPI + SQLModel service (`backend/app.py`) over SQLite,
  seeded on startup from bundled CSV/JSON fixtures (`backend/data/`,
  `backend/tools/`), serving `/api/v1/*`.

## Module map

- `backend/routers/` — endpoint modules for catalog, curriculum, journal,
  layer, phase, and strategy routes.
- `backend/services/`, `backend/schemas.py`, `backend/schemas_catalog.py`,
  `backend/cache.py` — aggregation and response shaping; `build_catalog`
  assembles layers, phases, curriculum entries, and strategies into a single
  cache-friendly payload.
- `frontend/WavelengthWatch/` — the Xcode project: `ContentViewModel`
  coordinates catalog loading, user selections, and journal submission;
  `CatalogRepository` persists the aggregated catalog to the watch's caches
  directory with a 24-hour TTL; `JournalClient` stamps a stable pseudo-user
  ID and saves entries locally first.
- `tests/` — pytest suite for the backend; watch test suites run via
  `frontend/WavelengthWatch/run-tests-individually.sh`.

## Data flow

1. The watch requests `/api/v1/catalog`; the backend aggregates the full
   curriculum into one payload with cache headers.
2. `CatalogRepository` replays the cached payload instantly (24h TTL) before
   attempting a refresh, so the curriculum is always available offline.
3. Journal entries are written to local SQLite first and only sync to
   `/api/v1/journal` if the user opts in to cloud sync — local-first,
   privacy-first by design.
4. The API base URL comes from `APIConfiguration.plist`; the default host is
   an intentionally unreachable placeholder, and debug builds assert until a
   real backend is configured.

## Key entry points

- Backend: `uvicorn backend.app:app --reload` (after
  `pip install -r backend/requirements.txt -r backend/requirements-dev.txt`).
- Full setup: `bash dev-setup.sh` (venv, pre-commit, SwiftFormat).
- Quality gates: `scripts/check-backend.sh` (lint, format, type, test);
  `swiftformat --lint frontend` for Swift.
- Knowledge graph: committed in-tree at `graphify-out/graph.json` (the
  satellite pattern), merged nightly into adepthood's `pan-graph.json`.

## Relation to Adepthood

WavelengthWatch serves the same six-phase, ten-layer Wavelength model that
Adepthood's course and Map use, packaged for glanceable wrist access. It is
promoted by `wavelength-demo` and shares no code with the app — the shared
surface is the ontology, not a library.
