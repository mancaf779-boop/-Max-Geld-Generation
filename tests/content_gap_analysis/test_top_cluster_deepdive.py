"""End-to-end tests for scripts/top_cluster_deepdive.py."""
import subprocess
import sys

import pandas as pd

import conftest

SCRIPT = conftest.SKILL_SCRIPTS / "top_cluster_deepdive.py"
FIXTURES = conftest.FIXTURES


def run_script(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd, capture_output=True, text=True,
    )


def test_help_exits_zero():
    result = run_script(["--help"], cwd=str(FIXTURES))
    assert result.returncode == 0


def test_survey_mode_lists_folders(tmp_path):
    result = run_script([
        "--pages", str(FIXTURES / "competitor_pages.csv"),
        "--positions", str(FIXTURES / "competitor_positions.csv"),
        "--survey",
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert "Largest folders by traffic" in result.stdout
    assert "REPLICABLE" in result.stdout


def test_folder_deepdive_end_to_end(tmp_path):
    out = tmp_path / "winning_pages.csv"
    result = run_script([
        "--pages", str(FIXTURES / "competitor_pages.csv"),
        "--positions", str(FIXTURES / "competitor_positions.csv"),
        "--folder", "/translate",
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert out.exists()

    df = pd.read_csv(out)
    assert set(["slug", "traffic", "keywords", "best_pos", "recent_traj%"]).issubset(df.columns)
    assert len(df) >= 1
    assert all("/translate" in s for s in df["slug"])


def test_folder_deepdive_no_matches_exits_cleanly(tmp_path):
    out = tmp_path / "winning_pages.csv"
    result = run_script([
        "--pages", str(FIXTURES / "competitor_pages.csv"),
        "--positions", str(FIXTURES / "competitor_positions.csv"),
        "--folder", "/does-not-exist",
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode != 0
    assert "no rows" in (result.stdout + result.stderr).lower()


def test_folder_deepdive_missing_column_exits_cleanly(tmp_path):
    out = tmp_path / "out.csv"
    result = run_script([
        "--pages", str(FIXTURES / "competitor_pages.csv"),
        "--positions", str(FIXTURES / "competitor_positions.csv"),
        "--folder", "/translate",
        "--traffic-col", "NopeCol",
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode != 0
