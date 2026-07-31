# wavelength-demo — module map

Deep reference for the [wavelength-demo](https://github.com/Geoffe-Ga/wavelength-demo)
repository, generated from source. For the product-level story see
[the product page](../../products/wavelength-demo.md).

The repo is a dependency-light Vite + React 18 + TypeScript single-page site.
Runtime dependencies are exactly `react`, `react-dom`, and `serve`
(`package.json:24-28`); everything else — the Markdown reader, the color math,
the scroll engine — is written in-repo. There is no router library, no state
library, and no CSS framework (one stylesheet, `src/index.css`).

## Source module map

Complete: all 18 TypeScript modules under `src/` (excluding the 12 co-located
`*.test.ts` files and `vite-env.d.ts`). "Imported by" is taken from the
`import` statements of the listed consumers.

| Module | Purpose | Key exports | Imported by |
| --- | --- | --- | --- |
| `src/main.tsx` | Entry point; mounts `<App />` under `StrictMode` (`src/main.tsx:6-10`) | — | `index.html:21` (`<script type="module" src="/src/main.tsx">`) |
| `src/App.tsx` | Hash router: renders `ReferencePage` or `HomePage` from `window.location.hash` (`src/App.tsx:6-21`) | `App` (default) | `src/main.tsx` |
| `src/lib/route.ts` | Maps a URL hash to `"home" \| "reference"` (`src/lib/route.ts:4-8`) | `Route`, `parseRoute` | `src/App.tsx` |
| `src/lib/waveMath.ts` | Pure sine-wave geometry for the SVG wave (`src/lib/waveMath.ts:1-26`) | `VB_W`, `VB_H`, `MID`, `AMP`, `yAt`, `buildPath`, `angleAt` | `src/components/WaveForm.tsx` |
| `src/lib/scroll.ts` | Pure scroll-state computation (`computeWaveState`) (`src/lib/scroll.ts:24-49`) | `WaveState`, `clamp01`, `computeWaveState` | `src/components/useWaveReveal.tsx` |
| `src/lib/modeSelection.ts` | Desktop vs mobile mode subset (`src/lib/modeSelection.ts:5-10`) | `MOBILE_MODES`, `selectModes` | `src/pages/HomePage.tsx` |
| `src/lib/color.ts` | Dependency-free color math: hex parsing, WCAG luminance, ink selection, mixing (`src/lib/color.ts:6-56`) | `hexToRgb`, `rgbToHex`, `luminance`, `readableInk`, `mix`, `shade` | `src/pages/ReferencePage.tsx` |
| `src/content/markdown.ts` | Tiny Markdown reader: frontmatter, lead paragraph, pipe tables, `##` sections (`src/content/markdown.ts:1-152`) | `Frontmatter`, `parseFrontmatter`, `leadText`, `parseTable`, `indexByFirstCell`, `parseSections` | `src/content/pages.ts`, `src/data/modes.ts`, `src/data/reference.ts` |
| `src/content/inline.ts` | Inline formatting tokenizer for hero copy (`src/content/inline.ts:22-44`) | `InlineToken`, `tokenizeInline` | `src/components/RichText.tsx` |
| `src/content/pages.ts` | Loads and validates the four page-copy documents (`src/content/pages.ts:104-107`) | `HeroCopy`, `OriginCopy`, `ClosingCopy`, `parseHero`, `parseOrigin`, `parseClosing`, `HOME_HERO`, `REFERENCE_HERO`, `ORIGIN`, `CLOSING` | `src/pages/HomePage.tsx`, `src/pages/ReferencePage.tsx` |
| `src/data/modes.ts` | The Archetypal Wavelength data model: phases, quadrants, wave nodes, and the mode loader (`src/data/modes.ts:14-245`) | `PHASES`, `Phase`, `PhaseMap`, `QuadrantId`, `QUADRANTS`, `Mode`, `CANONICAL`, `PHASE_BLURBS`, `WaveNode`, `WAVE_NODES`, `WAVE_YELLOW`, `WAVE_PURPLE`, `FIELD`, `toMode`, `MODES` | `src/data/reference.ts`, `src/lib/modeSelection.ts`, `src/components/WaveForm.tsx`, both pages |
| `src/data/reference.ts` | The Reference catalog: nine developmental layers with medicinal/toxic dosage pairs (`src/data/reference.ts:19-106`) | `DosagePair`, `ReferenceLayer`, `TOXIC_HEX`, `toLayer`, `REFERENCE_LAYERS` | `src/pages/ReferencePage.tsx` |
| `src/components/WaveForm.tsx` | The SVG wavelength + phase-copy cards (`src/components/WaveForm.tsx:35-144`) | `WaveForm` | both pages |
| `src/components/useWaveReveal.tsx` | Scroll-driven reveal hook; writes opacity imperatively to the DOM (`src/components/useWaveReveal.tsx:40-94`) | `RevealPanel`, `WaveReveal`, `useWaveReveal` | both pages |
| `src/components/RichText.tsx` | Renders inline tokens / multi-line copy (`src/components/RichText.tsx:22-38`) | `RichText`, `Lines` | both pages |
| `src/components/MobileAppCta.tsx` | Bottom-pinned "Get the App" button for phones (`src/components/MobileAppCta.tsx:6-14`) | `MobileAppCta` | both pages |
| `src/pages/HomePage.tsx` | The scroll-driven home experience (`src/pages/HomePage.tsx:23-205`) | `HomePage` | `src/App.tsx` |
| `src/pages/ReferencePage.tsx` | The nine-layer Reference experience (`src/pages/ReferencePage.tsx:18-177`) | `ReferencePage` | `src/App.tsx` |

The repo's committed knowledge graph agrees with this structure — e.g. it
records `toMode()` at `src/data/modes.ts` L220 (graph node
`src_data_modes_tomode`) and `computeWaveState()` at `src/lib/scroll.ts` L24
(graph node `src_lib_scroll_computewavestate`), both matching the source lines
cited above (`graphify-out/graph.json`).

## Content tree (the editable copy)

All user-visible words live as Markdown under `content/`, not in code
(`content/README.md:1-13`):

| Directory | Files | Consumed by |
| --- | --- | --- |
| `content/wavelengths/` | 21 mode files (`01-narrative.md` … `21-tuckman-model.md`) | `src/data/modes.ts:200-204` (`import.meta.glob`, eager, raw) |
| `content/reference/` | 9 layer files (`01-beige.md` … `09-ultraviolet.md`) | `src/data/reference.ts:55-59` |
| `content/pages/` | 4 page-copy files (`home.md`, `reference.md`, `origin.md`, `closing.md`) | `src/content/pages.ts:5-8` (static `?raw` imports) |

11 of the 21 wavelength files carry `mobile: true` and appear on the narrow
mobile layout; the mobile subset is `01`, `02`, `03`, `04`, `05`, `06`, `07`,
`08`, `09`, `10`, and `21`. Details in
[Content pipeline](content-pipeline.md).

## Build, test, and deploy surface

Complete `package.json` script table (`package.json:10-23`):

| Script | Command | Purpose |
| --- | --- | --- |
| `dev` | `vite` | Local dev server |
| `build` | `tsc -b && vite build` | Type-check then bundle to `dist/` |
| `preview` | `vite preview` | Serve the built bundle locally |
| `start` | `serve -s dist -l ${PORT:-3000}` | Production static serve (Railway entry point) |
| `type-check` / `typecheck` | `tsc -b --noEmit` | Type-check only (both aliases exist) |
| `lint` / `lint:fix` | `eslint . --ext .ts,.tsx` (+ `--fix`) | Lint |
| `format` / `format:check` | `prettier --write .` / `--check .` | Format |
| `test` / `test:coverage` | `vitest run` (+ `--coverage`) | Unit tests |

Deployment is Railway with Nixpacks: build `npm run build`, start
`npm run start`, restart `ON_FAILURE` with 10 retries (`railway.json:3-11`).
The Vite config is minimal — the React plugin only (`vite.config.ts:5-7`).
Repo quality scripts (`scripts/check-all.sh`, `scripts/audit-gate.mjs`, etc.)
wrap these npm scripts for CI.

## Page inventory (public surface)

The app has exactly two client-side routes, switched on the URL hash — there
is no server routing (`src/App.tsx:20`, `src/lib/route.ts:4-8`):

| Route | Hash | Component | Content |
| --- | --- | --- | --- |
| Home | `""` / `#` / anything not `reference` | `HomePage` | Hero, "Why Archetypal" origin section, 21 (desktop) or 11 (mobile) wavelength cards, closing CTA |
| Reference | `#reference` (or `#/reference`, case-insensitive) | `ReferencePage` | Hero, 9 developmental-layer bars with medicinal/toxic wave reveals, closing CTA |

Both pages walk-through: [App shell and pages](app-shell.md).

## Relationship to the rest of the ecosystem

The site has zero runtime coupling to the other repos; its only integration is
shared ontology and outbound links, both hard-coded:

- `COURSE_URL = "https://aptitude.guru/philosophy/archetypal-wavelength"`
  (`src/pages/HomePage.tsx:14`) — the aptitude-course-published philosophy.
- `APP_URL = "https://github.com/Geoffe-Ga/WavelengthWatch"`
  (`src/pages/HomePage.tsx:15`, `src/components/MobileAppCta.tsx:1`) — the
  watch app whose journaling model uses the same six phases.
- The six phase names (`Rising`, `Peaking`, `Withdrawal`, `Diminishing`,
  `Bottoming Out`, `Restoration`, `src/data/modes.ts:14-21`) and the
  medicinal/toxic dosage framing (`src/data/reference.ts:14-17`) are the same
  Archetypal Wavelength vocabulary used by WavelengthWatch's curriculum data
  and adepthood's APTITUDE stage model.

---

*Grounded in wavelength-demo@78c703e, 2026-07-31.*
