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
`mkdocs.yml`**. The docs-sync agent must never create, modify, or delete
`.pages` files, anything under `docs/stylesheets/`, or `docs/index.md` —
those are static theme/navigation config outside its writable surface.

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

## Knowledge Graph (graphify)

This corpus ships a queryable knowledge graph, built by `scripts/graph/`
and **committed in-tree** at `graphify-out/graph.json` (satellite pattern:
the corpus is small, so the graph rides `main` and adepthood's federation
workflow fetches it over `raw.githubusercontent.com` and merges it into the
ecosystem `pan-graph.json` nightly). The `graph-build` workflow keeps the
committed graph at most 24h fresh.

When `graphify-out/graph.json` exists, prefer it over blind grep/read
sweeps:

- For corpus questions, run `graphify query "<question>"` first; use
  `graphify path "A" "B"` for relationships between pages or concepts,
  `graphify explain "X"` for a plain-language summary of a node, and
  `graphify affected "X"` for the impact of changing a page.
- When citing a fact from the graph, quote each node's `source_location`.
- After editing docs, refresh the graph with `./scripts/graph/build.sh`
  (keyless AST/prose pass — no LLM calls, ~seconds). Commit the refreshed
  `graphify-out/graph.json` alongside doc changes when convenient; the
  `graph-build` workflow rebuilds and commits it on merge anyway.
- If the graph is absent, build it with `./scripts/graph/build.sh` or
  proceed without it.

A weekly LLM semantic layer (`graphify extract --backend claude`) is
documented but not yet enabled — see `scripts/graph/README.md` and the
follow-up issue linked from issue #6.
