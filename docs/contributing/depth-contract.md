# Reference depth contract

The binding quality bar for every page under
[Reference](../reference/index.md) and every
[end-to-end walkthrough](../architecture/walkthroughs/index.md). It was
set by [epic #17](https://github.com/Geoffe-Ga/adepthood-docs/issues/17)
after owner feedback that README-level summaries are not enough: these
pages must be fed directly from source code and explain behavior with
significant clarity and precision.

Every future edit to those pages — by the docs-sync agent, a Ralph lane,
or a human — is held to this bar. An edit that lowers a page below it is
a regression, even if all CI gates pass.

## The six rules

1. **Every factual claim cites its source** as a repo-relative
   `file:line` (or `file:start-end`) reference. Load-bearing logic gets
   a short verbatim code excerpt, not a paraphrase.
2. **Enumerable surfaces get complete tables** — every endpoint (method,
   path, auth, request schema, response schema, status codes/errors),
   every model (fields: name, type, constraints, relations, purpose),
   every screen/store/hook that is part of the public shape of a module.
   "Complete" means enumerated from code, not sampled.
3. **Explain why, not just what** — link the relevant ADR in
   [Decisions](../decisions/index.md) where one exists; where behavior
   encodes an undocumented decision, say so explicitly.
4. **No invented behavior.** If code is ambiguous or a branch is
   unreachable/unclear, the page says that plainly instead of guessing.
5. **One module/concern per page**, so docs-sync diffs map cleanly onto
   pages. Each page ends with a provenance footer:
   `*Grounded in <repo>@<sha>, <YYYY-MM-DD>.*`
6. **All pages pass the existing gates** (markdownlint, offline link
   check, `mkdocs build --strict`) and land under the auto-nav (no
   `nav:` key in `mkdocs.yml`; `.pages` ordering may be extended by
   humans or lanes, never by the sync agent).

## How the contract is maintained

The docs-sync agent carries this contract inline in
`scripts/sync/PROMPT.md`: when a folded PR touches code documented under
`docs/reference/**` or `docs/architecture/walkthroughs/**`, it must
re-verify the affected tables against the diff, refresh citations and
verbatim excerpts to the post-merge source, and update the provenance
footer to the merged `repo@sha` and sync date. When a truncated patch
makes verification impossible, the agent leaves the page unchanged and
records the skip in the changelog rather than guessing.

## Reviewing against the contract

Spot-check protocol, from the epic's acceptance criteria: pick any
endpoint, model, or screen table and diff it against the cited source at
the footer's pinned SHA. Any omission, invention, or stale citation is a
contract violation and should be filed (or fixed) as such.
