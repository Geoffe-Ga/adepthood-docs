# wavelength-demo — app shell and pages

The component layer: routing, the two pages, and the shared presentational
pieces. (The data and math they consume are covered in
[Content pipeline](content-pipeline.md) and
[Wave geometry](wave-geometry.md).)

## Routing

There is no router library. `App` holds the parsed hash route in state,
re-parses on `hashchange`, and scrolls to the top on every navigation
(`src/App.tsx:6-21`):

```tsx
export default function App() {
  const [route, setRoute] = useState(() =>
    parseRoute(typeof window !== "undefined" ? window.location.hash : ""),
  );

  useEffect(() => {
    const onHash = () => {
      setRoute(parseRoute(window.location.hash));
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  return route === "reference" ? <ReferencePage /> : <HomePage />;
}
```

`parseRoute` accepts `#reference` or `#/reference`, case-insensitively;
anything else is home (`src/lib/route.ts:4-8`). Because the deploy is a
static `serve -s dist` (`package.json:14`), hash routing means both pages
work with zero server configuration.

## HomePage anatomy

`src/pages/HomePage.tsx` renders, in order (`:45-204`):

1. **Fixed wave stage** behind everything: axis labels from `FIELD` (energy
   high/low, ascending-attractive / descending-aversive,
   `src/data/modes.ts:189-194`) around a `WaveForm` (`:48-56`).
2. **Top bar** with the brand mark (linking to the course), a `#reference`
   nav link, the philosophy link, and a "Get the App" button (`:58-82`).
3. **Hero** from `HOME_HERO` (eyebrow / heading / intro / scroll cue), with
   CTAs "Explore the Course" and "Track Your Wave" (`:85-117`).
4. **Origin section** from `ORIGIN`, including the original labeled
   wavelength diagram with a long descriptive `alt` text (`:119-138`).
5. **Mode sections**: one full-screen bar per mode (index `01 / 21`, title,
   gloss, optional `after <source>` attribution) followed by a transparent
   `reveal` zone the scroll engine measures (`:140-165`).
6. **Closing CTA** from `CLOSING`, with the `{count}` footnote replaced by
   the live `MODES.length` (`:167-199`).
7. **`MobileAppCta`** — the bottom-pinned app button on phones (`:203`).

The copy the wave carries is chosen per phase: the canonical phase blurbs
while `panel.canonical` is true, otherwise the active mode's phase strings
(`src/pages/HomePage.tsx:39-43`; `PHASE_BLURBS` at
`src/data/modes.ts:90-97`).

## ReferencePage anatomy

`src/pages/ReferencePage.tsx` reuses "the home page's machinery: one fixed
wavelength behind everything, full-screen 'bars' … and transparent reveal
zones between them where the wave fills in that Mode's medicinal (Mode color)
and toxic (red) doses" (comment, `:14-17`). Differences from home:

- The wave gets `variant="ref"` and a per-layer `tint` — the active layer's
  `colorHex` multiplied onto the energy field only, never the wave stroke
  (`src/pages/ReferencePage.tsx:50-55`,
  `src/components/WaveForm.tsx:21-27`, `:45-50`).
- Each phase card shows a two-line dosage: medicinal in the layer's readable
  `textHex`, toxic always in `TOXIC_HEX` (`src/pages/ReferencePage.tsx:27-39`).
- Each of the nine bars is themed at render time: `readableInk(colorHex)`
  chooses the ink, and the background is a gradient to
  `shade(colorHex, 0.2)` (`src/pages/ReferencePage.tsx:104-116`).
- Bars show spiral color name, `MODE (Orientation)` heading, description,
  orientation gloss, and a scroll hint (`:122-135`).

## Shared components

| Component | File | Contract |
| --- | --- | --- |
| `WaveForm` | `src/components/WaveForm.tsx:35-144` | Props: `bodyOf(phase) => ReactNode`, `cardsRef` (opacity-driven copy layer), optional `tint`, `variant: "home" \| "ref"`. Renders field, tint layer, SVG wave, and one absolutely-positioned card per `WAVE_NODES` entry with CSS variables `--band` / `--ink` / `--accent` (`:124-141`) |
| `useWaveReveal` | `src/components/useWaveReveal.tsx:40-94` | `(count) => { revealRefs, cardsRef, panel }`; see [Wave geometry](wave-geometry.md) |
| `RichText` / `Lines` | `src/components/RichText.tsx:22-38` | Inline-token rendering / line-break preservation for copy |
| `MobileAppCta` | `src/components/MobileAppCta.tsx:6-14` | Fixed bottom "Get the App" link, hidden on desktop via `.app-cta-float` CSS |

## Accessibility notes encoded in the markup

- The entire fixed wave stage is `aria-hidden="true"` — it is decorative
  relative to the readable bars (`src/pages/HomePage.tsx:48`,
  `src/pages/ReferencePage.tsx:44`); each mode section instead carries
  `aria-label={m.title}` (`src/pages/HomePage.tsx:142`) and each layer
  section `aria-label` of `MODE (Orientation)`
  (`src/pages/ReferencePage.tsx:114`).
- The origin diagram's `alt` text narrates the full wave semantics rather
  than describing pixels (`src/pages/HomePage.tsx:131`).
- Scroll listeners are `passive: true`
  (`src/components/useWaveReveal.tsx:83`).

## External links (complete)

Every outbound URL in the component layer:

| Constant | Value | Declared at |
| --- | --- | --- |
| `COURSE_URL` | `https://aptitude.guru/philosophy/archetypal-wavelength` | `src/pages/HomePage.tsx:14`, `src/pages/ReferencePage.tsx:12` |
| `APP_URL` | `https://github.com/Geoffe-Ga/WavelengthWatch` | `src/pages/HomePage.tsx:15`, `src/pages/ReferencePage.tsx:11`, `src/components/MobileAppCta.tsx:1` |

---

*Grounded in wavelength-demo@78c703e, 2026-07-31.*
