# 0008. graphify knowledge graphs for agent orientation

## Status

Accepted (backfilled 2026-07-31; documented in adepthood
`scripts/graph/README.md`).

## Context

Agent sessions orient in unfamiliar code by grepping and reading broadly,
which is slow, token-expensive, and easy to get wrong in a codebase with
dozens of interlocking modules. The ecosystem needed a cheap, reproducible
way to answer "what connects X and Y", "what depends on X", and "explain X"
before opening files.

## Decision

Adopt the graphify toolchain (upstream `safishamsi/graphify`, installed from
PyPI as `graphifyy`, version-pinned in `scripts/graph/requirements.txt`) to
build a queryable graph of code entities — files, classes, functions, calls,
imports — via a local, deterministic tree-sitter AST pass with no LLM calls.
Every repo in the ecosystem builds one. Adepthood layers on top:

- A **weekly LLM semantic pass** (`graph-semantic.yml`) upgrades the graph
  from `code-only` to `code+semantic`, with a content-keyed cache so
  unchanged prose costs nothing, plus LLM-labelled community clustering and
  an agent-crawlable wiki export.
- A **memory loop**: agents record whether graph queries helped
  (`graphify save-result … --memory-dir graph/memory/`), and a weekly
  `graphify reflect` distils the committed traces into a lessons digest that
  feeds the playbook curator.
- Steering: `CLAUDE.md` directs agents to prefer `graphify query` /
  `path` / `explain` / `affected` over blind grep sweeps and to refresh the
  graph after code changes (`./scripts/graph/update.sh`).

## Consequences

- Orientation cost drops (the nightly benchmark records a tokens-per-query
  reduction factor in `graph/metrics/benchmark-trend.jsonl`).
- The toolchain is free and reproducible anywhere — dev laptop, Ralph
  worktree, CI, web session — because the code pass needs no keys.
- Provenance was verified explicitly (the `graphifyy` name is a PyPI
  availability quirk, not a typosquat — `scripts/graph/README.md`).
- Distribution needed its own decisions:
  [ADR 0009](0009-rolling-release-graph-distribution.md) (rolling release)
  and [ADR 0010](0010-pan-graph-federation.md) (federation).
