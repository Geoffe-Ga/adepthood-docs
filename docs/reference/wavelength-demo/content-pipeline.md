# wavelength-demo — content pipeline

How editable Markdown in `content/` becomes typed data at build time. The
pipeline is deliberately dependency-free: a ~150-line Markdown reader
(`src/content/markdown.ts`) plus three loaders that fail loudly on malformed
copy, so a bad edit breaks the build instead of silently breaking the page.

## The tiny Markdown reader

`src/content/markdown.ts` understands exactly four shapes — frontmatter, lead
paragraph, one pipe table, and `##` sections
(`src/content/markdown.ts:1-6`):

| Function | Input → output | Failure mode |
| --- | --- | --- |
| `parseFrontmatter(raw)` | Document → `{ data, body }`; `key: value` lines between `---` fences, one layer of quotes stripped (`src/content/markdown.ts:33-59`) | Throws if the leading or closing `---` fence is missing (`:35-37`, `:49-51`) |
| `leadText(body)` | Body → paragraphs before the first `\|` row, collapsed to one line (`src/content/markdown.ts:62-70`) | — (empty string if no lead) |
| `parseTable(body)` | Body → `string[][]` of trimmed cells, separator rows (`:?-{2,}:?`) skipped, header preserved (`src/content/markdown.ts:90-99`) | — |
| `indexByFirstCell(rows, keys)` | Rows → `Record<key, trailingCells>` (`src/content/markdown.ts:110-122`) | Throws `table is missing row "<key>"` for any absent key (`:118-120`) |
| `parseSections(raw)` | Document → map of lowercased `##` heading → verbatim section text; content before the first `##` is ignored (`src/content/markdown.ts:133-152`) | — |

## Loader 1: wavelengths → `MODES`

`src/data/modes.ts` globs every wavelength file eagerly as a raw string —
sorted path order **is** page order, which is why the files are numbered
(`src/data/modes.ts:200-204`, `content/README.md:18-20`):

```ts
const wavelengthFiles = import.meta.glob("../../content/wavelengths/*.md", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;
```

Each document is converted by `toMode` (`src/data/modes.ts:220-241`), which
validates the quadrant against `QUADRANTS` and requires all six phase rows:

```ts
export function toMode(raw: string): Mode {
  const { data, body } = parseFrontmatter(raw);
  const quadrant = field(data, "quadrant") as QuadrantId;
  if (!(quadrant in QUADRANTS)) {
    throw new Error(`wavelength has unknown quadrant "${quadrant}"`);
  }
  const rows = indexByFirstCell(parseTable(body), PHASES);
  ...
  if (data.source) mode.source = data.source;
  if (data.mobile === "true") mode.mobile = true;
  return mode;
}
```

### Worked example

Input, `content/wavelengths/05-addiction.md` (verbatim, abridged table):

```markdown
---
mode: Addiction
title: The Addiction Roller Coaster
quadrant: IT
mobile: true
---

Whether your addiction is to alcohol, cocaine, heroin, social media,
shopping or chocolate, the same cyclical pattern describes it.

| Phase | On this wavelength |
| --- | --- |
| Rising | Using |
| Peaking | Bliss |
| Withdrawal | Come down |
| Diminishing | Hangover |
| Bottoming Out | Depression |
| Restoration | Craving |
```

Pipeline steps:

1. `parseFrontmatter` → `data = { mode: "Addiction", title: "The Addiction
   Roller Coaster", quadrant: "IT", mobile: "true" }`, body = everything
   after the second `---`.
2. `"IT" in QUADRANTS` passes (`src/data/modes.ts:44-49` defines `IT` as
   "Individual · Exterior", accent `#3f8e88`).
3. `parseTable` yields 7 rows (header + 6 phases); the `| --- | --- |`
   separator is dropped by `isSeparator` (`src/content/markdown.ts:82-84`).
4. `indexByFirstCell(rows, PHASES)` → `{ Rising: ["Using"], Peaking:
   ["Bliss"], … }`; the header row `["Phase", "On this wavelength"]` is
   ignored because `"Phase"` is not in `PHASES`.
5. `leadText` collapses the lead paragraph into the `gloss`.

