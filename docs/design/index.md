# Design

Visual and interaction design across the ecosystem: design systems, tokens,
typography, component visual language, and product design north stars
(for example Adepthood's "Candle & Ink" system).

## Site theme provenance

This docs site itself wears [Candle & Ink](candle-and-ink.md): the values
in `docs/stylesheets/extra.css` are copied from the semantic token layer in
`frontend/src/design/tokens.ts` in the adepthood repo (`surface` / `ink` /
`accent`, plus the warm-dark `surfaceDark` / `inkDark` / `accentDark`
counterparts), with `frontend/src/design/DESIGN.md` as the narrative
reference. When a merged adepthood PR changes those tokens, the docs-sync
pipeline updates the prose here as usual, and a human or agent then updates
`extra.css` from the cited source — the stylesheet is static config the
sync agent never edits.

## Inclusion criteria

File a page (or update an existing one) here when a merged PR:

- Adds or changes design tokens (color, spacing, typography, elevation,
  motion) or the theme system that serves them.
- Changes the visual language of shared components or establishes a new
  component pattern.
- Changes an interaction pattern users experience (navigation structure,
  gesture vocabulary, feedback and empty states).
- Updates a product's design north star or aesthetic reference material.
- Changes accessibility conventions (contrast rules, focus behavior,
  reduced-motion handling).

Do **not** file here for: layout tweaks with no systemic intent, copy
changes, or feature scope changes — those belong in
[Products](../products/index.md).

## Conventions

- One page per design system or per product design surface, named after it
  (`candle-and-ink.md`, `wavelengthwatch-complications.md`).
