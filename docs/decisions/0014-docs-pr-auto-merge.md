# 0014. Docs PRs land by auto-merge with CI gates as the only reviewer

## Status

Accepted (owner-confirmed 2026-07-31; epic #1 in this repo).

## Context

An autonomous sync pipeline that opens a PR every few hours cannot depend on
a human approver — a required review would either stall the corpus or decay
into rubber-stamping. But landing agent-written prose with no checks at all
would let broken links, malformed Markdown, and unbuildable nav reach the
published site.

## Decision

Every docs PR — agent or human — must pass three CI gates
(`.github/workflows/docs-ci.yml`): markdownlint (`markdownlint-cli2` with
the committed `.markdownlint-cli2.jsonc`), an offline internal-only link
check (lychee `--offline` — external links are deliberately not checked so
a flaky third-party site can never block the pipeline), and
`mkdocs build --strict`. When the gates pass, the PR auto-merges. **No human
is in the loop**: a human can intervene on any PR but is never required.
Anything the gates cannot catch is treated as a gap to fix in the gates,
not a reason to add manual review.

## Consequences

- The corpus stays current around the clock; the merge latency of a docs PR
  is CI time, not reviewer availability.
- Gate integrity becomes sacred — this repo's `CLAUDE.md` forbids weakening
  the gates to get a PR through, the same stay-green posture as
  [ADR 0007](0007-ralph-fleet-stay-green.md).
- Factual accuracy is *not* machine-checked; the defense is upstream (the
  sync agent's grounding rules and filing criteria) and downstream (humans
  read the published site and file issues when the corpus is wrong).
- One-time repo settings are prerequisites: auto-merge enabled, and the
  pipeline's labels bootstrapped by `labels-bootstrap.yml`.
