# Add a backend migration in adepthood

Create and apply an Alembic migration for a schema change in
`Geoffe-Ga/adepthood`. Verified against the repo state of 2026-07-31.

## Prerequisites

- `.venv` activated, backend requirements installed
- A local PostgreSQL reachable via `DATABASE_URL` (or the default in
  `backend/src/database.py`)
- Migrations live in `backend/migrations/` (`alembic.ini` sets
  `script_location = %(here)s/migrations`); `migrations/env.py` injects the
  runtime `DATABASE_URL`, normalized for asyncpg

## Steps

1. **Write the test first** (TDD is required — adepthood `AGENTS.md`): a
   failing test that exercises the new column/table through the model or
   endpoint.

2. Change or add the SQLModel class under `backend/src/models/` (one module
   per table; export it via `models/__init__.py` so autogenerate sees it).

3. Generate the revision from `backend/`:

   ```bash
   cd backend
   alembic revision --autogenerate -m "add <thing>"
   ```

4. **Review the generated file** in `backend/migrations/versions/` —
   autogenerate output is a draft, not a truth. Ensure both `upgrade()` and
   `downgrade()` are correct; follow the existing revision naming style
   (`<hash>_<snake_case_summary>.py`).

5. Apply and test:

   ```bash
   alembic upgrade head
   pytest
   ```

## Verify

- `alembic upgrade head` runs cleanly on a fresh database, and
  `alembic downgrade -1` reverses it.
- Your new test passes; the full gate run
  ([quality gates](run-the-adepthood-quality-gates.md)) stays green.
