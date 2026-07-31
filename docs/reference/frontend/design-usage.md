# Design-system usage

How the Candle & Ink system is *consumed* in code. The visual language and
its rationale live in [Candle & Ink](../../design/candle-and-ink.md) and
[ADR 0005](../../decisions/0005-candle-and-ink-design-system.md); this page
documents the implementation surface in `frontend/src/design/` (3 files:
`tokens.ts`, `ThemeContext.tsx`, `useResponsive.ts`).

## tokens.ts — the single source of truth

"Every color, spacing value, radius, shadow, and typography scale in the app
should be imported from this module. Do not define design constants
elsewhere." (`frontend/src/design/tokens.ts:1-6`.)

### The semantic warm layer: surface / ink / accent

The app-wide language is the semantic trio added in #798
(`tokens.ts:681-740`), derived from the journal's paper palette so the whole
app reads as paper-on-desk:

```ts
export const surface = {
  canvas: colors.paper.background, // #faf6ef — the app ground
  raised: '#ffffff',               // lifted cards / sheets
  sunken: colors.paper.backgroundAlt, // #f3ecdf — recessed wells
  desk: colors.paper.desk,         // #e7dcc8 — the deeper ground a sheet floats above
  hairline: colors.paper.hairline, // #e3dccd — faint warm rule
} as const;
```

- `ink` — `primary #2b2620` (13.9:1 AAA), `soft #5a5046` (7.3:1),
  `muted #6b6055` (5.7:1); every value clears WCAG AA on the canvas and is
  asserted in `semanticTokens.test.ts` (`tokens.ts:699-707`).
- `accent` — terracotta `primary #a5572f` (4.9:1 as text), `strong
  #8f4a28`, `onPrimary #ffffff`; deliberately darkened from the
  graphical-only tier swatch so it clears AA as text (`tokens.ts:709-718`).
- Dark counterparts `surfaceDark` / `inkDark` / `accentDark` are warm
  umber/off-white — "NOT Material's neutral `#121212` … candlelit paper
  rather than a black slab" (`tokens.ts:742-778`) — plus
  `surfaceShadow`/`surfaceShadowDark` elevation pairs
  (`tokens.ts:720-740,784-799`).
- `showcase` / `onShowcase` / `showcaseShadow` give hero moments (the
  Practice player, Course cover, Map celebration) a warm-dark band on an
  otherwise light screen (`tokens.ts:801-837`). The Practice player is the
  heaviest consumer (`frontend/src/features/Practice/PracticeScreen.tsx:2-5,52-62`).

The legacy grey `colors.background`/`colors.text` palette remains for
un-migrated screens "but [is] no longer the design default"
(`tokens.ts:685-690`); `colors.paper.*` stays the journal-only editorial
palette with AAA-checked ink values (`tokens.ts:123-149`).

### Typography — `type(width)`, `editorialType`, `fonts`

Only platform-system fonts are used — no bundled faces
(`tokens.ts:547-556`): serif resolves to Georgia on iOS / `serif` on
Android / a CSS stack on web, resolved from `Platform.OS` (not
`Platform.select`) so the module stays loadable under the repo's
hand-rolled test mocks (`tokens.ts:520-545`).

The app-wide responsive ramp `type(width)` (#800) pairs a serif
display/heading face with clean sans body/labels (`tokens.ts:596-636`):

```ts
export const type = (width: number) => {
  const base =
    width < breakpoints.sm ? 15
    : width < breakpoints.md ? 16
    : width < breakpoints.lg ? 17
    : width < breakpoints.xl ? 18
    : 19;
  …
  return {
    display: serif(Math.round(base * 2.1), '700'),
    title: serif(Math.round(base * 1.6), '600'),
    heading: serif(Math.round(base * 1.25), '600'),
    body: sans(base, '400'),
    label: sans(Math.round(base * 0.9), '600'),
    caption: sans(Math.round(base * 0.8), '400'),
  } as const;
};
```

Usage pattern — call with the live window width and spread the face into
styles, e.g. `const t = typeRamp(width); … style={[t.label, styles.rowLabel]}`
(`frontend/src/features/Settings/SettingsHubScreen.tsx:19,58-77`).

`editorialType` is the journal's all-serif long-form ramp (display 34 →
caption 13, plus the italic `marginNote` face) (`tokens.ts:569-592`);
`uiType.button` and `INTERACTIVE_TEXT_MIN = 16` pin interactive text to a
legibility floor distinct from the 44 dp `touchTarget.minimum` tap-area
floor (`tokens.ts:443-455,558-567,642-645`).

