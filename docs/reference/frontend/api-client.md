# API client

The HTTP layer lives in `frontend/src/api/` (5 files): `index.ts` (the
client and all 26 endpoint namespaces), `schemas.ts` (Zod runtime
validators), `errorMessages.ts` (error → user-copy mapping),
`flattenGoalCompletions.ts`, and `practiceShare.ts` (a re-export module
giving the share surface a discoverable path, `practiceShare.ts:1-20`).

## Client setup

### Base URL

`API_BASE_URL` comes from `EXPO_PUBLIC_API_BASE_URL`; production builds must
use HTTPS or a `CONFIG_ERROR` is captured (not thrown — a top-level throw
would blank the screen before React mounts) and App.tsx renders a visible
error screen. Trailing slashes are stripped so `${API_BASE_URL}${path}`
can't produce `//auth/signup` (`frontend/src/config.ts:1-36`).

### Auth wiring — getter/callback seams

The client holds module-level seams that `AuthContext` registers on mount
(`frontend/src/api/index.ts:200,236-238,273-286`;
`frontend/src/context/AuthContext.tsx:321-346`):

- `setTokenGetter` — polled per request; the resolved token is attached as
  `Authorization: Bearer <token>` (`index.ts:330-347`).
- `setOnUnauthorized(reason)` — fired when a 401 survives the refresh path;
  `reason` is the `UnauthorizedReason` union
  `'session_expired' | 'invalid_token' | 'not_authenticated'`
  (BUG-API-018, `index.ts:202-224`).
- `setOnTokenRefreshed(token, timezone, expectedPriorToken)` — lets the
  AuthContext persist a refreshed JWT with an identity guard against stale
  refreshes (`index.ts:225-237`).
- `setLlmApiKeyGetter` / `setLlmApiKeyReset` — the BYOK key bridge; when a
  key is registered, LLM endpoints attach `X-LLM-API-Key`
  (`index.ts:238-315,1364-1371`).
- `setNetworkOnlineGetter` — registered by `NetworkStatusProvider`; known
  offline GETs fail fast with `ApiError(0, 'network_error')` instead of
  stalling to the timeout (`index.ts:189-198,840-845`,
  `frontend/src/context/NetworkStatusContext.tsx:43-63`).

### Timeouts, retries, and idempotency

`request()` (`index.ts:816-857`) drives every wrapper:

- `FETCH_TIMEOUT_MS = 30_000`; each attempt runs through
  `fetchWithTimeout`, which merges an `AbortController` timeout with any
  caller signal and throws `ApiTimeoutError` when the clock wins
  (`index.ts:85,399-430`). Transcription overrides to 60 s
  (`TRANSCRIBE_TIMEOUT_MS`, `index.ts:162-167`).
- Up to `MAX_RETRIES = 2` retries after the initial attempt, exponential
  backoff 500 ms doubling to a 2 000 ms cap with 100 % jitter
  (`index.ts:87-90,388-397`).
- Retry eligibility: safe methods (`GET`, `HEAD`, `OPTIONS`, `DELETE`)
  always; mutations only when they carry an idempotency header
  (`index.ts:95-98,372-375`). Transient statuses are
  `408, 429, 500, 502, 503, 504` — every transient class except 401
  (`index.ts:92-93`).
- `idempotencyKey(intent, ...parts)` builds deterministic
  `intent[:part]*` keys — wall-clock values are deliberately forbidden so
  the built-in retry loop and a user retry surface the *same* key and the
  backend dedupes (BUG-API-008, `index.ts:249-271`). Header name:
  `Idempotency-Key` (`index.ts:245-249`).

### 401 handling and token refresh

On a 401, `attemptRequest` stashes the response detail and routes through
`handleUnauthorizedRetry` (`index.ts:754-789`):

- Auth-path requests (`/auth/*`) and `invalid_credentials` details never
  trigger the global callback — login forms own those 401s
  (`index.ts:715-731`).
- Otherwise the client attempts one token refresh and replays the request.
  Concurrent 401s coalesce onto a single in-flight refresh promise
  (audit-contracts-05, `index.ts:549-625`). The refresh response is
  validated with `loginAuthResponseSchema` so a `{}` body becomes a refresh
  failure rather than a `Bearer undefined` zombie session
  (BUG-API-007/017, `index.ts:575-599`).
- `reasonForUnauthorized(detail, hadToken)`: an anonymous request is always
  `'not_authenticated'`; with a token, `classifyUnauthorizedDetail` maps the
  backend's stable detail vocabulary (`unauthorized` → `session_expired`,
  `invalid_token` → itself, `invalid_credentials` → `null`)
  (`index.ts:472-509,659-678`).

