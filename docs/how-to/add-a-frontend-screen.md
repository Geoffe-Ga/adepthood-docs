# Add a frontend screen in adepthood

Add a new screen to the React Native app and wire it into navigation.
Verified against the repo state of 2026-07-31.

## Prerequisites

- `cd frontend && npm ci`
- Familiarity with the feature-module layout: each domain owns a directory
  under `frontend/src/features/` (`Auth`, `Course`, `Habits`, `Journal`,
  `Map`, `Practice`, `Return`, `Settings`, `Welcome`, `Invitations`)

## Steps

1. **Write the test first** (Jest + `@testing-library/react-native`):

   ```typescript
   import { render, fireEvent } from "@testing-library/react-native";

   it("does the thing", () => {
     const { getByText } = render(<MyScreen />);
     fireEvent.press(getByText("Button"));
     expect(getByText("Result")).toBeTruthy();
   });
   ```

2. Create the screen in its feature module (a new directory under
   `frontend/src/features/` for a new domain, or alongside siblings in an
   existing one). Style exclusively with Candle & Ink tokens from
   `frontend/src/design/tokens.ts` — no raw hex values
   ([Candle & Ink](../design/candle-and-ink.md)).

3. Register the route in `frontend/src/navigation/` — `BottomTabs.tsx` for
   a new tab, `RootStack.tsx` for a stacked screen — and add its typed
   destination to `navigation/destinations.ts`.

4. If the screen talks to the backend, go through the shared API layer
   (`frontend/src/api/`) and typed response schemas; state that outlives
   the screen belongs in a Zustand store (`frontend/src/store/`).

## Verify

```bash
npm test
npm run lint          # zero warnings
npx tsc --noEmit      # strict mode
```

All exit 0, coverage stays at or above the 90% jest threshold, and the
screen renders in `npm start` with tokens (no hard-coded colors).
