# API — energy router

`backend/src/routers/energy.py` (55 lines).
`APIRouter(prefix="/v1/energy", tags=["energy"])` (`energy.py:19`) — the
only router mounted under a `/v1` prefix. A thin HTTP adapter over
`services.energy` (`energy.py:1`).

| Method | Path | Auth | Request | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| POST | `/v1/energy/plan` | JWT | `EnergyPlanRequest` + optional `X-Idempotency-Key` header (max 255 chars) | `EnergyPlanResponse` | 200 | 403/404 (a habit the caller does not own), 422 (over-long idempotency key, habit list over `MAX_HABITS_PER_PLAN`) |

Behavior notes (`energy.py:22-55`):

- **Auth is a cost control** (BUG-PRACTICE-010): the planner runs
  CPU-bound scheduling on a thread pool, "so an unauthenticated endpoint
  would let a single attacker spawn arbitrary expensive work for free"
  (`energy.py:31-34`).
- **Server-trusted inputs**: `energy_cost`/`energy_return` are loaded
  from the caller's own `Habit` rows (`resolve_trusted_habits`);
  client-sent costs are ignored — "the plan can no longer be steered by
  forged client values" (`energy.py:36-40`).
- **Durable idempotency**: the generated plan persists to the
  `energyplan` table keyed by `(current_user, X-Idempotency-Key)`, so a
  keyed retry replays the stored plan across restarts and workers
  (`energy.py:42-45`); the header cap reuses the model's
  `IDEM_KEY_MAX_LENGTH` so an over-long key is a clean 422 rather than a
  DB error (`backend/src/models/energy_plan.py:20-24`).
- `generate_plan` runs off the event loop (BUG-INFRA-009,
  `energy.py:44-45`); the algorithm itself is
  [domain/energy](../domain/energy.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
