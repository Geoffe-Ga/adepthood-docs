# Adepthood Docs — Claude Code Project Configuration

## Repo Purpose

This is the living-docs corpus for the five-repo Adepthood ecosystem
(adepthood, Creek-Vault, WavelengthWatch, aptitude-course,
wavelength-demo). An autonomous pull-model pipeline keeps it current:
a cron workflow polls merged PRs across the source repos, an agent folds
them into the corpus, and the resulting PR auto-merges on green gates.
There is no human in the loop — the CI gates are the reviewer, so never
weaken them to get a PR through.

## Taxonomy Filing Rules (summary)

Each category's `docs/<category>/index.md` carries the authoritative
inclusion criteria. Read them before filing. In brief:

- `docs/architecture/` — components, boundaries, data flow, deployment
  topology. File when a merged PR changes system structure.
- `docs/decisions/` — ADRs. File when a merged PR commits to a choice with
  lasting consequences.
- `docs/design/` — tokens, visual language, interaction patterns. File
  when a merged PR changes how things look or feel systemically.
- `docs/how-to/` — task guides. File when a merged PR adds or changes a
  procedure; update stale steps in the same run.
- `docs/contributing/` — quality gates, conventions, agent workflow
  policy. File when a merged PR changes the rules of work.
- `docs/products/` — per-repo overviews. File when a merged PR changes a
  user-facing feature surface or product scope.
- `docs/changelog/` — one dated digest entry per sync run that processed
  merged PRs.

Every page lives in exactly one category. Navigation is derived from the
directory tree by the awesome-pages plugin — **never add a `nav:` key to
`mkdocs.yml`**.

## ADR Format

`docs/decisions/NNNN-slug.md`, zero-padded sequence number, with exactly
these sections: `## Status`, `## Context`, `## Decision`,
`## Consequences`. Supersede old ADRs with a new record; never rewrite an
accepted one.

## Markdownlint Conventions

`.markdownlint-cli2.jsonc` is the single source of lint truth. MD013
(line length) and MD033 (inline HTML) are off; MD024 allows duplicate
headings when not siblings. Everything else is default — fix the prose,
don't add per-file suppressions. Validate locally with:

```bash
npx --yes markdownlint-cli2 "**/*.md"
```

Before pushing, also run the strict build:

```bash
pip install -r requirements.txt
mkdocs build --strict
```

## Commit Style

Conventional commits, small and atomic:

```text
docs(architecture): fold adepthood#123 energy-domain split into backend page
feat(sync): advance watermark handling for renamed repos
ci(docs): tighten lychee glob to docs tree
```

## Knowledge Graph

Filled in by issue #6 — graph-first steering lands with the graphify
adoption.
