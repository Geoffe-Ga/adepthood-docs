# Creek-Vault — crawdad (Discord bot)

CrawDad is "the Discord-side interface to a Creek vault. It consumes the
creek-tools MCP surface … and answers Discord messages in your voice using
the FEAT-015 agent loop (Haiku router → MCP dispatcher → Sonnet composer
with voice-skill activation)" (`crawdad/README.md:3-7`). It is a separate
Python package under `crawdad/` (23 modules).

## Module map (complete)

| Module | Concern |
| --- | --- |
| `crawdad/bot.py` | `discord.py` client; forwards messages to a pure-logic handler; user + channel allowlist (non-allowlisted callers get **no response**); graceful "creek-tools is unreachable" reply (`crawdad/README.md:19-24`) |
| `crawdad/loop.py` | The bounded agent loop (below) |
| `crawdad/router.py` | Haiku intent extraction — "intent extraction only, never prose. Haiku emits JSON; Sonnet … does composition" (`crawdad/router.py:10-12`) |
| `crawdad/intents.py` | The intent schema: every intent `type` is an MCP tool name, 1-to-1, generated from the live `tools/list` response so "the router prompt and the dispatcher [stay] honest as the tool surface grows" (`crawdad/intents.py:3-8`) |
| `crawdad/dispatcher.py` | Validates intents against the session's tool snapshot and invokes them; forwards `privacy_tier_ceiling` verbatim "because the MCP server enforces the policy at the protocol boundary" (`crawdad/dispatcher.py:9-12`) |
| `crawdad/composer.py` | Sonnet voice-faithful composition |
| `crawdad/mcp_client.py` | Async MCP stdio client (fresh session per tool-call round, FEAT-013) |
| `crawdad/skill_loader.py` | Voice-skill activation per session from `<vault>/creek-skills/` |
| `crawdad/slash_commands.py` | The `/crawdad` command tree (below) |
| `crawdad/workflows.py` | The YAML workflow DSL (below) |
| `crawdad/consent.py`, `crawdad/capture.py`, `crawdad/attachments.py`, `crawdad/history.py`, `crawdad/state.py`, `crawdad/config.py`, `crawdad/cli.py` | Capture consent, message capture, attachment handling, truncated conversation history (last 20 entries × 2000 chars — `crawdad/router.py:16-18`), session state, YAML config, `crawdad run` entry point |
| `crawdad/llm/` | Provider abstraction: `anthropic.py`, `openai.py`, `gemini.py` behind `base.py` — selected via `CRAWDAD_PROVIDER` (`crawdad/README.md:36-39`); no model-ID literals outside config, enforced by `tests/test_no_model_literals.py` |

## The agent loop (core algorithm)

Per message: the Haiku router emits strict JSON intents; the dispatcher
runs them against MCP; the loop repeats until the router sets
`compose: true`, then Sonnet composes the reply. Load-bearing rules from
the `crawdad/loop.py` module docstring (`:25-55`):

- **`compose` is read *after* dispatch**: "a bundled round must run the
  tools it asked for and then compose within that same round (#915). Only
  an *empty* intent list short-circuits straight to the composer."
- **Bounded**: cap defaults to `MAX_LOOP_ROUNDS` (5), operator-configurable
  via `crawdad.yaml::max_loop_rounds`, bounded `[1, 50]` (FEAT-036). "The
  cap is reached only when the router keeps returning intents with
  `compose=false`"; on cap exhaustion the reply is refused and history
  cleared (FEAT-015 §27).
- **Paradox routing (§31)**: "if any tool result mentions a paradox AND the
  advertised tool set includes `creek.save`, the loop injects a
  `creek.save` call (target=paradox) so the surfaced contradiction is
  routed to `10-Liminal/Paradoxes/` before the composer sees it."
- **Wavelength-aware routing**: the router prompt names the current phase
  "so Haiku biases toward phase-appropriate intents (no `mine` / `draft`
  during Bottoming Out; prefer `surface_paradox` / `compost`)"
  (`crawdad/router.py:13-15`).

Two client-side intent types are handled *before* the MCP known-tools
check, namespaced `crawdad.` to stay collision-free with `creek.*` tools:
`crawdad.activate_register` (dynamic voice-register switching, FEAT-029)
and `crawdad.run_workflow` (ADAPT-003)
(`crawdad/intents.py:24-39`).

## Slash-command surface (complete — 8 commands)

From `_COMMAND_DESCRIPTIONS` (`crawdad/slash_commands.py:87-96`; an
import-time invariant asserts the command list and descriptions never drift,
`:98-106`). Registration sites at `:487-644`:

| Command | Purpose |
| --- | --- |
| `/crawdad reflect` | Open reflective conversation mode (FEAT-015 loop) |
| `/crawdad checkin` | Wavelength check-in — read the current phase + dosage state |
| `/crawdad surface` | Surface paradoxes, liminal content, or emerging themes |
| `/crawdad draft` | Draft an essay on a topic (routes through `creek.author`, essay medium) |
| `/crawdad ask` | Ask a question; get a cited, voiced answer (routes through `creek.author`) |
| `/crawdad save` | File the supplied content back to the vault via `creek.save` |
| `/crawdad register` | Switch the active voice register (FEAT-029) |
| `/crawdad workflow` | List or run named workflows (ADAPT-003) |

(The README's "six `/crawdad` slash commands (FEAT-016)" list predates
`ask` and `register`; the code registers eight.)

## The workflow DSL

Composite commands "compile down to a deterministic walk over authored YAML
files" — each declares steps that "map one-to-one to MCP tool calls, plus
first-class constraint metadata (`phase_aware` / `privacy_tier_floor`) the
walker enforces before any tool fires"; "Plain YAML. No custom grammar, no
Jinja2 dependency" (`crawdad/workflows.py:1-15`). Example shape from the
docstring: a workflow names `allowed_phases`, a `privacy_tier_floor`,
`inputs`, and steps whose args interpolate `{{state.phase}}` /
`{{input.topic}}` (`crawdad/workflows.py:16-31`).

Three built-in workflows ship in `crawdad/builtin_workflows/`:
`compost-surfacing`, `substack-draft-phase-transitions`, and
`wavelength-checkin` (`*.workflow.yaml`).

## Configuration

Required env: `DISCORD_BOT_TOKEN` plus the provider key
(`ANTHROPIC_API_KEY` by default; `OPENAI_API_KEY` / `GOOGLE_API_KEY` when
`CRAWDAD_PROVIDER` selects those backends). `crawdad.yaml` supplies
`vault_path`, `mcp_server_command` (e.g. `creek-tools-mcp`),
`allowed_user_ids`, and optional `max_loop_rounds`
(`crawdad/README.md:26-50`). The entry point is
`crawdad run --config ./crawdad.yaml` (`crawdad/cli.py`).

---

*Grounded in creek-vault@85d230b, 2026-07-31.*
