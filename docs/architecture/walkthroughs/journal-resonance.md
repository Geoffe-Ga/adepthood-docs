# Walkthrough: journal entry → Higher Self resonance

A journal entry from creation to the resonance pass — the privacy floor,
the care screen, the wallet charge, the literary marginalia, completion
detection — and how the resulting suggestion surfaces in the UI as a
declinable invitation whose acceptance records a real habit check-in.
This is the graduated-engagement principle as implemented: the system
notices, asks quietly, and takes "Not now" for an answer. All paths are
repo-relative to `Geoffe-Ga/adepthood`.

## Creating the entry

1. **Autosave creates.** The journal editor's autosave calls
   `journal.create` exactly once for an id-less draft — overlapping
   saves are serialized so "two id-less saves can't each fire
   `journal.create`"
   (`frontend/src/features/Journal/JournalEntryScreen.tsx:165` and
   `685-688`).

2. **`POST /journal/`.** `create_journal_entry` sanitizes the body at
   the router boundary — control characters, zero-width, and
   bidi-override codepoints are stripped as "defense against
   stored-XSS payloads in journal renderers and Trojan-Source
   smuggling in log viewers" (BUG-JOURNAL-003,
   `backend/src/routers/journal.py:252-290`, sanitizer at `96`). The
   DTO is `JournalMessageCreate`
   (`backend/src/schemas/journal.py:60`); the row is stamped
   `sender="user"` with the authenticated `user_id`
   (`backend/src/routers/journal.py:275`), committed, and returned as
   a 201.

## Requesting resonance

1. **One pass at a time.** Tapping *Get Resonance* runs
   `requestResonance`, guarded by an in-flight ref — "one pass at a
   time — no double-charge" — which first flushes the draft (so the
   pass runs against the saved text) and errors on an empty body
   without any network call
   (`frontend/src/features/Journal/useResonance.ts:180-201`, hook
   wired at
   `frontend/src/features/Journal/JournalEntryScreen.tsx:1719`).

2. **The call.** `resonance.generate(entryId)` POSTs
   `/journal/{entry_id}/resonance`, Zod-validating the response
   (`frontend/src/api/index.ts:1599-1608`).

3. **The route.** `run_resonance` (rate-limited 10/minute) loads the
   entry ownership-scoped — a missing or foreign entry is a
   `404 journal_entry` (`backend/src/routers/journal.py:867-905`).

4. **Care screen first, locally.** The entry is screened for an
   acute-distress signal with a pure, local check — no cloud, no
   charge, no log (`backend/src/routers/journal.py:639-651`, invoked
   at `905`). On an elevated signal the response will carry a `care`
   surface that "accompanies — never replaces — the reflection"
   (NORTH-STAR §10, `backend/src/routers/journal.py:889-894`).

5. **The privacy floor.** An entry persisted with the `INTIMATE`
   classification is *never* sent to a cloud LLM: the route returns a
   private response "before wallet charge, LLM construction, or
   usage-log write — so the cloud is provably unreachable for intimate
   entries" (issue #895, `backend/src/routers/journal.py:906-912`):

    ```python
    care = _care_response(_care_for(entry.message))
    if entry.classification == JournalClassification.INTIMATE:
        return await _private_response(session, current_user, care)
    ```

6. **Wallet pre-flight.** One BotMason message is deducted up front;
   when the monthly counter (cap `BOTMASON_MONTHLY_CAP`, default 50 —
   `backend/src/services/usage.py:24` and `33-45`) and the offering
   balance are both empty, the route raises
   `402 insufficient_offerings`
   (`backend/src/services/wallet.py:299-318`).

7. **The literary pass.** The reflection LLM — the connected Creek
   Vault corpus when eligible, else the local cloud LLM
   (`backend/src/routers/journal.py:913-919`) — produces margin notes
   that the server anchors in the text
   (`_generate_marginalia_or_502`,
   `backend/src/routers/journal.py:623`; persisted at `557` and
   `759-770`).

8. **Completion detection, same pass.** `_detect_and_persist_suggestions`
   gathers the user's real tracked habits and practices as indexed
   candidates (`gather_candidates`,
   `backend/src/services/completion_candidates.py:111`) — with no
   candidates the LLM is never called, "a hard cost guard"
   (`backend/src/domain/detection.py:180-186`) — then asks the model
   which candidates the writer *actually did*
   (`backend/src/routers/journal.py:601-620`). The prompt excludes
   intentions and avoidance
   (`backend/src/domain/detection.py:68-96`):

    ```text
    - Only count things the writer actually did/completed — NOT things
      they planned, intended, wanted, hoped, or AVOIDED (skipping a bad
      habit is not a completion).
    ```

    The trust model never believes the model's ids or offsets: it may
    only return a candidate **index** plus a **verbatim quote**, which
    the server re-anchors in the body itself; anything that does not
    resolve cleanly is dropped, duplicates are removed, and hits are
    capped at `MAX_HITS = 5`
    (`backend/src/domain/detection.py:1-12`, `30`, `124-175`).
    Surviving hits are staged as `PENDING` `CompletionSuggestion` rows
    (`backend/src/routers/journal.py:578-599`).

