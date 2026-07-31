# Adepthood Docs

The living documentation corpus for the five-repo Adepthood ecosystem:

- [`Geoffe-Ga/adepthood`](https://github.com/Geoffe-Ga/adepthood)
- [`Geoffe-Ga/Creek-Vault`](https://github.com/Geoffe-Ga/Creek-Vault)
- [`Geoffe-Ga/WavelengthWatch`](https://github.com/Geoffe-Ga/WavelengthWatch)
- [`Geoffe-Ga/aptitude-course`](https://github.com/Geoffe-Ga/aptitude-course)
- [`Geoffe-Ga/wavelength-demo`](https://github.com/Geoffe-Ga/wavelength-demo)

Documentation here is **pulled from the source repos, not pushed to it**.
Humans and agents working in the product repos never write docs here
directly; the corpus stays current on its own.

## How it stays current: the pull-model sync

1. A scheduled workflow polls the source repos for pull requests merged
   since the last watermark (`state/sync-watermarks.json`).
2. A Sonnet-powered agent reads each merged PR and folds its consequences
   into the corpus, using the inclusion criteria in each category's
   `index.md` as filing rules.
3. The agent opens a PR against this repo. When the quality gates pass
   (markdownlint, offline internal-link check, `mkdocs build --strict`),
   the PR auto-merges.

**No human in the loop.** The gates are the reviewer. Anything the gates
cannot catch is a gap to fix in the gates, not a reason to add manual
review. Humans read the published site and file issues when the corpus is
wrong; they do not approve sync PRs.

## Reading the docs

The corpus is a [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
site with navigation derived from the directory tree (awesome-pages — no
`nav:` key, ever). Published site:
<https://docs.aptitude.guru/> — deployed automatically on
every merge to `main`.

Build locally:

```bash
pip install -r requirements.txt
mkdocs serve
```

## Repository layout

- `docs/` — the corpus. Seven categories, each with filing rules in its
  `index.md`: architecture, decisions, design, how-to, contributing,
  products, changelog.
- `state/sync-watermarks.json` — per-repo `last_synced_merged_at`
  watermarks the sync workflow reads and advances.
- `.github/workflows/docs-ci.yml` — the PR quality gates.
- `CLAUDE.md` — steering for agent sessions in this repo.

## Roadmap

This repo is built out under epic
[#1](https://github.com/Geoffe-Ga/adepthood-docs/issues/1), which defines
the sync architecture and the issue graph that implements it.
