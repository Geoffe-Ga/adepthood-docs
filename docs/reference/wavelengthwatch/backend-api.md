# WavelengthWatch — backend API

The FastAPI surface, enumerated from the routers. All API routes are mounted
under `API_V1_PREFIX = "/api/v1"` (`backend/app.py:18`, `:84-92`); `/health`
is unprefixed (`backend/app.py:94-96`). There is **no authentication layer**
— callers pass `user_id` explicitly (single-user watch deployment; an
undocumented decision encoded in the code, stated here plainly rather than
guessed at).

## Endpoint inventory (complete — 32 routes)

### Health

| Method | Path | Response |
| --- | --- | --- |
| GET | `/health` | `{"status": "ok"}` (`backend/app.py:94-96`) |

### Catalog (read-only aggregate)

| Method | Path | Query | Response | Notes |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/catalog` | — | `CatalogResponse` | Sets `Cache-Control: public, max-age=3600` (`backend/routers/catalog.py:70`) |

### Reference-table CRUD

Four routers share the same 5-route shape (list with `limit` 1-1000
default 100 / `offset`; get; create → 201; put; delete → 204). Filters vary:

| Router (prefix) | List filters | Declared at |
| --- | --- | --- |
| `/api/v1/layer` | none | `backend/routers/layer.py:33-83` |
| `/api/v1/phase` | none | `backend/routers/phase.py:33-83` |
| `/api/v1/curriculum` | `layer_id`, `phase_id`, `dosage` (`backend/routers/curriculum.py:65-74`) | `backend/routers/curriculum.py:65-130` |
| `/api/v1/strategy` | `layer_id`, `color_layer_id`, `phase_id` (`backend/routers/strategy.py:76-84`) | `backend/routers/strategy.py:76-141` |

Missing ids return 404; invalid foreign keys on create/update return 400.

### Journal

| Method | Path | Params / body | Status codes | Notes |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/journal` | `limit` (1-1000, default 100), `offset`, `user_id`, `strategy_id`, `from` (alias of `from_`), `to` (`backend/routers/journal.py:181-207`) | 200 | Eager-loads curriculum/layer/phase/strategy via `joinedload`, newest first (`:33-46`) |
| GET | `/api/v1/journal/{id}` | — | 200 / 404 | |
| POST | `/api/v1/journal` | `JournalCreate` body; optional `X-Idempotency-Key` header (UUID) | 201 created / 200 idempotent replay / 400 | Full algorithm in [Offline sync and flows](offline-sync-and-flows.md) |
| PUT | `/api/v1/journal/{id}` | `JournalUpdate` (all fields optional, `exclude_unset`) | 200 / 400 / 404 | Re-validates references with merged values (`backend/routers/journal.py:303-330`) |
| DELETE | `/api/v1/journal/{id}` | — | 204 / 404 | |

Validation rule: for `entry_type == EMOTION` (the only type),
`curriculum_id` is required — `"curriculum_id is required for emotion
entries"` (`backend/routers/journal.py:69-73`).

### Analytics (read-only, per-user)

All five take `user_id` (required), `start_date` (default: 30 days before
end), `end_date` (default: now, UTC):

