"""Tests for the internet-skill-finder skill's scripts/fetch_skills.py.

Covers the bug fixes made to the original script:
  - bounded timeouts on subprocess/HTTP calls (no hangs)
  - graceful handling of failed/timed-out/malformed responses instead of
    bare excepts / crashes
  - cache staleness detection (age-based, not "cache forever")
  - the readme-skill import_url heuristic no longer produces broken links
    for bare owner/repo landing page links
"""

import base64
import importlib.util
import json
import subprocess
import time
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SKILL_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / ".claude"
    / "skills"
    / "internet-skill-finder"
    / "scripts"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("fetch_skills", SKILL_SCRIPTS_DIR / "fetch_skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def fs():
    # Fresh module import per test so USE_GH_CLI global doesn't leak between tests.
    return _load_module()


# --- check_gh_cli -------------------------------------------------------------


def test_check_gh_cli_returns_false_when_binary_missing(fs):
    with patch("subprocess.run", side_effect=FileNotFoundError()):
        assert fs.check_gh_cli() is False


def test_check_gh_cli_returns_false_on_timeout(fs):
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="gh", timeout=5)):
        assert fs.check_gh_cli() is False


def test_check_gh_cli_returns_true_on_success(fs):
    mock_result = MagicMock(returncode=0)
    with patch("subprocess.run", return_value=mock_result):
        assert fs.check_gh_cli() is True


def test_check_gh_cli_uses_bounded_timeout(fs):
    mock_result = MagicMock(returncode=0)
    with patch("subprocess.run", return_value=mock_result) as mock_run:
        fs.check_gh_cli()
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == fs.GH_CLI_CHECK_TIMEOUT


# --- gh_api --------------------------------------------------------------------


def test_gh_api_returns_none_on_timeout(fs):
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="gh", timeout=20)):
        assert fs.gh_api("repos/foo/bar") is None


def test_gh_api_returns_none_on_nonzero_exit(fs):
    mock_result = MagicMock(returncode=1, stderr="not found", stdout="")
    with patch("subprocess.run", return_value=mock_result):
        assert fs.gh_api("repos/foo/bar") is None


def test_gh_api_returns_none_on_invalid_json(fs):
    mock_result = MagicMock(returncode=0, stdout="not json{{{")
    with patch("subprocess.run", return_value=mock_result):
        assert fs.gh_api("repos/foo/bar") is None


def test_gh_api_returns_parsed_json_on_success(fs):
    mock_result = MagicMock(returncode=0, stdout=json.dumps({"stargazers_count": 42}))
    with patch("subprocess.run", return_value=mock_result):
        result = fs.gh_api("repos/foo/bar")
    assert result == {"stargazers_count": 42}


# --- http_api --------------------------------------------------------------------


def test_http_api_handles_rate_limit_403(fs):
    err = urllib.error.HTTPError(url="x", code=403, msg="Forbidden", hdrs=None, fp=None)
    with patch("urllib.request.urlopen", side_effect=err):
        assert fs.http_api("https://api.github.com/rate_limit") is None


def test_http_api_handles_timeout(fs):
    with patch("urllib.request.urlopen", side_effect=TimeoutError()):
        assert fs.http_api("https://api.github.com/repos/foo/bar") is None


def test_http_api_handles_connection_error(fs):
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("no network")):
        assert fs.http_api("https://api.github.com/repos/foo/bar") is None


def test_http_api_handles_invalid_json(fs):
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value.read.return_value = b"not json"
    with patch("urllib.request.urlopen", return_value=mock_cm):
        assert fs.http_api("https://api.github.com/repos/foo/bar") is None


def test_http_api_success(fs):
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value.read.return_value = json.dumps({"ok": True}).encode()
    with patch("urllib.request.urlopen", return_value=mock_cm):
        result = fs.http_api("https://api.github.com/repos/foo/bar")
    assert result == {"ok": True}