9. **Commit and respond.** Usage is recorded, the transaction commits,
   and — on this healthy, non-intimate path only — a read-only
   contraction check may add a "warm, declinable" reflection when the
   habit foundation has thinned; it "never writes and never touches
   progression" (`backend/src/routers/journal.py:782-817`, invoked at
   `938-940`). The `ResonanceResponse` carries the marginalia, the
   suggestions, refreshed balances
   (`remaining_messages = max(cap - monthly_used, 0)`), and the
   optional `care` / `contraction` surfaces
   (`backend/src/routers/journal.py:818-853`; response schema
   documented at `backend/src/schemas/marginalia.py:76-96`).

## The invitation in the UI

1. **Merge, don't replace.** The hook merges returned marginalia and
   suggestions into local state and normalizes the optional surfaces
   to `null` so a distressed-then-calm sequence never leaves a stale
   crisis banner
   (`frontend/src/features/Journal/useResonance.ts:186-211`).

2. **The margin card.** Each pending suggestion renders a
   `CompletionSuggestionNote` pinned next to the sentence the writer
   wrote — "You wrote about **Daily run**. Check it off?" — with a
   clear **OK** and a quiet **Not now**
   (`frontend/src/features/Journal/JournalEntryScreen.tsx:1468`,
   `frontend/src/features/Journal/CompletionSuggestionNote.tsx:1-12`,
   labels at `30-36`). Dismissed suggestions render nothing; there is
   no nag path.

3. **Accepting.** OK calls `completionSuggestions.accept(id)` →
   `POST /journal/suggestions/{suggestion_id}/accept`
   (`frontend/src/api/index.ts:1647-1650`;
   `frontend/src/features/Journal/useResonance.ts:105-126`).

4. **The same check-in path.** For a habit suggestion the server logs
   *today's* completion through the exact `record_goal_completion`
   service the Habits screen uses — identical streak and milestone
   math — then flips the row to `ACCEPTED`
   (`backend/src/routers/journal.py:1036-1052` and `1135-1160`). The
   response returns the updated suggestion plus the `CheckInResult`,
   and the card settles into "✓ Checked off — N-day streak"
   (`frontend/src/features/Journal/CompletionSuggestionNote.tsx:38-42`).
   A practice suggestion instead records a journal-attested
   `PracticeSession` (no streak — `check_in` is `null`), idempotent
   via the key `accept-suggestion:practice:{id}`
   (`backend/src/routers/journal.py:1080-1118`).

## Failure modes

- **Empty draft** — the hook refuses locally: "Write a little first,
  then ask for its resonance."
  (`frontend/src/features/Journal/useResonance.ts:34` and `198-200`).
- **Out of capacity** — `402 insufficient_offerings` before any LLM
  call (`backend/src/services/wallet.py:318`).
- **LLM provider failure** — the pass raises
  `502 llm_provider_error` and "any provider error rolls the
  deduction back so a failed pass never charges"
  (`backend/src/routers/journal.py:874-877`). If the entry was
  care-flagged, the 502 is swallowed and a care-only response is
  returned instead — "care must never depend on the LLM succeeding"
  (`backend/src/routers/journal.py:737-757` and `922-925`).
- **Detection failure is invisible** — a provider error during
  completion detection is swallowed and returns `[]`; "detection is
  strictly additive" and never rolls back the literary pass or the
  charge (`backend/src/routers/journal.py:601-617`).
- **Malformed model output** — non-verbatim quotes, unknown indexes,
  or oversized labels are silently dropped during anchoring rather
  than trusted (`backend/src/domain/detection.py:124-146`).
- **Accepting a dismissed suggestion** — `409 suggestion_dismissed`;
  re-accepting an accepted one is an idempotent no-op that re-derives
  the streak without writing
  (`backend/src/routers/journal.py:1120-1160`).
- **Locked stage** — attesting a practice for a stage the user has
  not unlocked is rejected `403 stage_locked` before any write
  (`backend/src/routers/journal.py:1090-1101`).
- **Duplicate scoped entry** — the create route maps the partial
  unique index violation to `409 reflection_scope_taken`
  (`backend/src/routers/journal.py:277-285`).

*Grounded in Geoffe-Ga/adepthood@55eef11, 2026-07-31.*
