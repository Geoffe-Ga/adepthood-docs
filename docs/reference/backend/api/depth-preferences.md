# API — depth-preferences router

`backend/src/routers/depth_preferences.py` (68 lines).
`APIRouter(prefix="/depth-preferences", tags=["depth-preferences"])`
(`depth_preferences.py:23`). The toggles for the optional program rings —
"Nothing is gated; these toggles simply let the user quiet rings they
have not chosen" (`depth_preferences.py:1-8`; ADR
[0006 — graduated engagement](../../../decisions/0006-graduated-engagement.md)).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/depth-preferences` | JWT | — | `DepthPreferencesResponse` | 200 | — |
| PATCH | `/depth-preferences` | JWT | `DepthPreferencesUpdate` (`backend/src/schemas/depth_preferences.py`) | `DepthPreferencesResponse` | 200 | 422 (empty body, rejected by the schema) |

- GET provisions an **all-true** row on first access
  (`ensure_depth_preferences` — see
  [domain/depth-preferences](../domain/depth-preferences.md)):
  a fresh account starts fully opted-in and can decline later
  (`depth_preferences.py:36-47`).
- PATCH applies only the rings present in the request
  (`exclude_unset=True`) and returns the full four-boolean state:
  `enable_habits`, `enable_practices`, `enable_course`, `enable_sangha`
  (`depth_preferences.py:50-68`).

No `user_id` appears in the body, path, or response — the caller is the
JWT subject only (`depth_preferences.py:6-8`). Model:
[data-model/preferences-invitations](../data-model/preferences-invitations.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
