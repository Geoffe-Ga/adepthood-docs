# Creek-Vault

As of the 2026-07-31 baseline seed (issue #3).

A Python CLI and pipeline (`creek`) for organizing large volumes of
semi-structured personal data — chat exports, documents, notes, screenshots,
messages — into an interlinked Obsidian knowledge base, plus the chat-side
tooling that queries it. Source: Creek-Vault `README.md` and `CLAUDE.md`.

## Stack

- Python 3.11+ (CI tests 3.11–3.13), Typer + Rich CLI.
- Local-first NLP: classification on Ollama by default, embeddings via
  `sentence-transformers`; the Anthropic API path is opt-in.
- `uv` for reproducible installs (`creek-tools/uv.lock` is canonical).

## Module map

- `creek-tools/` — the main Python subproject: the `creek` package (flat
  layout), `creek_mcp` (MCP server exposing the vault to agents), `tests/`,
  and `scripts/` (`check-all.sh`, `test.sh`, `typecheck.sh`, …). It has its
  own `CLAUDE.md` with quality standards.
- `creek-tools/creek/templates/` — canonical templates deployed by
  `creek init`: the vault folder scaffold, the schema-skill tree
  (`*.SKILL.md`), and the per-vault `AGENTS.md` agent contract.
- `crawdad/` — a Discord bot: the chat-side interface to the vault,
  consuming the MCP server.
- `docs/Ontology/` — the canonical ontology specification tying Obsidian,
  the APTITUDE frequency framework, and the Archetypal Wavelength together.

The user's personal vault lives **outside the repo** (scaffolded by
`creek init --vault <path>`; no vault content is ever checked in).

## Data flow: the five-stage pipeline

1. **Redaction** — pattern-based scanning for secrets, API keys, and PII
   before anything else touches the data.
2. **Ingestion** — eleven source-specific ingestors (Claude/ChatGPT exports,
   Discord, markdown, PDF/DOCX, XLSX/CSV, PPTX, code, images via OCR,
   Substack, generic text) plus a read-only Google Drive downloader; each
   normalizes input to UTF-8 markdown with YAML frontmatter. Fragment IDs
   are hashed from `(source, timestamp, content)` so re-processing is
   idempotent.
3. **Classification** — rule-based pre-classification plus opt-in
   LLM-assisted tagging (topic, voice register, frequency, archetypal phase,
   privacy tier, confidence).
4. **Linking** — embedding-based semantic similarity, temporal proximity,
   and density-based "eddy" detection.
5. **Generation** — index notes, wavelength reports, the Voice Skill Tree,
   blog-idea mining, and voice-aware essay drafting.

Privacy is structural: fragments carry an `Open` / `Personal` / `Intimate`
tier, ingestion gates each source on logged consent, downstream stages filter
by tier independently, and `creek purge` implements right-to-be-forgotten
with hash-chained audit logs. See
[ADR 0012](../decisions/0012-local-first-privacy-tiers.md).

## Key entry points

- Install: `pip install -e creek-tools` (or `cd creek-tools && uv sync
  --all-extras` for the pinned environment).
- Scaffold a vault: `creek init --vault ~/Obsidian/Creek-Vault` (refuses
  paths inside a git repo by default).
- Quality gates: `./scripts/check-all.sh` from `creek-tools/` — coverage
  ≥ 90% (branch), docstring coverage ≥ 95%, complexity ≤ 10, mypy strict.
- Knowledge graph: built with the shared graphify toolchain; Creek-Vault's
  graph is ~30 MB and ships as a rolling release asset rather than being
  committed in-tree (adepthood `scripts/graph/README.md`, "Federation").

## Relation to Adepthood

Creek-Vault is the power-user, desktop-side expression of the same ontology
the Adepthood app carries: Creek's Frequencies are Adepthood's Aspects, and
the vault's `05-Wavelength/` and `06-Frequencies/` folders mirror the app's
stage and phase model (adepthood `NORTH-STAR.md`, section 11 names the Creek
Vault MCP seam and the shared ontology explicitly).
