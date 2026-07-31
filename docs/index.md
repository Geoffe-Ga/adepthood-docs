# Adepthood Docs

This is the living documentation corpus for the five-repo Adepthood
ecosystem. It is maintained by an autonomous sync pipeline: a scheduled
workflow polls merged pull requests across the product repos, an agent folds
each change into the appropriate category below, and the resulting PR
auto-merges once the quality gates pass.

## Taxonomy

Every page lives in exactly one category. Each category's `index.md` states
its purpose and the explicit inclusion criteria the sync agent uses as
filing rules.

- **[Architecture](architecture/index.md)** — system structure, data flow,
  and component boundaries.
- **[Decisions](decisions/index.md)** — architectural decision records
  (ADRs) with lasting consequences.
- **[Design](design/index.md)** — visual language, design tokens, and
  interaction patterns.
- **[How-To](how-to/index.md)** — task-oriented guides for developers and
  agents.
- **[Contributing](contributing/index.md)** — conventions, quality gates,
  and workflow policy.
- **[Products](products/index.md)** — per-product overviews of the five
  repos.
- **[Changelog](changelog/index.md)** — dated digests of merged PRs folded
  into this corpus.

## Source repositories

- `Geoffe-Ga/adepthood`
- `Geoffe-Ga/Creek-Vault`
- `Geoffe-Ga/WavelengthWatch`
- `Geoffe-Ga/aptitude-course`
- `Geoffe-Ga/wavelength-demo`
