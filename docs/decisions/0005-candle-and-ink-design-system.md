# 0005. Candle & Ink: a warm-editorial, token-driven design system

## Status

Accepted (backfilled 2026-07-31; adopted via adepthood epic #798 and its
sub-issues #799–#804).

## Context

Adepthood's journal-first identity called for a "paper-on-desk" feel — the
opposite of flat grey SaaS chrome — and the app already had warm values on
the journal-resonance surface (`colors.paper`, `editorialType`,
`paperShadow`). The look needed to be promoted app-wide without breaking
un-migrated screens, without proprietary fonts, and without copying any
brand's palette.

## Decision

Establish "Candle & Ink" as the canonical visual language, implemented as a
semantic token layer in `frontend/src/design/tokens.ts` and documented in
`frontend/src/design/DESIGN.md` (where code and doc disagree, `tokens.ts`
wins). Core commitments:

- A `surface` / `ink` / `accent` semantic layer derived from the existing
  warm paper values, with an original terracotta accent derived from the
  app's own `colors.tier.clear` swatch.
- A WCAG contrast contract — every `ink.*` and on-canvas `accent.*` value
  clears AA on `surface.canvas` — enforced by
  `__tests__/semanticTokens.test.ts`.
- A serif-display + clean-sans type ramp on platform-system font stacks
  (no bundled fonts), with a 16px interactive-text floor guarded by test.
- Additive adoption: legacy grey `colors.background` / `colors.surface`
  remain for un-migrated screens; the new layer is the default,
  adopted screen by screen.
- Warm-dark "showcase" surfaces (umber, not `#121212`) for hero moments,
  with their own tested contrast contract.

## Consequences

- Accessibility is a build-time property, not a review checklist — token
  changes that break contrast fail tests.
- Screens migrate incrementally, so the app temporarily carries two visual
  generations; the epic's adoption map tracks the migration.
- Provenance constraints (original palette, free fonts, `ATTRIBUTION` file)
  keep the system legally and ethically clean.
- The docs summary lives at [Candle & Ink](../design/candle-and-ink.md);
  this ADR records the choice, `DESIGN.md` remains the living reference.
