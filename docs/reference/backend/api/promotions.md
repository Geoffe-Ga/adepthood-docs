# API — promotions router

`backend/src/routers/promotions.py` (201 lines).
`APIRouter(tags=["promotions"])` — no prefix; paths mount under
`/journal/...` and `/promotions/...` (`promotions.py:29`). Quote
promotion: lift a span from one journal entry, optionally fold it into a
hierarchical reflection. "The server slices and snapshots the text (the
client sends only offsets) so the quote survives later edits. `user_id`
is never returned" (`promotions.py:1-7`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| POST | `/journal/{entry_id}/promote` | JWT + owned entry | `PromoteQuoteCreate` | `PromotedQuoteResponse` | **201** | 404 `journal_entry_not_found` (missing/soft-deleted/foreign), 422 `anchor_out_of_range` / `quote_too_long` |
| GET | `/journal/{entry_id}/promotions` | JWT + owned entry | — | `list[PromotedQuoteResponse]` | 200 | 404 (as above) |
| PATCH | `/promotions/{promotion_id}` | JWT | `PromotionUpdate` | `PromotedQuoteResponse` | 200 | 404 `promotion_not_found`; 404 `journal_entry_not_found` / 422 `target_not_reflection` (bad fold target) |
| DELETE | `/promotions/{promotion_id}` | JWT | — | — | **204** | 404 `promotion_not_found` (repeat delete 404s — enumeration-safe) |

Behavior:

- **Server-side slicing** (`promotions.py:45-61`): offsets are Unicode
  code points validated against the *server-held* body — never client
  text; `anchor_end` past the body length is 422 `anchor_out_of_range`,
  and a sanitized span over `PROMOTED_QUOTE_TEXT_MAX` (1000,
  `backend/src/models/promoted_quote.py:20-23`) is 422 `quote_too_long`.
- **Listing** returns every quote for the entry regardless of status —
  pending, folded, stale — ordered `(anchor_start, id)`, "so a reopened
  entry can rehydrate all of its highlights" (`promotions.py:96-118`).
  `pending` in the DTO is computed as `included_in_entry_id is None`
  (`promotions.py:32-42`).
- **Folding** (`promotions.py:156-201`): setting `included_in_entry_id`
  requires the target to be the caller's own live entry *and* tagged
  `hierarchical_reflection` (else 422 `target_not_reflection`); `null`
  returns the quote to pending.
- All single-quote lookups are scoped by `id` + owner in one query
  (enumeration-safe 404s, `promotions.py:121-131`).

DTOs: `backend/src/schemas/promotion.py`. Model:
[data-model/journal-reflection](../data-model/journal-reflection.md);
reflection targets: [domain/reflection-hierarchy](../domain/reflection-hierarchy.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
