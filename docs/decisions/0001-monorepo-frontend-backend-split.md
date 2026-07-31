# 0001. Monorepo with a frontend/backend split for adepthood

## Status

Accepted (backfilled 2026-07-31; the structure predates this record).

## Context

Adepthood ships a React Native mobile app and a FastAPI API that evolve in
lockstep — API contract changes, shared roadmap issues, and full-stack
features (auth, habits, practices) routinely touch both sides. Separate
repos would force cross-repo PR choreography for nearly every feature;
a single mixed-language tree with no boundary would blur tooling and
ownership.

## Decision

Keep one repository (`Geoffe-Ga/adepthood`) with two top-level trees:
`frontend/` (React Native + Expo, TypeScript) and `backend/` (FastAPI,
Python). Each side owns its own toolchain and quality scripts
(`scripts/frontend/check-all.sh`, `scripts/backend/check-all.sh`), while the
repo shares one roadmap (`prompts/github-issues/`), one pre-commit config,
and one agent fleet.

## Consequences

- Full-stack changes land as one atomic PR; the phased roadmap can specify
  "Full-stack" scope per issue.
- Tooling must be namespaced: pre-commit runs both Python and Node hooks,
  and CI gates are split per side.
- Cross-cutting conventions (conventional commits, TDD, coverage floors)
  are stated once and enforced repo-wide.
- Anything that is genuinely a separate product (course content, the watch
  app, the vault) lives in its own satellite repo instead — the monorepo
  boundary is the app, not the ecosystem.
