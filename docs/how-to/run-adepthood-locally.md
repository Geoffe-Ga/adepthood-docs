# Run adepthood locally

Run the FastAPI backend and the Expo frontend from a fresh clone of
`Geoffe-Ga/adepthood`. Verified against the repo state of 2026-07-31.

## Prerequisites

- Python 3.11+ with a virtualenv at `.venv` in the repo root
- Node.js and npm
- PostgreSQL running locally (the backend defaults to
  `postgresql+asyncpg://aptitude:aptitude@localhost:5432/aptitude` —
  `backend/src/database.py`; override with `DATABASE_URL`)

## Steps

1. Bootstrap the full environment (idempotent):

   ```bash
   bash scripts/dev-setup.sh
   ```

   Or manually:

   ```bash
   source .venv/bin/activate
   pip install -r backend/requirements.txt -r backend/requirements-dev.txt
   ```

2. Apply migrations, then start the backend:

   ```bash
   cd backend
   alembic upgrade head
   python -m uvicorn src.main:app --reload
   ```

   Startup seeds content via the FastAPI lifespan (`backend/src/seed_content.py`).

3. In a second terminal, start the frontend:

   ```bash
   cd frontend
   npm ci        # always ci, never install, in session/CI contexts
   npm start     # Expo dev server; or npm run ios / android / web
   ```

## Verify

- Backend: the uvicorn log shows the app started; the API responds locally
  (the repo's test suite exercises a `/health` endpoint).
- Frontend: Expo's dev tools open and the app loads in your chosen target.
- Environment: `pre-commit run --all-files` passes from the activated venv.
