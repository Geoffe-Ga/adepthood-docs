# Docs-Sync Agent Instructions

You are the autonomous sync agent for the Adepthood living-docs corpus
(ADR 0013, pull model). A workflow step has already collected every PR
merged in the source repos since the last sync into `sync-input.json` at
the repository root. Your job is to fold those PRs into the corpus by
editing files — nothing else. The workflow around you handles all git
mechanics: do **not** create branches, commit, push, or open PRs.

## Input

Read `sync-input.json`:

- `prs` — merged PRs in `merged_at`-ascending order. Each has `repo`,
  `number`, `title`, `body`, `merged_at`, `html_url`, `files` (filename +
  additions/deletions), and a unified `patch`. When `truncated` is true the
  patch was dropped for size — reason in `truncation` — so work from the
  title, body, and file list instead.
- `new_watermarks` — the per-repo `merged_at` high-water marks this run
  must commit.

Process PRs oldest-first so later changes land on top of earlier ones.

## Filing rules

Each category's `docs/<category>/index.md` carries the authoritative
inclusion criteria. Read the relevant index before filing, then for each
PR decide which categories it touches:

- `docs/architecture/` — update the affected repo/concern page **in
  place** when a PR changes components, boundaries, data flow, schemas, or
  deployment topology.
- `docs/how-to/` — update task guides in place when a PR adds or changes a
  procedure; fix steps the PR made stale in the same run.
- `docs/design/` — update in place when a PR changes tokens, visual
  language, or interaction patterns systemically.
- `docs/products/` — update the repo's overview when a PR changes a
  user-facing feature surface or product scope.
- `docs/contributing/` — update when a PR changes quality gates,
  conventions, or agent workflow policy.
- `docs/decisions/` — write a **new** ADR `docs/decisions/NNNN-slug.md`
  ONLY for a genuine architectural decision: a choice between alternatives
  with lasting consequences. Routine implementation gets no ADR. Use the
  next zero-padded sequence number and exactly the sections `## Status`,
  `## Context`, `## Decision`, `## Consequences`. Never rewrite an
  accepted ADR — supersede it with a new record.

Many PRs (small fixes, dependency bumps, internal refactors) rightly touch
no architecture/design/how-to/products page at all. That is fine — but the
changelog is never optional.

## Changelog — every PR, no exceptions

EVERY PR in `sync-input.json` gets a dated entry appended to its repo's
rolling digest in `docs/changelog/`. The files (they already exist — use
these exact names):

| `repo` in sync-input.json  | changelog file       |
| -------------------------- | -------------------- |
| Geoffe-Ga/adepthood        | `adepthood.md`       |
| Geoffe-Ga/Creek-Vault      | `creek-vault.md`     |
| Geoffe-Ga/WavelengthWatch  | `wavelengthwatch.md` |
| Geoffe-Ga/aptitude-course  | `aptitude-course.md` |
| Geoffe-Ga/wavelength-demo  | `wavelength-demo.md` |

Entries are newest-first: insert a `## YYYY-MM-DD — <short summary>`
section (UTC date of this sync run) directly under the file's intro
paragraph, above older entries. In it, list each folded PR on one line:
number (linked to `html_url`), one-line summary, and which docs pages were
created or updated — or an explicit "no docs change" line when you
deliberately filed nothing. Silence is indistinguishable from a missed
sync.

Also follow `docs/changelog/index.md`: each run that processed merged PRs
files (or appends to) the dated run digest `docs/changelog/YYYY-MM-DD.md`,
newest-run-first, each run under an `## HH:MM UTC` heading.

## Watermarks — atomic with the doc edits

Copy `new_watermarks` from `sync-input.json` into
`state/sync-watermarks.json`, preserving that file's shape:

```json
{
  "owner/repo": { "last_synced_merged_at": "<timestamp>" }
}
```

This edit ships in the same PR as the doc changes — that atomicity is what
makes the pipeline idempotent and resumable. Never advance a watermark for
a repo whose PRs you did not process.

## Hard boundaries

- Edit ONLY files under `docs/` plus `state/sync-watermarks.json`.
- Never touch `mkdocs.yml`, `README.md`, `.github/`, `scripts/`, or
  anything else outside `docs/` + `state/`.
- Within `docs/`, never create, modify, or delete `.pages` files,
  anything under `docs/stylesheets/`, or the site homepage
  `docs/index.md` — those are static theme/navigation config, not corpus
  content.
- Never add a `nav:` key to `mkdocs.yml` — navigation derives from the
  directory tree (awesome-pages).
- Every page lives in exactly one category.

## Quality gates

Your edits must pass Docs CI unmodified — never weaken a gate:

- `markdownlint-cli2` per `.markdownlint-cli2.jsonc` (MD013/MD033 off,
  MD024 siblings-only; everything else default — fix the prose, never add
  per-file suppressions).
- The offline internal link check: every relative link you write must
  resolve to a real file in the repo.
- `mkdocs build --strict`: new pages must be linkable from their category
  (the awesome-pages nav picks them up automatically), and no warnings.
