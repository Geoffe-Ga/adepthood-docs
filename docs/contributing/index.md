# Contributing

Conventions and policy that govern work across the ecosystem: quality
gates, commit style, branching, review workflow, and the contracts the
autonomous pipeline enforces.

## Inclusion criteria

File a page (or update an existing one) here when a merged PR:

- Changes a quality threshold (coverage minimums, lint rulesets, complexity
  grades, docstring coverage).
- Adds, removes, or reorders a CI gate or pre-commit hook in any repo.
- Changes commit-message, branching, or PR conventions.
- Changes how the agent fleet works (Ralph loop mechanics, review verdicts,
  auto-merge rules, label semantics).
- Establishes a new cross-repo convention contributors must follow.

Do **not** file here for: one repo's internal implementation detail with no
policy weight, or decision rationale — record that as an ADR in
[Decisions](../decisions/index.md) and link it from the policy page.

## Conventions

- One page per policy area (`quality-gates.md`, `commit-style.md`,
  `agent-workflow.md`).
- State rules in the imperative and note which repos each rule applies to.
