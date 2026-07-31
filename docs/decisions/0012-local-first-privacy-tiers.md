# 0012. Local-first processing with explicit privacy tiers

## Status

Accepted (backfilled 2026-07-31; grounded in adepthood `NORTH-STAR.md`
section 10 and Creek-Vault's README/pipeline design).

## Context

Both Adepthood (an intimate journal) and Creek-Vault (a pipeline over a
person's entire digital exhaust) handle content people would never hand to
a cloud model. Privacy could have been a settings toggle; the ecosystem's
positioning ("privacy becomes the pitch rather than the plumbing" —
`NORTH-STAR.md`, section 9) demanded it be architectural.

## Decision

Make privacy tiering and local routing first-class:

- **Creek-Vault** classifies every fragment into `Open` / `Personal` /
  `Intimate` tiers; classification runs on local Ollama by default and
  embeddings on local `sentence-transformers`, with the Anthropic API path
  opt-in. Ingestion gates each source on explicit, logged consent;
  downstream stages filter by tier independently; redaction runs before
  anything else touches the data; and `creek purge` implements
  right-to-be-forgotten with hash-chained audit logs.
- **Adepthood** commits (as a design guardrail) that intimate-tier content
  is classified and routed locally, encrypted at rest, and never sent to a
  cloud LLM — surfaced to the user as a feature, not buried.
- **WavelengthWatch** applies the same instinct at smaller scale: journal
  entries store locally first, and cloud sync is opt-in.

## Consequences

- The local path is the default path, so features must be designed to work
  without cloud inference; cloud assistance is an upgrade, not a
  requirement.
- Consent and deletion are auditable events (consent logs, hash-chained
  purge logs), not implicit states.
- The privacy stance is a competitive position against cloud-AI journaling
  apps and constrains all future AI features — any new pipeline stage must
  declare how it honors tiers.