### Response validation

Wrappers may pass a Zod `schema`; `parseResponse` then validates and throws
a typed `ApiValidationError` (with the issue list logged, full body only in
`__DEV__`) on mismatch (BUG-FRONTEND-INFRA-024, `index.ts:516-547`). Error
classes: `ApiError { status, detail }` (`index.ts:100-110`),
`ApiValidationError` (`:118-130`), `ApiTimeoutError` (`:132-138`), and the
transcription-specific `TranscriptionError` with a closed `kind` taxonomy
that never carries the image payload (`:143-187,1373-1425`).

### Pagination

`fetchAllPages(fetchPage)` drains the shared `Page<T>` envelope
(`{ items, total, limit, offset, has_more }`, `schemas.ts:38-54`) into one
flat array, with an empty-page guard against a server looping on
`has_more: true` (`index.ts:1020-1060`). `pageQuery` always opts in via
`paginate=true` (`index.ts:1028-1039`).

### Trailing-slash discipline

Collection URLs mirror each FastAPI route's declared form exactly, because a
307 redirect can drop `Authorization` (or downgrade https behind a proxy):
`/habits/`, `/journal/`, `/goal_completions/` keep the slash;
`/stages`, `/depth-preferences`, `/ui-flags`, `/invitations`,
`/metta-return` are served without one (`index.ts:1062-1068,1437-1440,
1875,2855-2857,2892-2895`).

## Complete endpoint-wrapper table

26 namespaces, **93 methods**, enumerated from `frontend/src/api/index.ts`.
"Validated" names the Zod schema passed to `request()`; "—" means the
response is trusted to the TS type only. Backend routes are cited by router
module (all under `backend/src/routers/`).

