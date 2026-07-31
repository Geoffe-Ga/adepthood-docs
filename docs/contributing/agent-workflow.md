# Agent workflow: fleet, playbook, graph-first

How the autonomous side of the ecosystem works, as of 2026-07-31. Sources:
adepthood `scripts/ralph/FLEET.md`, `scripts/ralph/PROMPT.md`, `CLAUDE.md`.
Applies to: adepthood primarily; this docs repo runs its own no-human
pipeline ([ADR 0013](../decisions/0013-pull-model-docs-sync.md),
[ADR 0014](../decisions/0014-docs-pr-auto-merge.md)).

## The Ralph fleet

One orchestrator session (`/loop /ralph-tick`) runs up to 4 **lanes**, each
one backlog issue in its own git worktree
(`.ralph/worktrees/issue-<N>`, branch `issue/<N>-<slug>`), moving
independently through four gates:

1. **TDD** — red–green–refactor via `stay-green`.
2. **Local quality** — the relevant `check-all.sh` exits 0, then a
   pre-push self-review must return clean.
3. **CI** — all Actions jobs green (failures route through `ci-debugging`).
4. **Review** — the reviewer's top-level `Verdict:` comment must be `LGTM`
   (`CHANGES_REQUESTED`/`COMMENTS` route through `address-feedback`).

Core principle: **optimistic parallelism, pessimistic merge.**
`pick-next.sh` hands out issues that merely *look* independent (label
heuristics: `solo` monopolizes the fleet, shared epic labels block
parallel pickup unless `parallelizable`); correctness never depends on the
guess. Merges are serialized by the orchestrator and require the branch to
be **proven current** — the compare API's `behind_by == 0` — because
GitHub's `mergeStateStatus: CLEAN` is not a freshness signal on this repo.
A behind lane lazily merges `main` in (never force-push, never rebase of a
pushed branch) and merges on a later wake. Workers never merge and never
touch `main`.

## The playbook system

Concrete "when X, do Y" rules are distilled **weekly from real failures** —
flare-filed bugs, review verdicts that blocked LGTM, and the graph memory's
lessons digest — by `.github/workflows/weekly-playbook.yml`, which specs
each week's delta as a P0 `agent-ready` issue (label `playbook`) that the
fleet implements. Every curated rule carries an HTML-comment evidence
marker; the playbook may add, edit, or retire only marker-bearing rules
(in `CLAUDE.md`, `.claude/agents/`, and `.claude/skills/` playbook
sections). Humans edit freely — removing the marker takes a rule out of
the playbook's jurisdiction.

## Graph-first orientation

Before sweeping files, agents query the knowledge graph
(`graphify query` / `path` / `explain` / `affected`), cite node
`source_location`s, refresh the graph after changes
(`./scripts/graph/update.sh`), and record whether queries helped
(`graphify save-result … --memory-dir graph/memory/`). Graph absence never
stalls work. See
[Query the knowledge graph](../how-to/query-the-knowledge-graph.md) and
ADRs [0008](../decisions/0008-graphify-knowledge-graph.md)–[0010](../decisions/0010-pan-graph-federation.md).

## Where this docs repo fits

The same gates-as-reviewer philosophy, applied to prose: a scheduled sync
agent files changes by each category's `index.md` rules, and CI
(markdownlint + offline links + strict build) is the only reviewer. Never
weaken those gates to land a PR.
