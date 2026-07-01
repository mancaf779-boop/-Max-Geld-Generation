"""End-to-end tests for scripts/near_winners.py."""
import subprocess
import sys

import pandas as pd

from . import conftest

SCRIPT = conftest.SKILL_SCRIPTS / "near_winners.py"
FIXTURES = conftest.FIXTURES


def run_script(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd, capture_output=True, text=True,
    )


def test_help_exits_zero():
    result = run_script(["--help"], cwd=str(FIXTURES))
    assert result.returncode == 0


def test_near_winners_end_to_end(tmp_path):
    out = tmp_path / "near_winners.csv"
    result = run_script([
        "--positions", str(FIXTURES / "target_positions.csv"),
        "--min-pos", "4", "--max-pos", "15", "--min-volume", "2000",
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert out.exists()

    df = pd.read_csv(out)
    # From the fixture, three keywords sit within position 4-15 with volume >= 2000:
    # "best ai writer" (pos 7, vol 3000), "ai image generator" (pos 5, vol 2500),
    # and "translate english to spanish" (pos 12, vol 4000).
    assert set(df["Keyword"]) == {
        "best ai writer", "ai image generator", "translate english to spanish",
    }
    assert (df["Position"] >= 4).all()
    assert (df["Position"] <= 15).all()
    assert (df["Search Volume"] >= 2000).all()


def test_near_winners_no_matches_writes_empty_csv_not_crash(tmp_path):
    out = tmp_path / "near_winners.csv"
    result = run_script([
        "--positions", str(FIXTURES / "target_positions.csv"),
        "--min-volume", "999999",
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert "No near-winner keywords matched" in result.stdout


def test_near_winners_missing_column_exits_cleanly(tmp_path):
    out = tmp_path / "out.csv"
    result = run_script([
        "--positions", str(FIXTURES / "target_positions.csv"),
        "--position-col", "NopeCol",
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode != 0