### habits (`index.ts:1069-1114`) → `habits.py` (prefix `/habits`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `list` | GET | `/habits/` | `z.array(habitWithGoalsSchema)` — retained as wire-contract guard; screens use `listAll` (`:1070-1076`) |
| `listAll` | GET | `/habits/?paginate=true…` (drained) | `pageSchema(habitWithGoalsSchema)` |
| `create` | POST | `/habits/` | — |
| `update` | PUT | `/habits/{id}` | — |
| `updateGoalUnits` | PUT | `/habits/{id}/goals/units` | — (atomic all-tier unit update, issue #289) |
| `delete` | DELETE | `/habits/{id}` | — |
| `clearCompletions` | DELETE | `/habits/{id}/completions` | — |
| `getStats` | GET | `/habits/{id}/stats` | — |

### goalCompletions (`index.ts:1133-1156`) → `goal_completions.py` (prefix `/goal_completions`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `create` | POST | `/goal_completions/` | — ; accepts an optional caller idempotency key (`log-unit:{goalId}:{dayISO}` pattern) |

### goals (`index.ts:1181-1185`) → `goals.py` (prefix `/goals`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `update` | PUT | `/goals/{id}` | — (full-replace PUT; `habit_id` excluded — backend forbids reparenting, `backend/src/schemas/goal.py` `GoalUpdate`) |

### goalGroups (`index.ts:1188-1201`) → `goal_groups.py` (prefix `/goal-groups`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `list` | GET | `/goal-groups/` | `z.array(apiGoalGroupSchema)` |
| `get` | GET | `/goal-groups/{id}` | `apiGoalGroupSchema` |

### journal (`index.ts:1427-1497`) → `journal.py` + `transcription.py` (prefix `/journal`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `list` | GET | `/journal/?search&tag&practice_session_id&limit&offset` | `journalListResponseSchema` |
| `get` | GET | `/journal/{entryId}` | — |
| `create` | POST | `/journal/` | — |
| `update` | PATCH | `/journal/{entryId}` | — (sparse patch; `undefined` fields dropped by JSON) |
| `delete` | DELETE | `/journal/{entryId}` | — |
| `transcribePage` | POST | `/journal/transcribe-page` | `transcribePageSchema`; 60 s timeout, BYOK header, deliberately non-idempotent (charges a wallet unit), errors mapped to `TranscriptionError` (`:1470-1496`) |

### promotions (`index.ts:1510-1548`) → `journal.py`

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `create` | POST | `/journal/{entryId}/promote` | `promotedQuoteSchema` |
| `remove` | DELETE | `/promotions/{id}` | — |
| `setIncluded` | PATCH | `/promotions/{id}` | `promotedQuoteSchema` |
| `list` | GET | `/journal/{entryId}/promotions` | `z.array(promotedQuoteSchema)` |

### reflections (`index.ts:1565-1592`) → `reflections.py` (prefix `/reflections`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `due` | GET | `/reflections/due` | `reflectionDueResponseSchema` |
| `sources` | GET | `/reflections/sources?level&scope_key` (scope key URL-encoded — `c1:s3` → `c1%3As3`) | `reflectionSourcesResponseSchema` |

### resonance (`index.ts:1594-1621`) → `journal.py`

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `generate` | POST | `/journal/{entryId}/resonance` | `resonanceResponseSchema`; BYOK header; may surface `402 insufficient_offerings` / `502 llm_provider_error` |
| `list` | GET | `/journal/{entryId}/marginalia` | — |
| `essay` | POST | `/journal/marginalia/{id}/essay` | — ; BYOK header |

### completionSuggestions (`index.ts:1633-1662`) → `journal.py`

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `list` | GET | `/journal/{entryId}/suggestions` | `completionSuggestionListResponseSchema` |
| `accept` | POST | `/journal/suggestions/{id}/accept` | `acceptSuggestionResultSchema`; idempotency key `accept-suggestion:{id}` |
| `dismiss` | POST | `/journal/suggestions/{id}/dismiss` | `completionSuggestionSchema` |

### invitations (`index.ts:1672-1693`) → `invitations.py` (prefix `/invitations`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `list` | GET | `/invitations` | `z.array(invitationSchema)` (bare array, no envelope) |
| `dismiss` | POST | `/invitations/{id}/dismiss` | — ; idempotency key `dismiss-invitation:{id}`; the 200 body is intentionally dropped as `void` |

### mettaReturn (`index.ts:1701-1768`) → `metta_return.py` (prefix `/metta-return`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `state` | GET | `/metta-return` | `mettaReturnStateSchema` |
| `start` | POST | `/metta-return/arc` | `returnArcSchema`; idempotency key `start-return` |
| `pause` | POST | `/metta-return/arc/pause` | `returnArcSchema` |
| `resume` | POST | `/metta-return/arc/resume` | `returnArcSchema` |
| `leave` | POST | `/metta-return/arc/leave` | `returnArcSchema` |
| `dismissOffer` | POST | `/metta-return/offer/dismiss` | `mettaReturnStateSchema` |
| `release` | POST | `/metta-return/arc/release` | `z.array(releasedHabitSchema)` |
| `recommit` | POST | `/metta-return/arc/recommit` | `z.array(releasedHabitSchema)` |

### prompts (`index.ts:1787-1816`) → `prompts.py` (prefix `/prompts`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `current` | GET | `/prompts/current` | — |
| `respond` | POST | `/prompts/{weekNumber}/respond` | — |
| `history` | GET | `/prompts/history?limit&offset` | `promptListResponseSchema` (`total` is nullable — see drift list) |

### stages (`index.ts:1874-1902`) → `stages.py` (prefix `/stages`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `listAll` | GET | `/stages?paginate=true…` (drained; no trailing slash) | `pageSchema(stageSchema)` |
| `history` | GET | `/stages/{stageNumber}/history` | — |
| `beginAgain` | POST | `/stages/begin-again` | `stageProgressRecordSchema` |
| `programCalendar` | GET | `/stages/program-calendar` | `programCalendarSchema` |

### wheel (`index.ts:1910-1921`) → `stages.py`

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `get` | GET | `/stages/wheel` | `wheelBalanceSchema` |

### course (`index.ts:1972-2009`) → `course.py` (prefix `/course`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `stageContentAll` | GET | `/course/stages/{n}/content?paginate=true…` (drained) | `pageSchema(contentItemSchema)` |
| `markRead` | POST | `/course/content/{id}/mark-read` | — |
| `stageProgress` | GET | `/course/stages/{n}/progress` | — |
| `contentBody` | GET | `/course/content/{id}/body` | — |
| `siteResources` | GET | `/course/site-resources` | — |
| `siteResourceBody` | GET | `/course/site-resources/{slug}/body` | — |
| `stageIntro` | GET | `/course/stages/{n}/intro` | `stageIntroSchema` |
| `stageIntroBody` | GET | `/course/stages/{n}/intro/body` | — |

### practices (`index.ts:2237-2280`) → `practices.py` (prefix `/practices`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `listAll` | GET | `/practices/?paginate=true&stage_number={n}[&include_mine=true]` (drained) | `pageSchema(practiceItemSchema)`; `includeMine` adds the caller's unapproved drafts (custom-practices-07) |
| `get` | GET | `/practices/{id}` | `practiceItemSchema` |
| `create` | POST | `/practices/` | — (drafts land `approved=false`) |

### userPractices (`index.ts:2282-2318`) → `user_practices.py` (prefix `/user-practices`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `create` | POST | `/user-practices/` | `userPracticeSchema` |
| `list` | GET | `/user-practices/` | `z.array(userPracticeSchema)` |
| `customize` | PATCH | `/user-practices/{id}/customize` | `userPracticeSchema`; `null` clears an override, absent leaves it (ritual-03) |

### practiceTags (`index.ts:2350-2373`) → `practice_tags.py` (prefix `/practice-tags`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `list` | GET | `/practice-tags/` | `z.array(practiceTagSchema)` |
| `create` | POST | `/practice-tags/` | `practiceTagSchema` |
| `update` | PATCH | `/practice-tags/{id}` | `practiceTagSchema` |
| `remove` | DELETE | `/practice-tags/{id}` | — |

### practiceRecipes (`index.ts:2432-2471`) → `practice_recipes.py` (prefix `/practice-recipes`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `list` | GET | `/practice-recipes/[?mode=]` | `z.array(practiceRecipeSchema)` |
| `create` | POST | `/practice-recipes/` | `practiceRecipeSchema` |
| `update` | PATCH | `/practice-recipes/{id}` | `practiceRecipeSchema` |
| `remove` | DELETE | `/practice-recipes/{id}` | — |
| `apply` | POST | `/practice-recipes/{id}/apply-to/{userPracticeId}` | `userPracticeSchema`; cross-mode swaps rejected server-side with `400 mode_mismatch` |

### frequency (`index.ts:2482-2511`) → `user_practices.py`

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `current` | GET | `/user-practices/current/frequency[?stage_number=]` | `frequencyResponseSchema`; `banner_text` is rendered verbatim, never client-assembled (ritual-05) |

### practiceSessions (`index.ts:2513-2532`) → `practice_sessions.py` (prefix `/practice-sessions`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `create` | POST | `/practice-sessions/` | `practiceSessionResponseSchema`; clients send wall-clock `started_at`/`ended_at` and the **server** derives duration (BUG-PRACTICE-006, `:2162-2176`) |
| `weekCount` | GET | `/practice-sessions/week-count` | — |
| `insights` | GET | `/practice-sessions/insights` | — (ritual-04 rollup; `useWeeklyProgress` falls back to `weekCount` on failure) |

### practiceShare (`index.ts:2591-2631`) → `practice_share.py` (prefix `/practices`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `create` | POST | `/practices/{id}/share-link` | — (rate-limited 10/hour server-side) |
| `list` | GET | `/practices/{id}/share-links` | — |
| `preview` | GET | `/practices/share/{token}` | — |
| `import` | POST | `/practices/share/{token}/import` | — |
| `revoke` | DELETE | `/practices/share-links/{id}` | — (idempotent) |

### auth (`index.ts:2722-2818`) → `auth.py` (prefix `/auth`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `login` | POST | `/auth/login` | `loginAuthResponseSchema` (rejects `user_id == 0`, BUG-API-017) |
| `signup` | POST | `/auth/signup` | `authResponseSchema` (`user_id == 0` is the anti-enumeration duplicate-email sentinel, BUG-AUTH-002) |
| `oauthGoogle` | POST | `/auth/oauth/google` | `loginAuthResponseSchema`; anonymous by design |
| `oauthApple` | POST | `/auth/oauth/apple` | `loginAuthResponseSchema`; carries Apple's one-shot `full_name` |
| `refresh` | POST | `/auth/refresh` | `loginAuthResponseSchema` |
| `requestPasswordReset` | POST | `/auth/password-reset/request` | `passwordResetAcceptedSchema` (always 202, anti-enumeration) |
| `confirmPasswordReset` | POST | `/auth/password-reset/confirm` | `loginAuthResponseSchema` (invalidates all other sessions server-side) |
| `cancelPasswordReset` | POST | `/auth/password-reset/cancel` | — (204 regardless of token validity) |

### users (`index.ts:2820-2844`) → `users.py` (prefix `/users`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `updateMyTimezone` | PUT | `/users/me/timezone` | `timezoneReadSchema`; callers push the echoed zone into `AuthContext.setUserTimezone` (issue #261) |

### depthPreferences (`index.ts:2846-2882`) → `depth_preferences.py` (prefix `/depth-preferences`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `get` | GET | `/depth-preferences` | `depthPreferencesSchema` |
| `update` | PATCH | `/depth-preferences` | `depthPreferencesSchema` (partial in, full four-key state echoed back) |

### uiFlags (`index.ts:2884-2919`) → `ui_flags.py` (prefix `/ui-flags`)

| Method | HTTP | Path | Validated |
| --- | --- | --- | --- |
| `get` | GET | `/ui-flags` | `uiFlagsSchema` |
| `update` | PATCH | `/ui-flags` | `uiFlagsSchema` |

### Backend routes with no client wrapper

Enumerated against `backend/src/routers/` for completeness: the `admin.py`
(`/admin`), `energy.py` (`/v1/energy`), and `gumroad.py`
(`/webhooks/gumroad`) routers are server-/webhook-only; and the client sends
nothing to `GET /goal-groups/…` write routes
(`POST/PUT/DELETE`, `goal_groups.py:116-190`), `GET /prompts/{week_number}`
(`prompts.py:191`), `PUT /stages/progress` (`stages.py:409`),
`GET /stages/{n}/progress` (`stages.py:212`), or the item-level
`GET /practice-tags/{id}` / `GET /practice-recipes/{id}` /
`GET /user-practices/{id}` / `GET /practices/{user_practice_id}` reads.
This is coverage information, not drift.

## TypeScript types vs backend schemas

The TS interfaces in `index.ts` are the compile-time contract; `schemas.ts`
re-checks the wire at runtime because "the TypeScript types … have no
bearing at runtime" (`schemas.ts:1-18`). Where the backend deliberately
omits a field, the client is *absence-tolerant* rather than mirroring the
omission — see the intentional entries below.

### Known drift

Factual differences between the frontend types/validators and the backend
schemas at this commit:

1. **`JournalMessage` drops `reflection_level` / `reflection_scope_key`.**
   Backend `JournalMessageResponse` includes both
   (`backend/src/schemas/journal.py:137-138`), but neither the TS interface
   (`frontend/src/api/index.ts:1237-1255`) nor `journalMessageSchema`
   (`frontend/src/api/schemas.ts:248-270`) carries them. Because Zod strips
   unknown keys, validated `journal.list` responses silently lose the two
   fields; `journal.get` (unvalidated) passes them through at runtime but
   the type doesn't expose them.
2. **Client-optional fields the backend always sends.** `title`, `status`,
   `updated_at`, and `classification` are non-optional on
   `JournalMessageResponse` (`journal.py:124-132`) but `.optional()`
   client-side for fixture/back-compat (`schemas.ts:258-265`). Same pattern
   for `Habit.revealed` / `is_carryover` (`schemas.ts:196-203` vs
   `backend/src/schemas/habit.py:44-45`) and `Stage.manifestations`
   (`schemas.ts:324-326`).
3. **`sender` narrower client-side.** Backend types it `str`
   (`journal.py:128`); the client pins `z.enum(['user', 'bot'])`
   (`schemas.ts:251`). A third sender value would fail whole-list
   validation.
4. **`tier` looser client-side (intentional).** Backend serialises a
   `GoalTier` enum (`backend/src/schemas/goal.py` `Goal.tier`); the client
   accepts any string and narrows via `narrowTier` with a `'clear'`
   fallback so a newly-rolled-out tier can't crater the UI (BUG-010 /
   BUG-FRONTEND-INFRA-010, `schemas.ts:130-141`,
   `index.ts:973-981`).
