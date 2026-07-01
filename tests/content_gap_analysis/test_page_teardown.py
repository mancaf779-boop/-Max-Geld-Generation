"""Tests for scripts/page_teardown.py.

The HTML-analysis logic is exercised directly (no live network calls, per the
task's preference for real execution over mocking network-dependent code);
only the CLI usage/help path is exercised via subprocess.
"""
import subprocess
import sys

from . import conftest

SCRIPT = conftest.SKILL_SCRIPTS / "page_teardown.py"

sys.path.insert(0, str(conftest.SKILL_SCRIPTS))
import page_teardown as pt  # noqa: E402


SAMPLE_HTML = """
<html><head>
<script type="application/ld+json">
{"@type": "BlogPosting", "datePublished": "2024-01-01", "dateModified": "2024-06-01"}
</script>
</head>
<body>
<h1>Best AI Tools</h1>
<p>We tested these tools ourselves. Our team found them useful for our workflow.</p>
<h2>Section One</h2>
<table><tr><td>Tool</td><td>Price</td></tr></table>
<img src="a.png"><img src="b.png">
<div class="author">Written by Jane Doe</div>
<iframe src="https://youtube.com/embed/xyz"></iframe>
</body></html>
"""


def test_analyze_html_extracts_expected_signals():
    result = pt.analyze_html(SAMPLE_HTML, status=200)
    assert result["status"] == 200
    assert result["word_count"] > 0
    assert result["h2_count"] == 1
    assert result["table_count"] == 1
    assert result["image_count"] == 2
    assert result["has_video"] is True
    assert result["has_author_byline"] is True
    assert result["first_person_mentions"] >= 3
    assert "BlogPosting" in result["jsonld_types"]
    assert result["has_date_published"] is True
    assert result["has_date_modified"] is True


def test_analyze_html_no_signals_present():
    result = pt.analyze_html("<html><body><p>Nothing special here.</p></body></html>")
    assert result["h2_count"] == 0
    assert result["table_count"] == 0
    assert result["image_count"] == 0
    assert result["has_video"] is False
    assert result["has_author_byline"] is False
    assert result["jsonld_types"] == []
    assert result["has_date_published"] is False


def test_jsonld_types_handles_malformed_json_gracefully():
    html = '<script type="application/ld+json">{not valid json "@type": "FAQPage"</script>'
    types = pt.jsonld_types(html)
    assert "FAQPage" in types


def test_cli_help_exits_zero():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_cli_no_args_exits_nonzero():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0


def test_cli_unreachable_url_reports_failure_not_crash():
    # Use a URL that will fail fast (invalid scheme) rather than really hitting the network.
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "not-a-valid-url"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode != 0
    assert "FETCH FAILED" in result.stdout
