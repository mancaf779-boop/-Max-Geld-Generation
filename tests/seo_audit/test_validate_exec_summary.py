"""End-to-end tests for scripts/validate_exec_summary.py."""
import subprocess
import sys

from . import conftest

SCRIPT = conftest.SKILL_SCRIPTS / "validate_exec_summary.py"
FIXTURES = conftest.FIXTURES


def run_script(args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


def test_help_exits_zero():
    result = run_script(["--help"])
    assert result.returncode == 0


def test_good_report_passes():
    result = run_script([str(FIXTURES / "good_report.md")])
    assert result.returncode == 0, result.stdout
    assert "PASS: Executive Summary has exactly 1 paragraph" in result.stdout
    assert "PASS: Paragraph 1 starts with a bold audit headline." in result.stdout


def test_bad_report_fails_word_count_and_headline_and_forbidden_section():
    result = run_script([str(FIXTURES / "bad_report.md")])
    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "should start with a bold audit headline" in result.stdout
    assert "Forbidden standalone section found" in result.stdout


def test_missing_report_file_exits_cleanly():
    result = run_script(["/tmp/does-not-exist-report.md"])
    assert result.returncode == 2
    assert "not found" in result.stdout.lower()


def test_report_missing_heading_fails_cleanly(tmp_path):
    report = tmp_path / "no_heading.md"
    report.write_text("# Report\n\nJust some prose, no Executive Summary heading.\n")
    result = run_script([str(report)])
    assert result.returncode == 1
    assert "FAIL" in result.stdout


def test_empty_report_file_exits_cleanly(tmp_path):
    report = tmp_path / "empty.md"
    report.write_text("")
    result = run_script([str(report)])
    assert result.returncode == 2
    assert "empty" in result.stdout.lower()


def test_target_words_with_tolerance():
    result = run_script([
        str(FIXTURES / "good_report.md"),
        "--target-words", "165", "--tolerance", "5",
    ])
    assert result.returncode == 0, result.stdout
