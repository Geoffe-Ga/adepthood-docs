# API — users router

`backend/src/routers/users.py` (53 lines).
`APIRouter(prefix="/users", tags=["users"])` (`users.py:25`). A single
profile route (issue #261): correcting the IANA timezone stored at signup
— needed when a user travels, immigrates, or signed up on a device with a
wrong zone; without it "streak and daily-completion math would use the
original zone forever, re-introducing the off-by-one boundary bug PR #260
closed" (`users.py:1-8`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| PUT | `/users/me/timezone` | JWT (full `User` row via `get_current_user_model`) | `TimezoneUpdate` (`backend/src/schemas/timezone.py`) | `TimezoneRead` | 200 | 422 (unknown or oversized zone name, from schema validation); 403 `user_not_found` (JWT valid but account deleted, `backend/src/dependencies/auth.py:27-36`) |

Validation mirrors signup exactly — both call
`domain.timezone.normalize_timezone` (see
[domain/timezone](../domain/timezone.md)): blank input coerces to
`"UTC"`, an unknown/oversized name is a 422 (`users.py:34-40`). Only the
caller's own row is ever mutated (resolved from the JWT); the change is
committed and logged as `timezone_changed` with old/new values
(`users.py:41-53`).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
