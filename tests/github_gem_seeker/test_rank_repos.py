"""Tests for the github-gem-seeker skill's scripts/rank_repos.py."""

import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SKILL_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / ".claude"
    / "skills"
    / "github-gem-seeker"
    / "scripts"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("rank_repos", SKILL_SCRIPTS_DIR / "rank_repos.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def rr():
    return _load_module()


FIXED_NOW = datetime(2026, 7, 1, tzinfo=timezone.utc)


def _iso(days_ago):
    return (FIXED_NOW - timedelta(days=days_ago)).date().isoformat()


def test_classify_legendary(rr):
    repo = {"name": "ffmpeg", "stars": 55000, "last_commit_date": _iso(10), "has_readme": True, "open_issues": 100}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["tier"] == "Legendary"


def test_classify_excellent(rr):
    repo = {"name": "archivebox", "stars": 15000, "last_commit_date": _iso(10), "has_readme": True, "open_issues": 50}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["tier"] == "Excellent"


def test_classify_solid(rr):
    repo = {"name": "some-tool", "stars": 2000, "last_commit_date": _iso(30), "has_readme": True, "open_issues": 10}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["tier"] == "Solid"


def test_classify_promising(rr):
    repo = {"name": "niche-tool", "stars": 500, "last_commit_date": _iso(20), "has_readme": True, "open_issues": 5}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["tier"] == "Promising"
    assert result["is_active"] is True


def test_boundary_exactly_50000_is_legendary(rr):
    repo = {"name": "boundary", "stars": 50000}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["tier"] == "Legendary"


def test_boundary_exactly_10000_is_excellent(rr):
    repo = {"name": "boundary", "stars": 10000}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["tier"] == "Excellent"


def test_boundary_exactly_1000_is_solid(rr):
    repo = {"name": "boundary", "stars": 1000}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["tier"] == "Solid"


def test_boundary_999_is_promising(rr):
    repo = {"name": "boundary", "stars": 999}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["tier"] == "Promising"


def test_stale_repo_flagged_but_still_classified(rr):
    repo = {"name": "abandoned", "stars": 500, "last_commit_date": _iso(1000)}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["tier"] == "Promising"
    assert result["is_stale"] is True
    assert result["is_active"] is False


def test_missing_last_commit_date_is_unknown_not_penalized(rr):
    repo = {"name": "no-date", "stars": 50000}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["tier"] == "Legendary"
    assert result["is_active"] is None
    assert result["is_stale"] is None


def test_missing_stars_defaults_to_zero(rr):
    repo = {"name": "no-stars"}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["stars"] == 0
    assert result["tier"] == "Promising"


def test_non_numeric_stars_does_not_crash(rr):
    repo = {"name": "weird", "stars": "not-a-number"}
    result = rr.classify_repo(repo, now=FIXED_NOW)
    assert result["stars"] == 0


def test_rank_repos_sorts_by_tier_then_stars(rr):
    repos = [
        {"name": "solid-tool", "stars": 1500},
        {"name": "legendary-tool", "stars": 60000},
        {"name": "excellent-tool", "stars": 12000},
        {"name": "promising-tool", "stars": 200},
    ]
    ranked = rr.rank_repos(repos, now=FIXED_NOW)
    tiers = [r["tier"] for r in ranked]
    assert tiers == ["Legendary", "Excellent", "Solid", "Promising"]


def test_rank_repos_ties_broken_by_stars_desc(rr):
    repos = [
        {"name": "b", "stars": 5000},
        {"name": "a", "stars": 20000},
        {"name": "c", "stars": 11000},
    ]
    ranked = rr.rank_repos(repos, now=FIXED_NOW)
    names = [r["name"] for r in ranked]
    assert names == ["a", "c", "b"]


def test_rank_repos_ties_broken_by_name_when_stars_equal(rr):
    repos = [
        {"name": "zeta", "stars": 5000},
        {"name": "alpha", "stars": 5000},
    ]
    ranked = rr.rank_repos(repos, now=FIXED_NOW)
    names = [r["name"] for r in ranked]
    assert names == ["alpha", "zeta"]


def test_rank_repos_empty_input(rr):
    assert rr.rank_repos([]) == []


def test_rank_repos_uses_full_name_when_name_missing(rr):
    repos = [{"full_name": "owner/repo", "stars": 100}]
    ranked = rr.rank_repos(repos, now=FIXED_NOW)
    assert ranked[0]["full_name"] == "owner/repo"


def test_cli_reads_json_file_and_writes_output(tmp_path, rr):
    input_path = tmp_path / "candidates.json"
    input_path.write_text(json.dumps([{"name": "yt-dlp", "stars": 90000, "last_commit_date": "2026-06-01"}]))
    output_path = tmp_path / "ranked.json"
    rc = rr.main([str(input_path), "--output", str(output_path)])
    assert rc == 0
    data = json.loads(output_path.read_text())
    assert data[0]["tier"] == "Legendary"


def test_cli_rejects_non_list_input(tmp_path, rr, capsys):
    input_path = tmp_path / "bad.json"
    input_path.write_text(json.dumps({"not": "a list"}))
    rc = rr.main([str(input_path)])
    assert rc == 1


def test_cli_reads_from_stdin(rr, monkeypatch, capsys):
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps([{"name": "tool", "stars": 2000}])))
    rc = rr.main(["-"])
    assert rc == 0
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output[0]["tier"] == "Solid"
