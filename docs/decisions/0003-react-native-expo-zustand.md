# 0003. React Native + Expo with Zustand and React Navigation

## Status

Accepted (backfilled 2026-07-31; visible in `frontend/package.json` and
`frontend/src/`).

## Context

Adepthood targets phones first (with web export available) and is built
largely by an agent fleet, which rewards a mainstream, well-documented
stack, deterministic installs, and a state layer simple enough to test
exhaustively.

## Decision

Build the frontend on React Native 0.76 via Expo ~52 with TypeScript in
strict mode. Use Zustand (v5) for global state (`frontend/src/store/`),
React Navigation 7 for routing (`frontend/src/navigation/` — `BottomTabs`,
`RootStack`, typed `destinations.ts`), AsyncStorage for persistence
(`frontend/src/storage/`), and Jest 29 with Testing Library for tests.
Install with `npm ci` from the lockfile in CI and agent sessions.

## Consequences

- Expo manages the native toolchain: `npm start` / `npm run ios` /
  `npm run android` / `npm run web` all work from one project, and
  `expo export --platform web` gives a web build.
- Zustand keeps state logic in plain functions that unit-test without
  providers; the roadmap's phase-2 and phase-7 refactors (extracting hooks,
  unifying state) build on that.
- Feature code organizes by domain (`frontend/src/features/<Feature>/`),
  which the [add-a-frontend-screen guide](../how-to/add-a-frontend-screen.md)
  codifies.
- Upgrades ride Expo's SDK cadence; the repo pins exact React Native and
  Expo versions to keep the fleet's environments reproducible.
