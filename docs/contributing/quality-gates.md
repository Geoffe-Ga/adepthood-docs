# Quality gates and thresholds

The stay-green enforcement ladder, as of 2026-07-31. Primary source:
adepthood `CLAUDE.md`; satellite thresholds from each repo's `CLAUDE.md`.
Applies to: adepthood in full; satellites run the analogous script-first
gates noted at the end.

## The three gates (adepthood)

1. **Gate 1 — pre-commit** (~10s): format, lint, and hygiene. The config
   (`.pre-commit-config.yaml`) carries 34 hook entries, including ruff +
   ruff-format, mypy, isort, bandit, pip-audit, detect-secrets, shellcheck,
   frontend eslint/prettier/typecheck/tests, xenon complexity, radon
   maintainability, per-side coverage runs, commitlint, and a
   no-commit-to-`main` guard.
2. **Gate 2 — pre-push**: the full test suite plus coverage and complexity
   (`scripts/backend/check-all.sh`, `scripts/frontend/check-all.sh`).
3. **Gate 3 — CI**: everything above plus cross-version compatibility
   (Python 3.11/3.12/3.13), docstring coverage, branch coverage, and the
   security audit.

## Thresholds (adepthood)

| Dimension | Floor |
| --- | --- |
| Line coverage | 90% (backend pytest-cov, frontend jest) |
| Branch coverage | 80% CI gate (target 90%) |
| Docstring coverage | 85% (interrogate, backend) |
| Lint | zero warnings — ruff `select = ["ALL"]`; ESLint with sonarjs/unicorn |
| Types | strict mode, mypy and TypeScript |
| Complexity | xenon A-grade absolute/modules/average; radon MI ≥ B |
| Security | bandit + pip-audit + detect-secrets all pass |

## The non-negotiables

Never, in any repo of the ecosystem:

- Commit with `--no-verify` or push with failing gates.
- Comment out tests to make the suite pass.
- Add `# noqa`, `# type: ignore`, `// @ts-ignore`, or
  `// eslint-disable` for real errors.
- Reduce coverage thresholds or weaken test config.
- Push directly to `main` — feature branches always.

If a gate fails, fix the root cause; a check that cannot be satisfied
honestly is a bug in the code, not in the check.

## Satellite equivalents

- **Creek-Vault** (`creek-tools/`): `./scripts/check-all.sh`; coverage
  ≥ 90% branch, docstrings ≥ 95%, complexity ≤ 10, mypy strict.
- **wavelength-demo**: `./scripts/check-all.sh`; coverage ≥ 90%, mutation
  score ≥ 80%, complexity ≤ 10.
- **WavelengthWatch**: `scripts/check-backend.sh` + `swiftformat --lint`.
- **aptitude-course**: content gates — manifest schema validation and link
  checking (`scripts/build_manifest.py`, `scripts/check_links.py`).
- **adepthood-docs** (this repo): markdownlint, offline link check,
  `mkdocs build --strict`
  ([ADR 0014](../decisions/0014-docs-pr-auto-merge.md)).
