# State — Zustand stores and persistence

`frontend/src/store/` contains **6 Zustand stores** plus three support
modules: the logout reset registry (`registry.ts`), the normalized-collection
helper (`normalizedCollection.ts`), and the derived program hooks
(`useProgramProgression.ts`). Persistence lives separately in
`frontend/src/storage/` (**16 modules**). Library choice:
[ADR 0003](../../decisions/0003-react-native-expo-zustand.md).

Two architectural rules hold across every store:

1. **Stores are dumb state containers.** API calls live in feature service
   layers — e.g. "No API calls live here; those belong in
   `features/Habits/services/habitManager.ts`"
   (`frontend/src/store/useHabitStore.ts:9-11`); the stage equivalent is
   `features/Map/services/stageService.ts`
   (`frontend/src/store/useStageStore.ts:9-11`). The two exceptions are
   `useDepthPreferencesStore` and `useWelcomeStore`, whose actions call the
   API directly (`useDepthPreferencesStore.ts:50-67`,
   `useWelcomeStore.ts:60-66`).
2. **Every store registers a reset.** `registerStoreReset` publishes each
   store's `reset` at module load; `resetAllStores()` — called from
   `AuthContext`'s logout teardown — invokes them all, tolerating a thrown
   reset so one failure can't strand another store's data
   (BUG-FE-STATE-001, `frontend/src/store/registry.ts:18-36`,
   `frontend/src/context/AuthContext.tsx:201-220`).

## Store-by-store state shapes

### `useHabitStore` (`frontend/src/store/useHabitStore.ts`)

| Field | Type | Purpose |
| --- | --- | --- |
| `habitsById` | `Record<number, Habit>` | canonical ID-keyed map, O(1) lookup (`:19-20`) |
| `habitOrder` | `number[]` | insertion order preserved across mutations (`:21-22`) |
| `habits` | `Habit[]` | derived array cache kept in sync by actions (`:23-24`) |
| `loading` | `boolean` | (`:25`) |
| `error` | `string \| null` | (`:26`) |

Actions: `setHabits`, `setLoading`, `setError`, `updateHabit` (no-op for
unknown ids), `removeHabit`, `reset` (`:28-34,54-75`). Selector:
`selectHabitById(id)` returns a **cached** per-id closure so Zustand's slice
ref stays warm instead of re-subscribing every render (BUG-FE-STATE-002,
`:104-117`).

### `useStageStore` (`frontend/src/store/useStageStore.ts`)

| Field | Type | Purpose |
| --- | --- | --- |
| `stagesByNumber` | `Record<number, StageData>` | keyed by `stageNumber` (`:19-21`) |
| `stageOrder` | `number[]` | display order — descending, stage 10 first (`:22-23`) |
| `stages` | `StageData[]` | derived cache (`:24`) |
| `currentStage` | `number` | initial `1` (`:25,48`) |
| `cycleNumber` | `number` | which pass through the arc; initial `1` (`:26-27,49`) |
| `loading` / `error` | `boolean` / `string \| null` | (`:28-29`) |
| `hasAttempted` | `boolean` | whether a load has started since last reset (`:30-31`) |

Actions: `setStages`, `setCurrentStage`, `setCycleNumber`, `setLoading`,
`setError`, `markAttempted`, `updateStageProgress`, `reset` (`:33-41,64-96`).
`updateStageProgress` on an unknown stage logs a warning instead of silently
returning — surfacing client/backend stage-set drift without breaking the
render (BUG-FE-STATE-003, `:74-88`). Six value selectors are exported
(`:109-115`).

### `useProgramStore` (`frontend/src/store/useProgramStore.ts`)

The "master clock for the 36-week journey: drives BotMason week, active
practice, course unlock, and map stage" (`:1`).

| Field | Type | Purpose |
| --- | --- | --- |
| `programStartDate` | `Date \| null` | the program anchor, normalized to local midnight (`:22,34-38`) |

Actions: `setProgramStartDate` (persists via `programStorage`, `:50-54`),
`hydrateProgramStartDate` (seed from storage without re-writing, `:55-58`),
`reset` (also clears storage, `:59-62`). Pure helpers exported alongside:
`programDayOffset`, `programWeek` (clamped 1..36), `daysUntilStage`,
`programStage` (walks `STAGE_DURATIONS_DAYS` so the 21/42-day split is
honoured) (`:73-123`), and `TOTAL_PROGRAM_WEEKS` integer-pinned at `:16-19`.
`useHydrateProgramStore()` loads the anchor from AsyncStorage on cold start
(cancellation-guarded) and is mounted in `AppShell`
(`:126-137`, `frontend/src/App.tsx:223`).