### Layout, motion, accessibility invariants

- `spacing(n, scale)` = `n * 8 * scale`; static `SPACING` constants include
  the deliberate 14 px `buttonV` (`tokens.ts:337-355`).
- `rhythm` (#825) is the editorial screen rhythm consumed by the layout
  primitives (`ScreenScaffold` / `ScreenHeader` / `EditorialSection`):
  16 px gutters, 24 px section gaps, and the 64 px `bottomFadeHeight` for
  the `BottomFade` veil (`tokens.ts:357-370`).
- `motion` centralizes durations (fast 90 / base 220 / threshold 400 ms,
  settle 6 px); "Every consumer gates on `useReducedMotion` and falls back
  to the resting state" (`tokens.ts:372-383`).
- Stage color utilities: `STAGE_COLORS`/`STAGE_ORDER` with a legacy
  `Turquoise → Teal` alias in `resolveStageColor` (`tokens.ts:166-211`),
  `brightenColor`/`mixColors` (`tokens.ts:213-269`), and `readableGlyphOn`,
  a full WCAG relative-luminance computation that picks a black or white
  glyph per fill (`tokens.ts:271-331`).

## ThemeContext — mode as token swap

`ThemeProvider` initialises from the system color scheme and `setMode`
"reskins the tree by swapping the resolved tokens without touching layout or
testIDs (#804)" (`frontend/src/design/ThemeContext.tsx:59-68`). The context
value is the resolved token set for the active mode:

```tsx
const LIGHT_TOKENS: ThemeTokens = { mode: 'light', surface, ink, accent, surfaceShadow };
const DARK_TOKENS: ThemeTokens = {
  mode: 'dark',
  surface: surfaceDark, ink: inkDark, accent: accentDark, surfaceShadow: surfaceShadowDark,
};
```

(`ThemeContext.tsx:31-38`.) `useTheme()` outside a provider resolves the
light set with a no-op setter so screen tests need no wrapper
(`ThemeContext.tsx:44-47,71`). Consumers read `useTheme().mode` — e.g.
`AppShell` selects `navThemeFor(mode)` so React Navigation chrome follows
the same tokens (`frontend/src/App.tsx:224-226`,
`frontend/src/navigation/theme.ts:12-47`).

## useResponsive

`useResponsive()` (`frontend/src/design/useResponsive.ts:35-60`) wraps
`useWindowDimensions` over the shared `breakpoints`
(`xs 0 / sm 360 / md 600 / lg 900 / xl 1200`, `tokens.ts:471`) and returns:

| Field | Meaning |
| --- | --- |
| `width`, `height` | raw viewport |
| `contentWidth` | width clamped to `contentLayout.maxWidth` (900 = journal page 680 + margin column 220, `tokens.ts:501-517`) |
| `isXS…isXL` | breakpoint flags |
| `scale` | breakpoint scale (0.85–1.2) × a 0.85 short-screen factor below 700 px height (`useResponsive.ts:5-33`) |
| `columns` | 2 in landscape, 1 in portrait |
| `gridGutter` | `spacing(1, scale)` |

Typical consumer: `HabitsScreen` feeds `scale` into tile density and layout
(`frontend/src/features/Habits/HabitsScreen.tsx:9-10`).

## Where the docs corpus complements this

This page covers consumption only; token rationale, palette provenance, and
the visual north star live in `docs/design/` (see
[Candle & Ink](../../design/candle-and-ink.md)). The design section's
`DESIGN.md` inside the repo (`frontend/src/design/DESIGN.md`) remains the
in-repo spec.

*Grounded in adepthood@55eef11, 2026-07-31.*