| Method | Path | Extra query | Response model | Cached? |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/analytics/overview` | — | `AnalyticsOverview` (`backend/routers/analytics.py:240-247`) | 404 if user has no entries |
| GET | `/api/v1/analytics/emotional-landscape` | `limit` 1-100, default 10 | `EmotionalLandscape` (`:397-405`) | 404 if none |
| GET | `/api/v1/analytics/self-care` | `limit` 1-100, default 5 | `SelfCareAnalytics` (`:664-672`) | yes (`make_cache_key`, `:692-696`) |
| GET | `/api/v1/analytics/temporal` | — | `TemporalPatterns` (`:817-824`) | — |
| GET | `/api/v1/analytics/growth` | — | `GrowthIndicators` (`:920-927`) | yes (`:939-947`) |

The cache is per-user, TTL 300 s, invalidated on journal creation
(`backend/cache.py:23`, `:98-111`).

## Data model (complete — 6 tables, 3 enums)

From `backend/models.py`:

| Table | Fields | Relations / constraints |
| --- | --- | --- |
| `Layer` (`:39-61`) | `id` PK, `color`, `title`, `subtitle` | `curriculum_items`, `strategies` (via `layer_id`), `color_strategies` (via `color_layer_id`) |
| `Phase` (`:64-71`) | `id` PK, `name` | `curriculum_items`, `strategies` |
| `Curriculum` (`:74-98`) | `id` PK, `layer_id` FK idx, `phase_id` FK idx, `dosage` (enum `curriculum_dosage`, non-native), `expression` | `layer`, `phase`, `journal_entries`, `secondary_journal_entries` |
| `Strategy` (`:101-130`) | `id` PK, `strategy`, `layer_id` FK idx, `color_layer_id` FK idx, `phase_id` FK idx | Dual layer links: owning `layer` vs display `color_layer` |
| `Journal` (`:133-192`) | `id` PK, `created_at` (tz-aware, indexed), `user_id` idx, `curriculum_id` FK nullable idx, `secondary_curriculum_id` FK nullable idx, `strategy_id` FK nullable idx, `initiated_by` (`self`/`scheduled`), `entry_type` (`emotion`) | Composite index `ix_journal_user_created (user_id, created_at)` for analytics range scans (`:190-192`) |
| `IdempotencyRecord` (`:195-217`) | Composite PK (`idempotency_key`, `user_id`), `journal_id` FK idx, `created_at`, `expires_at` idx | "Composite primary key … ensures per-user uniqueness and prevents race conditions via database-level constraint" (`:201-204`) |

Enums: `Dosage` = `Medicinal`/`Toxic` (`:13-17`); `InitiatedBy` =
`self`/`scheduled` (`:20-24`); `EntryType` = `emotion` only — "the
rest-period feature was removed (#435). Legacy `"rest"` rows are rewritten
to `"emotion"` on startup" via `rewrite_legacy_rest_entries`
(`backend/models.py:27-36`, invoked at `backend/app.py:64`).

## Catalog aggregation

`build_catalog` (`backend/services/catalog.py:34-138`) produces the single
payload the watch renders from:

1. Load all phases ordered by id; build `phase_order` (names) and a
   `phase_index` map (`:37-48`).
2. Load all layers with `selectinload` of curriculum items (+phase) and
   strategies (+phase, +color_layer) — no N+1 (`:50-61`).
3. For each layer, pre-build one empty `CatalogPhase` per phase, then walk
   curriculum items sorted by `(phase_index, id)`, routing each entry into
   `medicinal` or `toxic` by its dosage (`:66-105`).
4. Strategies are appended per phase, colored by their `color_layer` falling
   back to the owning layer's color (`:107-131`).
5. Any reference row without a persisted id raises `CatalogDataError`
   (`:21-31`).

Response shape (nested, from `backend/schemas_catalog.py:10-59`):
`CatalogResponse{phase_order, layers[CatalogLayer{id,color,title,subtitle,
phases[CatalogPhase{id,name,medicinal[],toxic[],strategies[]}]}]}` — the
docstring at `backend/routers/catalog.py:28-67` shows a worked example
payload.

## Startup, seeding, and configuration

The lifespan hook (`backend/app.py:58-70`) runs, in order:
`create_db_and_tables()` → `rewrite_legacy_rest_entries` →
`seed_database` → `cleanup_expired_idempotency_records`. Seeding reads the
five CSVs in `backend/tools/data/` and inserts **only into empty tables**
(`_table_has_rows`, `backend/tools/seed_data.py:31-32`), so redeploys never
duplicate reference data.

Configuration knobs (env vars):

| Variable | Effect |
| --- | --- |
| `DATABASE_URL` | Default `sqlite:///./app.db`; bare `postgres://`/`postgresql://` is rewritten to `postgresql+psycopg://` for psycopg 3 (`backend/database.py:26-37`) |
| `APP_ENV` | `production` makes missing CORS config a hard startup error (`backend/app.py:43-48`) |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins; dev default is the localhost list at `backend/app.py:20-27` |

---

*Grounded in wavelengthwatch@d8342ad, 2026-07-31.*
