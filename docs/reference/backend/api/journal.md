# API — journal router

`backend/src/routers/journal.py` (1289 lines) — the second-largest
router. `APIRouter(prefix="/journal", tags=["journal"])`
(`journal.py:127`). The journal floor plus the resonance/suggestion
surfaces. (The stateless transcription route lives in
[transcription](transcription.md); quote promotion in
[promotions](promotions.md).)

## Endpoint table (all 11 routes)

| Method | Path | Rate limit | Auth | Request | Response | Success | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- |
| POST | `/journal/` | — | JWT | `JournalMessageCreate` | `JournalMessageResponse` | **201** | 422 `message_too_long` / `entry_date_in_future`; 409 `reflection_scope_taken` (`journal.py:110,179,284`) |
| GET | `/journal/` | 30/minute | JWT | `_ListFilters` query | `JournalListResponse` | 200 | 422 (search term outside 3..64 chars) |
| GET | `/journal/{entry_id}` | — | JWT + owned | — | `JournalMessageResponse` | 200 | 404 (missing, soft-deleted, or foreign — enumeration-safe) |
| PATCH | `/journal/{entry_id}` | — | JWT | `JournalEntryUpdate` | `JournalMessageResponse` | 200 | 404; 409 `reflection_scope_taken`; 422 |
| DELETE | `/journal/{entry_id}` | — | JWT + owned | — | — | **204** | 404 |
| POST | `/journal/{entry_id}/resonance` | 10/minute | JWT | — | `ResonanceResponse` | 200 | 404; 402 (wallet empty); 502 `llm_provider_error` |
| GET | `/journal/{entry_id}/marginalia` | — | JWT | — | `MarginaliaListResponse` | 200 | 404 |
| GET | `/journal/{entry_id}/suggestions?status=` | — | JWT | optional status filter | `CompletionSuggestionListResponse` | 200 | 404 |
| POST | `/journal/suggestions/{id}/accept` | — | JWT | — | `AcceptSuggestionResponse` | 200 (idempotent re-accept) | 404 `completion_suggestion_not_found` / `goal_not_found`; 409 `suggestion_dismissed`; 403 `stage_locked` (`journal.py:1098`) |
| POST | `/journal/suggestions/{id}/dismiss` | — | JWT | — | `CompletionSuggestionResponse` | 200 (idempotent) | 404; 409 `suggestion_accepted` |
| POST | `/journal/marginalia/{id}/essay` | 10/minute | JWT (+ optional `X-LLM-API-Key`) | — | `MarginaliaResponse` | 200 (cached after first call) | 404 `marginalia_not_found` / `journal_entry_not_found`; 502 `llm_provider_error` |

## Write path

- **Create** sanitizes the body at the router boundary (BUG-JOURNAL-003)
  so the persisted row "has no control characters, zero-width, or bidi-
  override codepoints — defense against stored-XSS payloads in journal
  renderers and Trojan-Source smuggling in log viewers"
  (`journal.py:259-265`). Backdated entries pin to noon UTC
  (`BACKDATED_ENTRY_NOON_UTC_HOUR = 12`, `journal.py:164`) and a future
  `entry_date` is 422 (`journal.py:179`). A hierarchical-reflection
  scope collision maps the partial-unique-index `IntegrityError` to 409
  `reflection_scope_taken` (`journal.py:284`;
  [data-model/journal-reflection](../data-model/journal-reflection.md)).
  When a vault is connected, the entry is ingested and `vault_ref` /
  `vault_tags` recorded.
- **Update** re-sanitizes an edited body, invokes the marginalia
  re-anchor seam ([domain/marginalia-anchoring](../domain/marginalia-anchoring.md)),
  refreshes `updated_at`, and re-ingests to the vault when `message` or
  `classification` changed (`_VAULT_REINGEST_FIELDS`,
  `journal.py:192,479-485`).
- **Delete is soft** (BUG-JOURNAL-007): stamps `deleted_at` instead of
  a hard DELETE, preserving the `LLMUsageLog.journal_entry_id` audit
  trail and allowing recovery; every read path filters
  `deleted_at IS NULL` (`journal.py:1266-1280`).

## Read path

Listing excludes soft-deleted rows and supports filters including search
(term length 3..64, `JOURNAL_SEARCH_MIN_LENGTH` /
`JOURNAL_SEARCH_MAX_LENGTH`, `journal.py:135-136`); because bodies are
encrypted at rest, search scans decrypted content in memory and warns
past `_ENCRYPTED_SCAN_WARN_THRESHOLD = 2000` rows (`journal.py:141`).
Ordering follows the `(timestamp DESC, id DESC)` composite index so
backdated entries sort by date
(`backend/src/models/journal_entry.py:154-159`).

## `POST /{entry_id}/resonance` — the Higher Self pass

The full contract (`journal.py:876-896`): wallet pre-flight deducts one
message (402 when out of capacity); the LLM pass + persistence + charge
commit atomically, and "any provider error rolls the deduction back so a
failed pass never charges." The entry is first screened locally by
[domain/safety](../domain/safety.md); on an elevated signal the response
carries the [care surface](../domain/care.md) that "accompanies — never
replaces — the reflection, and is returned even if the LLM pass fails,
so care never depends on the LLM (NORTH-STAR §10)." After commit, a
read-only [contraction](../domain/contraction.md) check may add a warm,
declinable reflection — "never for an intimate entry, whose privacy
floor returns above — and never mutates progression." A connected vault
serves the reflection from the user's corpus when the entry is neither
intimate nor distress-flagged; otherwise the cloud LLM path runs
([domain/resonance](../domain/resonance.md), prior-entry context capped
at `_RESONANCE_PRIOR_LIMIT = 3`, `journal.py:517`).

## Suggestions and essays

- **Accept** logs the completion through the *shared* check-in path
  (`record_goal_completion` — idempotent per goal/day) for habit
  targets, or a journal-attested `PracticeSession` (fallback duration
  `_JOURNAL_ATTESTED_FALLBACK_MINUTES = 1.0`, `journal.py:1056`) for
  practice targets; re-accept is an idempotent no-op; accepting a
  dismissed suggestion is a 409 illegal transition
  (`journal.py:1142-1154`). Logging into a locked stage is 403
  `stage_locked` (`journal.py:1098`).
- **Dismiss** mirrors it: idempotent, 409 `suggestion_accepted` for the
  reverse illegal transition (`journal.py:1162-1173`).
- **Essay expansion** is lazy and cached — "once `essay` is set the
  cached value is returned without another LLM call"; free by default
  (`ESSAY_PRICE_UNITS = 0`, `journal.py:1185,1210-1215`).

DTOs: `backend/src/schemas/journal.py`, `schemas/marginalia.py`,
`schemas/completion_suggestion.py`.

---

*Grounded in adepthood@fbc529d, 2026-07-31.*
