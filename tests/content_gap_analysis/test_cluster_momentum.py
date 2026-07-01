"""End-to-end tests for scripts/cluster_momentum.py."""
import subprocess
import sys

import pandas as pd

from . import conftest

SCRIPT = conftest.SKILL_SCRIPTS / "cluster_momentum.py"
FIXTURES = conftest.FIXTURES


def run_script(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd, capture_output=True, text=True,
    )


def test_help_exits_zero():
    result = run_script(["--help"], cwd=str(FIXTURES))
    assert result.returncode == 0


def test_cluster_momentum_end_to_end(tmp_path):
    out = tmp_path / "cluster_momentum.csv"
    result = run_script([
        "--positions", str(FIXTURES / "competitor_positions.csv"),
        "--clusters", str(FIXTURES / "clusters.json"),
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert out.exists()

    df = pd.read_csv(out)
    assert set(["cluster", "total_volume", "keywords", "trend_12mo_%",
                "recent_trajectory_%", "direction"]).issubset(df.columns)
    assert (df["direction"].isin(["Growing", "Declining", "Stable / Maturing"])).all()
    # Translation cluster should exist given the fixture keywords.
    assert "Translation" in df["cluster"].values


def test_cluster_momentum_missing_clusters_file_exits_cleanly(tmp_path):
    out = tmp_path / "out.csv"
    result = run_script([
        "--positions", str(FIXTURES / "competitor_positions.csv"),
        "--clusters", str(tmp_path / "does_not_exist.json"),
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode != 0
    assert "not found" in (result.stdout + result.stderr).lower()


def test_cluster_momentum_bad_json_exits_cleanly(tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not valid json")
    out = tmp_path / "out.csv"
    result = run_script([
        "--positions", str(FIXTURES / "competitor_positions.csv"),
        "--clusters", str(bad_json),
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode != 0
    assert "not valid json" in (result.stdout + result.stderr).lower()


def test_cluster_momentum_missing_column_exits_cleanly(tmp_path):
    out = tmp_path / "out.csv"
    result = run_script([
        "--positions", str(FIXTURES / "competitor_positions.csv"),
        "--clusters", str(FIXTURES / "clusters.json"),
        "--keyword-col", "NopeCol",
        "--out", str(out),
    ], cwd=str(tmp_path))
    assert result.returncode != 0
    assert "not in export" in (result.stdout + result.stderr).lower()
