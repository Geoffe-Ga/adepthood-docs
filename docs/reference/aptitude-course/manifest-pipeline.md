# aptitude-course — manifest pipeline

The Python toolchain under `scripts/` that turned a Google-Docs export into a
machine-readable corpus, and keeps it that way. Four scripts, run in
historical order: `normalize_markdown.py` (clean the bodies),
`add_frontmatter.py` (make them machine-readable), `build_manifest.py`
(generate the contract), `check_links.py` (keep references honest). The
first two were one-time migrations that remain runnable and idempotent; the
last two run in CI on every push (`.github/workflows/content-ci.yml`).

## Stage 0 (legacy): `convert_docs.sh`

The original import is 19 lines of shell (`convert_docs.sh:1-19`): unzip
every `google_docs/*.zip`, then for each HTML export run

```bash
pandoc "$htmlfile" -f html -t gfm -o "../markdown/${filename}.md" --extract-media=../markdown/images
```

This produced GFM full of Google-Docs artifacts — which is exactly what the
next stage exists to remove.

## Stage 1: `normalize_markdown.py` — word-preserving HTML removal

The corpus "still carr[ied] inline HTML: `<span class="...">` wrappers
(often splitting text mid-word), empty spans inside headings,
`<a>`/`<img>` tags, and `&amp;`/`&nbsp;` entities"
(`scripts/normalize_markdown.py:5-9`). The core safety property is stated
and enforced in code — "reformatting, not rewriting":

> every visible prose word must survive untouched. The script therefore reads
> each file …, computes the normalized version, and *asserts that the
> sequence of visible prose words is identical before and after*.
> (`scripts/normalize_markdown.py:11-17`)

The normalization passes (`scripts/normalize_markdown.py:48-80`):

1. `html.unescape` decodes entities; the resulting non-breaking spaces are
   normalized to plain spaces (`:50-53`).
2. `<span …>` wrappers are deleted with the **empty string**, deliberately
   rejoining words Google Docs split mid-token across styling spans —
   `"T</span><span>he" -> "The"` (`:55-59`).
3. `<a href="URL">TEXT</a>` → `[TEXT](URL)`, multiline-safe (`:61-67`).
4. `<img … src="URL" …>` → `![](URL)` with a tempered regex
   `(?:(?!\n\n)[^>])` so an *unclosed* Google-Docs image tag ends at its
   paragraph break "instead of swallowing the rest of the document"
   (`:69-80`).

Only files that actually contain markup are candidates
(`MARKUP_RE`, `:38-42`), avoiding cosmetic churn; `--check` verifies without
writing, `--stage 02-purple` limits scope (`:18-22`).

## Stage 2: `add_frontmatter.py` — mechanical metadata

Everything except `release_day` is derived from the
`markdown/<NN-stage>/<NN-slug>.md` convention "so the metadata cannot
disagree with the file's location" (`scripts/add_frontmatter.py:8-22`):

| Field | Derivation |
| --- | --- |
| `stage` | Folder's numeric prefix (1..10) |
| `chapter` | 1-based position within the stage, sorted by filename |
| `order` | Same as `chapter` |
| `slug` | Filename minus `NN-` prefix and `.md` |
| `id` | `"<stage-slug>-<chapter>"`, e.g. `beige-1` |
| `title` | The file's first Markdown heading |
| `content_type` | `chapter` |
| `release_day` | `chapter - 1` (the "daily" drip default) — the **single non-mechanical knob**, hand-tunable later |

The script "**only prepends** the block: the body bytes are asserted
unchanged" and is idempotent — files already starting with frontmatter are
skipped (`scripts/add_frontmatter.py:24-26`).

## Stage 3: `build_manifest.py` — the contract generator

"Pure and deterministic (no network, stable key order): the same content
always yields a byte-identical manifest" (`scripts/build_manifest.py:9-11`).
`SCHEMA_VERSION = "1.1.0"` is pinned in code with the coordination note
(`scripts/build_manifest.py:45`).

### Collection

- `collect_chapters` walks stage dirs matching `^\d{2}-[a-z0-9]+$`, takes
  files matching `^(\d{2})-(.+)\.md$`, and **skips `00-` files** (TOCs);
  entries sort by `(stage, order)` (`scripts/build_manifest.py:86-101`).
