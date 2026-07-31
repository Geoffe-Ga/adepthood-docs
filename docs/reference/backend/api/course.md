# API — course router

`backend/src/routers/course.py` (684 lines).
`APIRouter(prefix="/course", tags=["course"])` (`course.py:57`).
Drip-fed course content with read-tracking, plus the vendored-content
body proxy (rate-limited `30/minute`, `_CMS_PROXY_RATE_LIMIT`,
`course.py:53`).

| Method | Path | Rate limit | Auth | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/course/stages/{n}/content` | — | JWT | `Page[ContentItemResponse]` or bare list | 200 | 404 `stage_not_found` |
| GET | `/course/content/{content_id}` | — | JWT | `ContentItemResponse` | 200 | 404 `content_not_found` (also masks "locked") |
| POST | `/course/content/{content_id}/mark-read` | — | JWT | `ContentCompletionResponse` | 200 (idempotent) | 404 `content_not_found` |
| GET | `/course/stages/{n}/progress` | — | JWT | `CourseProgressResponse` | 200 | 404 `stage_not_found`, 403 `stage_locked` |
| GET | `/course/content/{content_id}/body` | 30/min | JWT | `ContentBodyResponse` | 200 | 404 `content_not_found`, 502 `content_unavailable` |
| GET | `/course/site-resources` | — | JWT | `list[SiteResourceResponse]` | 200 | — |
| GET | `/course/site-resources/{slug}/body` | 30/min | JWT | `ContentBodyResponse` | 200 | 404 `content_not_found`, 502 `content_unavailable` |
| GET | `/course/stages/{n}/intro` | — | JWT | `StageIntroResponse` | 200 | 404 `content_not_found` (masks locked stage / missing intro) |
| GET | `/course/stages/{n}/intro/body` | 30/min | JWT | `ContentBodyResponse` | 200 | 404 `content_not_found`, 502 `content_unavailable` |

Notes:

- **Listing on a locked stage is titles-only by design**: "the course
  drawer renders the full chapter map (every item locked with `url`
  nulled) while bodies and urls stay protected. Item detail … and
  `mark_content_read` remain gated — only this table-of-contents view is
  open on a locked stage" (`course.py:261-265`). Pagination applies
  **after** drip-feed filtering so the envelope's `total` "reflects the
  items the user can actually see" (`course.py:256-259`; BUG-INFRA-018).
  The drip math is [domain/course](../domain/course.md), driven by the
  calendar day-in-stage.
- **BUG-COURSE-004 — the enumeration mask**: on item detail, body,
  intro, and intro-body, "stage locked" 403 collapses into the same 404
  `content_not_found` as a genuinely missing row, "so an attacker
  enumerating `content_id` cannot distinguish 'row exists but locked for
  me' from 'row does not exist'" (`course.py:300-308,566-572,646-651`).
  The one intentional exception: `/stages/{n}/progress` returns an
  explicit 403 `stage_locked` (`course.py:204,440-447`) — the stage
  number is not a secret, only content rows are.
- **mark-read** is idempotent: a pre-check serves the retry/refresh fast
  path, and the `uq_contentcompletion_user_content` constraint catches
  the concurrent loser via `IntegrityError`, returning the existing row
  (closes the BUG-COURSE-002 TOCTOU, `course.py:402-416`;
  [data-model/course-content](../data-model/course-content.md)).
- **Body proxy**: raw Markdown comes from the vendored content
  repository (`aptitude-course` pin); a broken repository surfaces as
  502 `content_unavailable` rather than a 500 (`course.py:484-507`).
- **Site resources** (issue #395) are manifest-driven, auth-required but
  not stage-gated; "without a usable manifest — the bootstrap state
  before the first content pin — the list is simply empty"
  (`course.py:577-590`); unknown slugs are plain 404s
  (`course.py:614-618`).
- **Stage intro** is ungated by `release_day` but gated by stage unlock
  (`course.py:646-651`).

DTOs: `backend/src/schemas/course.py`. Content pinning/manifest:
`backend/src/content_config.py` (see
[infrastructure](../infrastructure.md)).

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
