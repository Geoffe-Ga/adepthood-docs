# API — invitations router

`backend/src/routers/invitations.py` (113 lines).
`APIRouter(prefix="/invitations", tags=["invitations"])`
(`invitations.py:37`). Lists the caller's pending invitations toward
deeper rings and lets them decline — "never to gate or pressure"
(`invitations.py:1-7`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/invitations` | JWT | — | `list[InvitationResponse]` | 200 | — |
| POST | `/invitations/{invitation_id}/dismiss` | JWT | — | `InvitationResponse` | 200 (idempotent) | 404 `invitation_not_found` (missing **or** another user's — same bytes) |

Behavior:

- **GET generates before it lists** (`invitations.py:54-79`): the
  idempotent generation pass (`services.invitations
  .generate_invitation_signals`, fed by
  [domain/invitations](../domain/invitations.md) and, when connected, a
  Creek Vault corpus-theme reading) "inserts only coordinates that have
  no prior row (dismissed rows included), so polling this endpoint never
  accumulates duplicates" (`invitations.py:62-66`). The listing returns
  only the caller's rows with `dismissed_at IS NULL`, ordered by
  `created_at`.
- **Dismiss is idempotent and enumeration-safe**
  (`invitations.py:82-113`): the row is selected by `id` **and** owner
  in one `FOR UPDATE` query, never fetched-then-compared — "a row the
  caller does not own is indistinguishable from a missing one and both
  raise the same 404 … so existence is never confirmed to a non-owner";
  an already-dismissed row returns unchanged as a 200 no-op.
- The response DTO deliberately omits `user_id`
  (`invitations.py:40-51`; `backend/src/schemas/invitations.py`).

The DB guarantees a declined invitation can never be silently recreated
(the dismissed-inclusive unique indexes,
[data-model/preferences-invitations](../data-model/preferences-invitations.md)).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