### `useDepthPreferencesStore` (`frontend/src/store/useDepthPreferencesStore.ts`)

Client-side mirror of the "you choose your depth" ring toggles
([ADR 0006](../../decisions/0006-graduated-engagement.md)).

| Field | Type | Initial |
| --- | --- | --- |
| `enable_habits` | `boolean` | `true` (`:19,33`) |
| `enable_practices` | `boolean` | `true` (`:20,34`) |
| `enable_course` | `boolean` | `true` (`:21,35`) |
| `enable_sangha` | `boolean` | `true` (`:22,36`) |

All-on defaults encode "a user opts *out* of a depth, never in"
(`:9-13`). `load` and `update` are **non-optimistic**: state is replaced only
by the server's echoed full snapshot, because a backend rule may force a
dependent ring off; a failed call leaves flags untouched (`:14-17,50-67`).
Module-level `load`/`update` bindings let non-subscribing callers invoke
actions with stable identity (`:78-90`); four per-ring selectors at
`:97-104`.

### `useWelcomeStore` (`frontend/src/store/useWelcomeStore.ts`)

| Field | Type | Purpose |
| --- | --- | --- |
| `hasSeenWelcome` | `boolean \| null` | `null` until hydration resolves, so returning users never see an intro flash (`:19-22`) |

The **server owns** the per-account flag after login (`GET /ui-flags`);
AsyncStorage is only an offline/latency cache, re-seeded in both directions
(`:1-6,45-52`). `markWelcomeSeen` sets state, persists locally, and PATCHes
the server best-effort (`:60-66`). The consumer hook `useFirstRun(token)`
exposes `{ isFirstRun, hydrated, markSeen }`, where `isFirstRun` is true
exactly when the flag resolved to unset (`:77-123`).

### `useContractionSignalStore` (`frontend/src/store/useContractionSignalStore.ts`)

| Field | Type | Purpose |
| --- | --- | --- |
| `active` | `boolean` | true only while the most recent resonance pass observed a `return_offer` contraction (`:17-19`) |

Deliberately **not persisted** — derived fresh from each journal resonance
pass, session-only, wiped on logout (`:1-3`). `observe(contraction)` applies
latest-pass-wins: a healthy or `simple_ease_off` pass retracts a prior offer
signal (`:34-37`). The Journal writes it; the Return surface reads it.

### Derived hooks (`frontend/src/store/useProgramProgression.ts`)

`useDerivedCurrentStage(fallback)`, `useDerivedCurrentWeek(fallback)`, and
`useDaysUntilStage(stageNumber)` subscribe to the program anchor and wrap the
pure helpers, falling back to a server-derived value when no anchor is set
(`:4-18`).

### `normalizedCollection` (`frontend/src/store/normalizedCollection.ts`)

Factory for the canonical `byId` + `order` + derived-`list` triple shared by
the habit and stage stores: `normalize` (last-item-wins on duplicate keys)
and `rebuild` (projects `order` through `byId`, dropping absent keys)
(`:39-55`).

## Persistence layer (`frontend/src/storage/`)

Shared infrastructure:

- **`jsonStore.ts`** — fail-safe JSON-array reads. Transient `getItem`
  rejections keep stored data (return `null` / propagate for RMW), while
  genuinely corrupt JSON self-heals via `resetCorruptKey`
  (BUG-FRONTEND-INFRA-011, `:8-73`).
- **`serializedWrite.ts`** — per-key promise chains (`serialize(key, fn)`)
  make AsyncStorage read-modify-writes atomic w.r.t. other callers
  (BUG-FE-STORAGE-002, `:15-48`).
- **`secureStringStore.ts`** — a factory for single-secret stores: native
  Keychain/Keystore via `expo-secure-store`, with a deliberate, audited
  **localStorage fallback on web** (expo-secure-store v55 ships no web
  implementation). The XSS-window tradeoff, its mitigations, and the
  httpOnly-cookie migration plan are documented in the file header
  (BUG-FE-AUTH-007, `:7-46`). Saves trim and reject empty input
  (BUG-FE-STORAGE-004) and are serialized per key (`:81-105`).

