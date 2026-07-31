# API — practice-share router

`backend/src/routers/practice_share.py` (509 lines).
`APIRouter(prefix="/practices", tags=["practice-share"])`
(`practice_share.py:84`) — shares the `/practices` prefix with the
[practices](practices.md) router but is a separate module. Four routes
joined by the `PracticeShareLink` token table plus a listing route
(`practice_share.py:1-13`).

| Method | Path | Rate limit | Auth | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| POST | `/practices/{practice_id}/share-link` | 10/hour per user | JWT, owner (or preset) | `ShareLinkResponse` | **201** | 404 `practice_not_found`, 403 `forbidden` |
| GET | `/practices/share/{token}` | 30/hour | JWT (any signed-in user) | `ShareLinkPreviewResponse` | 200 | 404 `share_link_not_found`; 410 `share_link_expired` / `share_link_revoked` / `share_link_exhausted` |
| POST | `/practices/share/{token}/import` | 30/hour | JWT | `ShareLinkImportResponse` | **201** | 404 / 410 (as above); 400 `cannot_import_own_practice` |
| DELETE | `/practices/share-links/{share_link_id}` | — | JWT, minter | — | **204** (idempotent) | 404 `share_link_not_found`, 403 `forbidden` |
| GET | `/practices/{practice_id}/share-links?limit=` | — | JWT, owner | `list[ShareLinkResponse]` | 200 | 404 / 403 |

The 404/410 split is deliberate (`practice_share.py:16-23`): 404 means
the token does not exist; 410 means it existed but "has aged out, been
revoked, or hit its `max_uses` cap — 410 tells the client the link
itself is dead and not worth retrying."

Notes:

- **Mint** — ownership is "I submitted this row"; preset practices
  (`submitted_by_user_id IS NULL`) can be shared by anyone (#348);
  someone else's submission 403s (`practice_share.py:259-265`). Tokens
  are `secrets.token_urlsafe(32)` with up to 4 mint attempts on the
  vanishingly-unlikely unique collision (`practice_share.py:61-65`).
- **Preview** requires authentication "so an anonymous link harvester
  cannot crawl tokens without paying the signup tax", and the response
  omits `submitted_by_user_id` so the endpoint cannot double as a
  user-id enumeration oracle (`practice_share.py:298-305`).
- **Import** clones the source as an `approved=False` row with
  `submitted_by_user_id` = recipient, keeping it private to them
  (`practice_share.py:9-12`). Self-import is a 400 "UX foot-gun"
  rejection (`practice_share.py:389-391,404`). Race safety: one guarded
  `UPDATE … SET use_count = use_count + 1 WHERE … use_count < max_uses`
  claims the slot, so "two concurrent importers of a `max_uses=1` link
  cannot both bypass the cap"; the loser gets the same 410
  `share_link_exhausted` as a sequential third importer, and the
  increment and clone share one transaction (`practice_share.py:393-400`;
  model rationale at
  `backend/src/models/practice_share_link.py:48-55`).
- **Revoke** — no-op 204 on an already-revoked link; `revoked_at` is not
  pushed forward (`practice_share.py:445-450`).
- **List** powers the frontend ShareSheet's "active links with Revoke"
  panel, newest-first, bounded to `limit` ∈ [1, 200] (default 50)
  (`practice_share.py:467-494`).

DTOs: `backend/src/schemas/practice_share.py`. Model:
[data-model/practice](../data-model/practice.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
