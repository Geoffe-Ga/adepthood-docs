# Creek-Vault — repo map

Deep reference for the
[Creek-Vault](https://github.com/Geoffe-Ga/Creek-Vault) repository,
generated from source. For the product-level story see
[the product page](../../products/creek-vault.md).

Creek-Vault is by far the largest satellite (≈250 Python source modules
across three components), so this section covers it at package granularity
with deep dives into the CLI surface, the pipeline's core algorithms, the
MCP server, and the crawdad bot — rather than per-function coverage.

## Repository topology

The repo is "the **toolchain** plus the **canonical reference material**.
Your personal vault … lives *elsewhere on disk* and is never checked in"
(`README.md`, "Repository topology"; enforced as FEAT-019 per
`CLAUDE.md:13`):

| Path | What it is |
| --- | --- |
| `creek-tools/creek/` | The `creek` CLI + pipeline package — 191 Python files in 20 sub-packages |
| `creek-tools/creek_mcp/` | The `creek-tools-mcp` MCP server — 30 Python files |
| `creek-tools/creek/templates/` | Canonical vault scaffold, schema-skill tree (`*.SKILL.md`), and `AGENTS.md` agent contract, deployed by `creek init` |
| `creek-tools/docs/` | 30+ design docs incl. 7 ADRs (`docs/architecture/ADR/0001…0007`) and a threat model |
| `crawdad/` | The Discord bot — 23 Python files consuming the MCP surface |
| `docs/Ontology/` | The master Creek Ontology specification |

## `creek` package map (all 20 sub-packages)

| Package | Concern |
| --- | --- |
| `creek/ingest/` | 11 source ingestors (Claude, ChatGPT, Discord, code, documents, markdown, spreadsheets, presentations, images/OCR, Substack, generic) + Google Drive downloader, ingest ledger, journal staging, refresh (`README.md`, "Key capabilities") |
| `creek/redact/` | Pattern-based PII/secret scanner, redactor, review queue, audit |
| `creek/classify/` | Rule-based + LLM classification: engine, few-shot examples, calibration, privacy passes, weighted/holonic scoring, review runner; `classify/llm/` holds the provider router with the Intimate-never-cloud gate |
| `creek/clean/` | Hygiene: authorship, dedup (exact + semantic), quality filters, per-source filters |
| `creek/link/` | Embedding similarity, temporal proximity, thread building, density-based eddy detection |
| `creek/generate/` | Index notes, wavelength reports, compost surfacing, mining, drafts, voice fingerprinting (`generate/ai_style/` — 20 modules of AI-tell scanning/sanitizing), lexicon, synchronicity/paradox/unnamed detectors, state reports |
| `creek/atomize/` | Fragment splitting/aggregation (FEAT-021/022) |
| `creek/compile/` | Fragment → compiled-layer page roll-ups with provenance |
| `creek/author/` | The Writing Desk: agents, contracts, conductor, reflection, voice |
| `creek/save/` | Filing answers back into the vault (router, writer, slug) |
| `creek/lint/` | Unified vault hygiene checks (11 checks under `lint/checks/`) |
| `creek/purge/` | Right-to-be-forgotten engine + audit (see [Pipeline](pipeline.md)) |
| `creek/audit/` | Hash-chained audit logs, yield summaries |
| `creek/care/` | Acute-distress guardrail used by the MCP surface |
| `creek/confidential/` | Key vault for the confidential-hosting path (ADRs 0005-0007) |
| `creek/sync/` | Scheduled sync (launchd/systemd unit emission) |
| `creek/vault/` | Vault reader/writer, other-author support |
| `creek/templates/` | Canonical scaffold (see below) |
| `creek/classify/examples/`, `creek/generate/exemplars/` | YAML few-shot/calibration data |
| Top-level modules | `cli.py` (5,727 lines — the whole command surface), `pipeline.py`, `models.py`, `config.py`, `consent.py`, `fragment.py`, `hierarchy.py`, `scaffold.py`, `time.py`, `main.py` |

## The vault scaffold (canonical template)

`creek init` deploys this structure (from
`creek-tools/creek/templates/vault/`):

| Folder | Layer |
| --- | --- |
| `00-Creek-Meta/` | Ontology copy, Skills, Templates, Scripts, Processing-Log (consent log, audit logs, embeddings cache) |
| `01-Fragments/` | Atomic content: Conversations, Journal, Messages, Technical, Writing (incl. Substack), Unsorted |
| `02-Threads/` | Compiled narratives: Active / Dormant / Resolved |
| `03-Eddies/` | Density-detected clusters |
| `04-Praxis/` | Actionable: Daily / Seasonal / Situational |
| `05-Wavelength/` | Mode-Profiles, Observations, Phase-Maps |
| `06-Frequencies/` | `F1-Agency`, `F2-Receptivity`, `F3-Self-Love-Power`, `F4-Community-Love`, `F5-Achievism`, `F6-Pluralism`, `F7-Integration`, `F8-True-Self`, `F9-Unity`, `F10-Emptiness` |
| `07-Voice/` | Drafts, Lexicon, Register-Samples, Rhetorical-Patterns |
| `08-Decisions/` | Active / Archive / Frameworks |
| `09-Reference/` | APTITUDE-Course, External-Sources, Published-Essays |
| `10-Liminal/` | Compost, Paradoxes, Synchronicities, Unnamed |
| `11-Other-Authors/` | Per-author sub-vaults (incl. `ai-as-user/`) |

## The shared ontology, in code

`creek/models.py` encodes the APTITUDE / Archetypal Wavelength ontology as
enums with legacy-alias migration (INC-019):

- `Frequency` — `F1` … `F10` + `unclassified` (`creek/models.py:115-133`).
- `Phase` — `rising`, `peaking`, `withdrawal`, `diminishing`,
  `bottoming_out`, `restoration`, `unclassified`
  (`creek/models.py:136-150`) — the same six phases WavelengthWatch stores
  in its `Phase` table and wavelength-demo hard-codes in `PHASES`.
- `Mode` — `inhabit`, `express`, `collaborate`, `integrate`, `absorb`
  (`creek/models.py:153-165`).
- `PrivacyTier` — `open` / `personal` / `intimate`; "``intimate`` content is
  reserved exclusively for self-authored fragments", and the legacy
  `"public"` value maps to `OPEN` with a `DeprecationWarning` (INC-003,
  `creek/models.py:329-346`).

## Integration points with adepthood

- **`creek.journal` MCP tool** — "Ingest one Adepthood journal entry as a
  vault fragment (idempotent)" (`creek_mcp/server.py:360`) is a direct,
  code-level bridge: adepthood journal entries can flow into the vault's
  `01-Fragments/Journal/`.
- **`creek.reflect` / `creek.wheel`** — "anchored Higher-Self margin notes
  on a single journal entry" and "a per-frequency balance read of the corpus
  for the Map" (`creek_mcp/server.py:332`, `:349`) implement, on the vault
  corpus, the same Higher-Self reflection and Map concepts adepthood's
  product vision names.
- **Shared ontology** — the `Frequency`/`Phase`/`Mode`/`PrivacyTier` enums
  above mirror adepthood's APTITUDE stage model and the ecosystem-wide
  wavelength vocabulary.
- **Vault folder `09-Reference/APTITUDE-Course/`** reserves a home for the
  aptitude-course corpus inside a personal vault.

Deep dives: [CLI surface](creek-cli.md) ·
[Pipeline and core algorithms](pipeline.md) ·
[MCP server](mcp-server.md) · [crawdad bot](crawdad.md).

---

*Grounded in creek-vault@85d230b, 2026-07-31.*
