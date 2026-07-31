# scripts/graph — corpus knowledge graph

A pinned, reproducible knowledge-graph toolchain for this docs corpus,
using [graphify](https://github.com/safishamsi/graphify) (PyPI `graphifyy`,
pinned in [`requirements.txt`](./requirements.txt) — the pin MUST match
adepthood's `scripts/graph/requirements.txt` for federation compatibility).

Extraction is graphify's deterministic AST/prose pass: markdown headings
and inter-page links, local and keyless — no LLM calls. `build.sh` runs
`graphify update` rather than plain `extract` because `extract` routes
`.md` files to LLM semantic extraction and hard-fails without an API key,
while `update` re-extracts the full corpus through the AST extractors
(which cover markdown) with no key at all.

## In-tree distribution (satellite pattern)

Unlike adepthood's release-based distribution, this repo **commits**
`graphify-out/graph.json` on `main` — the corpus is small, so the graph
rides the tree. The adepthood hub fetches it over
`raw.githubusercontent.com` and merges it into the ecosystem
`pan-graph.json` nightly (`graph-federate.yml` in adepthood). Everything
else under `graphify-out/` (extraction cache, manifest) is git-ignored.

`.github/workflows/graph-build.yml` keeps the committed graph at most 24h
fresh: it rebuilds on every push to `main` touching `docs/**`,
`mkdocs.yml`, or `scripts/graph/**`, plus a nightly cron and manual
dispatch, and commits the result back only when it changed. The push path
filter excludes `graphify-out/**`, so the commit-back can never retrigger
the workflow.

## Commands

```bash
./scripts/graph/build.sh    # full AST/prose extract → graphify-out/graph.json
                            # prints "<nodes> nodes / <edges> edges"
```

The script installs the pinned toolchain into the active environment only
if the `graphify` CLI is missing, then operates on the repo root. Activate
a venv first so the install lands there.

## `GRAPHIFY_FORCE`

graphify has a **shrink guard**: a rebuild that would produce fewer nodes
than the existing `graph.json` refuses to overwrite it, protecting against
a truncated extract. After intentional page deletions, bypass it:

```bash
GRAPHIFY_FORCE=1 ./scripts/graph/build.sh
```

The workflow's nightly and `workflow_dispatch` runs always set it, so
deletions are reflected within 24h even if a push build declined the
smaller graph.

## Semantic layer (documented, not built)

A weekly `graphify extract . --backend claude` semantic pass — mirroring
adepthood's `graph-semantic.yml` (weekly cron + dispatch, hard-fail when
`ANTHROPIC_API_KEY` is missing, SHA256-content-keyed semantic cache
persisted between runs) — can upgrade the graph from structure-only to
meaning-bearing edges once the `ANTHROPIC_API_KEY` secret is added. It is
deliberately not part of `graph-build.yml`, which must stay $0 and
keyless. See the follow-up issue linked from issue #6.
