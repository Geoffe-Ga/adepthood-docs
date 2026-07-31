# Walkthrough: a code merge → knowledge graph → pan-graph

A merge to `adepthood`'s `main` traced through the graph-build workflow,
the rolling `knowledge-graph` release, the nightly federation of six
repos into one pan-graph, and the way an agent session actually consumes
the result with `graphify query`. Paths are repo-relative to
`Geoffe-Ga/adepthood` unless a repo is named.

The distribution design in one sentence: three workflows — graph-build
(code-only), graph-semantic, graph-federate — publish **disjoint asset
sets** onto one rolling GitHub release tagged `knowledge-graph`, so
"three writers, one release, three disjoint asset sets" never clobber
each other (`.github/workflows/graph-federate.yml:9-13`).

## From merge to published graph

1. **The trigger.** A push to `main` touching `backend/**`,
   `frontend/**`, `scripts/**`, or the workflow itself starts
   graph-build (`.github/workflows/graph-build.yml:20-27`); a nightly
   cron at 04:40 UTC and manual dispatch run the full-rebuild path
   (`.github/workflows/graph-build.yml:27-30`). Runs serialize under a
   `graph-build` concurrency group and are never cancelled mid-publish
   (`.github/workflows/graph-build.yml:40-42`).

2. **Restore the prior graph.** On the push path, the job downloads the
   previously published `graph.json` from the rolling release so it can
   refresh incrementally
   (`.github/workflows/graph-build.yml:87-99`).

3. **Incremental refresh.** `scripts/graph/update.sh` runs
   `graphify update` — an AST-only re-extract of changed files, "no
   LLM calls, no API keys" (`scripts/graph/update.sh:1-10` and `29`).
   If the incremental update fails — "most often because deleted files
   would shrink the graph past graphify's shrink guard" — the step
   forces a full rebuild with `GRAPHIFY_FORCE=1`
   (`.github/workflows/graph-build.yml:101-113`).

4. **Nightly full rebuild.** Scheduled and manual runs always build
   from scratch via `scripts/graph/build.sh` (`graphify extract
   --code-only`, `scripts/graph/build.sh:46-47`) with
   `GRAPHIFY_FORCE=1`, because only a forced full build "can shrink
   the graph when files were deleted"
   (`.github/workflows/graph-build.yml:115-124`).

5. **Provenance sidecar.** The job writes `graph-meta.json` — built-at
   timestamp, short commit SHA, node/edge counts, the pinned graphifyy
   version, and `"kind": "code-only"`
   (`.github/workflows/graph-build.yml:126-158`). The version pin is
   read from `scripts/graph/requirements.txt` and fails the run loudly
   if unreadable (`.github/workflows/graph-build.yml:65-75`).

6. **Publish to the rolling release.** `gh release upload ... --clobber`
   upserts `graph.json` + `graph-meta.json` (and, after full builds,
   `GRAPH_REPORT.md`) onto the `knowledge-graph` release, retrying once
   after 10 s and then failing loudly — "publishing is never silently
   skipped" (`.github/workflows/graph-build.yml:159-199`). The release
   is explicitly "rolling": assets are re-uploaded in place and the tag
   is not a version (`.github/workflows/graph-build.yml:178-183`).

7. **Nightly observability tail.** Schedule/dispatch runs also append a
   benchmark line to `graph/metrics/benchmark-trend.jsonl` (committed
   back to `main`), probe the semantic layer's staleness, and — past a
   14-day threshold — file a deduplicated `graph-staleness` issue
   (`.github/workflows/graph-build.yml:201-332`); all of it best-effort
   so "a clustering/benchmark/parse failure ... must warn and move on"
   (`.github/workflows/graph-build.yml:203-210`).

## From six graphs to one pan-graph

1. **The federate trigger.** Graph-federate runs nightly at 06:10 UTC —
   deliberately "after graph-build's 04:40 nightly rebuild has
   published a fresh own graph" — plus on manual dispatch and on a
   `repository_dispatch` of type `graph-updated`, which "lets a
   satellite repo poke a re-federation when its own graph updates"
   (`.github/workflows/graph-federate.yml:31-38`).

2. **Own graph, fatal fetch.** The job downloads adepthood's
   `graph.json` from the rolling release into
   `fed/adepthood/graphify-out/graph.json`; a miss is the only fatal
   fetch — "without adepthood's own graph there is nothing to federate"
   (`.github/workflows/graph-federate.yml:94-112`). The odd directory
   layout is load-bearing: merge-graphs derives each input's repo tag
   from the graph file's *grandparent directory name*, so
   `fed/<repo>/graphify-out/graph.json` makes the tag resolve to
   `<repo>` (`.github/workflows/graph-federate.yml:95-103`).

