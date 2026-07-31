# Build the aptitude-course manifest

Regenerate and validate `manifest.json` after editing course content in
`Geoffe-Ga/aptitude-course`. Verified against the repo state of 2026-07-31.

## Prerequisites

- Python 3.x
- `pip install -r scripts/requirements.txt` from the repo root

## Steps

1. Edit content under `markdown/<NN>-<stage>/` following the dialect and
   frontmatter rules in `CONTENT_FORMAT.md` (CommonMark, no raw HTML).

2. Rebuild the manifest — never edit `manifest.json` by hand:

   ```bash
   python scripts/build_manifest.py
   ```

   The build validates against `schema/manifest.schema.json`.

3. Check internal links:

   ```bash
   python scripts/check_links.py
   ```

## Verify

- `manifest.json` diff shows your chapters with correct `id`, `order`,
  `release_day`, and `path` fields, and the `schema_version` you expect.
- Both scripts exit 0.
- Remember the consumption contract
  ([ADR 0011](../decisions/0011-manifest-consumption-contract.md)): the app
  reads only the manifest, the bodies it references, and their assets — if
  your change isn't reachable from the manifest, the app will never see it.
