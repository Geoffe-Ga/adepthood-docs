# Welcome

`frontend/src/features/Welcome/` (3 files: `WelcomeScreen.tsx`,
`welcomeContent.ts`, `Welcome.styles.ts`) — the one-time editorial program
intro shown above the app shell on first run (#836).

## Surface

`WelcomeScreen` is not a navigator route: `WelcomeGate` renders it *instead
of* `RootStack` while `useFirstRun().isFirstRun` is true
(`frontend/src/App.tsx:144-160`). It is a horizontally paged set of
editorial panels — each a `ShowcaseCard` hero with eyebrow / title / body,
optional pillar rows, and an optional privacy note — with non-interactive
`PagerDots` ("paging stays the single seam") and reduced-motion awareness
(`WelcomeScreen.tsx:13-60`). Panel copy lives in `WELCOME_PANELS`
(`welcomeContent.ts`).

## Behavior

- Both **Begin and Skip** call `onComplete` → `markSeen`, so either path
  persists the flag and lands the user on the Journal home
  (`App.tsx:146-152`).
- First-run state is **per-account, server-owned**: `useFirstRun` hydrates
  from `GET /ui-flags`, re-seeds the AsyncStorage cache in both directions,
  and falls back to the cache offline; before hydration `isFirstRun` is
  false so returning users never see a flash of the intro
  (`frontend/src/store/useWelcomeStore.ts:1-6,87-123`).

## Stores and API

Stores: `useWelcomeStore` (via `useFirstRun`, wired in `App.tsx` rather
than inside this module). API: none directly — the store handles the
`uiFlags` sync.

*Grounded in adepthood@55eef11, 2026-07-31.*
