"""Collect merged PRs from the Adepthood source repos since per-repo watermarks.

Stdlib-only poller for the docs-sync pipeline (ADR 0013, pull model). Reads
``state/sync-watermarks.json``, queries the GitHub REST API for each source
repo's closed PRs (sorted by ``updated`` descending, paginating until the
window falls behind the watermark), and keeps PRs whose ``merged_at`` is
strictly greater than the repo's watermark.

For each kept PR it captures title, body, merge metadata, the changed-file
list (capped), and a size-capped unified patch assembled from the per-file
``patch`` fields. Output is a single ``sync-input.json`` document consumed by
the sync agent (see ``scripts/sync/PROMPT.md``)::

    {
      "generated_at": "...",
      "new_watermarks": {"owner/repo": "<max merged_at seen or existing>"},
      "prs": [...]
    }

Exit code is 0 even when the window is empty (``"prs": []``). Rate-limit
responses (HTTP 403/429) skip the affected repo with a stderr warning and
leave its watermark untouched, so a later run retries the same window.

Usage::

    GITHUB_TOKEN=... python3 scripts/sync/collect_merged_prs.py \
        --watermarks state/sync-watermarks.json --out sync-input.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

API_ROOT = "https://api.github.com"
PER_PAGE = 100
MAX_FILES_PER_PR = 200
DEFAULT_MAX_PATCH_LINES = 3000
DEFAULT_MAX_TOTAL_LINES = 15000
REQUEST_TIMEOUT_SECONDS = 30
RATE_LIMIT_STATUSES = frozenset({403, 429})


class RateLimitError(RuntimeError):
    """Raised when the GitHub API answers with a rate-limit status (403/429)."""


def _log(message: str) -> None:
    """Write a diagnostic line to stderr (stdout stays clean for tooling)."""
    print(message, file=sys.stderr)


def _http_get_json(url: str) -> Any:
    """GET ``url`` and return the parsed JSON body.

    Sends a Bearer token when the ``GITHUB_TOKEN`` environment variable is
    non-empty; unauthenticated requests are allowed (all source repos are
    public). Raises :class:`RateLimitError` on 403/429 so callers can skip
    the repo gracefully; every other HTTP error propagates.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "adepthood-docs-sync",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code in RATE_LIMIT_STATUSES:
            msg = f"HTTP {exc.code} from {url} (rate limited or forbidden)"
            raise RateLimitError(msg) from exc
        raise


