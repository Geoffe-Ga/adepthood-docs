# API — reflections router

`backend/src/routers/reflections.py` (345 lines).
`APIRouter(prefix="/reflections", tags=["reflections"])`
(`reflections.py:58`). Two read surfaces over the nested APTITUDE
reflection calendar; "all schedule math lives in
`domain.reflection_hierarchy`; this router only turns program weeks into
datetime windows and shuttles rows to and from it"
(`reflections.py:1-13`).

| Method | Path | Auth | Request | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/reflections/due` | JWT | — | `ReflectionDueResponse` | 200 (`due` may be `null`) | — |
| GET | `/reflections/sources?level=…&scope_key=…` | JWT | query: `ReflectionLevel`, `scope_key` | `ReflectionSourcesResponse` | 200 | 422 `invalid_scope` (malformed key, level/token mismatch, out-of-range index — `reflections.py:135`), 403 `scope_locked` (scope's first week not yet reached — `reflections.py:150`) |

Behavior:

- **`/due`** (`reflections.py:94-105`): a user with no program progress,
  or whose current day is not a week-closing day (only day 7 of a
  program week is — [domain/reflection-hierarchy](../domain/reflection-hierarchy.md)),
  gets `due: null`. Otherwise the widest closing layer wins
  (program > tier > component > stage > week), returned with its
  calendar window and any existing reflection already claiming the scope
  (`c{cycle}:{token}` key on `JournalEntry.reflection_scope_key`).
- **`/sources`** (`reflections.py:313-328`): walks the hierarchy
  top-down — "an existing child reflection stands in for its whole span,
  and every gap decomposes to that week's raw daily entries, yielding a
  chronological feed with each promoted quote flagged pending or
  included." The `scope_locked` gate stops a caller from decomposing
  spans their calendar has not reached.

The reflection *entries* themselves are journal rows tagged
`hierarchical_reflection`, created via the journal write path with the
per-(user, scope) live-row uniqueness index
([data-model/journal-reflection](../data-model/journal-reflection.md));
quotes folded into a reflection come from
[api/promotions](promotions.md).

DTOs: `backend/src/schemas/reflection.py`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
