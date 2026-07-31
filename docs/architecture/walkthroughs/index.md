# End-to-end walkthroughs

Narrative traces that follow one real action through the entire stack, hop
by hop, with a `file:line` citation at every hop. Where the reference pages
answer "what is this module?", these pages answer "what actually happens,
in order, when a user (or a robot) does the thing?" — including what
happens at each hop when things go wrong, taken from the real error
handling rather than imagined.

Every code excerpt is quoted verbatim from the cited source at the pinned
commit in each page's provenance footer. Paths are repo-relative; pages
that span more than one repository name the repo alongside the path.

## The five traces

- [Completing a habit](habit-completion.md) — a tap in the Habits screen
  through the optimistic store mutation, the API client, the FastAPI
  check-in route, the streak and milestone math, the database write, and
  the toast on the way back.
- [Signing in](sign-in.md) — credentials through lockout and bcrypt
  verification to JWT issuance, secure token storage, navigator gating,
  how every later request attaches the token, and the 401 → refresh →
  retry lifecycle.
- [Journal entry → Higher Self resonance](journal-resonance.md) — entry
  creation, the resonance pass (privacy floor, care screen, wallet
  charge, marginalia, completion detection), and how a resonant
  invitation surfaces — and gets accepted — in the UI.
- [A code merge → knowledge graph → pan-graph](graph-pipeline.md) — a
  push to `main` through the graph-build workflow, the rolling release,
  the nightly federation into a pan-graph, and how an agent session
  consumes it via `graphify query`.
- [A source-repo PR → this docs site](docs-sync.md) — a merged PR through
  the watermark poller, `sync-input.json`, the sync agent's edits, the
  auto-merged docs PR, and the Pages deploy.

## Reading a walkthrough

Hops are numbered in causal order. A hop is one sentence of what happens,
the citation that proves it, and — where the logic is load-bearing — a
minimal verbatim excerpt. Diagrams are deliberately plain-markdown hop
lists rather than rendered sequence diagrams: even though this site's
`mkdocs.yml` now registers a mermaid custom fence under
`pymdownx.superfences` (`mkdocs.yml:57-61`), a hop list keeps every hop
adjacent to its citation, which a rendered diagram cannot.

*Grounded in Geoffe-Ga/adepthood@55eef11 and
Geoffe-Ga/adepthood-docs@8b73a15, 2026-07-31.*
