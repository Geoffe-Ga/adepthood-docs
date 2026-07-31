# WavelengthWatch — changelog

Rolling digest for `Geoffe-Ga/WavelengthWatch`. The sync pipeline appends
an entry per processed batch of merged PRs, newest first.

## 2026-07-31 — Baseline

State of the repo at the corpus seed (issue #3): watchOS SwiftUI app with
catalog browsing, offline caching (24h TTL), and a local-first journal
loop; FastAPI + SQLModel backend over SQLite serving `/api/v1/*`, seeded
from bundled CSV/JSON fixtures. Not yet deployed to production; App Store
launch planned. Knowledge graph committed in-tree at
`graphify-out/graph.json`. See
[architecture](../architecture/wavelengthwatch.md) and
[product](../products/wavelengthwatch.md).
