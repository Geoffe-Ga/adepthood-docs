# Journal

`frontend/src/features/Journal/` — the largest module (49 non-test files):
the app's home surface (the shelf), the long-form entry editor, the
photograph-capture flow, and the resonance/marginalia surface. Privacy
grounding: [ADR 0012 — local-first privacy tiers](../../../decisions/0012-local-first-privacy-tiers.md).

## Screens

| Screen | Route | Responsibility |
| --- | --- | --- |
| `JournalShelfScreen` | `Journal` tab (initial route) | "the journal's landing surface, restyled as an editorial library": `JournalHero`, `StatTileRow`, `ReturnStack`, `InvitationStack`, the weekly prompt, `ReflectionInvitationBand`, `MorningPagesTip`, `SearchBar`, then entries grouped This week / This month / Earlier as lifted paper tiles with reading-time + "saved … ago" captions (`JournalShelfScreen.tsx:1-10,55-78`) |
| `JournalEntryScreen` | `JournalEntry` (RootStack) | "the long-form page the user writes in … autosaves as a draft on idle — there is no send button and no chat UI" (`JournalEntryScreen.tsx:1-8`); reserved right-hand margin column for marginalia, stacking under 600 px (`:66-67`) |
| `JournalPhotographScreen` | `JournalPhotograph` (RootStack) | photograph-capture → transcription flow (`capture/prepareImage.ts`, `captureSession.ts`, `useTranscriptionRun.ts`, `transcriptionRun.ts`); the intimate "Type it instead" offramp passes only the scalar tier, never a page image (`RootStack.tsx:46-49`) |

## Shelf behavior

- `usePagedJournal` drives offset paging; search is debounced via
  `SearchBar`, gated to the backend's 3–64-char bounds so out-of-range
  queries never 422 (`JournalShelfScreen.tsx:45-46,80-120`).
- Reading-time is computed at 200 wpm with a 1-minute floor
  (`JournalShelfScreen.tsx:48,55-60`).
- A brand-new journal shows the single curated prompt "What brought you
  here?" (`JournalShelfScreen.tsx:50-51`).
- The shelf hosts the Return and Invitation bands (see those pages) and
  reads `useDerivedCurrentWeek` for the weekly prompt title
  (`JournalShelfScreen.tsx:38-42`).

## Entry editor behavior

- **Autosave**: idle-triggered (1 500 ms default) via `useIdle`; the save
  hint cycles typing → Saving… → Saved → error copy that promises the
  writing is safe (`JournalEntryScreen.tsx:63-64,92-110`).
- **Save context**: a `weekNumber` makes the entry a weekly-prompt response
  recorded via the prompt endpoint — the server creates the journal entry,
  so the client never also calls `journal.create`; practice ids link
  session reflections (`JournalEntryScreen.tsx:112-120`).
- **Privacy**: `PrivacyTierControl` sets the classification; resonance is
  client-side gated off for intimate entries with dedicated copy
  (`JournalEntryScreen.tsx:72-73`).
- **Resonance** (`useResonance.ts:1-70`): on open it loads existing
  marginalia + suggestions; a request first *flushes the draft save* so the
  pass runs against the saved latest body, holds a single in-flight slot so
  rapid taps can't double-charge, and maps errors (notably 402) to friendly
  copy. Results carry `care` (acute-distress support surface),
  `contraction` (the declinable "tend your foundation" reflection — also
  pushed into `useContractionSignalStore`), and `privateMessage` for the
  intimate-entry gate.
- **Margin surface**: `MarginNote`, `HighlightedBody` +
  `highlightSegments.ts`, `ResonanceEssayModal` (lazy essay via
  `resonance.essay`), `CompletionSuggestionNote` (accept/dismiss with
  streak feedback), `CareSupportNote`, `ContractionReflectionNote`.
- **Promoted quotes**: `QuoteSelectionSurface` converts native UTF-16
  selections to Unicode code points (`codePoints.ts`) before calling the
  anchor API — the span is code-point-native end-exclusive
  (`frontend/src/api/index.ts:1499-1508`); `usePromotions` manages
  create/remove/fold-in.
- **Reflections**: `useReflectionMode` + `ReflectionSourcesPanel` implement
  the 7th-day reflection compose mode over `reflections.due` / `sources`;
  quote prefills seed the body as a blockquote
  (`reflectionCopy.ts`, `RootStack.tsx:58-68`).
- **Stat tiles**: `StatTile`, `HabitsStatTile` (via `useHabitsSummary`),
  `PracticesStatTile`.

## Stores and API

Stores: `useContractionSignalStore` (written by resonance passes),
`useHabitStore`, `useProgramStore` + `useDerivedCurrentWeek`,
`useDepthPreferencesStore`. API namespaces: `journal`, `prompts`,
`promotions`, `reflections`, `resonance`, `completionSuggestions`, `stages`.
Storage: `morningPagesTipStorage`, `reflectionDismissalStorage` (per-scope
declines).

*Grounded in adepthood@55eef11, 2026-07-31.*
