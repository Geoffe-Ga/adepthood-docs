# 0013. Pull-model docs sync from the five source repos

## Status

Accepted (owner-confirmed 2026-07-31; epic #1 in this repo).

## Context

The ecosystem wanted living documentation that stays current as code merges
across five repos. A push model — every source repo notifying or writing to
the docs repo on merge — would require workflow changes and cross-repo
credentials in all five repos, and would couple their CI to this repo's
availability.

## Decision

Centralize the sync as a **pull**: one `docs-sync` workflow in this repo
(cron every 6 hours plus `workflow_dispatch`) polls each source repo for
PRs merged since a committed per-repo watermark
(`state/sync-watermarks.json`). Each run feeds the merged PRs (title, body,
diff) to a Claude-powered sync agent that edits the corpus according to the
filing rules in each category's `index.md` and opens one docs PR per run.
All five source repos are public, so reads need no new secrets; writes stay
inside this repo, so the built-in `GITHUB_TOKEN` suffices — no cross-repo
PAT anywhere.

## Consequences

- Source repos need zero changes and hold zero docs-repo credentials; the
  entire pipeline's blast radius is this repo.
- Freshness is bounded by the poll interval (~6h from merge to corpus),
  which the epic accepts explicitly.
- Watermarks make the sync idempotent and resumable: a failed run re-reads
  from the last committed `last_synced_merged_at`; advancing the watermark
  is part of the synced change.
- The agent needs filing rules that are machine-followable — which is why
  each category `index.md` carries explicit inclusion criteria, and why
  this baseline seed (issue #3) matters: the incremental sync (issue #4)
  forever after only edits what this corpus established.