def test_http_api_sends_bounded_timeout(fs):
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value.read.return_value = b"{}"
    with patch("urllib.request.urlopen", return_value=mock_cm) as mock_urlopen:
        fs.http_api("https://api.github.com/repos/foo/bar")
        _, kwargs = mock_urlopen.call_args
        assert kwargs["timeout"] == fs.HTTP_TIMEOUT


def test_http_api_no_manus_user_agent(fs):
    """The original script sent a 'Manus-Skill-Finder' user agent; verify it's gone."""
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value.read.return_value = b"{}"
    with patch("urllib.request.urlopen", return_value=mock_cm) as mock_urlopen:
        fs.http_api("https://api.github.com/repos/foo/bar")
    request_obj = mock_urlopen.call_args[0][0]
    ua = request_obj.get_header("User-agent")
    assert ua is not None
    assert "manus" not in ua.lower()


# --- cache staleness -------------------------------------------------------------


def test_cache_age_hours_returns_none_for_missing_file(fs, tmp_path):
    missing = tmp_path / "no_such_cache.json"
    assert fs.cache_age_hours(missing) is None


def test_cache_age_hours_computes_age(fs, tmp_path):
    cache_file = tmp_path / "cache.json"
    cache_file.write_text("{}")
    old_time = time.time() - (3 * 3600)  # 3 hours ago
    import os

    os.utime(cache_file, (old_time, old_time))
    age = fs.cache_age_hours(cache_file)
    assert 2.9 <= age <= 3.1


def test_is_cache_stale_true_when_missing(fs, tmp_path):
    missing = tmp_path / "no_such_cache.json"
    assert fs.is_cache_stale(missing, max_age_hours=24) is True


def test_is_cache_stale_false_when_fresh(fs, tmp_path):
    cache_file = tmp_path / "cache.json"
    cache_file.write_text("{}")
    assert fs.is_cache_stale(cache_file, max_age_hours=24) is False


def test_is_cache_stale_true_when_old(fs, tmp_path):
    cache_file = tmp_path / "cache.json"
    cache_file.write_text("{}")
    old_time = time.time() - (48 * 3600)
    import os

    os.utime(cache_file, (old_time, old_time))
    assert fs.is_cache_stale(cache_file, max_age_hours=24) is True


def test_save_cache_stamps_fetched_at(fs, tmp_path):
    cache_file = tmp_path / "cache.json"
    fs.save_cache({"some/repo": {"stars": 1, "skills": []}}, cache_file)
    data = json.loads(cache_file.read_text())
    assert "_fetched_at" in data
    assert "some/repo" in data


def test_load_cache_returns_none_for_corrupt_file(fs, tmp_path):
    cache_file = tmp_path / "cache.json"
    cache_file.write_text("{not valid json")
    assert fs.load_cache(cache_file) is None


def test_load_cache_returns_none_for_missing_file(fs, tmp_path):
    assert fs.load_cache(tmp_path / "missing.json") is None


def test_repo_entries_excludes_metadata_keys(fs):
    payload = {"_fetched_at": 123, "_fetched_at_iso": "x", "owner/repo": {"stars": 1}}
    entries = fs._repo_entries(payload)
    assert "_fetched_at" not in entries
    assert "owner/repo" in entries


# --- parse_readme_skills: import_url heuristic fix -------------------------------


def test_parse_readme_skills_specific_path_gets_import_url(fs):
    readme = "- [My Skill](https://github.com/owner/repo/tree/main/skills/my-skill) - does a thing\n"
    skills = fs.parse_readme_skills(readme)
    assert len(skills) >= 1
    matching = [s for s in skills if s["name"] == "My Skill"]
    assert matching
    assert matching[0]["import_url"] != ""


