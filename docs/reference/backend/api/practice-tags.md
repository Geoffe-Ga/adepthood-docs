# API — practice-tags router

`backend/src/routers/practice_tags.py` (161 lines).
`APIRouter(prefix="/practice-tags", tags=["practice-tags"])`
(`practice_tags.py:45`). The personal tag library backing the recipe
builder (`practice_tags.py:1-18`).

| Method | Path | Auth | Request DTO | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/practice-tags/` | JWT | `PaginationParams` | `Page[PracticeTagOut]` or bare list | 200 | — |
| POST | `/practice-tags/` | JWT | `PracticeTagCreate` | `PracticeTagOut` | **201** | 409 `tag_slug_taken` |
| GET | `/practice-tags/{tag_id}` | JWT | — | `PracticeTagOut` | 200 | 404 `practice_tag_not_found` |
| PATCH | `/practice-tags/{tag_id}` | JWT | `PracticeTagUpdate` | `PracticeTagOut` | 200 | 404; 403 `cannot_modify_system_tag` |
| DELETE | `/practice-tags/{tag_id}` | JWT | — | — | **204** | 404; 403 `cannot_modify_system_tag` |

Rules:

- **Visibility** (reads): system rows (`owner_user_id IS NULL`) + the
  caller's own, via the shared `visible_to_user` /
  `system_or_owned_clause` predicates
  (`backend/src/dependencies/ownership.py:27-50`); a non-visible id is a
  404 (`practice_tags.py:48-60`).
- **Mutation** additionally requires a personal row: a system tag
  returns 403 `cannot_modify_system_tag` "rather than 404 so the client
  can render an informative message" (`practice_tags.py:14-17,63-66`).
- **Slug immutability**: PATCH changes `label` only — "slug is immutable
  so recipe steps that copied it stay valid" (`practice_tags.py:8-9,136`).
- **Create** maps the per-user partial-unique-index collision
  (migration `07b8c9d0e1f2`) to 409 `tag_slug_taken` instead of a bare
  500 (`practice_tags.py:97-111`).
- **Delete** leaves recipes intact — "recipe steps carry `tag_slug` by
  value, not by FK" (`practice_tags.py:152-156`).
- Listing orders system-first (`owner_user_id NULLS FIRST`) then label,
  with the `?paginate=true` envelope slicing that same ordering (issue
  #465, `practice_tags.py:74-88`).

DTOs: `backend/src/schemas/practice_tag.py`. Model:
[data-model/practice](../data-model/practice.md).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