5. **Ghost `user_id`-family fields.** Backend `OwnedResourcePublic`
   responses omit `user_id` entirely (BUG-T7), and `PracticeResponse` omits
   `submitted_by_user_id` (BUG-PRACTICE-001/BUG-SCHEMA-010) — yet the
   frontend types keep them as optional/nullish fields that the live wire
   never populates (`index.ts:2020-2035`, `schemas.ts:359-368,397-401,
   413-417`). Absence-tolerance is deliberate; the residual type fields are
   drift-adjacent surface.
6. **Stale comment on `userPractices.customize`.** The wrapper notes the
   ritual-03 endpoint is targeted "until that PR lands"
   (`index.ts:2298-2305`); the backend route exists
   (`backend/src/routers/user_practices.py:…` `PATCH /{user_practice_id}/customize`),
   so the code is aligned and only the comment is stale.
7. **`PromptListResponse.total` nullable — matched, worth knowing.**
   Backend returns `int | None`; the client type and schema accept `null`
   and consumers must guard before arithmetic (`index.ts:1779-1785`,
   `schemas.ts:219-228`). Not drift; recorded because the older client
   typed it `number`.
8. **`AuthResponse.timezone` optional client-side** for legacy API builds
   that omit it; consumers fall back to `'UTC'` (`schemas.ts:84-88`,
   `AuthContext.tsx:97-106`).

*Grounded in adepthood@55eef11, 2026-07-31.*