def test_parse_readme_skills_bare_repo_link_gets_no_import_url(fs):
    # A bare owner/repo landing-page link is not a specific skill path;
    # the fixed heuristic should not fabricate a misleading import_url for it.
    readme = "* [SomeProject](https://github.com/owner/repo)\n"
    skills = fs.parse_readme_skills(readme)
    assert len(skills) == 1
    assert skills[0]["import_url"] == ""


def test_parse_readme_skills_filters_badges(fs):
    readme = "[![badge](https://shields.io/x)](https://github.com/owner/repo)\n"
    skills = fs.parse_readme_skills(readme)
    assert skills == []


def test_parse_readme_skills_no_manus_import_url(fs):
    """The original script generated manus.im import URLs; verify that's gone."""
    readme = "- [My Skill](https://github.com/owner/repo/tree/main/skills/my-skill) - does a thing\n"
    skills = fs.parse_readme_skills(readme)
    for skill in skills:
        assert "manus" not in skill["import_url"].lower()


# --- search_skills / generate_github_url -----------------------------------------


def test_search_skills_matches_name_and_description(fs):
    all_repos = {
        "owner/repo": {
            "stars": 100,
            "type": "skills",
            "skills": [
                {"name": "pdf-tools", "github_url": "https://github.com/owner/repo/tree/main/skills/pdf-tools", "import_url": "x"},
                {"name": "other", "description": "handles pdf export", "github_url": "y", "import_url": "y"},
                {"name": "unrelated", "github_url": "z", "import_url": "z"},
            ],
        }
    }
    matches = fs.search_skills("pdf", all_repos)
    names = {m["name"] for m in matches}
    assert names == {"pdf-tools", "other"}


def test_search_skills_ignores_metadata_keys(fs):
    all_repos = {"_fetched_at": 123, "owner/repo": {"stars": 1, "type": "skills", "skills": []}}
    # Should not raise despite the non-repo "_fetched_at" key.
    assert fs.search_skills("anything", all_repos) == []


def test_generate_github_url_dot_path(fs):
    url = fs.generate_github_url("owner", "repo", "skillname", ".", "main")
    assert url == "https://github.com/owner/repo/tree/main/skillname"


def test_generate_github_url_subpath(fs):
    url = fs.generate_github_url("owner", "repo", "skillname", "skills", "main")
    assert url == "https://github.com/owner/repo/tree/main/skills/skillname"


def test_no_hardcoded_manus_home_path_in_module_source():
    """The original SKILL.md hardcoded /home/ubuntu/skills/...; ensure the
    installed script contains no such absolute path baked in."""
    source = (SKILL_SCRIPTS_DIR / "fetch_skills.py").read_text()
    assert "/home/ubuntu" not in source


# --- deep_dive -------------------------------------------------------------------


def test_deep_dive_unknown_repo_returns_error(fs):
    result = fs.deep_dive("nonexistent/repo", "some-skill")
    assert "error" in result


def test_deep_dive_curated_list_returns_error(fs):
    result = fs.deep_dive("travisvn/awesome-claude-skills", "some-skill")
    assert "error" in result


def test_deep_dive_success(fs):
    content = "---\nname: my-skill\ndescription: Does a thing\n---\n\n# My Skill\n"
    encoded = base64.b64encode(content.encode()).decode()
    with patch.object(fs, "api_request", return_value={"encoding": "base64", "content": encoded}):
        result = fs.deep_dive("anthropics/skills", "my-skill")
    assert result["name"] == "my-skill"
    assert result["description"] == "Does a thing"
    assert "my-skill" in result["github_url"]


def test_deep_dive_api_failure_returns_error(fs):
    with patch.object(fs, "api_request", return_value=None):
        result = fs.deep_dive("anthropics/skills", "my-skill")
    assert "error" in result


def test_deep_dive_bad_encoding_returns_error(fs):
    with patch.object(fs, "api_request", return_value={"encoding": "utf-8", "content": "raw"}):
        result = fs.deep_dive("anthropics/skills", "my-skill")
    assert "error" in result