def _parse_timestamp(value: str) -> datetime:
    """Parse a GitHub ISO-8601 timestamp (``2026-07-31T03:56:45Z``) to UTC."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _list_url(repo: str, page: int) -> str:
    """Build the closed-PRs listing URL for ``repo`` at ``page``."""
    query = urllib.parse.urlencode(
        {
            "state": "closed",
            "sort": "updated",
            "direction": "desc",
            "per_page": PER_PAGE,
            "page": page,
        }
    )
    return f"{API_ROOT}/repos/{repo}/pulls?{query}"


def _files_url(repo: str, number: int, page: int) -> str:
    """Build the changed-files listing URL for PR ``number`` at ``page``."""
    query = urllib.parse.urlencode({"per_page": PER_PAGE, "page": page})
    return f"{API_ROOT}/repos/{repo}/pulls/{number}/files?{query}"


def _fetch_merged_prs(repo: str, watermark: datetime) -> list[dict[str, Any]]:
    """Return PRs in ``repo`` merged strictly after ``watermark``.

    Pages through closed PRs newest-updated-first and stops as soon as a
    page entry's ``updated_at`` falls behind the watermark — everything
    after it is older still. ``merged_at`` equal to the watermark is
    excluded (strictly-greater keeps), which is what makes reruns
    idempotent.
    """
    kept: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = _http_get_json(_list_url(repo, page))
        if not batch:
            break
        exhausted = False
        for pull in batch:
            if _parse_timestamp(pull["updated_at"]) < watermark:
                exhausted = True
                break
            merged_at = pull.get("merged_at")
            if merged_at and _parse_timestamp(merged_at) > watermark:
                kept.append(pull)
        if exhausted or len(batch) < PER_PAGE:
            break
        page += 1
    return kept


def _fetch_pr_files(repo: str, number: int) -> tuple[list[dict[str, Any]], bool]:
    """Return (changed files, files_truncated) for a PR, capped at 200 files."""
    files: list[dict[str, Any]] = []
    truncated = False
    page = 1
    while len(files) < MAX_FILES_PER_PR:
        batch = _http_get_json(_files_url(repo, number, page))
        if not batch:
            break
        files.extend(batch)
        if len(batch) < PER_PAGE:
            break
        page += 1
    if len(files) > MAX_FILES_PER_PR:
        files = files[:MAX_FILES_PER_PR]
        truncated = True
    elif len(files) == MAX_FILES_PER_PR:
        # A full final page means more files may exist beyond the cap.
        truncated = True
    return files, truncated


def _build_patch(files: list[dict[str, Any]]) -> str:
    """Assemble one unified patch text from per-file ``patch`` fields.

    Files without a ``patch`` field (binary, or too large for the API) are
    represented by their header line only.
    """
    parts: list[str] = []
    for entry in files:
        header = (
            f"--- {entry['filename']} "
            f"(+{entry.get('additions', 0)}/-{entry.get('deletions', 0)})"
        )
        patch = entry.get("patch")
        parts.append(f"{header}\n{patch}" if patch else header)
    return "\n".join(parts)


def _collect_record(repo: str, pull: dict[str, Any]) -> dict[str, Any]:
    """Build the sync-input record for one merged PR (patch caps applied later)."""
    files, files_truncated = _fetch_pr_files(repo, pull["number"])
    return {
        "repo": repo,
        "number": pull["number"],
        "title": pull.get("title") or "",
        "body": pull.get("body") or "",
        "merged_at": pull["merged_at"],
        "html_url": pull.get("html_url") or "",
        "files": [
            {
                "filename": entry["filename"],
                "additions": entry.get("additions", 0),
                "deletions": entry.get("deletions", 0),
            }
            for entry in files
        ],
        "files_truncated": files_truncated,
        "patch": _build_patch(files),
        "truncated": False,
    }


def _count_lines(text: str) -> int:
    """Return the number of lines in ``text`` (0 for the empty string)."""
    return text.count("\n") + 1 if text else 0


def _apply_patch_caps(
    records: list[dict[str, Any]], max_patch_lines: int, max_total_lines: int
) -> None:
    """Enforce the per-PR and total patch-size caps in place.

    Records must already be in merged_at-ascending order so the total budget
    favors older PRs first. A capped record keeps its file list, gets an
    empty ``patch``, ``"truncated": true``, and a ``truncation`` note; every
    truncation is also logged to stderr — never silently.
    """
    total_lines = 0
    for record in records:
        lines = _count_lines(record["patch"])
        label = f"{record['repo']}#{record['number']}"
        if lines > max_patch_lines:
            note = (
                f"patch of {lines} lines exceeded the per-PR cap of "
                f"{max_patch_lines}; patch dropped, file list kept"
            )
        elif total_lines + lines > max_total_lines:
            note = (
                f"patch of {lines} lines would exceed the total cap of "
                f"{max_total_lines} (already at {total_lines}); patch "
                f"dropped, file list kept"
            )
        else:
            total_lines += lines
            continue
        record["patch"] = ""
        record["truncated"] = True
        record["truncation"] = note
        _log(f"warning: truncated {label}: {note}")


def collect(
    watermarks: dict[str, dict[str, str]],
    max_patch_lines: int,
    max_total_lines: int,
) -> dict[str, Any]:
    """Poll every watermarked repo and build the sync-input payload."""
    new_watermarks: dict[str, str] = {}
    records: list[dict[str, Any]] = []
    for repo, entry in watermarks.items():
        watermark_raw = entry["last_synced_merged_at"]
        try:
            pulls = _fetch_merged_prs(repo, _parse_timestamp(watermark_raw))
            repo_records = [_collect_record(repo, pull) for pull in pulls]
        except RateLimitError as exc:
            _log(f"warning: skipping {repo}, watermark unchanged: {exc}")
            new_watermarks[repo] = watermark_raw
            continue
        merged_seen = [record["merged_at"] for record in repo_records]
        new_watermarks[repo] = (
            max(merged_seen, key=_parse_timestamp) if merged_seen else watermark_raw
        )
        records.extend(repo_records)
        _log(f"{repo}: {len(repo_records)} merged PR(s) since {watermark_raw}")
    records.sort(key=lambda record: _parse_timestamp(record["merged_at"]))
    _apply_patch_caps(records, max_patch_lines, max_total_lines)
    generated_at = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    return {
        "generated_at": generated_at,
        "new_watermarks": new_watermarks,
        "prs": records,
    }


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Parse the command-line interface."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--watermarks",
        required=True,
        help="Path to state/sync-watermarks.json",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path to write sync-input.json",
    )
    parser.add_argument(
        "--max-patch-lines",
        type=int,
        default=DEFAULT_MAX_PATCH_LINES,
        help=f"Per-PR patch line cap (default {DEFAULT_MAX_PATCH_LINES})",
    )
    parser.add_argument(
        "--max-total-lines",
        type=int,
        default=DEFAULT_MAX_TOTAL_LINES,
        help=f"Total patch line cap across all PRs (default {DEFAULT_MAX_TOTAL_LINES})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: read watermarks, poll GitHub, write sync-input.json."""
    args = _parse_args(argv)
    with open(args.watermarks, encoding="utf-8") as handle:
        watermarks = json.load(handle)
    payload = collect(watermarks, args.max_patch_lines, args.max_total_lines)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    _log(f"wrote {args.out}: {len(payload['prs'])} PR(s) across {len(watermarks)} repo(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
