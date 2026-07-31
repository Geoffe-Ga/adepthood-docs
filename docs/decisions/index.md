# Decisions

Architectural decision records (ADRs): choices between alternatives that
have lasting consequences, captured at the moment they were made.

## Inclusion criteria

File an ADR here when a merged PR:

- Adopts, replaces, or removes a library, framework, protocol, or platform.
- Commits to a schema strategy, API contract shape, or data-ownership rule
  that future work must honor.
- Establishes or changes a policy that constrains later PRs (versioning
  scheme, compatibility guarantee, security posture).
- Reverses a previous ADR — file a new record that supersedes the old one;
  never rewrite history.

Do **not** file here for: changes with no rejected alternative (routine
implementation), or pure descriptions of current structure — those belong
in [Architecture](../architecture/index.md).

## Format

One file per decision, named `NNNN-slug.md` with a zero-padded sequence
number (`0001-use-mkdocs-material.md`). Each record has exactly these
sections:

```markdown
# NNNN. Title

## Status

Accepted | Superseded by [NNNN](NNNN-slug.md)

## Context

What situation forced a choice, and what options were considered.

## Decision

The choice that was made, stated in the active voice.

## Consequences

What becomes easier, what becomes harder, and what future work must honor.
```
