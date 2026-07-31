# 0002. FastAPI + SQLModel, fully async, with Alembic migrations

## Status

Accepted (backfilled 2026-07-31; visible throughout `backend/src/`).

## Context

The backend needed a Python API framework with first-class typing (the repo
enforces mypy strict), an ORM that shares models with request validation,
and a migration story for a schema that grows with every roadmap phase
(36 model modules as of this baseline).

## Decision

Build the backend on FastAPI with SQLModel ORM classes
(`backend/src/models/`), an async SQLAlchemy engine using asyncpg
(`backend/src/database.py` — `create_async_engine`, `async_sessionmaker`,
and a `get_session` dependency), and Alembic migrations under
`backend/migrations/` whose `env.py` injects the runtime `DATABASE_URL`.
`normalize_database_url` converts PaaS-style `postgres://` URLs to
`postgresql+asyncpg://` so Railway deployment needs no special-casing.

## Consequences

- One class per table serves both ORM and schema typing; separate Pydantic
  DTOs in `backend/src/schemas/` keep the wire contract independent of
  storage.
- Everything downstream must be async-aware: routers, domain calls that
  touch the session, and tests (pytest-asyncio with an `async_client`
  fixture in `backend/conftest.py`).
- Schema changes are reviewable artifacts (`backend/migrations/versions/`),
  and migrations run against the same normalized URL as the app.
- The default local URL (`postgresql+asyncpg://aptitude:aptitude@localhost:5432/aptitude`)
  means contributors need a local PostgreSQL to run the API.
