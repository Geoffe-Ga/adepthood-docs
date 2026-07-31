# Candle & Ink

Adepthood's warm-editorial design language. Canonical source:
`frontend/src/design/DESIGN.md` in the adepthood repo (epic #798); where
that doc and the code disagree, `frontend/src/design/tokens.ts` wins. This
page is a summary as of 2026-07-31 — see also
[ADR 0005](../decisions/0005-candle-and-ink-design-system.md).

## Intent

A warm, literary, paper-on-desk feel — the opposite of flat grey SaaS
chrome. The language began on the journal-resonance surface and is promoted
app-wide through a semantic `surface` / `ink` / `accent` token layer.

## The semantic layer

Defined in `tokens.ts`:

- **Surfaces** — `surface.canvas` (`#faf6ef`, warm off-white paper ground),
  `surface.raised` (white lifted cards), `surface.sunken` (recessed wells),
  `surface.desk` (`#e7dcc8`, the deeper ground a sheet floats above), and a
  faint warm `surface.hairline` rule.
- **Ink** — `ink.primary` (`#2b2620`, 13.9:1 on canvas), `ink.soft`,
  `ink.muted` for secondary text and captions.
- **Accent** — an original terracotta (`accent.primary` `#a5572f`, 4.9:1)
  derived from the app's own `colors.tier.clear` swatch — deliberately not
  copied from any product or brand (see the design system's `ATTRIBUTION`).
- **Elevation** — ink-tinted warm shadows (`surfaceShadow`), plus a
  "bottom fade" component that dissolves scrolling content into the paper
  ground (never black).

**Contrast contract:** every `ink.*` value and the on-canvas `accent.*`
values clear WCAG AA (most clear AAA) on `surface.canvas`, enforced by
`__tests__/semanticTokens.test.ts` — accessibility regressions fail the
build.

## Type system

A serif-display + clean-sans ramp (`type(width)` →
`display / title / heading / body / label / caption`), responsive from phone
to tablet. Both faces are platform-system stacks — no bundled or proprietary
fonts. The journal keeps its all-serif `editorialType` for long-form
reading. `INTERACTIVE_TEXT_MIN` (16px) is the legibility floor for any
tappable label, guarded by a test that fails if caption sizing reaches an
interactive control.

## Showcase surfaces

A warm-dark band for hero moments (Today's hero, the Practice player, the
Course cover, the Map celebration): deep warm umber (`showcase.canvas`
`#2a211a` — explicitly not navy and not `#121212`) with `onShowcase.*`
foregrounds that all clear AA, enforced by `showcaseTokens.test.ts`.
Primitives: `ShowcaseCard` and the sparingly-used full-bleed `CalloutBand`.

## Constraints

- No proprietary fonts; no third-party brand marks or swatches.
- Additive adoption — legacy grey tokens remain for un-migrated screens.
- Reuse the existing warm values — `surface`/`ink` derive from
  `colors.paper`, not a parallel palette.

## Relation to the external reference

Adepthood's root `DESIGN.md` is an external inspiration analysis (of the
Anthropic/Claude marketing-site aesthetic) that informed the Candle & Ink
vocabulary; `frontend/src/design/DESIGN.md` is the implemented system.
