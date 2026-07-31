# Creek-Vault — MCP server (`creek-tools-mcp`)

The Model Context Protocol surface other agents (crawdad, Claude Code,
adepthood integrations) use to touch a vault. Bootstrap lives in
`creek-tools/creek_mcp/server.py` — "stdio transport per the FEAT-010
pre-decided choice", with the whole registration in one `build_server`
function so tests can exercise it (`creek_mcp/server.py:1-12`).

## Tool inventory (complete — 23 tools)

Enumerated from the `@server.tool` registrations; descriptions are each
tool's own docstring.

| Tool | Registered at | Purpose |
| --- | --- | --- |
| `creek.handshake` | `creek_mcp/server.py:318` | Negotiate vault presence, versions, tier model, and capabilities |
| `creek.reflect` | `:332` | Return anchored Higher-Self margin notes on a single journal entry |
| `creek.wheel` | `:349` | Return a per-frequency balance read of the corpus for the Map |
| `creek.journal` | `:360` | Ingest one Adepthood journal entry as a vault fragment (idempotent) |
| `creek.state.read` | `:379` | Return the latest `00-Creek-Meta/State/latest.md` content |
| `creek.state.render` | `:390` | Re-render the audit report (the expensive path) |
| `creek.lint` | `:401` | Run the unified hygiene lint pass |
| `creek.mine` | `:416` | Mine essay seeds from the vault |
| `creek.draft` | `:431` | Generate an essay draft from a mined idea |
| `creek.author` | `:447` | Author a draft for a query via the Writing Desk |
| `creek.save` | `:466` | Save a Discord/Claude answer back into the vault |
| `creek.ingest` | `:495` | Ingest a single source into the vault |
| `creek.redact.scan` | `:510` | Read-only PII / secret scan over a vault-relative directory (FEAT-027) |
| `creek.classify` | `:523` | Re-classify existing fragments via rules or LLM |
| `creek.link` | `:538` | Run a single linker stage |
| `creek.report` | `:553` | Generate a vault-state report (`tags` or `voice`) |
| `creek.skills.refresh` | `:566` | Regenerate the voice-skill tree |
| `creek.compile` | `:577` | Roll fragments up into a compiled-layer page (FEAT-003) |
| `creek.purge.fragment` | `:597` | Delete one fragment by ID (elevated authorization required) |
| `creek.purge.source` | `:612` | Delete every fragment from a source type (elevated auth) |
| `creek.purge.classifications` | `:627` | Reset classification metadata vault-wide (elevated auth) |
| `creek.purge.daterange` | `:640` | Delete fragments created in `[start, end]` (elevated auth) |
| `creek.purge.vault` | `:657` | Destroy all vault content (elevated auth + path confirmation) |

Implementations live one-per-module under `creek_mcp/tools/` (20 modules),
keeping each tool a thin, testable function.

## The security substrate

Five modules gate every call; they are the reason this surface can face a
network at all.

### Tier ceiling (`tier_ceiling.py`)

"Every read tool accepts a required `privacy_tier_ceiling` parameter;
content above the ceiling is omitted or returned as a title-only stub"
(`creek_mcp/tier_ceiling.py:3-5`). The module answers two distinct
questions off one ranking — *admission* (`tier_allowed` /
`write_tier_allowed`) and *routing* (`routing_tier`, which keys LLM calls
so the Intimate-never-cloud gate #928 applies) — and pins the #961 rule
that `unclassified` ranks with `personal`, not `open`
(`creek_mcp/tier_ceiling.py:8-21`).

### Remote boundary (`remote_auth.py`, `auth.py`, `token_policy.py`)

A remote (network-authed) deployment is stricter than local stdio:

- Every request must present a bearer token the `ConsumerTokenVerifier`
  accepts — "no anonymous access" (`creek_mcp/server.py:300-303`).
- Remote callers may request only `OPEN` or `PERSONAL` ceilings:
  "INTIMATE and ALL are excluded so intimate content can never be reached
  over the network — the load-bearing boundary of #759. Local (stdio)
  callers are unaffected" (`_REMOTE_ADMITTED_CEILINGS`,
  `creek_mcp/server.py:76-81`).
- Destructive tools additionally require an elevated token
  (`ELEVATED_TOKEN_ENV`, `creek_mcp/auth.py`), with minimum-length policy
  (`token_policy.require_min_length`); `creek.purge.vault` further demands
  a path confirmation string.

### Path confinement (`path_confinement.py`)

Caller-supplied paths are confined to the vault root: absolute paths must
resolve inside the vault; relative paths join under the vault root, never
the cwd; "resolution collapses `..` segments and follows symlinks, so
neither a `..` traversal nor an in-vault symlink pointing outside can
escape" (`creek_mcp/path_confinement.py:3-17`). Existence is deliberately
not checked so "outside-the-vault" and "not found" produce distinct
refusals (`:19-22`).

### Read-gate posture manifest (`read_gate.py`)

`TOOL_POSTURES` is an audit record with "one entry per registered MCP tool,
stating how that tool relates to the caller's `privacy_tier_ceiling`" —
each tool is classified `GATED`, `NO_UNSUPPLIED_READ`,
`CALLER_NAMED_PATHS`, `METADATA_ONLY`, `AUTH_TOKEN`, or
`UNGATED_KNOWN_GAP` (with a tracking issue), "because a tool nobody triaged
is otherwise indistinguishable … from a tool somebody decided needs no
gate" (`creek_mcp/read_gate.py:1-14`). The canonical gate ordering it
teaches (`:16-25`): audit-log the attempt first (booleans only), resolve
not-found second, run the ceiling gate **above** every derived-signal seam
(care guards included).

### Audit log (`audit.py`)

Every invocation appends to `<vault>/00-Creek-Meta/audit/mcp.jsonl`, with a
per-entry `entry_hash` plus a chain verifier (FEAT-012) "so that tampering
with any single field is detectable" (`creek_mcp/audit.py:1-11`). The log
records `args_summary`, never raw arguments — "long strings become
`{"len": N}` … so an `intimate`-tier draft request never leaks the body to
the log" (`:14-17`) — and, per the read-gate discipline, never the probed
target id or outcome, so the trail "cannot answer 'did consumer X read
fragment F?' in either direction" (`creek_mcp/read_gate.py:20-24`).

Care layer: `acute_distress_guard` (`creek/care/guardrail.py`) is imported
by the server bootstrap (`creek_mcp/server.py:25`) and sits inside
composition-facing tools, below the ceiling gate per the ordering above.

## Integration notes

- **crawdad** consumes this exact surface over stdio; its Haiku router's
  intent schema is generated from the live `tools/list` response so bot and
  server cannot drift (see [crawdad](crawdad.md)).
- **adepthood** is the named consumer of `creek.journal`, `creek.reflect`,
  and `creek.wheel` — journal ingestion, Higher-Self reflection, and the
  Map's frequency balance (`creek_mcp/server.py:360`, `:332`, `:349`).

---

*Grounded in creek-vault@85d230b, 2026-07-31.*
