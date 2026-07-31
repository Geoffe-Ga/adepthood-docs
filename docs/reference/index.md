# Reference

Deep, code-grounded reference for every repo in the ecosystem — written
by reading source code, not project READMEs. Where
[Products](../products/index.md) tells the product story and
[Architecture](../architecture/index.md) draws the system shape, this
section enumerates the actual surfaces: every endpoint, every model
field, every screen and store, cited line by line. The companion
[end-to-end walkthroughs](../architecture/walkthroughs/index.md) trace
single actions through these surfaces hop by hop.

## The depth contract

Every page in this section is held to the depth contract of
[epic #17](https://github.com/Geoffe-Ga/adepthood-docs/issues/17),
stated in full in
[Contributing → Reference depth contract](../contributing/depth-contract.md).
In brief:

1. Every factual claim cites a repo-relative `file:line`; load-bearing
   logic is quoted verbatim, not paraphrased.
2. Enumerable surfaces (endpoints, models, screens, stores, hooks) get
   complete tables — enumerated from code, never sampled.
3. Pages explain *why*, linking the relevant
   [ADR](../decisions/index.md) where one exists and flagging
   undocumented decisions explicitly.
4. No invented behavior: ambiguity in the code is stated plainly, never
   papered over.
5. One module or concern per page, each ending with a provenance footer
   (`repo@sha`, date).
6. Every page passes the site gates (markdownlint, offline link check,
   `mkdocs build --strict`) and lands under the auto-nav.

## Sections

| Section | Pages | Covers |
| --- | --- | --- |
| [Adepthood backend](backend/index.md) | 68 | FastAPI backend of the adepthood monorepo: all 27 routers, the full data model, domain logic, and infrastructure |
| [Adepthood frontend](frontend/index.md) | 16 | React Native app: navigation graph, feature modules, Zustand stores, API client, design-system usage |
| [Creek-Vault](creek-vault/index.md) | 5 | The largest satellite at package granularity: CLI surface, pipeline algorithms, MCP server, crawdad bot |
| [WavelengthWatch](wavelengthwatch/index.md) | 4 | FastAPI backend plus the offline-first watchOS SwiftUI app and its sync flows |
| [aptitude-course](aptitude-course/index.md) | 3 | The 36-week course content repo: manifest pipeline and the consumption contract |
| [wavelength-demo](wavelength-demo/index.md) | 4 | Dependency-light Vite + React SPA: content pipeline, wave geometry, app shell |

Page counts include each section's own index.

## Maintenance

These pages are maintained at contract depth by the autonomous
docs-sync pipeline: when a merged PR touches code documented here, the
sync agent re-verifies the affected tables against the diff and
refreshes citations and provenance footers (see
`scripts/sync/PROMPT.md`). Corrections and additions by humans or lanes
are equally bound by the contract.
