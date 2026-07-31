# aptitude-course

As of the 2026-07-31 baseline seed (issue #3).

The complete APTITUDE curriculum — a ten-stage, 36-week program — as a
versioned Markdown content repository with a machine-readable manifest that
the Adepthood app consumes. Source: aptitude-course `README.md`,
`CLAUDE.md`, `CONSUMPTION.md`, `CONTENT_FORMAT.md`.

## Stack

- Markdown content (CommonMark dialect, no raw HTML — `CONTENT_FORMAT.md`).
- Python build scripts (`scripts/build_manifest.py`, `scripts/check_links.py`,
  `scripts/normalize_markdown.py`, `scripts/add_frontmatter.py`).
- JSON Schema validation (`schema/manifest.schema.json`).

## Module map

- `markdown/01-beige/` … `markdown/10-clearlight/` — one directory per
  stage, each holding the chapter sections (e.g. BEIGE has 19 sections).
  Stage chapters follow a fixed structure: mood, journaling prompts, the
  practice and its alternatives, default habit, gift/shadow, and a full
  six-phase Wavelength breakdown (Rising, Peaking, Withdrawal, Diminishing,
  Bottoming Out, Restoration — each with Rx and OD expressions).
- `manifest.json` — the generated index the app reads; never edited by
  hand. Carries `schema_version` (1.1.0 as of this baseline), and for each
  chapter: `id`, `stage`, `chapter`, `order`, `slug`, `title`,
  `content_type`, `release_day` (drip-feed pacing), `media`, and `path`.
- `schema/manifest.schema.json` — the manifest's JSON Schema.
- `google_docs/`, `prompts/`, `markdown/backup/`, `markdown/meta/` —
  internal working material, explicitly outside the consumption contract.

## Data flow (the consumption contract)

Defined in `CONSUMPTION.md` and recorded as
[ADR 0011](../decisions/0011-manifest-consumption-contract.md):

1. The Adepthood app vendors a **pinned commit** of this repo (the SHA lives
   in the app's `CONTENT_VERSION`).
2. Within that commit the app may rely on exactly three surfaces: the
   manifest, the Markdown bodies the manifest references, and the assets
   those bodies reference. Everything else may change without notice.
3. Reads go through the manifest — the app iterates `manifest.json`, never
   globs `markdown/**`. Identity is `id` (and `slug` for site resources);
   paths are stable but not identity.
4. `release_day` drives the app's drip-feed: content unlocks on a per-stage
   day offset, pacing the 36-week arc (eight 3-week stages, then Unity and
   Emptiness at 6 weeks each — adepthood `NORTH-STAR.md`, section 5).

## Key entry points

- Rebuild the manifest: `python scripts/build_manifest.py` (validated
  against the schema).
- Check internal links: `python scripts/check_links.py`.
- Authoring workflow: `CONTRIBUTING.md`; canonical dialect:
  `CONTENT_FORMAT.md`.
- Knowledge graph: committed in-tree at `graphify-out/graph.json`, federated
  nightly into adepthood's `pan-graph.json`.

## Relation to Adepthood

This repo is the app's course content supply chain. The ten stages (BEIGE
through CLEAR LIGHT) are the same ten Aspects the app's Map, habits, and
practice ramp are organized around; the journaling prompts here feed the
app's prompted-journaling ring.
