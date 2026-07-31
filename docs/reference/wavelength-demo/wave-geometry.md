# wavelength-demo — wave geometry and scroll engine

The three pure-math modules that make the page feel alive: the sine geometry
(`src/lib/waveMath.ts`), the scroll-driven copy selector
(`src/lib/scroll.ts` + `src/components/useWaveReveal.tsx`), and the color
math that themes the Reference page (`src/lib/color.ts`). All three are
DOM-free by design so they are unit-tested directly in Node
(`src/lib/scroll.ts:1-2`, `src/lib/color.ts:4`).

## 1. Sine geometry (`waveMath.ts`)

One full sine period spans a fixed 1200×760 viewBox; the crest (Peaking) sits
at 25% of the period and the trough (Bottoming Out) at 75%
(`src/lib/waveMath.ts:1-7`):

```ts
export const VB_W = 1200;
export const VB_H = 760;
export const MID = 380;
export const AMP = 232;

export const yAt = (f: number): number => MID - AMP * Math.sin(2 * Math.PI * f);
```

Worked example: `yAt(0) = 380` (midline start), `yAt(0.25) = 380 − 232 = 148`
(crest), `yAt(0.75) = 380 + 232 = 612` (trough).

`buildPath(f0, f1, steps = 120)` samples the curve into an SVG `M…L…` path
string (`src/lib/waveMath.ts:13-20`), and `angleAt(f)` returns the tangent
direction in degrees so arrowheads point along the direction of travel
(`src/lib/waveMath.ts:23-26`).

`WaveForm` composes these into the trajectory-not-a-loop rendering
(`src/components/WaveForm.tsx:58-98`): faded tails `buildPath(-0.16, 0.05)`
and `buildPath(0.95, 1.16)` show the wave arriving from the previous trough
and continuing to the next peak, while the main stroke is split by valence —
yellow (`WAVE_YELLOW = "#d6b23c"`) for the ascending segments `[0, 0.25]` and
`[0.75, 1]`, purple (`WAVE_PURPLE = "#9a5a8e"`) for the descending segment
`[0.25, 0.75]` (`src/data/modes.ts:186-187`,
`src/components/WaveForm.tsx:77-98`). Three arrowheads ride the wave at
`f = 0.15, 0.5, 0.85` (`src/components/WaveForm.tsx:10-14`). Phase markers
are white at the crest and black at the trough — the `dot` colors of
`WAVE_NODES`, which also pin each phase card to a fixed time-slot (`x` at
8.33%, 25%, 41.67%, 58.33%, 75%, 91.67% — the six sixths of the period,
`src/data/modes.ts:122-183`).

## 2. Scroll → copy selection (`computeWaveState`)

The core interaction: as you scroll, the fixed wave's copy cross-fades
between the canonical phase names and whichever mode's reveal zone is nearest
the viewport center. The decision is one pure function
(`src/lib/scroll.ts:24-49`):

```ts
export function computeWaveState(
  scrollY: number,
  vh: number,
  revealCenters: number[],
): WaveState {
  const center = vh / 2;
  const canonicalOpacity = clamp01(1 - scrollY / (0.6 * vh));

  const fade = 0.45 * vh;
  let best = 0;
  let bestOpacity = 0;
  for (let i = 0; i < revealCenters.length; i++) {
    const op = clamp01(1 - Math.abs(revealCenters[i] - center) / fade);
    if (op > bestOpacity) {
      bestOpacity = op;
      best = i;
    }
  }

  const canonical = canonicalOpacity >= bestOpacity;
  return { canonical, index: best, opacity: canonical ? canonicalOpacity : bestOpacity };
}
```

Rules, as documented at `src/lib/scroll.ts:15-23`: the hero copy fades out
over the first ~60% of a viewport of scroll; each mode is fully shown when its
reveal center hits the viewport center, fading to zero 0.45·vh either side;
whichever is stronger wins, so copy is never doubled.

Worked example, `vh = 800`:

- `scrollY = 240`, one reveal center at 500px →
  `canonicalOpacity = 1 − 240/480 = 0.5`;
  mode opacity `= 1 − |500 − 400|/360 ≈ 0.722`. Mode wins:
  `{ canonical: false, index: 0, opacity: 0.722 }`.
- `scrollY = 0`, no reveal zone near → canonical wins at opacity 1.
- Ties (`canonicalOpacity >= bestOpacity`) go to the canonical copy
  (`src/lib/scroll.ts:43`).

## 3. The reveal hook (`useWaveReveal`)

`useWaveReveal(count)` wires `computeWaveState` to the DOM
(`src/components/useWaveReveal.tsx:40-94`). The performance-relevant design,
per its doc comment (`:27-35`): every frame it measures each reveal zone's
`getBoundingClientRect()` center, writes the copy layer's opacity **straight
onto the DOM** (`cardsRef.current.style.opacity`, `:64-65`) with no per-frame
React render, and calls `setPanel` with an identity-preserving updater so
React re-renders only when the dominant panel actually changes (`:67-73`).
Scroll/resize events are coalesced through `requestAnimationFrame`
(`:76-84`); an unmounted zone contributes `Number.POSITIVE_INFINITY` as its
center so it can never win (`:54-57`). The effect re-runs when `count`
changes, i.e. on desktop ↔ mobile switches (`:90-91`).

Mobile selection itself is data-driven: `selectModes(isMobile)` returns
either all 21 modes or the 11 flagged `mobile: true`
(`src/lib/modeSelection.ts:5-10`), and `HomePage` tracks the
`(max-width: 760px)` media query (`src/pages/HomePage.tsx:21`, `:25-37`).

## 4. Color math (`color.ts`)

The Reference page themes each layer bar from a single hex color. Two
algorithms matter:

**Readable ink.** `luminance(hex)` implements the WCAG relative-luminance
formula, including the sRGB linearization branch at 0.03928
(`src/lib/color.ts:26-32`); `readableInk` picks dark ink (`#241f2b`) above a
0.45 luminance threshold, light ink (`#fbf7ec`) below it
(`src/lib/color.ts:38-44`). Worked examples (values from the formula):
Beige `#c9b27e` → luminance ≈ 0.458 > 0.45 → dark ink; Red `#b23b3b` →
≈ 0.129 → light ink. Beige is the only near-threshold layer, which is exactly
the case the function exists for (`src/lib/color.ts:36-37`).

**Gradient shading.** `mix(a, b, t)` linearly interpolates two hex colors per
channel and `shade(hex, amount)` mixes toward black
(`src/lib/color.ts:47-56`). `ReferencePage` builds each bar background as
`linear-gradient(180deg, colorHex 0%, shade(colorHex, 0.2) 100%)`
(`src/pages/ReferencePage.tsx:106-109`); e.g. Red `#b23b3b` →
`shade(…, 0.2) = #8e2f2f`.

---

*Grounded in wavelength-demo@78c703e, 2026-07-31.*