3. **Satellite fetches, degradable.** Five satellites — Creek-Vault,
   aptitude-course, wavelength-demo, WavelengthWatch, and this docs
   repo — are fetched over plain public HTTPS in a fixed order that
   pins the deterministic per-repo node-id prefixes
   (`.github/workflows/graph-federate.yml:113-133`). Each download is
   JSON-validated; a satellite that fails "degrades to a `::warning`
   and an excluded repo; it never fails the run"
   (`.github/workflows/graph-federate.yml:144-153`). A `fed/repos.json`
   manifest records exactly which repos made it
   (`.github/workflows/graph-federate.yml:155-180`).

4. **The merge.** `graphify merge-graphs` combines the own graph with
   every present satellite into `pan-graph.json`; because the tool
   requires at least two inputs, a zero-satellite night falls back to
   copying adepthood's graph verbatim
   (`.github/workflows/graph-federate.yml:182-213`).

5. **Pan-meta bookkeeping.** `pan-meta.json` records built-at, SHA,
   `"kind": "pan-graph"`, merged node/edge totals, and a per-repo table
   with `present` flags, per-repo node/edge counts, and the source URL,
   plus flat `repos_present` / `repos_missing` lists
   (`.github/workflows/graph-federate.yml:230-301`).

6. **Publish, together.** `pan-graph.json` and `pan-meta.json` are
   uploaded in a single `--clobber` call "so a pan-graph is never
   published without its manifest", with the same
   retry-once-then-fail-loud policy
   (`.github/workflows/graph-federate.yml:303-332`). This workflow
   never writes `graph.json`/`graph-meta.json` — the asset sets stay
   disjoint (`.github/workflows/graph-federate.yml:9-13`).

## How a session consumes it

1. **Restore on session start.** The Claude Code `SessionStart` hook
   refreshes `graphify-out/` from the rolling release unless a local
   copy is under 48 h old (`GRAPH_FRESH_MAX_AGE_SECONDS=172800`),
   fail-soft: a failed or malformed download "must never clobber an
   existing graphify-out/graph.json", so it validates JSON in a temp
   dir first; `pan-graph.json` and `graph-meta.json` are best-effort
   extras (`.claude/hooks/session-start.sh:35-39` and `113-137`).

2. **Prefer the pan-graph.** The graph skill points read subcommands at
   `graphify-out/pan-graph.json` whenever it exists — "it also carries
   the four satellite repos" — falling back to the repo's own
   `graph.json` (`.claude/skills/graph/SKILL.md:30-40`).

3. **Query instead of grep.** Agents then answer codebase questions
   with `graphify query "<question>"` (plus `path`, `explain`,
   `affected`) before any file sweep, per the repo instructions
   (`CLAUDE.md`, "Knowledge Graph (graphify)" section), and refresh
   after edits with `./scripts/graph/update.sh`.

## Failure modes

- **Missing own graph at federate time** — hard error, run fails:
  `"adepthood own graph.json missing from release — cannot federate"`
  (`.github/workflows/graph-federate.yml:108-112`).
- **Unreachable satellite** — warning + exclusion; the pan-graph
  ships without that repo, and `pan-meta.json` lists it under
  `repos_missing` (`.github/workflows/graph-federate.yml:148-153`).
- **A satellite goes private** — documented as the dangerous case: the
  fetch 404s (silent drop), and the workflow header forbids "fixing"
  it with a token because that "would leak private structure onto a
  public asset" (`.github/workflows/graph-federate.yml:20-29`).
- **Shrink guard trips on incremental update** — automatic
  `GRAPHIFY_FORCE=1` full rebuild keeps `main` green
  (`.github/workflows/graph-build.yml:106-113`).
- **Release upload fails** — one retry after 10 s, then a loud
  `::error` and job failure in both workflows
  (`.github/workflows/graph-build.yml:184-196`,
  `.github/workflows/graph-federate.yml:320-330`).
- **Semantic layer goes stale** — nightly probe files one deduplicated
  `graph-staleness` issue pointing at the graph-semantic dispatch
  (`.github/workflows/graph-build.yml:303-332`).
- **Session restore fails** — every error path in the hook warns and
  returns 0; a session never aborts because the graph could not be
  fetched (`.claude/hooks/session-start.sh:107-140`).

*Grounded in Geoffe-Ga/adepthood@55eef11, 2026-07-31.*
