# Walkthrough: a source-repo PR → this docs site

A pull request merged in any of the five source repos, traced through the
docs-sync poller's watermark window, the `sync-input.json` hand-off, the
sync agent's constrained edits, the deterministic PR that auto-merges on
green gates, and the Pages deploy that publishes the updated site. All
paths are repo-relative to `Geoffe-Ga/adepthood-docs`.

The pipeline is pull-model (ADR 0013): nothing in the source repos
notifies this repo. Every six hours this repo asks GitHub "what merged
since my last committed watermark?" and folds the answer in.

## Hop by hop

1. **A PR merges upstream.** Say `Geoffe-Ga/adepthood#900` merges at
   `2026-07-31T09:12:00Z`. The committed watermark file
   `state/sync-watermarks.json` still records the previous high-water
   mark per repo, e.g.
   `"Geoffe-Ga/adepthood": {"last_synced_merged_at": "2026-07-31T03:56:45Z"}`
   (`state/sync-watermarks.json:1-17`).

2. **The window opens.** The Docs Sync workflow fires on a
   `17 */6 * * *` cron (and on manual dispatch), serialized under a
   `docs-sync` concurrency group
   (`.github/workflows/docs-sync.yml:14-21`).

3. **Stuck-PR guard.** If a previous run's `docs-sync/*` PR is still
   open, its watermark advance has not merged, so a second run "would
   fold the same PRs again" — the job comments on the stuck PR and
   bails out cleanly (`.github/workflows/docs-sync.yml:38-56`).

4. **The poller.** `scripts/sync/collect_merged_prs.py` reads the
   watermarks and, per repo, pages through closed PRs sorted
   newest-updated-first, stopping "as soon as a page entry's
   `updated_at` falls behind the watermark — everything after it is
   older still" (`scripts/sync/collect_merged_prs.py:112-138`). The
   keep rule is strictly-greater on `merged_at`:

    ```python
    merged_at = pull.get("merged_at")
    if merged_at and _parse_timestamp(merged_at) > watermark:
        kept.append(pull)
    ```

    "`merged_at` equal to the watermark is excluded (strictly-greater
    keeps), which is what makes reruns idempotent"
    (`scripts/sync/collect_merged_prs.py:117-119`).

5. **Record building.** For each kept PR the poller captures title,
   body, merge metadata, the changed-file list (capped at
   `MAX_FILES_PER_PR = 200`), and one unified patch assembled from the
   per-file `patch` fields; binary or API-oversized files degrade to a
   header line (`scripts/sync/collect_merged_prs.py:44`, `141-201`).

6. **Patch caps.** Records are sorted `merged_at`-ascending "so the
   total budget favors older PRs first", then a 3 000-line per-PR cap
   and a 15 000-line total cap are enforced; a capped record keeps its
   file list, gets an empty patch, `"truncated": true`, a `truncation`
   note, and a stderr warning — "never silently"
   (`scripts/sync/collect_merged_prs.py:45-46`, `209-241`).

7. **The hand-off.** The output is a single `sync-input.json`:
   `generated_at`, `new_watermarks` (per-repo max `merged_at` seen, or
   the old mark when nothing merged), and the `prs` array
   (`scripts/sync/collect_merged_prs.py:243-275`). The workflow counts
   the PRs; a quiet window sets `has_prs=false` and **the agent step
   never runs — zero LLM cost**
   (`.github/workflows/docs-sync.yml:64-82`).

8. **The sync agent.** A Claude Code action step (model pinned in
   `claude_args`) is told to read `scripts/sync/PROMPT.md` and follow
   it exactly, editing "only files under docs/ plus
   state/sync-watermarks.json" and running no git commands
   (`.github/workflows/docs-sync.yml:86-98`). PROMPT.md binds the
   edits: file per-category updates in place per each category index's
   inclusion criteria; a new ADR only for "a genuine architectural
   decision"; a changelog entry for **every** PR, no exceptions —
   "silence is indistinguishable from a missed sync" — and copy
   `new_watermarks` into `state/sync-watermarks.json` in the same PR,
   because "that atomicity is what makes the pipeline idempotent and
   resumable" (`scripts/sync/PROMPT.md`, sections "Filing rules",
   "Changelog — every PR, no exceptions", "Watermarks — atomic with
   the doc edits", "Hard boundaries").

9. **Deterministic git mechanics.** The workflow — not the agent —
   creates the branch `docs-sync/<UTC timestamp>`, stages only
   `docs/` + `state/`, commits
   `docs(sync): fold N merged PRs from M repos`, and pushes
   (`.github/workflows/docs-sync.yml:100-121`).

10. **The docs PR.** A PR body is generated from `sync-input.json` —
    one line per folded PR (with truncation flags) plus the watermark
    advances — and the PR is opened against `main`
    (`.github/workflows/docs-sync.yml:123-177`), then squash
    auto-merge is enabled (`.github/workflows/docs-sync.yml:182-190`).

11. **The gates are the reviewer.** Docs CI runs on every PR:
    `npx --yes markdownlint-cli2 "**/*.md"`, an offline internal-only
    lychee link check (external links are deliberately unchecked so "a
    flaky third-party site must never block the autonomous sync
    pipeline"), and `mkdocs build --strict`
    (`.github/workflows/docs-ci.yml:3-7`, `31`, `43`, `67`). All three
    green → the PR auto-merges with no human in the loop (ADR 0014).

12. **Pages deploy.** The merge to `main` triggers the Pages workflow:
    a build job re-runs `mkdocs build --strict` and uploads `site/`,
    and only then a separate deploy job publishes to GitHub Pages
    (`.github/workflows/pages-deploy.yml:14-17`, `53-60`, `60-80`).
    The new watermark is now committed on `main`, so the next window
    starts exactly where this one ended.

## Failure modes

- **GitHub rate limit (403/429) while polling** — the poller skips
  that repo with a stderr warning and *leaves its watermark
  untouched*, "so a later run retries the same window"
  (`scripts/sync/collect_merged_prs.py:20-22`, `48-52`, `256-259`).
- **Quiet window** — `"prs": []`, exit 0, agent step skipped, no
  branch, no PR (`.github/workflows/docs-sync.yml:75-80`).
- **Stuck docs-sync PR** — the run comments on it and skips the
  window rather than double-folding
  (`.github/workflows/docs-sync.yml:46-56`).
- **Agent produced no changes** — the push step warns
  ("Agent produced no changes under docs/ or state/; nothing to
  push.") and exits without a PR
  (`.github/workflows/docs-sync.yml:109-112`).
- **Oversized patches** — dropped with the file list kept and the
  truncation reason recorded in both the record and the PR body
  (`scripts/sync/collect_merged_prs.py:223-240`,
  `.github/workflows/docs-sync.yml:147`).
- **Auto-merge unavailable** — if the repo's allow-auto-merge setting
  is off, the step degrades to a warning; "the PR is open either way
  and a human can merge it"
  (`.github/workflows/docs-sync.yml:179-190`).
- **Gate failure** — a red markdownlint / lychee / strict-build check
  simply leaves the PR unmerged; because the watermark advance is
  inside that same PR, no merged-PR window is ever lost — the guard
  in hop 3 then holds subsequent runs until a human resolves it.
- **Pages not enabled** — configure-pages / deploy-pages fail loudly
  by design; "do not swallow the error"
  (`.github/workflows/pages-deploy.yml:7-11`).

*Grounded in Geoffe-Ga/adepthood-docs@8b73a15, 2026-07-31.*
