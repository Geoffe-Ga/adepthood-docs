# WavelengthWatch — offline sync and core flows

The four load-bearing algorithms: the offline journal queue and its
idempotent sync, the catalog cache fallback, the emotion-logging state
machine, and the analytics streak computation.

## 1. Offline-first journaling (end to end)

### Local queue (watch)

`JournalQueue` is a SQLite-backed persistent queue
(`Services/JournalQueue.swift:19-58`): "**Offline-first**: All operations
persist to SQLite immediately; **Status tracking**: pending → syncing →
synced/failed; **Retry management** … ; **Cleanup**: Removes old synced
entries" (`:25-29`). The database lives at
`Documents/journal_queue.sqlite`, opened with `SQLITE_OPEN_FULLMUTEX`
(`:31-34`, `:91-113`). Its full public surface
(`JournalQueueProtocol`, `:8-17`): `enqueue`, `pendingEntries`, `fetch(id:)`,
`markSyncing`, `markSynced`, `markFailed`, `cleanupSynced(olderThan:)`,
`statistics`. A published `pendingCount` lets SwiftUI show an offline
indicator reactively (`:59-66`).

### Sync service (watch)

`JournalSyncService.sync()` (`Services/JournalSyncService.swift:107-215`;
graph node
`workspace_wavelengthwatch_frontend_…_journalsyncservice_journalsyncservice_sync`,
`source_location` `Services/JournalSyncService.swift` L121):

1. Bail if already syncing or offline (`NetworkMonitor`) (`:120-131`).
2. Fetch pending entries; filter out those at the retry cap using the queue
   item's **persisted** `retryCount` — the comment warns that the JSON
   snapshot's count "stays at zero forever, so reading it would silently
   bypass the retry cap" (`:139-146`; `maxRetries` defaults to 3, `:94-99`).
3. For each entry: mark syncing, POST to `/api/v1/journal` with
   **`X-Idempotency-Key` = the entry's local UUID** — "Reusing the key
   across retry attempts lets the backend deduplicate replayed submissions"
   (`:157-185`) — then mark synced; failures mark failed and continue with
   the next entry (`:189-200`).
4. Status ends `.success(syncedCount:)` if anything succeeded, `.error` if
   everything failed (`:203-213`). `startAutoSync()` subscribes to
   connectivity changes and re-syncs when the network returns (`:217-241`).

### Idempotent create (backend)

`POST /api/v1/journal` (`backend/routers/journal.py:215-301`; graph node
`workspace_wavelengthwatch_backend_routers_journal_create_journal`,
`source_location` `backend/routers/journal.py` L216):

1. If `X-Idempotency-Key` is present it must be a UUID, else 400
   (`:103-111`).
2. Replay check: look up `(idempotency_key, user_id)`; if found and
   unexpired, return the existing entry with **200** instead of 201
   (`:114-145`, `:229-240`). Expired records are deleted in-transaction
   (`:139-142`).
3. Otherwise validate references, insert the journal row, `flush()` to get
   its id, add an `IdempotencyRecord` with a 24-hour `expires_at`
   (`:148-162`), and **commit both in one transaction** (`:252-268`).
4. Race handling: if a concurrent request with the same key commits first,
   the composite-PK `IntegrityError` is caught, the session rolled back, and
   the winner's entry returned as a 200 replay — standard
   at-most-once-effect semantics (`:265-301`; model constraint at
   `backend/models.py:195-217`).
5. On success the user's analytics cache is invalidated
   (`analytics_cache.invalidate_user`).

Expired keys are also swept at startup
(`cleanup_expired_idempotency_records`, `backend/routers/journal.py:165-178`,
called from `backend/app.py:67-69`).

### Worked example

A user logs "Bliss" on the trail with no signal:

1. The flow submits → entry persists to SQLite with status `pending`, UUID
   `3f2c…`; `pendingCount` becomes 1 and the UI shows the offline badge.
2. Signal returns → `startAutoSync` fires `sync()`; the entry POSTs with
   `X-Idempotency-Key: 3f2c…`; backend inserts journal row 512 + an
   idempotency record expiring in 24 h; queue marks `synced`.
3. The watch retries the same POST after a timeout that actually reached the
   server: the backend finds `(3f2c…, user 1)` unexpired and returns row 512
   with 200 — no duplicate entry.
