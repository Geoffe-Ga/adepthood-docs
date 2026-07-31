# Creek-Vault — changelog

Rolling digest for `Geoffe-Ga/Creek-Vault`. The sync pipeline appends an
entry per processed batch of merged PRs, newest first.

## 2026-07-31 — Baseline

State of the repo at the corpus seed (issue #3): the five-stage pipeline
(redaction → ingestion → classification → linking → generation) is
operational with eleven ingestors plus a Google Drive downloader; privacy
tiers, consent logging, and `creek purge` right-to-be-forgotten are in
place; `creek_mcp` exposes the vault to agents and the `crawdad` Discord
bot consumes it. No user vault content lives in the repo. Knowledge graph
distributed as a rolling release asset (~30 MB, not committed). See
[architecture](../architecture/creek-vault.md) and
[product](../products/creek-vault.md).
