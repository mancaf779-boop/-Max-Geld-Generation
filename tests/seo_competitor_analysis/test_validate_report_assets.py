"""End-to-end tests for scripts/validate_report_assets.py."""
import shutil
import subprocess
import sys

from . import conftest

SCRIPT = conftest.SKILL_SCRIPTS / "validate_report_assets.py"
GEN_SCRIPT = conftest.SKILL_SCRIPTS / "generate_seo_charts.py"
PROJECT_FIXTURE = conftest.FIXTURES / "project"
FIXTURES = conftest.FIXTURES


def run_script(args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd, capture_output=True, text=True,
    )


def test_help_exits_zero():
    result = run_script(["--help"])
    assert result.returncode == 0


def _generate_charts(tmp_path):
    project_dir = tmp_path / "project"
    shutil.copytree(PROJECT_FIXTURE, project_dir)
    out_dir = project_dir / "charts"
    subprocess.run(
        [sys.executable, str(GEN_SCRIPT), "--project-dir", str(project_dir),
         "--output-dir", str(out_dir), "--title", "example-ai.com"],
        check=True, capture_output=True, text=True,
    )
    return project_dir, out_dir


def test_good_report_with_real_charts_passes(tmp_path):
    project_dir, charts_dir = _generate_charts(tmp_path)
    report = project_dir / "final_report.md"
    report.write_text((FIXTURES / "good_report.md").read_text())

    result = run_script(["--report", str(report), "--charts-dir", str(charts_dir)])
    assert result.returncode == 0, result.stdout
    assert '"errors": []' in result.stdout.replace(" ", "").replace("\n", "") or '"errors":[]' in result.stdout.replace(" ", "")


def test_bad_report_flags_prescriptive_language_and_missing_charts(tmp_path):
    report = tmp_path / "bad_report.md"
    report.write_text((FIXTURES / "bad_report.md").read_text())
    charts_dir = tmp_path / "charts"
    charts_dir.mkdir()

    result = run_script(["--report", str(report), "--charts-dir", str(charts_dir)])
    assert result.returncode == 1
    assert "Prescriptive language detected" in result.stdout
    assert "roadmap" in result.stdout.lower()


def test_missing_report_exits_with_error():
    result = run_script(["--report", "/tmp/does-not-exist-report.md"])
    assert result.returncode == 2
    assert "not found" in result.stdout.lower()


def test_missing_image_file_is_an_error(tmp_path):
    report = tmp_path / "report.md"
    report.write_text(
        "# Report\n\n"
        "![missing chart](charts/does_not_exist.png)\n"
        "![missing chart 2](charts/also_missing.png)\n"
        "![missing chart 3](charts/still_missing.png)\n"
    )
    charts_dir = tmp_path / "charts"
    charts_dir.mkdir()
    result = run_script(["--report", str(report), "--charts-dir", str(charts_dir)])
    assert result.returncode == 1
    assert "Missing referenced image" in result.stdout