4. Days later `cleanupSynced(olderThan: 30)` prunes the local row; the
   server sweeps the expired key at next startup.

## 2. Catalog cache fallback

`CatalogRepository.loadCatalog(forceRefresh:)`
(`Services/CatalogRepository.swift:129-149`) encodes a deliberate
freshness-vs-availability policy (#452):

- **Network-first**: always fetch when reachable "so freshly-published
  catalog changes … appear without waiting on a TTL. The on-disk cache is an
  OFFLINE fallback only" (`:131-134`); every successful fetch rewrites the
  cache envelope (fetch timestamp + payload, `:119-124`).
- **Offline**: serve the cached catalog *of any age* — unless the caller is
  an explicit user "refresh now" (`forceRefresh`), which "propagates the
  error instead of masking it with stale data" (`:136-148`);
  `refreshCatalog()` likewise always throws on failure (`:151-159`).
- The cache file is `Documents/catalog-cache.json` — Documents, not Caches,
  because Caches is "purgeable by the OS under storage pressure. The watch
  is an offline-first surface — losing the catalog leaves the user with no
  curriculum to browse" (`:46-55`). A corrupt cache is logged and deleted,
  not trusted (`:106-117`).

## 3. The emotion-logging flow state machine

`FlowCoordinator` is "PURE STATE MANAGEMENT … knows nothing about SwiftUI
views, sheets, alerts, or navigation"
(`ViewModels/FlowCoordinator.swift:11-13`). Its `FlowStep` enum is the whole
machine (`:149-158`):

```text
idle → selectingPrimary → confirmingPrimary
     → selectingSecondary → confirmingSecondary
     → selectingStrategy  → confirmingStrategy
     → review → (submit | cancel) → idle
```

Selections accumulate in `Selections{primary, secondary?, strategy?}`
(`:161-165`). The coordinator also drives what the main grid shows:
selecting a primary/secondary sets
`contentViewModel.layerFilterMode = .emotionsOnly`, selecting a strategy
sets `.strategiesOnly`, and `reset()` restores `.all` (`:40-43`, `:77-88`,
`:138-142`). `submit()` requires a primary emotion
(`FlowError.missingPrimaryEmotion`, `:107-110`) and deliberately does *not*
reset on success so the confirmation alert can be read before dismissal —
the fix for #161 (`:121-123`). `FlowStep` is `CaseIterable` specifically so
policy tests must cover every step (#428, `:146-148`). Submission goes
through `JournalClient` → the local queue, i.e. the flow ends at step 1 of
the offline pipeline above.

## 4. Analytics: streaks and ratios

The overview endpoint's core metrics (`backend/routers/analytics.py`; graph
node `workspace_wavelengthwatch_backend_routers_analytics_calculate_streak`,
`source_location` `backend/routers/analytics.py` L38):

**Current streak** (`_calculate_streak`, `:38-74`): reduce timestamps to
unique dates, newest first; if the newest is older than yesterday the streak
is 0 ("If the most recent entry is not today or yesterday, streak is 0",
`:57-59`); otherwise count consecutive days until the first gap. Worked
example, today = 2026-07-31: entries on 07-31, 07-30, 07-28 → dates
`[31, 30, 28]` → streak 2 (gap before the 28th). Entries on 07-30 and 07-29
(none today) → newest is yesterday → streak 2 still counts.

**Longest streak** (`_calculate_longest_streak`, `:77-105`): a single pass
over chronologically sorted unique dates, incrementing while consecutive and
tracking the max.

**Medicinal ratio** (`_calculate_medicinal_ratio`, `:108-138`): one grouped
SQL query joining `Journal → Curriculum`, counting per `dosage`; returns
`medicinal / total` as a 0-1 fraction (the comment insists: "not 0-100").
The medicinal-vs-toxic ratio and its trend
(`_calculate_medicinal_trend`) are the app's growth signal — the same
Medicine/Toxicity framing the reference layers carry in wavelength-demo and
the course carries in aptitude-course.

Expensive endpoints (`self-care`, `growth`) go through the per-user TTL
cache; journal creation invalidates exactly that user's keys
(`backend/cache.py:98-111`), so analytics are at most one write behind.

---

*Grounded in wavelengthwatch@d8342ad, 2026-07-31.*
