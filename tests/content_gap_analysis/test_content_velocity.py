"""End-to-end tests for scripts/content_velocity.py."""
import subprocess
import sys

import pandas as pd

from . import conftest

SCRIPT = conftest.SKILL_SCRIPTS / "content_velocity.py"
FIXTURES = conftest.FIXTURES


def run_script(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd, capture_output=True, text=True,
    )


def test_help_exits_zero():
    result = run_script(["--help"], cwd=str(FIXTURES))
    assert result.returncode == 0


def test_content_velocity_end_to_end(tmp_path):
    out_prefix = str(tmp_path / "velocity")
    result = run_script([
        "--pages", f"competitor={FIXTURES / 'competitor_pages.csv'}",
        "--out-prefix", out_prefix,
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    out_csv = tmp_path / "velocity_velocity.csv"
    assert out_csv.exists()

    df = pd.read_csv(out_csv)
    assert list(df.columns) == ["domain", "blog_pages", "blog_traffic", "traffic_per_blog_page"]
    row = df.iloc[0]
    assert row["domain"] == "competitor"
    assert row["blog_pages"] == 1  # only one /blog/ URL in the fixture
    assert row["blog_traffic"] == 900


def test_content_velocity_missing_url_column_skips_gracefully(tmp_path):
    out_prefix = str(tmp_path / "velocity")
    result = run_script([
        "--pages", f"competitor={FIXTURES / 'competitor_pages.csv'}",
        "--url-col", "NopeCol",
        "--out-prefix", out_prefix,
    ], cwd=str(tmp_path))
    assert result.returncode == 0
    assert "No URL column" in result.stdout
    # No rows collected -> no output file written.
    assert not (tmp_path / "velocity_velocity.csv").exists()


def test_content_velocity_bad_spec_exits_cleanly(tmp_path):
    result = run_script(["--pages", "no-equals-sign-here"], cwd=str(tmp_path))
    assert result.returncode != 0
