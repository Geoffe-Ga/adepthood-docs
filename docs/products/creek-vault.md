# Creek-Vault

As of the 2026-07-31 baseline seed (issue #3).

Creek-Vault turns a lifetime of scattered digital exhaust — chat exports,
documents, notes, screenshots, messages — into an interlinked Obsidian
knowledge base that knows your patterns. It is the desktop, power-user
expression of the ecosystem's ontology: every fragment classified by topic,
voice, Frequency, archetypal phase, and privacy tier.

## What it does for its user

- **Ingests almost anything.** Eleven source ingestors (Claude/ChatGPT
  exports, Discord, markdown, PDF/DOCX, spreadsheets, presentations, code,
  images via OCR, Substack, generic text) plus a read-only Google Drive
  downloader.
- **Protects before it processes.** Redaction scans for secrets and PII
  first; ingestion is consent-gated per source; classification runs locally
  (Ollama) by default; `creek purge` delivers right-to-be-forgotten with
  audit logs.
- **Finds the connections.** Embedding similarity, temporal proximity, and
  "eddy" cluster detection interlink fragments across sources.
- **Writes back.** Index notes, weekly/monthly wavelength reports, a
  per-frequency Voice Skill Tree, blog-idea mining, and essay drafting in
  the user's own voice (`creek skills` / `creek mine` / `creek draft`).
- **Talks to agents.** The `creek_mcp` server exposes the vault to AI
  agents, and the `crawdad` Discord bot is its chat-side interface.

## How to use it

Install the CLI, scaffold a vault outside the repo, run the pipeline, and
browse the result in Obsidian —
[Run Creek-Vault locally](../how-to/run-creek-vault-locally.md). The
repo's own `creek-tools/docs/` guides cover each stage end to end.

## Cross-repo relationships

The vault's `05-Wavelength/` and `06-Frequencies/` layers implement the
same model as Adepthood's Aspects and the course's stages
(`docs/Ontology/` is the canonical specification). Adepthood's north star
names the Creek Vault MCP seam as part of the app's future: the vault as
the deep, local corpus a Higher Self can draw on.
