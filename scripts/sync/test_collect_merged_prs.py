"""Offline tests for collect_merged_prs.py — HTTP layer fully stubbed.

Runs with ``python3 -m pytest scripts/sync/ -q`` using only stdlib + pytest.
"""

from __future__ import annotations

import json
import urllib.parse
from pathlib import Path
from typing import Any

import pytest

import collect_merged_prs as cmp_mod

WATERMARK = "2026-07-31T03:56:45Z"
REPO = "Geoffe-Ga/adepthood"


def _pull(
    number: int,
    merged_at: str | None,
    updated_at: str | None = None,
    title: str = "a change",
) -> dict[str, Any]:
    """Build a minimal closed-PR listing entry."""
    return {
        "number": number,
        "title": title,
        "body": f"body of #{number}",
        "merged_at": merged_at,
        "updated_at": updated_at or merged_at or "2026-07-31T12:00:00Z",
        "html_url": f"https://github.com/{REPO}/pull/{number}",
    }


def _file(filename: str, patch: str | None = "@@ -1 +1 @@\n-a\n+b") -> dict[str, Any]:
    """Build a minimal changed-file entry."""
    entry: dict[str, Any] = {"filename": filename, "additions": 1, "deletions": 1}
    if patch is not None:
        entry["patch"] = patch
    return entry


class FakeAPI:
    """URL-dispatching stub for _http_get_json.

    ``pull_pages`` maps repo -> list of listing pages (each a list of PR
    dicts); ``files`` maps (repo, number) -> list of file dicts (served as a
    single page unless longer than PER_PAGE).
    """

    def __init__(
        self,
        pull_pages: dict[str, list[list[dict[str, Any]]]],
        files: dict[tuple[str, int], list[dict[str, Any]]] | None = None,
    ) -> None:
        """Store canned responses and start the request log."""
        self.pull_pages = pull_pages
        self.files = files or {}
        self.requested: list[str] = []

    def __call__(self, url: str) -> Any:
        """Dispatch a GET to the canned pages, mimicking GitHub pagination."""
        self.requested.append(url)
        parsed = urllib.parse.urlparse(url)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        page = int(params.get("page", 1))
        parts = parsed.path.strip("/").split("/")
        repo = "/".join(parts[1:3])
        if parts[-1] == "files":
            number = int(parts[-2])
            entries = self.files.get((repo, number), [])
        else:
            pages = self.pull_pages.get(repo, [])
            return pages[page - 1] if page <= len(pages) else []
        per_page = cmp_mod.PER_PAGE
        return entries[(page - 1) * per_page : page * per_page]


def _run(
    tmp_path: Path,
    api: FakeAPI,
    monkeypatch: pytest.MonkeyPatch,
    watermarks: dict[str, dict[str, str]] | None = None,
    extra_args: list[str] | None = None,
) -> dict[str, Any]:
    """Run main() against the stubbed API and return the parsed output."""
    monkeypatch.setattr(cmp_mod, "_http_get_json", api)
    watermarks_path = tmp_path / "watermarks.json"
    out_path = tmp_path / "sync-input.json"
    watermarks_path.write_text(
        json.dumps(watermarks or {REPO: {"last_synced_merged_at": WATERMARK}})
    )
    argv = ["--watermarks", str(watermarks_path), "--out", str(out_path)]
    argv += extra_args or []
    assert cmp_mod.main(argv) == 0
    return json.loads(out_path.read_text())


