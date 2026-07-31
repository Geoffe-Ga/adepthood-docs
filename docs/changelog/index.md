# Changelog

Dated digests of what the sync pipeline folded into this corpus: one entry
per sync run that found merged PRs, newest first.

## Inclusion criteria

File an entry here on **every** sync run that processes at least one merged
PR:

- Create (or append to) `YYYY-MM-DD.md` for the run date, in UTC.
- List each merged PR processed: repo, PR number, one-line summary, and
  which docs pages were created or updated as a result.
- If a PR was examined and deliberately produced no docs change, say so in
  one line — silence is indistinguishable from a missed sync.

Do **not** file here: narrative documentation of the changes themselves —
that belongs in the category pages the entry links to. Entries are an audit
trail, not prose.

## Conventions

- One file per day with activity, named `YYYY-MM-DD.md`.
- Entries within a file are ordered newest-run-first, each under an
  `## HH:MM UTC` heading.

## Per-repo rolling digests

Alongside the dated run digests, one file per source repo carries that
repo's rolling change digest, seeded at the 2026-07-31 baseline (issue #3)
and appended to by the sync pipeline (newest entries first):

- [adepthood](adepthood.md)
- [Creek-Vault](creek-vault.md)
- [WavelengthWatch](wavelengthwatch.md)
- [aptitude-course](aptitude-course.md)
- [wavelength-demo](wavelength-demo.md)
