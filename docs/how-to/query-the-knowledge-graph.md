# Query the knowledge graph

Orient in the adepthood codebase (or across the ecosystem) with graphify
before sweeping files. Verified against adepthood `scripts/graph/README.md`
as of 2026-07-31.

## Prerequisites

- adepthood's `.venv` activated (the scripts install the pinned `graphifyy`
  toolchain if the `graphify` CLI is missing)
- A graph on disk at `graphify-out/graph.json` — fetch or build below

## Steps

1. Get a graph. `graphify-out/` is git-ignored in adepthood, so a fresh
   clone or worktree has none. Fastest — download the rolling release
   (at most 24h stale):

   ```bash
   gh release download knowledge-graph --pattern graph.json --dir graphify-out
   ```

   Or build locally (~2 min, AST-only, no API keys):

   ```bash
   ./scripts/graph/build.sh
   ```

2. Ask questions:

   ```bash
   graphify query "how are habit streaks calculated?"   # general questions
   graphify path "HabitsScreen" "streaks"               # what connects A and B
   graphify explain "resonance"                          # explain a node
   graphify affected "get_session"                       # change impact
   ```

3. For cross-repo questions, fetch the federated pan-graph instead:

   ```bash
   gh release download knowledge-graph --pattern 'pan-*.json' --dir graphify-out
   ```

   `pan-meta.json` tells you which of the five repos are present in the
   build.

4. After modifying code, refresh the graph so it stays honest:

   ```bash
   ./scripts/graph/update.sh   # incremental, exit 0 when clean
   ```

5. When a graph answer materially helped (or misled you), record the trace
   so the weekly reflection can learn from it:

   ```bash
   graphify save-result --question "…" --answer "…" --type query \
     --nodes NodeA NodeB --outcome useful --memory-dir graph/memory/
   ```

   (Outcomes: `useful`, `dead_end`, or `corrected` with `--correction`.)
   Commit the trace file — `graph/memory/` is committed, unlike
   `graphify-out/`.

## Verify

- Queries return nodes with `source_location` fields — cite those when
  using graph facts.
- `graph-meta.json` (or `pan-meta.json`) shows a recent `built_at` and the
  `kind` you expect (`code-only`, `code+semantic`, or `pan-graph`).
- Never stall on graph absence: if no graph is available, proceed without
  it (adepthood `scripts/ralph/PROMPT.md`, step 0.5).
