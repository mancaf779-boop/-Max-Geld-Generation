"""End-to-end tests for scripts/generate_seo_charts.py."""
import json
import shutil
import subprocess
import sys

from . import conftest

SCRIPT = conftest.SKILL_SCRIPTS / "generate_seo_charts.py"
PROJECT_FIXTURE = conftest.FIXTURES / "project"


def run_script(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd, capture_output=True, text=True,
    )


def test_help_exits_zero():
    result = run_script(["--help"], cwd=str(PROJECT_FIXTURE))
    assert result.returncode == 0


def test_generate_charts_end_to_end(tmp_path):
    project_dir = tmp_path / "project"
    shutil.copytree(PROJECT_FIXTURE, project_dir)
    out_dir = project_dir / "charts"

    result = run_script([
        "--project-dir", str(project_dir),
        "--output-dir", str(out_dir),
        "--title", "example-ai.com",
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr

    manifest = json.loads((out_dir / "asset_manifest.json").read_text())
    assert manifest["created_count"] >= 8

    expected_files = {
        "global_organic_trend.png",
        "top_countries_bar.png",
        "country_trend.png",
        "page_type_traffic_bar.png",
        "top_landing_pages_bar.png",
        "branded_nonbranded_comparison.png",
        "largest_page_losses_bar.png",
        "largest_keyword_losses_bar.png",
        "backlink_anchor_mix_bar.png",
        "backlink_destination_mix_bar.png",
    }
    for filename in expected_files:
        path = out_dir / filename
        assert path.exists(), f"expected {filename} to be generated"
        assert path.stat().st_size > 0

    manifest_md = (out_dir / "asset_manifest.md").read_text()
    assert "SEO Chart Asset Manifest" in manifest_md


def test_missing_project_dir_exits_nonzero(tmp_path):
    result = run_script([
        "--project-dir", str(tmp_path / "does_not_exist"),
    ], cwd=str(tmp_path))
    assert result.returncode == 2
    assert "does not exist" in result.stdout


def test_empty_project_dir_reports_all_missing_but_does_not_crash(tmp_path):
    empty_project = tmp_path / "empty_project"
    empty_project.mkdir()
    result = run_script([
        "--project-dir", str(empty_project),
    ], cwd=str(tmp_path))
    # Exit code 2 = no charts created, but must not be an unhandled traceback.
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    manifest = json.loads((empty_project / "charts" / "asset_manifest.json").read_text())
    assert manifest["created_count"] == 0
    assert len(manifest["missing_or_skipped"]) > 0