Result: `{ mode: "Addiction", title: "The Addiction Roller Coaster", gloss:
"Whether your addiction is …", quadrant: "IT", mobile: true, phases: {
Rising: "Using", …, Restoration: "Craving" } }` — one of the 21 entries in
`MODES` (`src/data/modes.ts:243-245`).

## Loader 2: reference layers → `REFERENCE_LAYERS`

`src/data/reference.ts` runs the same glob-and-parse pattern over
`content/reference/*.md` (`src/data/reference.ts:55-59`, `:104-106`), with two
deliberate differences:

- **Colors live in code, not copy.** `LAYER_COLORS` maps layer ids 1-9 to a
  vivid `colorHex` and a readable `textHex` "so a copy edit can't break the
  page's theming" (`src/data/reference.ts:39-50`, comment at `:10-13`). An
  unknown `id` throws (`src/data/reference.ts:82`).
- **Two-column dosage rows.** Each phase row carries `[medicinal, toxic]`
  cells, packed into `DosagePair` objects (`src/data/reference.ts:83-89`).
  Toxic copy is always rendered in `TOXIC_HEX = "#cf3a33"`
  (`src/data/reference.ts:37`).

Frontmatter contract per layer file (all required, enforced by `field`,
`src/data/reference.ts:62-68`): `id`, `color` (spiral color name, e.g.
"Beige"), `mode` (e.g. "INHABIT"), `orientation` (e.g. "Do"),
`orientationGloss`. Example: `content/reference/01-beige.md` opens with
`id: 1`, `color: Beige`, `mode: INHABIT`, `orientation: Do`,
`orientationGloss: agency, action, building`.

## Loader 3: page copy → hero constants

`src/content/pages.ts` statically imports the four page documents with Vite's
`?raw` suffix (`src/content/pages.ts:5-8`) and splits each into `##` sections
via `parseSections`. Three parsers pull required, named sections
(`src/content/pages.ts:58-102`); a missing section throws
`page is missing the "<key>" section` (`:45-49`):

| Constant | Source file | Required sections |
| --- | --- | --- |
| `HOME_HERO` | `content/pages/home.md` | `eyebrow`, `heading`, `intro`, `scroll cue` |
| `REFERENCE_HERO` | `content/pages/reference.md` | `eyebrow`, `heading`, `intro`, `scroll cue` |
| `ORIGIN` | `content/pages/origin.md` | `eyebrow`, `heading`, `lead`, `caption` |
| `CLOSING` | `content/pages/closing.md` | `eyebrow`, `heading`, `lede`, `footnote` |

`CLOSING.footnote` may contain a `{count}` placeholder, replaced at render
time with the live mode count (`src/content/pages.ts:41`,
`src/pages/HomePage.tsx:196-198`).

## Inline formatting

Hero copy supports exactly three inline forms — `**bold**`, `*italic*`, and
`[text]{.class}` colored spans — tokenized by one regex
(`src/content/inline.ts:14`):

```ts
const PATTERN = /\*\*([^*]+)\*\*|\*([^*]+)\*|\[([^\]]+)\]\{\.([a-z][\w-]*)\}/g;
```

Alternation order is load-bearing: `**bold**` is tried before `*italic*` "so
the longer fence wins" (`src/content/inline.ts:13`). `tokenizeInline`
(`src/content/inline.ts:22-44`) walks the matches and emits a flat token list;
e.g. `"See **the wave** as [Bliss]{.crest}"` becomes

```text
[ { kind: "text",   text: "See " },
  { kind: "strong", text: "the wave" },
  { kind: "text",   text: " as " },
  { kind: "span",   text: "Bliss", className: "crest" } ]
```

React mapping lives separately in `RichText`
(`src/components/RichText.tsx:4-24`): `strong` → `<strong>`, `em` → `<em>`,
`span` → `<span class="…">`, `text` → fragment.

## Enumeration summary

- 21 wavelength documents → `MODES` (11 with `mobile: true`); 3 carry a
  `source` attribution (Bruce Tuckman, Cory Doctorow, Mihaly
  Csikszentmihalyi).
- 9 reference documents → `REFERENCE_LAYERS` (ids 1-9, Beige → Ultraviolet).
- 4 page documents → 4 hero-copy constants.
- 6 phases (`src/data/modes.ts:14-21`), 4 AQAL quadrants
  (`src/data/modes.ts:37-62`).

---

*Grounded in wavelength-demo@78c703e, 2026-07-31.*
