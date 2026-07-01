"""Tests for the backlink-analysis skill's scripts/score_backlinks.py."""

import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SKILL_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / ".claude"
    / "skills"
    / "backlink-analysis"
    / "scripts"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "score_backlinks", SKILL_SCRIPTS_DIR / "score_backlinks.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def sb():
    return _load_module()


def test_high_risk_domain_flagged(sb):
    records = [
        {
            "domain": "spamlinks.shop",
            "domain_authority": "3",
            "follow": "true",
            "anchor_text": "buy backlinks cheap",
            "is_spam": "true",
            "links_to_target": "50",
        }
    ]
    scored = sb.score_backlinks(records)
    assert len(scored) == 1
    row = scored[0]
    assert row["domain"] == "spamlinks.shop"
    assert row["risk_band"] == "HIGH"
    assert "marked_spam" in row["toxic_flags"]
    assert "low_domain_authority" in row["toxic_flags"]
    assert "link_farm_tld" in row["toxic_flags"]
    assert "link_selling_anchor_text" in row["toxic_flags"]
    assert row["quality_score"] < 20


def test_low_risk_high_authority_domain(sb):
    records = [
        {
            "domain": "forbes.com",
            "domain_authority": "95",
            "follow": "true",
            "anchor_text": "our platform",
            "is_spam": "false",
            "links_to_target": "1",
        }
    ]
    scored = sb.score_backlinks(records)
    row = scored[0]
    assert row["risk_band"] == "LOW"
    assert row["toxic_flags"] == []
    assert row["quality_score"] == 95.0


def test_medium_risk_high_volume_no_spam_markers(sb):
    # A mostly-nofollow, non-spam, high-authority domain with a very large
    # links_to_target count (e.g. a sitewide footer/partner badge) should be
    # MEDIUM: high volume but none of the HIGH-risk toxic signals fire
    # (not near-all-dofollow, not spam, not low-DA, not a link-farm TLD,
    # no link-selling anchors).
    records = [
        {
            "domain": "partner-network.com",
            "domain_authority": "40",
            "follow": "false",
            "anchor_text": f"partner link {i}",
            "is_spam": "false",
            "links_to_target": "1",
        }
        for i in range(3)
    ]
    # Simulate one row carrying the full links_to_target count (as an export might).
    records[0]["links_to_target"] = "15000"
    records[1]["links_to_target"] = "0"
    records[2]["links_to_target"] = "0"
    scored = sb.score_backlinks(records)
    row = scored[0]
    assert row["toxic_flags"] == []
    assert row["risk_band"] == "MEDIUM"


def test_exact_match_anchor_over_optimization_flagged(sb):
    records = [
        {
            "domain": "seo-farm.net",
            "domain_authority": "25",
            "follow": "true",
            "anchor_text": "best cheap widgets online",
            "is_spam": "false",
            "links_to_target": "1",
        }
        for _ in range(5)
    ]
    scored = sb.score_backlinks(records)
    row = scored[0]
    flags = " ".join(row["toxic_flags"])
    assert "exact_match_anchor_over_optimization" in flags


def test_generic_and_brand_anchors_not_flagged_as_over_optimized(sb):
    records = [
        {"domain": "brandsite.com", "domain_authority": "60", "follow": "true", "anchor_text": a, "is_spam": "false", "links_to_target": "1"}
        for a in ["click here", "read more", "https://target.com", "BrandName", "our tool"]
    ]
    scored = sb.score_backlinks(records)
    row = scored[0]
    assert not any("over_optimization" in f for f in row["toxic_flags"])


def test_domains_aggregated_and_sorted_by_quality_score_desc(sb):
    records = [
        {"domain": "low.shop", "domain_authority": "5", "follow": "true", "anchor_text": "buy backlinks", "is_spam": "true", "links_to_target": "1"},
        {"domain": "high.com", "domain_authority": "80", "follow": "false", "anchor_text": "resource", "is_spam": "false", "links_to_target": "1"},
        {"domain": "mid.com", "domain_authority": "40", "follow": "true", "anchor_text": "check this out", "is_spam": "false", "links_to_target": "1"},
    ]
    scored = sb.score_backlinks(records)
    scores = [row["quality_score"] for row in scored]
    assert scores == sorted(scores, reverse=True)
    assert scored[0]["domain"] == "high.com"


def test_multiple_rows_same_domain_are_aggregated(sb):
    records = [
        {"domain": "example.com", "domain_authority": "50", "follow": "true", "anchor_text": "a", "is_spam": "false", "links_to_target": "1"},
        {"domain": "example.com", "domain_authority": "50", "follow": "false", "anchor_text": "b", "is_spam": "false", "links_to_target": "1"},
    ]
    scored = sb.score_backlinks(records)
    assert len(scored) == 1
    assert scored[0]["link_count"] == 2
    assert scored[0]["dofollow_count"] == 1


def test_empty_input_returns_empty_list(sb):
    assert sb.score_backlinks([]) == []


def test_missing_fields_do_not_crash(sb):
    records = [{"domain": "sparse.com"}]
    scored = sb.score_backlinks(records)
    assert len(scored) == 1
    assert scored[0]["domain_authority"] == 0.0
    assert scored[0]["risk_band"] in ("LOW", "MEDIUM", "HIGH")


def test_rows_missing_domain_are_skipped(sb):
    records = [{"domain": "", "domain_authority": "50"}, {"domain_authority": "50"}]
    scored = sb.score_backlinks(records)
    assert scored == []


def test_load_records_from_csv(tmp_path, sb):
    csv_path = tmp_path / "backlinks.csv"
    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["domain", "domain_authority", "follow", "anchor_text", "is_spam", "links_to_target"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "domain": "example.org",
                "domain_authority": "70",
                "follow": "true",
                "anchor_text": "great resource",
                "is_spam": "false",
                "links_to_target": "2",
            }
        )
    records = sb.load_records(str(csv_path))
    scored = sb.score_backlinks(records)
    assert scored[0]["domain"] == "example.org"


def test_cli_writes_json_output(tmp_path, sb):
    csv_path = tmp_path / "backlinks.csv"
    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["domain", "domain_authority", "follow", "anchor_text"])
        writer.writeheader()
        writer.writerow({"domain": "example.com", "domain_authority": "60", "follow": "true", "anchor_text": "resource"})
    out_path = tmp_path / "out.json"
    rc = sb.main([str(csv_path), "--output", str(out_path), "--format", "json"])
    assert rc == 0
    data = json.loads(out_path.read_text())
    assert data[0]["domain"] == "example.com"


def test_cli_writes_csv_output(tmp_path, sb):
    csv_path = tmp_path / "backlinks.csv"
    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["domain", "domain_authority", "follow", "anchor_text"])
        writer.writeheader()
        writer.writerow({"domain": "example.com", "domain_authority": "60", "follow": "true", "anchor_text": "resource"})
    out_path = tmp_path / "out.csv"
    rc = sb.main([str(csv_path), "--output", str(out_path), "--format", "csv"])
    assert rc == 0
    with open(out_path) as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["domain"] == "example.com"
