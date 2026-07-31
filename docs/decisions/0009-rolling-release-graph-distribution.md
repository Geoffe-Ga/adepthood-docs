# 0009. Distribute adepthood's graph via a rolling GitHub Release

## Status

Accepted (backfilled 2026-07-31; documented in adepthood
`scripts/graph/README.md`).

## Context

Adepthood's graph build writes ~17 MB to `graphify-out/graph.json`. With
several parallel Ralph worktrees each rebuilding it, committing the output
would put huge, churning binary-ish diffs into every PR. But every
environment — worktrees, CI, web sessions — still needs a fresh graph in
seconds, not the ~2 minutes a rebuild takes.

## Decision

Git-ignore `graphify-out/` in adepthood and distribute the graph as a
**rolling GitHub Release** tagged `knowledge-graph`. The `graph-build`
workflow keeps the release at most 24h stale, re-uploading `graph.json`,
`graph-meta.json` (build provenance: `built_at`, `sha`, node/edge counts,
pinned toolchain version, `kind`), and `GRAPH_REPORT.md` in place. The git
tag stays pinned at the release's creation commit and is not a version
marker — build identity lives in `graph-meta.json`'s `sha`. Consumers fetch
with:

```bash
gh release download knowledge-graph --pattern graph.json --dir graphify-out
```

Three workflows share the release ("three writers, one release"):
`graph-build` and `graph-semantic` share `graph.json` / `graph-meta.json` /
`GRAPH_REPORT.md` last-writer-wins, while `semantic-meta.json` (semantic
only) and `pan-graph.json` / `pan-meta.json` (federation only) have single
writers and cannot be clobbered.

## Consequences

- PRs stay clean and worktrees stay fast; any environment restores the
  graph in seconds without a rebuild.
- Eventual consistency is accepted: the nightly code-only rebuild can
  transiently reset `kind` to `code-only` until the next weekly semantic
  run; `semantic-meta.json` exists precisely so staleness probes see the
  true date of the last semantic pass.
- Small repos made the opposite call — satellites commit graphs in-tree
  because their corpora are small ([ADR 0010](0010-pan-graph-federation.md));
  the docs repo will follow the satellite pattern (epic #1, decision 6).
- A shrink guard refuses rebuilds that would produce fewer nodes, so a
  truncated extract can't silently replace a good graph
  (`GRAPHIFY_FORCE=1` overrides after intentional deletions).
