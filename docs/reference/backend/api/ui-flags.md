# API — ui-flags router

`backend/src/routers/ui_flags.py` (65 lines).
`APIRouter(prefix="/ui-flags", tags=["ui-flags"])` (`ui_flags.py:22`).
The caller is resolved from their JWT; "no `user_id` is ever accepted
from the body or path" (`ui_flags.py:1-7`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/ui-flags` | JWT | — | `UiFlagsResponse` | 200 | — |
| PATCH | `/ui-flags` | JWT | `UiFlagsUpdate` (`backend/src/schemas/ui_flags.py`) | `UiFlagsResponse` | 200 | 422 (empty body, rejected by the schema) |

- GET provisions an all-false row on first access via
  `domain.ui_flags.ensure_ui_flags` (race-safe — see
  [domain/ui-flags](../domain/ui-flags.md)); "repeated calls return the
  same state and never create a duplicate row" (`ui_flags.py:33-44`).
- PATCH is a partial update: only fields present in the request
  (`model_dump(exclude_unset=True)`) are applied; unspecified flags keep
  their stored value; the full new state is returned
  (`ui_flags.py:47-65`).

Fields: `has_seen_welcome`, `energy_scaffolding_archived` — see
[data-model/preferences-invitations](../data-model/preferences-invitations.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
