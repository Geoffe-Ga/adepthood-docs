# Run Creek-Vault locally

Install the `creek` CLI from `Geoffe-Ga/Creek-Vault` and scaffold a vault.
Verified against the repo state of 2026-07-31.

## Prerequisites

- Python 3.11+
- Obsidian (to browse the resulting vault; the pipeline itself is pure CLI)
- Optional for local classification: Ollama; embeddings use
  `sentence-transformers` locally by default

## Steps

1. Install the toolchain — either editable from the repo root:

   ```bash
   pip install -e creek-tools
   ```

   or the fully pinned dev environment:

   ```bash
   cd creek-tools
   uv sync --all-extras
   pre-commit install
   ```

2. Scaffold your vault **outside the repository** (the command refuses
   in-repo paths by default):

   ```bash
   creek init --vault ~/Obsidian/Creek-Vault
   ```

3. After upgrading the toolchain, re-deploy the schema skills into the
   vault:

   ```bash
   creek skills sync --vault ~/Obsidian/Creek-Vault
   ```

4. For development work, run everything through the scripts from
   `creek-tools/` (never raw tools):

   ```bash
   ./scripts/check-all.sh   # all quality checks
   ./scripts/test.sh        # unit tests
   ```

## Verify

- `creek --help` lists the pipeline commands.
- The vault path contains the scaffold (`00-Creek-Meta/`, `01-Fragments/`,
  …) described in the repo README.
- `./scripts/check-all.sh` exits 0 in `creek-tools/`.

For first-pipeline walkthroughs, the repo's own guides under
`creek-tools/docs/` (getting-started, ingestion, redaction, classification,
linking, generation) are canonical.
