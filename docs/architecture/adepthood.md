# adepthood

As of the 2026-07-31 baseline seed (issue #3).

The flagship monorepo: a React Native + Expo frontend and a FastAPI +
PostgreSQL backend, split at the repo root into `frontend/` and `backend/`
(see [ADR 0001](../decisions/0001-monorepo-frontend-backend-split.md)).

## Stack

- **Frontend** — React Native 0.76 with Expo ~52, TypeScript (strict),
  Zustand for state, React Navigation 7, Jest 29 for tests
  (`frontend/package.json`).
- **Backend** — FastAPI with SQLModel ORM, fully async (asyncpg engine),
  Alembic migrations, pytest (`backend/pyproject.toml`,
  `backend/src/database.py`). See
  [ADR 0002](../decisions/0002-fastapi-sqlmodel-async-alembic.md).
- **Deployment** — Railway (backend `Dockerfile`, `backend/railway.toml`).

## Module map

### Backend (`backend/src/`)

- `main.py` — FastAPI app assembly: CORS, rate limiting (slowapi),
  correlation-ID / security-header / request-logging middleware, exception
  handlers, and mounting of the routers listed below.
- `database.py` — async engine + session factory; `normalize_database_url`
  converts PaaS-style `postgres://` URLs to `postgresql+asyncpg://`.
- `models/` — SQLModel ORM classes, one module per table (36 modules as of
  this baseline): users and auth (`user.py`, `auth_identity.py`,
  `revoked_token.py`, `login_attempt.py`, `password_reset_token.py`), habits
  and goals (`habit.py`, `goal.py`, `goal_group.py`, `goal_completion.py`),
  practices (`practice.py`, `practice_session.py`, `practice_recipe.py`,
  `practice_share_link.py`, `user_practice.py`), journal (`journal_entry.py`,
  `marginalia.py`, `promoted_quote.py`), course (`course_stage.py`,
  `stage_content.py`, `stage_progress.py`, `content_completion.py`),
  monetization (`entitlement.py`, `gumroad_sale.py`, `wallet_audit.py`), and
  depth/invitation state (`user_depth_preferences.py`,
  `invitation_signal.py`, `metta_return_arc.py`).
- `routers/` — 27 route modules mirroring the model areas: `auth.py`,
  `habits.py`, `goals.py`, `goal_groups.py`, `goal_completions.py`,
  `practices.py`, `practice_sessions.py`, `practice_recipes.py`,
  `practice_share.py`, `practice_tags.py`, `journal.py`, `botmason.py`,
  `course.py`, `stages.py`, `prompts.py`, `reflections.py`, `energy.py`,
  `depth_preferences.py`, `invitations.py`, `metta_return.py`, `gumroad.py`,
  `promotions.py`, `transcription.py`, `ui_flags.py`, `user_practices.py`,
  `users.py`, `admin.py`.
- `domain/` — pure business logic kept out of the routers: energy planning
  (`energy.py`), streaks (`streaks.py`), stage progress
  (`stage_progress.py`), resonance and completion-suggestion detection
  (`resonance.py`, `detection.py`), invitations (`invitations.py`), care
  guardrails (`care.py`, `safety.py`), program calendar
  (`program_calendar.py`), and more.
- `schemas/` — Pydantic request/response DTOs, separate from the ORM layer.
- `seed_content.py` — content seeder run in the FastAPI startup lifespan.

### Frontend (`frontend/src/`)

- `App.tsx` — entry point wiring the AuthProvider and navigation.
- `features/` — feature modules: `Auth`, `Course`, `Habits`, `Invitations`,
  `Journal`, `Map`, `Practice`, `Return`, `Settings`, `Welcome`.
- `navigation/` — `BottomTabs.tsx`, `RootStack.tsx`, plus typed
  `destinations.ts` and navigation `theme.ts`.
- `api/` — HTTP client, zod-style response `schemas.ts`, and user-facing
  `errorMessages.ts`.
- `design/` — the Candle & Ink design system: `tokens.ts`, `ThemeContext.tsx`,
  `useResponsive.ts`, documented in `frontend/src/design/DESIGN.md`
  (see [Candle & Ink](../design/candle-and-ink.md)).
- `context/`, `store/`, `storage/` — auth context (JWT management), Zustand
  stores, AsyncStorage persistence.

## Data flow

1. Frontend feature screens call the API layer (`frontend/src/api/`), which
   attaches the JWT from the auth context
   ([ADR 0004](../decisions/0004-jwt-auth.md)).
2. FastAPI routers validate DTOs (`backend/src/schemas/`), delegate rules to
   `backend/src/domain/`, and persist via async SQLModel sessions from
   `get_session` (`backend/src/database.py`).
3. Schema changes travel as Alembic migrations in
   `backend/migrations/versions/`; `migrations/env.py` injects the runtime
   `DATABASE_URL` so migrations run against the same database as the app.
4. Course content is not authored in this repo — it is consumed from
   `aptitude-course` via its manifest contract
   ([ADR 0011](../decisions/0011-manifest-consumption-contract.md)).

## Key entry points

- Backend dev server: `cd backend && python -m uvicorn src.main:app --reload`
- Frontend dev server: `cd frontend && npm ci && npm start` (Expo)
- Full environment bootstrap: `bash scripts/dev-setup.sh`
- Quality gates: `pre-commit run --all-files`,
  `scripts/backend/check-all.sh`, `scripts/frontend/check-all.sh`
- Roadmap: `prompts/github-issues/README.md` (phased epics + dependency
  graphs); agent fleet under `scripts/ralph/` and `.claude/`
