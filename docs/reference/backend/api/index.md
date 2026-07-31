# Backend API reference

One page per router module in `backend/src/routers/`. **Covers all 27
routers** (28 files minus `__init__.py`), enumerated from the directory
listing and cross-checked against the 27 `app.include_router` calls in
`backend/src/main.py:592-618` — none sampled.

| Page | Module | Prefix | Concern |
| --- | --- | --- | --- |
| [admin](admin.md) | `admin.py` | `/admin` | Usage stats, stage-progress audit/repair, retention sweeps |
| [auth](auth.md) | `auth.py` | `/auth` | Signup, login, JWT refresh, password reset, social sign-in |
| [botmason](botmason.md) | `botmason.py` | `/user/*` | Wallet balance / usage / admin credit |
| [course](course.md) | `course.py` | `/course` | Drip-fed content, read tracking, body proxy |
| [depth-preferences](depth-preferences.md) | `depth_preferences.py` | `/depth-preferences` | Ring toggles |
| [energy](energy.md) | `energy.py` | `/v1/energy` | Energy plan generation |
| [goal-completions](goal-completions.md) | `goal_completions.py` | `/goal_completions` | Check-ins |
| [goal-groups](goal-groups.md) | `goal_groups.py` | `/goal-groups` | Tier-group CRUD + templates |
| [goals](goals.md) | `goals.py` | `/goals` | Goal field edits |
| [gumroad](gumroad.md) | `gumroad.py` | `/webhooks/gumroad` | Sale/reversal webhooks |
| [habits](habits.md) | `habits.py` | `/habits` | Habit CRUD, stats, bulk operations |
| [invitations](invitations.md) | `invitations.py` | `/invitations` | Resonant invitations: list + decline |
| [journal](journal.md) | `journal.py` | `/journal` | Entries, resonance, marginalia, suggestions |
| [metta-return](metta-return.md) | `metta_return.py` | `/metta-return` | The five-week Return arc lifecycle |
| [practice-recipes](practice-recipes.md) | `practice_recipes.py` | `/practice-recipes` | Recipe library + apply |
| [practice-sessions](practice-sessions.md) | `practice_sessions.py` | `/practice-sessions` | Session logging, insights |
| [practice-share](practice-share.md) | `practice_share.py` | `/practices/share…` | Share links |
| [practice-tags](practice-tags.md) | `practice_tags.py` | `/practice-tags` | Tag library |
| [practices](practices.md) | `practices.py` | `/practices` | Catalog browse + submit |
| [prompts](prompts.md) | `prompts.py` | `/prompts` | Weekly prompts + responses |
| [promotions](promotions.md) | `promotions.py` | `/journal/...`, `/promotions/...` | Quote promotion |
| [reflections](reflections.md) | `reflections.py` | `/reflections` | Due reflections + source resolution |
| [stages](stages.md) | `stages.py` | `/stages` | Stage list, calendar, wheel, advancement |
| [transcription](transcription.md) | `transcription.py` | `/journal/transcribe-page` | Handwriting transcription |
| [ui-flags](ui-flags.md) | `ui_flags.py` | `/ui-flags` | One-time UI state |
| [user-practices](user-practices.md) | `user_practices.py` | `/user-practices` | Practice selection + overrides |
| [users](users.md) | `users.py` | `/users` | Profile (timezone) |

## Cross-cutting conventions

- **Auth**: nearly every route depends on
  `routers.auth.get_current_user` (JWT → `int` user id); admin routes
  layer `dependencies.auth.require_admin`
  (`backend/src/dependencies/auth.py:39-51`). The exceptions: the
  Gumroad webhook (shared secret) and the auth router's own
  unauthenticated routes.
- **Errors** use the stable snake_case helpers in
  `backend/src/errors.py` (`{"detail": "..."}` bodies); unhandled
  exceptions get the sanitized `{error, request_id}` 500 envelope — see
  [infrastructure](../infrastructure.md#error-helpers-backendsrcerrorspy).
- **Ownership** goes through `backend/src/dependencies/ownership.py`:
  per-resource dependencies with either the canonical 404 (missing) /
  403 (cross-user, audited via `resource_access_denied` WARNINGs) split,
  or the fully-collapsed enumeration-safe 404 for sensitive surfaces
  (journal entries, goals, invitations, course content).
- **Pagination** (`backend/src/schemas/pagination.py`): list endpoints
  take `PaginationParams` and return the `Page[...]` envelope when
  `?paginate=true`, else the legacy bare list "for one release while the
  frontend migrates" (BUG-INFRA-012/-014/-015/-016/-017/-018).
- **Timezone-aware day math** flows through the request-scoped
  `current_user_timezone` dependency
  (`backend/src/dependencies/timezone.py:30-40`) — at most one lookup
  per request.
- **Rate limits** use slowapi's `limiter` (`backend/src/rate_limit.py`),
  IP-keyed by default with `per_user_rate_limit_key` for user-scoped
  caps.
- **Idempotency**: money- and history-touching writes are idempotent by
  DB constraint (energy plans, practice sessions, check-ins, content
  read-marks, prompt responses, Gumroad pings) rather than by
  application-level pre-checks alone.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
