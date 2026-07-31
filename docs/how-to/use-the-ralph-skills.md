# Use the Ralph skills

Drive adepthood development with the repo's agent skills, from a phone
session or the autonomous loop. Verified against adepthood `CLAUDE.md`,
`.claude/skills/`, and `.claude/commands/ralph-tick.md` as of 2026-07-31.

## Prerequisites

- A Claude Code session in the adepthood repo (the skills live in
  `.claude/skills/`; the orchestrator command in `.claude/commands/`)
- For anything that commits: the `.venv` activated and gates runnable
  ([quality gates](run-the-adepthood-quality-gates.md))

## The day-to-day skills

- `/continue-epic` — pick up the next issue from the roadmap
  (`prompts/github-issues/`) and drive it to PR.
- `/triage-and-plan` — analyze the codebase and generate a new epic of
  issues.
- `/preflight` — run pre-commit, fix all failures, iterate until green.
- `/review-diff` — self-review the current branch diff before PR.
- `/flare` — turn a short bug/idea description into a grounded,
  Ralph-ready GitHub issue in one shot.
- `/graph` — graph-first codebase questions
  ([query the knowledge graph](query-the-knowledge-graph.md)).

Supporting skills the workflow leans on: `stay-green` (the TDD loop),
`ci-debugging` (CI failures), `address-feedback` (iterate on the reviewer's
`Verdict:` comment), `await-claude-review` (wait for the verdict without
polling), and `de-slopify` / `backlog-grooming` for maintenance.

## The autonomous loop

Start the fleet orchestrator:

```text
/loop /ralph-tick
```

One re-entrant session runs a pool of up to 4 worktree lanes
(`scripts/ralph/fleet.sh`), each moving independently through the four
gates — TDD → local check-all → CI → review — with the orchestrator alone
merging (`scripts/ralph/FLEET.md`;
[ADR 0007](../decisions/0007-ralph-fleet-stay-green.md)). Workers follow
the per-issue contract in `scripts/ralph/PROMPT.md`: one issue, one PR,
never merge, never touch `main`.

## Verify

- A skill run ends with the state it promises (e.g. `/preflight` ends with
  `pre-commit run --all-files` exiting 0; `/continue-epic` ends with an
  open PR).
- Fleet health: merged PRs post a Discord recap (`scripts/ralph/RECAP.md`),
  and `scripts/ralph/pick-next.sh` / `pr-ready.sh` are the ground truth for
  what runs next and what may merge.
