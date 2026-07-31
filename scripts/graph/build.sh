#!/usr/bin/env bash
# scripts/graph/build.sh — full knowledge-graph extraction over the corpus.
#
# Installs the pinned graphify toolchain into the active environment (only
# when the CLI is absent), runs a deterministic full AST/prose extract over
# the whole repo (markdown headings + inter-page links — graphify's keyless
# doc-structure pass), and prints the resulting node / edge counts. Local
# only: no LLM calls, no API keys, safe to run inside any git worktree.
#
# `graphify update` (not `extract`) is the keyless path for a prose corpus:
# plain `extract` routes .md files to LLM semantic extraction and hard-fails
# without an API key, while `update` re-extracts the full corpus through the
# AST extractors, which cover markdown. With no changed-path argument it
# rebuilds everything, so this is a full build, not an incremental one.
#
# Unlike adepthood's release-based distribution, this repo follows the
# satellite pattern: graphify-out/graph.json is COMMITTED on main so the
# adepthood hub can fetch it over raw.githubusercontent.com and federate it
# into pan-graph.json nightly.
#
# Usage: ./scripts/graph/build.sh [extra graphify update args...]
# Env:   GRAPHIFY_FORCE=1  bypass graphify's shrink guard after intentional
#                          file deletions (the nightly rebuild sets this).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
OUT_DIR="$REPO_ROOT/graphify-out"

ensure_graphify() {
  if command -v graphify >/dev/null 2>&1; then
    return
  fi
  echo "graphify CLI not found — installing pinned toolchain into the active environment..."
  python3 -m pip install -r "$SCRIPT_DIR/requirements.txt"
}

print_counts() {
  local graph_json="$OUT_DIR/graph.json"
  if [[ ! -f "$graph_json" ]]; then
    echo "warning: $graph_json not found; cannot report counts" >&2
    return
  fi
  python3 - "$graph_json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    graph = json.load(handle)
node_count = len(graph.get("nodes", []))
# Raw (--no-cluster) extraction stores edges under node_link "links";
# clustered graphs may use "edges". Accept either.
edge_count = len(graph.get("edges") or graph.get("links") or [])
print(f"{node_count:,} nodes / {edge_count:,} edges")
PY
}

ensure_graphify
echo "Building knowledge graph for $REPO_ROOT ..."
graphify update "$REPO_ROOT" --no-cluster "$@"

# Reporting the counts is cosmetic; never let it override the extract exit code.
print_counts || true