- `collect_stage_intros` derives one intro per stage from its chapter 1 —
  "a second, ungated, non-drip-fed manifest entry pointing at that same
  file — never a separately authored one" — with `id`/`slug` derived from
  the folder name: `01-beige` → `beige-intro` / `beige-introduction`
  (`scripts/build_manifest.py:104-133`).
- `collect_site_resources` globs `markdown/resources/*.md`, sorted by slug
  (`scripts/build_manifest.py:136-148`).

### Validation (complete rule table)

Every rule that can fail the build, from `validate`, `validate_stage_intros`,
and `validate_media` (`scripts/build_manifest.py:154-241`):

| Rule | Error | Source |
| --- | --- | --- |
| Required chapter fields present (`id`, `stage`, `chapter`, `order`, `slug`, `title`, `content_type`, `release_day`) | `missing required field` | `:157-165` |
| `slug` equals filename slug | `slug '…' != filename slug '…'` | `:167-169` |
| `slug` matches `^[a-z0-9]+(?:-[a-z0-9]+)*$` | `slug '…' is not URL-safe` | `:170-171` |
| `content_type` in `{chapter, essay, prompt, video}` | `bad content_type` | `:172-173` |
| `release_day` int ≥ 0 | `release_day must be an int >= 0` | `:174-175` |
| `stage` in 1..10 | `stage … out of range 1..10` | `:176-177` |
| `id` unique repo-wide (chapters **and** intros share the namespace) | `duplicate id` | `:179-182`, `:207-210` |
| `(stage, chapter)` unique | `duplicate (stage,chapter)=…` | `:184-188` |
| One intro per stage | `duplicate stage_intro for stage …` | `:212-216` |
| `media[]` items: known fields only; `type` in `{video, image, audio}`; exactly one of `url`/`path`; `url` must be `https://` | various | `:219-241` |
| Manifest validates against `schema/manifest.schema.json` when `jsonschema` is installed | schema error | `:244-252` |

### Drift check

`--check` fails CI if the committed `manifest.json` differs byte-for-byte
from a fresh build (`scripts/build_manifest.py:288-300`), which is the
"Frontmatter + manifest" required status check
(`.github/workflows/content-ci.yml:28-45`).

### Worked example

For `markdown/01-beige/01-what-is-beige.md` (frontmatter shown in
[the repo map](index.md)):

1. `CHAPTER_FILE_RE` matches `01-what-is-beige.md` → filename slug
   `what-is-beige`; frontmatter `slug` agrees, so validation passes.
2. The chapter entry is emitted with keys in fixed `CHAPTER_KEYS` order plus
   the generated `path: "markdown/01-beige/01-what-is-beige.md"`
   (`scripts/build_manifest.py:56-57`, `:95-98`) — matching
   `manifest.json:5-16` exactly.
3. Because `chapter == 1`, it also yields the stage-1 intro:
   `{ "stage": 1, "id": "beige-intro", "slug": "beige-introduction",
   "title": "What is Beige?", "path": … }` — matching the first
   `stage_intros[]` entry in the committed manifest.

## Stage 4: `check_links.py` — internal references

Walks every corpus Markdown file (excluding `backup/` and `.obsidian/`),
extracts inline links and images with a single regex, and verifies every
repo-internal target exists on disk; external schemes
(`https?:`, `mailto:`, `tel:`, `data:`) and pure-fragment anchors are
skipped because "checking them needs the network, which CI deliberately
avoids" (`scripts/check_links.py:2-17`). Frontmatter `media[]`
`path`/`poster` entries are checked too (`:12-14`). Code fences are tracked
line-by-line so example links inside fences are ignored
(`scripts/check_links.py:55-60`).

## CI gates (complete)

`.github/workflows/content-ci.yml` runs three jobs on push to `main` and
every PR, all offline, no secrets (`:13-17`):

| Job (required check) | Tool | Enforces |
| --- | --- | --- |
| `Frontmatter + manifest` | `python scripts/build_manifest.py --check` | Frontmatter validity, identity rules, schema validation, manifest drift |
| `Markdown lint` | `markdownlint-cli2-action@v19` with `.markdownlint-cli2.jsonc` | No raw HTML (§2.2) + structural rules |
| `Internal links` | `python3 scripts/check_links.py` | Every internal link/image/media path resolves |

---

*Grounded in aptitude-course@064c6ca, 2026-07-31.*
