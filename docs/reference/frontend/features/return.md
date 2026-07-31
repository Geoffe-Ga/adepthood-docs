# Return

`frontend/src/features/Return/` — the declinable five-week Metta Return arc:
a soft-landing offer surfaced on the Journal shelf when a contraction is
observed, then the active arc's week-by-week card.

## Surface

`ReturnStack` is a band on the Journal shelf, not a route. It renders
exactly one card by precedence (`ReturnStack.tsx:9-53`):

1. `ReturnCompletionCard` — when `arc.complete` (leave + per-habit
   recommit).
2. `ReturnLetGoCard` — when the let-go step is visible (release habit ids,
   or skip).
3. `ReturnArcCard` — an active arc's week/focus with pause/resume/leave.
4. `ReturnOfferCard` — the declinable offer (accept → `start`, or dismiss).
5. `null` — the common, silent case.

## `useMettaReturn`

The hook "loads the Return surface on mount and drives its lifecycle
without ever nagging" (`useMettaReturn.ts:1-13`):

- Silent by default — a failed load leaves everything empty rather than
  crashing the tab.
- The offer is visible only when the person is **eligible**, a
  **contraction is currently observed** (via `useContractionSignalActive`
  reading `useContractionSignalStore` — fed by journal resonance passes,
  `contractionSignal.ts`, `useMettaReturn.ts:17`), they have **not already
  set the offer aside**, and **no arc is running**.
- `dismissOffer` persists the decline server-side and caches it
  best-effort in `returnOfferStorage` — "a failed cache write is harmless —
  the server flag remains the source of truth"
  (`useMettaReturn.ts:52-57`).
- `start` / `pause` / `resume` / `leave` commit the local arc only after
  the API confirms; a rejected call propagates and leaves the arc
  unchanged. An unmount guard drops late resolutions
  (`useMettaReturn.ts:5-13,66`).
- `release` / `recommit` set habits to rest during the arc and take them up
  again (the `habits` import supports the released-habit display).

## Copy and session modal

`returnCopy.ts` and `mettaSessionCopy.ts` hold the warm framing;
`MettaSessionModal` runs the metta sitting itself; `InvitationNote`-style
presentation stays declinable throughout — none of these calls mutate stage
progress (`frontend/src/api/index.ts:1701-1708`).

## Stores and API

Stores: `useContractionSignalStore` (read-only here). API: `mettaReturn`
(all 8 wrappers), `habits`. Storage: `returnOfferStorage`.

*Grounded in adepthood@55eef11, 2026-07-31.*
