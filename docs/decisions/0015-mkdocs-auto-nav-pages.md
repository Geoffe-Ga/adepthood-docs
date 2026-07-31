# 0015. MkDocs Material with directory-derived nav, published to GitHub Pages

## Status

Accepted (owner-confirmed 2026-07-31; epic #1 in this repo).

## Context

The corpus is written by an agent that adds and moves pages on every sync
run. Any static `nav:` key in `mkdocs.yml` would make every new page a
two-file change and turn nav drift into a recurring failure mode. The site
also needs to publish with zero human steps.

## Decision

Render the corpus with MkDocs Material plus the
`mkdocs-awesome-pages-plugin`, deriving navigation entirely from the
directory tree — `mkdocs.yml` deliberately has **no `nav:` key**, and both
`mkdocs.yml` and this repo's `CLAUDE.md` instruct that one must never be
added. The sync agent therefore only ever writes Markdown. Builds run with
`--strict` so broken internal references fail the gate rather than
publishing. The site deploys to GitHub Pages (source: GitHub Actions) on
every merge to `main`, at the URL in `mkdocs.yml`'s `site_url`
(Pages deployment itself lands as issue #5).

## Consequences

- Adding a page is one file; the taxonomy directories *are* the information
  architecture, which is why each category's `index.md` doubles as the
  filing rulebook.
- Nav ordering is alphabetical/tree-derived — acceptable for a reference
  corpus; any future curated ordering must use awesome-pages' mechanisms,
  not a `nav:` key.
- `mkdocs build --strict` becomes a meaningful correctness gate for links
  and references ([ADR 0014](0014-docs-pr-auto-merge.md)).
- The published site is the product; the repo is plumbing. Humans read the
  site and file issues, completing the loop that replaces human PR review.