def test_watermark_filtering_strictly_greater(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Older and watermark-equal merges are excluded; newer are kept."""
    api = FakeAPI(
        {
            REPO: [
                [
                    _pull(3, "2026-07-31T05:00:00Z"),
                    _pull(2, WATERMARK),  # equal to watermark: excluded
                    _pull(1, "2026-07-30T00:00:00Z", updated_at="2026-07-31T06:00:00Z"),
                ]
            ]
        },
        {(REPO, 3): [_file("a.py")]},
    )
    payload = _run(tmp_path, api, monkeypatch)
    assert [pr["number"] for pr in payload["prs"]] == [3]
    assert payload["prs"][0]["files"] == [{"filename": "a.py", "additions": 1, "deletions": 1}]
    assert payload["prs"][0]["truncated"] is False


def test_unmerged_closed_prs_are_ignored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Closed-but-not-merged PRs (merged_at null) never appear."""
    api = FakeAPI({REPO: [[_pull(9, None, updated_at="2026-07-31T09:00:00Z")]]})
    payload = _run(tmp_path, api, monkeypatch)
    assert payload["prs"] == []
    assert payload["new_watermarks"] == {REPO: WATERMARK}


def test_pagination_stops_once_updated_at_precedes_watermark(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An updated_at older than the watermark ends pagination early."""
    page_one = [_pull(50 - i, "2026-07-31T05:00:00Z") for i in range(99)]
    page_one.append(_pull(400, "2026-07-01T00:00:00Z", updated_at="2026-07-02T00:00:00Z"))
    api = FakeAPI(
        {REPO: [page_one, [_pull(999, "2026-07-31T06:00:00Z")]]},
        {(REPO, number): [_file("x.md")] for number in range(-48, 51)},
    )
    payload = _run(tmp_path, api, monkeypatch)
    numbers = {pr["number"] for pr in payload["prs"]}
    assert 400 not in numbers
    assert 999 not in numbers  # page 2 never fetched
    listing_urls = [url for url in api.requested if "/files" not in url]
    assert len(listing_urls) == 1


def test_per_pr_patch_cap_drops_patch_keeps_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A patch over --max-patch-lines is dropped, flagged, and logged."""
    big_patch = "\n".join(f"+line {i}" for i in range(50))
    api = FakeAPI(
        {REPO: [[_pull(7, "2026-07-31T05:00:00Z")]]},
        {(REPO, 7): [_file("big.py", patch=big_patch)]},
    )
    payload = _run(tmp_path, api, monkeypatch, extra_args=["--max-patch-lines", "10"])
    record = payload["prs"][0]
    assert record["truncated"] is True
    assert record["patch"] == ""
    assert record["files"] == [{"filename": "big.py", "additions": 1, "deletions": 1}]
    assert "per-PR cap" in record["truncation"]
    assert "truncated" in capsys.readouterr().err


def test_total_patch_cap_drops_later_prs_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The total budget favors older merges; later PRs lose their patch."""
    patch = "\n".join(f"+line {i}" for i in range(20))
    api = FakeAPI(
        {
            REPO: [
                [
                    _pull(12, "2026-07-31T06:00:00Z"),
                    _pull(11, "2026-07-31T05:00:00Z"),
                ]
            ]
        },
        {
            (REPO, 11): [_file("first.py", patch=patch)],
            (REPO, 12): [_file("second.py", patch=patch)],
        },
    )
    payload = _run(tmp_path, api, monkeypatch, extra_args=["--max-total-lines", "30"])
    by_number = {pr["number"]: pr for pr in payload["prs"]}
    assert by_number[11]["truncated"] is False
    assert by_number[11]["patch"] != ""
    assert by_number[12]["truncated"] is True
    assert by_number[12]["patch"] == ""
    assert "total cap" in by_number[12]["truncation"]
    assert "truncated" in capsys.readouterr().err


def test_prs_sorted_by_merged_at_ascending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Output PRs are ordered oldest-merge-first across repos."""
    other = "Geoffe-Ga/Creek-Vault"
    api = FakeAPI(
        {
            REPO: [[_pull(2, "2026-07-31T08:00:00Z")]],
            other: [[_pull(5, "2026-07-31T04:30:00Z")]],
        },
        {(REPO, 2): [_file("a.md")], (other, 5): [_file("b.md")]},
    )
    watermarks = {
        REPO: {"last_synced_merged_at": WATERMARK},
        other: {"last_synced_merged_at": WATERMARK},
    }
    payload = _run(tmp_path, api, monkeypatch, watermarks=watermarks)
    assert [pr["merged_at"] for pr in payload["prs"]] == [
        "2026-07-31T04:30:00Z",
        "2026-07-31T08:00:00Z",
    ]


def test_empty_window_writes_empty_prs_and_keeps_watermarks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No new merges: exit 0, prs is [], watermarks pass through unchanged."""
    api = FakeAPI({REPO: [[]]})
    payload = _run(tmp_path, api, monkeypatch)
    assert payload["prs"] == []
    assert payload["new_watermarks"] == {REPO: WATERMARK}
    assert "generated_at" in payload


def test_new_watermarks_advance_to_max_merged_at(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """new_watermarks carries the max merged_at seen per repo."""
    quiet = "Geoffe-Ga/wavelength-demo"
    api = FakeAPI(
        {
            REPO: [
                [
                    _pull(21, "2026-07-31T09:00:00Z"),
                    _pull(20, "2026-07-31T04:00:00Z"),
                ]
            ],
            quiet: [[]],
        },
        {(REPO, 21): [_file("a.py")], (REPO, 20): [_file("b.py")]},
    )
    watermarks = {
        REPO: {"last_synced_merged_at": WATERMARK},
        quiet: {"last_synced_merged_at": WATERMARK},
    }
    payload = _run(tmp_path, api, monkeypatch, watermarks=watermarks)
    assert payload["new_watermarks"] == {
        REPO: "2026-07-31T09:00:00Z",
        quiet: WATERMARK,
    }


def test_rate_limit_skips_repo_and_keeps_watermark(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A 403/429 skips the repo with a warning; other repos still collect."""
    limited = "Geoffe-Ga/aptitude-course"
    inner = FakeAPI(
        {REPO: [[_pull(31, "2026-07-31T07:00:00Z")]]},
        {(REPO, 31): [_file("a.py")]},
    )

    def dispatch(url: str) -> Any:
        if limited in url:
            raise cmp_mod.RateLimitError(f"HTTP 403 from {url}")
        return inner(url)

    monkeypatch.setattr(cmp_mod, "_http_get_json", dispatch)
    watermarks_path = tmp_path / "watermarks.json"
    out_path = tmp_path / "out.json"
    watermarks_path.write_text(
        json.dumps(
            {
                limited: {"last_synced_merged_at": WATERMARK},
                REPO: {"last_synced_merged_at": WATERMARK},
            }
        )
    )
    assert cmp_mod.main(["--watermarks", str(watermarks_path), "--out", str(out_path)]) == 0
    payload = json.loads(out_path.read_text())
    assert payload["new_watermarks"][limited] == WATERMARK
    assert [pr["number"] for pr in payload["prs"]] == [31]
    assert "skipping" in capsys.readouterr().err


def test_files_capped_at_two_hundred(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A PR with more than 200 changed files keeps 200 and sets the flag."""
    many_files = [_file(f"f{i}.py", patch=None) for i in range(250)]
    api = FakeAPI(
        {REPO: [[_pull(40, "2026-07-31T05:00:00Z")]]},
        {(REPO, 40): many_files},
    )
    payload = _run(tmp_path, api, monkeypatch)
    record = payload["prs"][0]
    assert len(record["files"]) == cmp_mod.MAX_FILES_PER_PR
    assert record["files_truncated"] is True
