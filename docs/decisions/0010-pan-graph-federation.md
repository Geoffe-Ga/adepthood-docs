# 0010. Pan-graph federation across the five repos

## Status

Accepted (backfilled 2026-07-31; documented in adepthood
`scripts/graph/README.md`, "Federation (nightly)").

## Context

Each repo's graph answers questions about that repo, but the ecosystem's
interesting questions cross boundaries — how the app consumes the course
manifest, where the ontology appears in the vault and the watch. Agents
needed one graph spanning all five repos without forcing every repo into
one build system.

## Decision

Federate rather than centralize. Adepthood's nightly `graph-federate.yml`
workflow (cron 06:10 UTC, plus `workflow_dispatch` and an inbound
`repository_dispatch` poke) merges adepthood's own published graph with the
published graphs of the four satellites into one `pan-graph.json`, released
on the same rolling `knowledge-graph` release with a `pan-meta.json`
manifest. Satellites keep their own distribution choices: aptitude-course,
wavelength-demo, and WavelengthWatch commit graphs in-tree (fetched raw);
Creek-Vault's ~30 MB graph ships as its own release asset. The whole
pipeline is $0 and `GITHUB_TOKEN`-only — satellite fetches are
unauthenticated public HTTPS.

## Consequences

- One query surface for cross-repo questions; `pan-meta.json` records
  exactly which repos made each build (`repos_present` / `repos_missing`).
- Failure is graceful and honest: an unfetchable satellite is excluded with
  a warning rather than failing the build; only a missing adepthood-own
  graph is fatal.
- Freshness is federated too — the pan-graph faithfully merges whatever
  each satellite last published, stale or not.
- A documented go-private caveat: the design assumes public satellites; if
  one goes private, distribution must be redesigned rather than quietly
  wiring a token into the fetch.
- This docs repo is slated to join as satellite #6 (epic #1, issue #6),
  making the documentation corpus itself graph-queryable.
