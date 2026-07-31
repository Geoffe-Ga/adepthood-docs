# 0007. Ralph fleet with a stay-green gated workflow

## Status

Accepted (backfilled 2026-07-31; documented in adepthood `CLAUDE.md`,
`scripts/ralph/FLEET.md`, and `scripts/ralph/PROMPT.md`).

## Context

Adepthood's backlog is executed largely by autonomous agent sessions. With
no human reviewing every diff, quality has to be enforced by machinery; and
a single sequential agent loop left throughput on the table when backlog
issues were independent.

## Decision

Adopt two complementary structures:

1. **Stay-green quality gates.** Every change passes a 3-gate ladder
   (adepthood `CLAUDE.md`): Gate 1 pre-commit (~10s format/lint/hygiene, 34
   hook entries in `.pre-commit-config.yaml`), Gate 2 pre-push (full test
   suite + coverage + complexity), Gate 3 CI (all of that plus cross-version
   compatibility on Python 3.11/3.12/3.13, docstring and branch coverage,
   security audit). Gates are never weakened to pass — a failing gate sends
   work back to the code.
2. **The Ralph fleet.** A single orchestrator session (`/loop /ralph-tick`)
   runs a worker pool of up to 4 lanes, each lane one issue in its own git
   worktree moving independently through a four-gate pipeline: TDD
   (red–green–refactor), local `check-all.sh` plus a pre-push self-review,
   CI green, and a reviewer verdict comment (`LGTM` required). Picking is
   optimistic (issues that look independent), merging is pessimistic —
   serialized, and only when the branch is proven current with `main`
   (compare API `behind_by == 0`). Workers never merge; the orchestrator
   does (`scripts/ralph/FLEET.md`).

## Consequences

- Parallelism can never merge broken or stale code: an imperfect
  independence guess costs at most a lazy sync, and a ready lane never
  waits on a slow one.
- The reviewer-verdict gate makes review part of the pipeline, not an
  optional courtesy; `CHANGES_REQUESTED` mechanically routes back to TDD.
- All process knowledge must live in files agents read (`CLAUDE.md`,
  `.claude/skills/`, `scripts/ralph/`), which is what makes this docs
  corpus's [contributing pages](../contributing/index.md) possible.
- The pattern exported cleanly: this docs repo's no-human-in-the-loop
  auto-merge pipeline ([ADR 0014](0014-docs-pr-auto-merge.md)) is the same
  gates-as-reviewer philosophy.
