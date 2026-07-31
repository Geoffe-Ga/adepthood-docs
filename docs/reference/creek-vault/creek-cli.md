# Creek-Vault — `creek` CLI surface

The complete command surface of the `creek` CLI, enumerated from the Typer
registrations in `creek-tools/creek/cli.py`. The root app is
`typer.Typer(name="creek", help="Creek knowledge organization pipeline")`
with four sub-apps — `clean`, `purge`, `skills`, `compost`
(`creek/cli.py:115-132`). Each line number below is the command's
registration site; the description is the command's own docstring summary.

## Root commands (25)

| Command | Declared at | Purpose (docstring) |
| --- | --- | --- |
| `creek init` | `creek/cli.py:466` | Scaffold a Creek vault at `--vault <path>` |
| `creek sync` | `creek/cli.py:878` | Run a scheduled sync pass, emit schedule units, or show status |
| `creek discord` | `creek/cli.py:1086` | Dispatch a Discord ingest mode (#685/#686/#688) |
| `creek process` | `creek/cli.py:1116` | Run the full pipeline: redact, ingest, classify, link, index |
| `creek ingest` | `creek/cli.py:1197` | Ingest a specific source type into the vault |
| `creek redact` | `creek/cli.py:1443` | Scan for sensitive data, apply redactions, or review the queue |
| `creek classify` | `creek/cli.py:1574` | Run classification on existing vault fragments |
| `creek link` | `creek/cli.py:1829` | Run a single linker stage against the vault |
| `creek index` | `creek/cli.py:1933` | Regenerate the Dataview index notes without running the full pipeline |
| `creek fill` | `creek/cli.py:2389` | Run the deterministic vault-population sequence in dependency order |
| `creek compile` | `creek/cli.py:2455` | Roll a fragment up into a compiled-layer page |
| `creek voice-check` | `creek/cli.py:2972` | Score a markdown FILE against the vault voice fingerprint |
| `creek voice-authenticity` | `creek/cli.py:3058` | Audit a vault's voice corpus (and optionally a draft) for authenticity |
| `creek report` | `creek/cli.py:3185` | Generate reports on vault state |
| `creek state` | `creek/cli.py:3251` | Render `00-Creek-Meta/State/<iso-week>.md` audit report |
| `creek state-budget` | `creek/cli.py:3303` | Verify `00-Creek-Meta/State/latest.md` is within its size budget |
| `creek lint` | `creek/cli.py:3327` | Run unified vault hygiene checks |
| `creek review` | `creek/cli.py:3379` | Walk the review queue and persist accept/override/defer decisions |
| `creek gdrive` | `creek/cli.py:3496` | Download from Google Drive, revoke the token, or run the doctor |
| `creek mine` | `creek/cli.py:3724` | Mine blog and essay ideas from the vault (Section 11.5) |
| `creek draft` | `creek/cli.py:4216` | Generate an essay draft from a mined idea |
| `creek author` | `creek/cli.py:4705` | Author a piece with the Creek Writing Desk |
| `creek save` | `creek/cli.py:4843` | File an answer back into the vault |

## Sub-app commands (11)

| Command | Declared at | Purpose (docstring) |
| --- | --- | --- |
| `creek skills generate` | `creek/cli.py:3584` | Generate the Voice Skill Tree (ontology §11.4) |
| `creek skills sync` | `creek/cli.py:3649` | Re-deploy the canonical schema-skill tree into `<vault>/00-Creek-Meta/Skills/` |
| `creek clean orphans` | `creek/cli.py:4960` | Identify fragments with zero incoming/outgoing links after N days |
| `creek clean stale-reviews` | `creek/cli.py:4985` | Find review queue items older than N days |
| `creek clean broken-links` | `creek/cli.py:5010` | Scan fragments for wiki-links pointing to nonexistent files |
| `creek clean duplicates` | `creek/cli.py:5038` | Execute normalized dedup sweep and output review report |
| `creek clean report` | `creek/cli.py:5064` | Provide summary statistics on vault health |
| `creek purge fragment` | `creek/cli.py:5169` | Delete a fragment and scrub every reference to it |
| `creek purge source` | `creek/cli.py:5216` | Delete every fragment ingested from a given source |
| `creek purge classifications` | `creek/cli.py:5315` | Reset classification fields on every fragment to unclassified |
| `creek purge daterange` | `creek/cli.py:5338` | Delete fragments created within a date range |
| `creek purge vault` | `creek/cli.py:5377` | Destroy every fragment, thread, and eddy (nuclear option) |
| `creek compost calibrate` | `creek/cli.py:5507` | Score the compost detector against a labelled fixture |

Total: **36 commands** (25 root + 11 sub-app; the two `skills` and one
`compost` command are registered with explicit names at
`creek/cli.py:3584`, `:3649`, `:5507`).

## Cross-cutting CLI behaviors

These guardrails apply across commands rather than to any one of them:

- **Vault-path guard.** `creek init` "refuses paths inside a git repository
  by default; pass `--allow-in-repo` to override (with a warning)"
  (`README.md`, Quickstart; implemented by `_guard_vault_path`,
  `creek/cli.py:445`).
- **Ingestion consent gate.** First-run ingestion of each source is gated on
  an explicit operator consent prompt, logged to
  `00-Creek-Meta/Processing-Log/consent-log.json` (`_gate_consent`,
  `creek/cli.py:195-266`; non-interactive runs exit code 2, declines exit
  code 1 — `:221-233`, `:262-266`).
- **Privacy-tier overrides are audited.** `--include-tier` values above the
  default are parsed by `_parse_include_tier` and recorded via
  `_audit_privacy_override_if_needed` (`creek/cli.py:87-113`) into the
  hash-chained audit substrate.
- **Exit-code convention.** Typer exits use code 1 for operator declines /
  environment failures and code 2 for invalid arguments (e.g. unknown
  ingestor type at `creek/cli.py:328`, unparseable `--since` at `:352`).
- **Scheduling.** `creek sync --install-schedule` emits launchd or systemd
  units (`_install_launchd` / `_install_systemd`,
  `creek/cli.py:784-856`), so the two-tier sync (`resolve_tier_a_plan` /
  `resolve_tier_b_plan`, imported at `creek/cli.py:30-35`) can run
  unattended.

The `creek process` pipeline these commands orchestrate is dissected in
[Pipeline and core algorithms](pipeline.md).

---

*Grounded in creek-vault@85d230b, 2026-07-31.*