### Complete storage-module table

| Module | Key(s) | Medium | Wiped on logout? |
| --- | --- | --- | --- |
| `authStorage.ts` | `adepthood_auth_token`; `@adepthood/logout_pending` | secureStringStore; AsyncStorage | yes — token cleared, plus a logout-pending marker retried on next boot if the clear fails (`:16,46-68`) |
| `llmKeyStorage.ts` | `adepthood_llm_api_key` | secureStringStore | yes — via `clearLlmApiKey` in the teardown (`:16-40`) |
| `habitStorage.ts` | `@adepthood/habits`; `@adepthood/pending_checkins` | AsyncStorage (serialized RMW queue for check-ins) | yes (`:8-9`, `AuthContext.tsx:204-209`) |
| `notificationStorage.ts` | `@adepthood/notifications/<habitId>`, `@adepthood/notification_habit_ids`; `adepthood_push_token` | AsyncStorage; SecureStore | per-user keys yes; the push token is deliberately kept — "a device credential, not a user credential" (`:30-42`) |
| `programStorage.ts` | `@adepthood/program_start_date` (stored as `YYYY-MM-DD` so TZ shifts can't roll the date) | AsyncStorage | yes — via `useProgramStore.reset` (`:1-42`, `useProgramStore.ts:59-62`) |
| `welcomeStorage.ts` | `@adepthood/has_seen_welcome` | AsyncStorage | yes — via `useWelcomeStore.reset` (`:5`, `useWelcomeStore.ts:67-70`) |
| `recentPracticesStorage.ts` | `@adepthood/recent_practices` (max 6, deduped, sanitized) | AsyncStorage (serialized RMW) | no |
| `energyScaffoldingStorage.ts` | `@adepthood/energy_scaffolding_archived` | AsyncStorage | no — "Device-scoped (not wiped on logout) so the dismissal survives the next login" (`:7`) |
| `morningPagesTipStorage.ts` | `@adepthood/morning_pages_tip_dismissed` | AsyncStorage | no |
| `paginationVisibilityStorage.ts` | `@adepthood/habits_pagination_hidden` | AsyncStorage | no |
| `reflectionDismissalStorage.ts` | `@adepthood/reflection_dismissed:<scopeKey>` (per reflection scope) | AsyncStorage | no |
| `returnOfferStorage.ts` | `@adepthood/return_offer_dismissed` | AsyncStorage | no |
| `jsonStore.ts` / `serializedWrite.ts` / `secureStringStore.ts` | (infrastructure — no own keys) | — | — |

SecureStore keys use bare underscored names because expo-secure-store only
allows alphanumerics plus `.`, `-`, `_` (`authStorage.ts:14-16`).

### The logout wipe

`wipeUserState` in `frontend/src/context/AuthContext.tsx:201-220` is the
BUG-FE-STATE-001 contract: reset the in-memory LLM-key getter synchronously
(`resetLlmApiKey`), call `resetAllStores()`, then concurrently clear habits,
pending check-ins, the LLM key, and notification data via
`Promise.allSettled` so one dead key doesn't strand the others.

## Hydration and invalidation summary

| Store | Hydrated by | When |
| --- | --- | --- |
| `useProgramStore` | `useHydrateProgramStore` ← `programStorage` | `AppShell` mount (`App.tsx:223`) |
| `useWelcomeStore` | `useFirstRun` ← `GET /ui-flags`, falling back to `welcomeStorage` | `WelcomeGate` mount (`App.tsx:153-160`) |
| `useDepthPreferencesStore` | `load(token)` ← `GET /depth-preferences` | `BottomTabs` mount, keyed on token (`BottomTabs.tsx:154-161`) |
| `useHabitStore` | `habitManager.loadHabits(userTimezone)` — cache-then-network; re-runs when the auth-hydrated timezone lands (#269) | `useBootstrapHabits` (`features/Habits/hooks/useHabits.ts:13-29`) |
| `useStageStore` | `stageService.loadStages()` | Map/Practice/Course effects (`features/Map/services/stageService.ts:1-8`) |
| `useContractionSignalStore` | `observe()` from resonance passes | per journal resonance pass (`features/Journal/useResonance.ts:32`) |

*Grounded in adepthood@55eef11, 2026-07-31.*
