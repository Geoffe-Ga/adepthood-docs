# Ecosystem overview

As of the 2026-07-31 baseline seed (issue #3). Grounded in the current state
of all five source repos.

The Adepthood ecosystem is five repositories orbiting one body of ideas — the
APTITUDE program and the Archetypal Wavelength — plus this docs repo, which
documents all of them.

## The five repos and how they relate

| Repo | What it is | Stack |
| --- | --- | --- |
| `Geoffe-Ga/adepthood` | The flagship app: journal-first PKM with optional depths (habits, practices, course, community) | React Native + Expo frontend, FastAPI + PostgreSQL backend |
| `Geoffe-Ga/aptitude-course` | The 36-week, 10-stage APTITUDE curriculum as versioned Markdown content | Markdown corpus + Python build scripts + JSON Schema manifest |
| `Geoffe-Ga/Creek-Vault` | CLI + pipeline that organizes personal data exports into an Obsidian knowledge vault | Python (Typer CLI), local-first NLP, MCP server, Discord bot |
| `Geoffe-Ga/WavelengthWatch` | watchOS companion for browsing the Archetypal Wavelength from the wrist | SwiftUI watch app + FastAPI/SQLModel backend (SQLite) |
| `Geoffe-Ga/wavelength-demo` | Scroll-driven promo page making the Wavelength visceral | React 18 + Vite + TypeScript |

The connective tissue:

- **Shared ontology.** Adepthood's ten Aspects equal Creek's Frequencies equal
  the Wavelength phases' parent stages (adepthood `NORTH-STAR.md`, section 11;
  Creek-Vault `docs/Ontology/`). The same ten-stage, six-phase model drives
  the app, the vault classification, the watch catalog, and the demo page.
- **Content consumption.** The Adepthood app vendors a pinned commit of
  `aptitude-course` and reads it exclusively through the generated
  `manifest.json` (aptitude-course `CONSUMPTION.md`). See
  [ADR 0011](../decisions/0011-manifest-consumption-contract.md).
- **Promotion.** `wavelength-demo` links out to the philosophy and to
  WavelengthWatch; it shares the six-phase vocabulary (Rising, Peaking,
  Withdrawal, Diminishing, Bottoming Out, Restoration) from its
  `src/data/modes.ts`.
- **Documentation.** This repo (`adepthood-docs`) pulls merged-PR activity
  from all five and folds it into this corpus (epic #1;
  [ADR 0013](../decisions/0013-pull-model-docs-sync.md)).

## Knowledge-graph federation

Every repo carries a queryable code graph built by the pinned `graphify`
toolchain (PyPI `graphifyy`), and adepthood federates them.

- **Per-repo graphs.** aptitude-course, wavelength-demo, and WavelengthWatch
  commit their graphs in-tree at `graphify-out/graph.json` on `main`.
  Creek-Vault's graph is ~30 MB and ships as a rolling GitHub Release asset
  instead of being committed. Adepthood git-ignores `graphify-out/` entirely
  and distributes via release (see next point). Source: adepthood
  `scripts/graph/README.md`, "Federation (nightly)".
- **Adepthood's rolling release.** The `graph-build` workflow keeps a rolling
  release tagged `knowledge-graph` carrying `graph.json` and
  `graph-meta.json`, at most 24h stale. A weekly `graph-semantic` workflow
  upgrades the graph from `code-only` to `code+semantic` with an LLM pass over
  the prose corpus, publishing `semantic-meta.json`, a semantic cache, and an
  agent-crawlable `wiki.tar.gz`.
- **`pan-graph.json`.** The nightly `graph-federate` workflow (cron 06:10 UTC)
  merges adepthood's own graph with the four satellite graphs into one
  `pan-graph.json` + `pan-meta.json`, published on the same rolling release.
  An unfetchable satellite is skipped with a warning; only a missing
  adepthood-own graph fails the job. `pan-meta.json` records exactly which
  repos made it into each build.
- **This repo as satellite #6.** Epic #1 (decision 6) plans for
  `adepthood-docs` to commit its own graph in-tree (the small-corpus satellite
  pattern) and join the federation; that lands with issue #6 and an
  adepthood-side federation change. Not yet implemented as of this baseline.

See [Query the knowledge graph](../how-to/query-the-knowledge-graph.md) for
the commands, and ADRs [0008](../decisions/0008-graphify-knowledge-graph.md),
[0009](../decisions/0009-rolling-release-graph-distribution.md), and
[0010](../decisions/0010-pan-graph-federation.md) for the rationale.

## Per-repo deep dives

- [adepthood](adepthood.md)
- [Creek-Vault](creek-vault.md)
- [WavelengthWatch](wavelengthwatch.md)
- [aptitude-course](aptitude-course.md)
- [wavelength-demo](wavelength-demo.md)
