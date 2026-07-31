# aptitude-course — repo map

Deep reference for the
[aptitude-course](https://github.com/Geoffe-Ga/aptitude-course) repository,
generated from source. For the product-level story see
[the product page](../../products/aptitude-course.md).

This is a **content repository, not an application**: the 36-week APTITUDE
course corpus as Markdown, plus a small Python toolchain that makes it
machine-readable. Its one consumer-facing artifact is `manifest.json`, the
schema-versioned index the adepthood app vendors at a pinned SHA
(`CONSUMPTION.md:17-25`).

## Top-level map

| Path | Purpose | Contracted? |
| --- | --- | --- |
| `markdown/<NN-stage>/` | The course corpus: 10 stage folders (`01-beige` … `10-clearlight`) of numbered chapter files with YAML frontmatter | Yes — via manifest `path` refs |
| `markdown/resources/` | 5 non-stage-gated site resources (`about`, `aptitude-stages`, `archetypal-wavelength`, `liminal-creep`, `wavelength-explainer`) | Yes — `site_resources[]` |
| `manifest.json` | Generated machine-readable index (`schema_version: "1.1.0"`, 209 chapters, 5 site resources, 10 stage intros) | Yes — the contract itself |
| `schema/manifest.schema.json` | JSON Schema (draft 2020-12) for the manifest (`schema/manifest.schema.json:1-8`) | Yes |
| `scripts/` | The 4-script toolchain (see [Manifest pipeline](manifest-pipeline.md)) | No — internal |
| `google_docs/` | Original Google-Docs exports (`.zip` + `.html`) and the curriculum CSV database | No — explicitly internal (`CONSUMPTION.md:31-39`) |
| `markdown/backup/`, `markdown/meta/`, `markdown/images/` | Pre-normalization backups, generated corpus statistics, extracted images | No — internal |
| `convert_docs.sh` | Legacy one-shot importer: unzips `google_docs/*.zip` and pandoc-converts each HTML export to GFM in `markdown/` (`convert_docs.sh:4-16`) | No — internal |
| `CONTENT_FORMAT.md` | Canonical spec: Markdown dialect + frontmatter schema (`CONTENT_FORMAT.md:1-14`) | Governs the contract |
| `CONSUMPTION.md` | Canonical spec: published surface, semver rules, release tagging, update handshake | Governs the contract |
| `.github/workflows/content-ci.yml` | Content CI: manifest drift check, markdownlint, internal-link check | Gatekeeper |

## The corpus, enumerated

209 chapters across 10 stages (counts derived from `manifest.json`; each
stage folder also holds a `00-table-of-contents.md` and `README.md`, which
the generator deliberately skips — `scripts/build_manifest.py:91-93`):

| `stage` | Folder | Archetype (per `CONTENT_FORMAT.md` §4) | Chapters |
| --- | --- | --- | --- |
| 1 | `01-beige` | Beige — Survival | 17 |
| 2 | `02-purple` | Purple — Mythic | 15 |
| 3 | `03-red` | Red — Power | 14 |
| 4 | `04-blue` | Blue — Conformity | 15 |
| 5 | `05-orange` | Orange — Rationality | 29 |
| 6 | `06-green` | Green — Plurality | 24 |
| 7 | `07-yellow` | Yellow — Integrative | 26 |
| 8 | `08-teal` | Teal — True Self | 24 |
| 9 | `09-ultraviolet` | Ultraviolet — Unity | 21 |
| 10 | `10-clearlight` | Clear Light — Emptiness | 24 |

All 209 chapter entries have `content_type: chapter`; `release_day` ranges
0-28; every manifest `path` resolves on disk (verified against the checkout).
Each of the 10 stages contributes exactly one derived `stage_intros[]` entry
(its chapter 1), and `site_resources[]` carries the 5 resource essays.

## The Markdown dialect (what a chapter may contain)

Bodies are CommonMark with a deliberately small feature set — headings,
emphasis, lists, links, images, blockquotes, code, GFM pipe tables, thematic
breaks (`CONTENT_FORMAT.md` §2.1). **Raw HTML is banned outright** because
"the app renders Markdown natively … and does not execute HTML"
(`CONTENT_FORMAT.md` §2, §2.2), and CI enforces it: the markdownlint config
runs with `"default": false` and switches on only `no-inline-html` plus four
structural rules (`no-reversed-links`, `no-empty-links`,
`no-missing-space-atx`, `no-multiple-space-atx`)
(`.markdownlint-cli2.jsonc:8-17`) — stylistic rules are deliberately off
because "the corpus is literary prose" (`.markdownlint-cli2.jsonc:3-6`).

Frontmatter contract (per chapter, `CONTENT_FORMAT.md` §3.1): required
`id`, `stage` (1-10), `chapter`, `order`, `slug` (must match the filename
slug), `title`, `content_type` (`chapter | essay | prompt | video`),
`release_day` (≥ 0); optional `summary` and `media[]`. Identity rules: `id`
unique repo-wide and never reused; `(stage, chapter)` unique; `slug` derived
mechanically from the filename (`CONTENT_FORMAT.md` §3.2). Example, verbatim
from `markdown/01-beige/01-what-is-beige.md:1-11`:

```yaml
---
id: beige-1
stage: 1
chapter: 1
order: 1
slug: what-is-beige
title: "What is Beige?"
content_type: chapter
release_day: 0
media: []
---
```

## Curriculum database (internal source material)

`google_docs/database_of_course_curriculum/` holds six CSVs distilled from
the original course spreadsheet — internal to this repo but the shared
ancestor of the ecosystem's ontology:

| CSV | Rows (incl. header) | Shape |
| --- | --- | --- |
| `APTITUDE Complete Map.csv` | 11 | One row per stage: Week, Mode, Spiral Dynamics Color, Growing Up Stage, Free Will relationship, books, practice, habit, and the four AQAL-quadrant exercises (I/IT/ITS/WE) |
| `The Archetypal Wavelength - Modes of the Wavelength.csv` | 18 | `dosage,stage,mode,orientation,rising,peaking,withdrawal,diminishing,bottoming out,restoration` — Medicine/Toxicity rows per stage |
| `The Archetypal Wavelength - Self-Care Strategies.csv` | 52 | Per-phase self-care strategies |
| `APTITUDE - Quotes.csv` | 58 | Course quotes |
| `APTITUDE - Alternative Practices.csv` | 16 | Alternative practices per stage |
| `APTITUDE - Book Recommendations.csv` | 11 | Reading list |

The same mode/orientation/six-phase columns appear as WavelengthWatch's seed
CSVs (`backend/data/a-w-curriculum.csv` there) and as the six phase names in
wavelength-demo (`src/data/modes.ts:14-21` there) — this spreadsheet is the
common origin.

## Relationship to adepthood

The adepthood app is the manifest's consumer: it "vendors a pinned commit of
this repository (the SHA lives in the app's `CONTENT_VERSION`)" and may rely
on exactly three surfaces — `manifest.json`, the Markdown bodies it
references, and their assets (`CONSUMPTION.md:17-30`). Reads go through the
manifest, never by globbing; durable identity is frontmatter `id`
(`CONSUMPTION.md:41-48`). Details in
[Consumption contract](consumption-contract.md).

---

*Grounded in aptitude-course@064c6ca, 2026-07-31.*
