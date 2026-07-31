# domain/energy — energy plan generation

`backend/src/domain/energy.py` (62 lines). Pure energy-planning functions
(`energy.py:1`): given a set of habits with energy costs/returns, produce
a 21-day schedule and its cumulative net energy.

## Types

| Type | Fields | Notes |
| --- | --- | --- |
| `Habit` (frozen dataclass) | `id`, `name`, `energy_cost`, `energy_return`; property `net_energy = energy_return - energy_cost` | Domain-local shape, distinct from the ORM `models.Habit` (`energy.py:8-20`) |
| `EnergyPlanItem` | `habit_id`, `date` | One scheduled occurrence (`energy.py:23-28`) |
| `EnergyPlan` | `items: list[EnergyPlanItem]`, `net_energy: int` | The full schedule (`energy.py:31-36`) |

`PLAN_DURATION_DAYS = 21` — one standard stage cycle: "Stages 1-8 each
last 21 days (3 weeks). Energy plans are generated for this duration so
the user has a full stage's worth of scheduled habits at a time"
(`energy.py:39-42`).

## `generate_plan(habits, start_date) -> tuple[EnergyPlan, str]`

The complete algorithm (`backend/src/domain/energy.py:45-62`):

```python
def generate_plan(habits: Sequence[Habit], start_date: date) -> tuple[EnergyPlan, str]:
    """Generate a single-stage energy plan cycling through ``habits``.

    The plan covers :data:`PLAN_DURATION_DAYS` (21 days, one standard stage
    cycle). Returns the plan and a ``reason_code`` for auditability.
    """
    if not habits:
        raise ValueError("habits must not be empty")

    items: list[EnergyPlanItem] = []
    net_energy = 0
    for offset in range(PLAN_DURATION_DAYS):
        habit = habits[offset % len(habits)]
        plan_date = start_date + timedelta(days=offset)
        items.append(EnergyPlanItem(habit_id=habit.id, date=plan_date))
        net_energy += habit.net_energy
    plan = EnergyPlan(items=items, net_energy=net_energy)
    return plan, "generated_21_day_plan"
```

Rules: exactly one habit per day for 21 days, round-robin
(`habits[offset % len(habits)]`); `net_energy` is the sum of each
scheduled occurrence's `net_energy`; empty input raises `ValueError`; the
reason code `"generated_21_day_plan"` is persisted alongside the plan for
auditability (`EnergyPlan.reason_code`,
`backend/src/models/energy_plan.py:68`).

## Worked example

Habits A (`cost=2, return=5` → net +3) and B (`cost=4, return=3` → net
−1), `start_date=2026-07-01`: days 0,2,4,… get A and days 1,3,5,… get B;
21 days = 11×A + 10×B; `net_energy = 11·3 + 10·(−1) = 23`. Items run
2026-07-01 through 2026-07-21 inclusive.

Durable storage and idempotent replay of generated plans live in
[data-model/habits-goals](../data-model/habits-goals.md)
and the endpoint behavior in [api/energy](../api/energy.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
