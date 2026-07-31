# Run wavelength-demo locally

Run the scroll-driven promo page from a fresh clone of
`Geoffe-Ga/wavelength-demo`. Verified against the repo state of 2026-07-31.

## Prerequisites

- Node.js and npm

## Steps

1. Install from the lockfile:

   ```bash
   npm ci
   ```

2. Start the Vite dev server:

   ```bash
   npm run dev
   ```

3. For a production build and preview:

   ```bash
   npm run build     # tsc -b && vite build
   npm run preview
   ```

## Verify

- The dev server URL renders the page: a sine wave fixed mid-screen, header
  bars sweeping past on scroll, phase copy fading onto the wave.
- Quality gates pass: `./scripts/check-all.sh` exits 0 (tests, lint,
  typecheck; the repo holds itself to 90% coverage and a mutation-score
  gate per its `CLAUDE.md`).
