# Adepthood Docs

The living documentation corpus for the five-repo Adepthood ecosystem. It
is maintained by an autonomous sync pipeline: a scheduled workflow polls
merged pull requests across the product repos, an agent folds each change
into the appropriate category below, and the resulting PR auto-merges once
the quality gates pass.

Every page lives in exactly one category. Each category's index states its
purpose and the explicit inclusion criteria the sync agent uses as filing
rules.

<div class="grid cards" markdown>

- **[Products](products/index.md)**

    ---

    Per-product overviews of the five repos: what each one is, who it
    serves, and its current feature surface.

- **[Architecture](architecture/index.md)**

    ---

    System structure, service boundaries, data flow, and deployment
    topology — per repo and across the ecosystem.

- **[How-To](how-to/index.md)**

    ---

    Task-oriented guides: numbered steps for developers and agents,
    verified against the current state of the repos.

- **[Reference](reference/index.md)**

    ---

    Deep, code-grounded reference for every repo — enumerated API,
    model, and screen surfaces with `file:line` citations, plus
    end-to-end walkthroughs.

- **[Decisions](decisions/index.md)**

    ---

    Architectural decision records (ADRs) — choices between alternatives
    with lasting consequences, captured when made.

- **[Design](design/index.md)**

    ---

    Visual language, design tokens, and interaction patterns, including
    Adepthood's Candle & Ink system (this site's own theme).

- **[Contributing](contributing/index.md)**

    ---

    Conventions, quality gates, and the workflow policy the autonomous
    pipeline enforces.

- **[Changelog](changelog/index.md)**

    ---

    Dated digests of merged PRs folded into this corpus — the audit trail
    of the sync pipeline.

</div>

## Source repositories

- `Geoffe-Ga/adepthood`
- `Geoffe-Ga/Creek-Vault`
- `Geoffe-Ga/WavelengthWatch`
- `Geoffe-Ga/aptitude-course`
- `Geoffe-Ga/wavelength-demo`
