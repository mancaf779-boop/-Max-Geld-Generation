"""End-to-end tests for scripts/build_gap_workbook.py."""
import csv
import subprocess
import sys
from pathlib import Path

import conftest

SCRIPT = conftest.SKILL_SCRIPTS / "build_gap_workbook.py"
FIXTURES = conftest.FIXTURES


def run_script(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd, capture_output=True, text=True,
    )


def test_help_exits_zero():
    result = run_script(["--help"], cwd=str(FIXTURES))
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_build_gap_workbook_end_to_end(tmp_path):
    # Reuse the Positions fixtures as generic keyword exports: Keyword/Position/Search Volume columns.
    out = tmp_path / "gap_workbook.csv"
    result = run_script([
        "--target", str(FIXTURES / "target_positions.csv"),
        "--competitor", str(FIXTURES / "competitor_positions.csv"),
        "--keyword-col", "Keyword",
        "--volume-col", "Search Volume",
        "--kd-col", "Keyword Difficulty",
        "--position-col", "Position",
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert out.exists()

    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) > 0
    fieldnames = rows[0].keys()
    for col in ("keyword", "gap_type", "priority_score", "demand_score", "winnability_score"):
        assert col in fieldnames

    gap_types = {r["gap_type"] for r in rows}
    assert gap_types <= {"missing", "weak"}
    # "translate english to french" only exists for the competitor -> missing gap.
    keywords = {r["keyword"] for r in rows}
    assert "translate english to french" in keywords

    # Priority scores should be sorted descending.
    scores = [int(r["priority_score"]) for r in rows]
    assert scores == sorted(scores, reverse=True)


def test_build_gap_workbook_bad_column_errors_clearly(tmp_path):
    out = tmp_path / "gap_workbook.csv"
    result = run_script([
        "--target", str(FIXTURES / "target_positions.csv"),
        "--competitor", str(FIXTURES / "competitor_positions.csv"),
        "--keyword-col", "NotAColumn",
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode != 0
    assert "not found" in result.stdout or "not found" in result.stderr
