# wavelength-demo

As of the 2026-07-31 baseline seed (issue #3).

A scroll-driven React page promoting the Archetypal Wavelength philosophy and
the WavelengthWatch app: one sine wave fixed in the center of the screen
while scrolling header bars re-caption its six phases as different "modes"
of the same wave. Source: wavelength-demo `README.md` and `CLAUDE.md`.

## Stack

- React 18 + TypeScript + Vite 7; Vitest for tests.
- No backend — a static site (`npm run build` produces `dist/`, served in
  production via the `start` script; `railway.json` and `DEPLOY.md` cover
  deployment).

## Module map

- `src/App.tsx`, `src/main.tsx` — app shell.
- `src/components/`, `src/pages/`, `src/lib/` — the scroll choreography:
  header bars sweep past, then each mode's phase copy fades onto the wave in
  its own horizontal time-slot (one sixth of the width) so cards never
  collide; on phones the wave unrolls into a vertical stack of full-width
  phase bands.
- `src/data/modes.ts` — the data source: 19 modes quoted verbatim from the
  "Expanded List" sheet of the Archetypal Wavelength spreadsheet (rows
  marked for inclusion), each with per-phase manifestation copy; modes are
  colored by their AQAL quadrant (`I`, `IT`, `WE`, `ITS`).
- `content/` — page and reference content.
- `scripts/` — `check-all.sh`, `test.sh`, `lint.sh`, `typecheck.sh`,
  `audit-gate.mjs`, mirroring the ecosystem's script-first convention.

## Data flow

Static and unidirectional: `src/data/modes.ts` → scroll-driven rendering.
The wave's geometry is meaningful — vertical position encodes energy (white
crest high, black trough low) and direction encodes valence (warm yellow
ascending, cool purple descending) — and the six phases run in time order:
Rising → Peaking → Withdrawal → Diminishing → Bottoming Out → Restoration.

The page is explicit that it renders a **wavelength** (a trajectory through
time), not a cycle (the same shape with time removed and the arrows looping
back) — the same distinction adepthood's `NORTH-STAR.md` (section 5) makes
for the app's Map.

## Key entry points

- Dev server: `npm run dev` (Vite).
- Build: `npm run build` (`tsc -b && vite build`); preview with
  `npm run preview`.
- Quality gates: `./scripts/check-all.sh` — 90% coverage, complexity ≤ 10,
  mutation score ≥ 80% per its `CLAUDE.md` 4-gate workflow.
- Knowledge graph: committed in-tree at `graphify-out/graph.json`, federated
  nightly into adepthood's `pan-graph.json`.

## Relation to the ecosystem

The demo is the ecosystem's front door for the core idea: one wave, six
phases, under many human and natural rhythms. It links out to the philosophy
and to WavelengthWatch and shares the phase vocabulary used by the course,
the app, and the watch.
