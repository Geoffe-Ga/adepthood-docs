# Run WavelengthWatch locally

Run the FastAPI backend and the watchOS app from a fresh clone of
`Geoffe-Ga/WavelengthWatch`. Verified against the repo state of 2026-07-31.

## Prerequisites

- Python 3.x with venv
- Xcode 26.3+ (16.4 still builds, but Liquid Glass APIs require the
  watchOS 26 SDK) and an Apple Watch simulator
- macOS for the frontend; the backend runs anywhere

## Steps

1. Bootstrap (venv, pre-commit, SwiftFormat):

   ```bash
   bash dev-setup.sh
   ```

   Or manually:

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r backend/requirements.txt -r backend/requirements-dev.txt
   ```

2. Start the backend (SQLite is seeded on startup):

   ```bash
   uvicorn backend.app:app --reload
   ```

3. Point the watch app at your backend: edit
   `frontend/WavelengthWatch/WavelengthWatch Watch App/Resources/APIConfiguration.plist`
   and set `API_BASE_URL` to `http://127.0.0.1:8000`. The default host is an
   intentional placeholder; debug builds assert until you change it.

4. Open `frontend/WavelengthWatch/WavelengthWatch.xcodeproj` in Xcode,
   select an Apple Watch simulator, and run.

## Verify

- Backend checks pass: `scripts/check-backend.sh` exits 0.
- The watch app loads the catalog (layers and phases) instead of the retry
  state — cached thereafter for offline use.
- Watch test suites: `frontend/WavelengthWatch/run-tests-individually.sh`.
