# API — admin router

`backend/src/routers/admin.py` (328 lines).
`APIRouter(prefix="/admin", tags=["admin"])` (`admin.py:64`). Every route
is gated on `dependencies.auth.require_admin` "so admin identity is a
first-class per-user flag rather than a shared header secret"
(`admin.py:1-5`; gate at `backend/src/dependencies/auth.py:39-51` — 401
for unauthenticated, 403 `admin_required` for non-admins).

| Method | Path | Auth | Request | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/admin/usage-stats` | admin | `PaginationParams` | `UsageStatsResponse` | 200 | 401/403 |
| GET | `/admin/stage-progress/gaps` | admin | `PaginationParams` | `StageProgressGapsPage` or `StageProgressGapsResponse` | 200 | 401/403 |
| POST | `/admin/stage-progress/{user_id}/repair` | admin | — | `StageProgressRepairResult` | 200 | 404 `stage_progress_not_found` (`admin.py:278`) |
| POST | `/admin/maintenance/energy-plans?older_than_days=N` | admin | — | `EnergyPlanCleanupResult` | 200 | 400 (invalid retention arg, `admin.py:323`) |

Notes:

- **usage-stats** aggregates `LLMUsageLog` in three views in one
  response (all-time totals, per-user, per-model); `per_user` is
  unbounded, so `?paginate=true` bounds it to a highest-cost-first page
  with `per_user_total` / `per_user_has_more` (`admin.py:110-130`). Cost
  sums are exact `Decimal` (`_ZERO_COST`, `admin.py:42`;
  [data-model/commerce-wallet](../data-model/commerce-wallet.md)).
- **stage-progress/gaps** is the read-only audit surface over the
  contiguity invariant (`completed_stages == {1..current_stage-1}`,
  [domain/stage-progress](../domain/stage-progress.md)); under
  `?paginate=true` "only `limit` `StageProgress` rows are materialised —
  not the whole table", with `scanned_total`/`has_more_rows` naming the
  row-scan semantics explicitly (`admin.py:214-236`).
- **repair** rewrites one user's `completed_stages` to the canonical set
  — "a decision to forfeit whatever intermediate-stage credit the gap
  encoded" — returns the delta, and emits a structured
  `stage_progress_repaired` log with admin, target, and delta because
  "repair mutates user progression irreversibly" (`admin.py:255-272`).
- **maintenance/energy-plans** is the retention sweep for the durable
  `energyplan` table, which otherwise grows unbounded (unkeyed requests
  are not deduplicated); "safe to call from a cron via an admin token"
  (`admin.py:308-319`).

DTOs: `backend/src/schemas/admin.py`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
