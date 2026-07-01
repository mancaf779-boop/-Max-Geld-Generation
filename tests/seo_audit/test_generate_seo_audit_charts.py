"""End-to-end tests for scripts/generate_seo_audit_charts.py."""
import subprocess
import sys

from . import conftest

SCRIPT = conftest.SKILL_SCRIPTS / "generate_seo_audit_charts.py"
CHART_DATA = conftest.FIXTURES / "chart_data"

EXPECTED_CHARTS = [
    "organic_traffic_trend.png",
    "top_organic_countries.png",
    "page_type_traffic_share.png",
    "branded_nonbranded_mix.png",
    "keyword_portfolio_brand_mix.png",
    "content_cluster_clicks.png",
    "locale_traffic_share.png",
    "site_architecture_click_depth.png",
    "backlink_referring_domains.png",
    "backlink_quality_distribution.png",
    "core_web_vitals_snapshot.png",
]


def run_script(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd, capture_output=True, text=True,
    )


def test_help_exits_zero():
    result = run_script(["--help"], cwd=str(CHART_DATA))
    assert result.returncode == 0


def test_generate_all_charts_end_to_end(tmp_path):
    output_dir = tmp_path / "assets"
    manifest = tmp_path / "chart_manifest.md"
    result = run_script([
        "--data-dir", str(CHART_DATA),
        "--output-dir", str(output_dir),
        "--manifest", str(manifest),
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert manifest.exists()

    for chart_file in EXPECTED_CHARTS:
        path = output_dir / chart_file
        assert path.exists(), f"expected chart {chart_file} to be generated"
        assert path.stat().st_size > 0

    manifest_text = manifest.read_text()
    assert "Generated charts: **11**" in manifest_text
    assert "Skipped charts: **0**" in manifest_text


def test_missing_data_dir_exits_nonzero(tmp_path):
    result = run_script([
        "--data-dir", str(tmp_path / "does_not_exist"),
        "--output-dir", str(tmp_path / "assets"),
    ], cwd=str(tmp_path))
    assert result.returncode != 0
    assert "does not exist" in result.stderr or "does not exist" in result.stdout


def test_partial_data_reports_skipped_charts_in_manifest(tmp_path):
    # Only provide one of the eleven supported CSVs.
    data_dir = tmp_path / "chart_data"
    data_dir.mkdir()
    (data_dir / "organic_traffic_trend.csv").write_text(
        (CHART_DATA / "organic_traffic_trend.csv").read_text()
    )
    output_dir = tmp_path / "assets"
    manifest = tmp_path / "chart_manifest.md"
    result = run_script([
        "--data-dir", str(data_dir),
        "--output-dir", str(output_dir),
        "--manifest", str(manifest),
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert (output_dir / "organic_traffic_trend.png").exists()
    manifest_text = manifest.read_text()
    assert "Generated charts: **1**" in manifest_text
    assert "Skipped charts: **10**" in manifest_text
    assert "Missing input file" in manifest_text


def test_malformed_csv_is_skipped_not_crashed(tmp_path):
    """A malformed/empty CSV must be skipped gracefully, not crash the whole run."""
    data_dir = tmp_path / "chart_data"
    data_dir.mkdir()
    # Empty file triggers pandas.errors.EmptyDataError inside read_csv.
    (data_dir / "top_organic_countries.csv").write_text("")
    output_dir = tmp_path / "assets"
    manifest = tmp_path / "chart_manifest.md"
    result = run_script([
        "--data-dir", str(data_dir),
        "--output-dir", str(output_dir),
        "--manifest", str(manifest),
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    manifest_text = manifest.read_text()
    assert "top_organic_countries" in manifest_text
    assert "Skipped charts: **11**" in manifest_text


def test_json_manifest_written_when_requested(tmp_path):
    output_dir = tmp_path / "assets"
    manifest = tmp_path / "chart_manifest.md"
    json_manifest = tmp_path / "chart_manifest.json"
    result = run_script([
        "--data-dir", str(CHART_DATA),
        "--output-dir", str(output_dir),
        "--manifest", str(manifest),
        "--json", str(json_manifest),
    ], cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert json_manifest.exists()
    import json
    data = json.loads(json_manifest.read_text())
    assert isinstance(data, list)
    assert len(data) == 11
