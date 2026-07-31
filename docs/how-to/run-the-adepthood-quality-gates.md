# Run the adepthood quality gates

Run the full local quality ladder before committing or pushing in
`Geoffe-Ga/adepthood`. Verified against the repo state of 2026-07-31.

## Prerequisites

- The repo's `.venv` activated: `source .venv/bin/activate` (always, before
  any Python or pre-commit work)
- Frontend dependencies installed: `cd frontend && npm ci`

## Steps

1. **Gate 1 — pre-commit** (format, lint, hygiene; ~10s):

   ```bash
   pre-commit run --all-files
   # or a single hook:
   pre-commit run <hook-id> --all-files
   ```

2. **Gate 2 — full local suites.** Run the side(s) you touched:

   ```bash
   scripts/backend/check-all.sh
   scripts/frontend/check-all.sh
   ```

   Or the pieces directly:

   ```bash
   cd backend && pytest --cov=. --cov-report=term-missing --cov-fail-under=90
   cd frontend && npm test && npm run lint && npx tsc --noEmit
   ```

3. **Gate 3 — CI** runs on the PR: everything above plus cross-version
   compatibility (Python 3.11/3.12/3.13), docstring coverage, branch
   coverage, and the security audit.

## The rules

- Never commit with `--no-verify`; never push with failing gates.
- If a gate fails, fix the root cause — never comment out tests, add
  `# noqa` / `@ts-ignore` for real errors, or weaken thresholds.
- Thresholds: 90% line coverage, 80% branch (CI gate), 85% docstring
  (interrogate), ruff `select = ["ALL"]` at zero warnings, strict mypy and
  TypeScript, xenon A-grade complexity, radon MI ≥ B.

## Verify

All commands exit 0 and pre-commit reports every hook passed. See
[Quality gates and thresholds](../contributing/quality-gates.md) for the
policy behind these commands.
