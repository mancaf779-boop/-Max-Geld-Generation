#!/usr/bin/env python3
"""
score_backlinks.py

Formalizes the backlink-analysis skill's Step 2.3 (risk scoring) and Step 2.4
(anchor classification / toxic-pattern detection) rules from SKILL.md and
references/writing_rules.md into a reusable, testable transform.

Input: a list of backlink records (dicts) or a CSV file with (at minimum)
the columns:
    domain              - referring domain (str)
    domain_authority    - Ahrefs DR / Semrush AS / equivalent (0-100, numeric)
    follow              - truthy/"dofollow" or falsy/"nofollow"
    anchor_text         - the anchor text used in the link
    is_spam             - optional bool, defaults to False if absent
    links_to_target     - optional int, total links from this domain to target

Output: one row per unique domain with:
    domain, domain_authority, link_count, dofollow_count, quality_score,
    risk_band (HIGH/MEDIUM/LOW), toxic_flags (list of flag strings)

Scoring heuristics (derived from SKILL.md Step 2.3/2.4 and writing_rules.md):
  - HIGH risk when 2+ of: is_spam true; DR < 10; near-all dofollow with high
    links_to_target; link-network TLD (.shop/.site/.space/.top/.cloud);
    link-selling anchor text (e.g. "buy backlinks", "seo links", telegram handle).
  - MEDIUM risk when links_to_target > 10,000 with no spam markers (sitewide/
    owned/partner placement needing ownership confirmation, not removal).
  - Exact-match / topical anchor over-optimization is flagged separately when
    a single domain's anchors are dominated (>= 60%) by the same non-brand,
    non-generic anchor text -- this is the "over-optimization" signal from
    Step 2.4 / the Executive Summary decision rules (topical anchor share > 15%).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from typing import Any, Iterable

LINK_FARM_TLDS = (".shop", ".site", ".space", ".top", ".cloud")

LINK_SELLING_PATTERNS = (
    re.compile(r"\bbuy\s+backlinks?\b", re.I),
    re.compile(r"\bseo\s+links?\b", re.I),
    re.compile(r"\bcheap\s+links?\b", re.I),
    re.compile(r"\bguest\s+post\s+service\b", re.I),
    re.compile(r"t\.me/\w+", re.I),  # Telegram handle
    re.compile(r"@\w+.*telegram", re.I),
)

GENERIC_ANCHOR_PATTERNS = (
    re.compile(r"^\s*click here\s*$", re.I),
    re.compile(r"^\s*read more\s*$", re.I),
    re.compile(r"^\s*here\s*$", re.I),
    re.compile(r"^\s*website\s*$", re.I),
    re.compile(r"^https?://", re.I),
    re.compile(r"^\s*$"),
)

HIGH_VOLUME_THRESHOLD = 10_000
LOW_DA_THRESHOLD = 10
OVER_OPTIMIZATION_SHARE = 0.60  # single anchor dominates >=60% of a domain's anchors


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in ("true", "1", "yes", "dofollow", "follow", "y")


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _is_link_farm_tld(domain: str) -> bool:
    domain = (domain or "").lower()
    return any(domain.endswith(tld) for tld in LINK_FARM_TLDS)


def _is_link_selling_anchor(anchor: str) -> bool:
    anchor = anchor or ""
    return any(pattern.search(anchor) for pattern in LINK_SELLING_PATTERNS)


def _is_generic_anchor(anchor: str) -> bool:
    anchor = anchor or ""
    return any(pattern.match(anchor) for pattern in GENERIC_ANCHOR_PATTERNS)


def load_records(path: str) -> list[dict]:
    """Load backlink records from a CSV file."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _aggregate_by_domain(records: Iterable[dict]) -> dict[str, dict]:
    """Group raw backlink rows by referring domain."""
    domains: dict[str, dict] = {}
    for row in records:
        domain = (row.get("domain") or row.get("referring_domain") or "").strip()
        if not domain:
            continue
        bucket = domains.setdefault(
            domain,
            {
                "domain": domain,
                "domain_authority": _to_float(row.get("domain_authority") or row.get("domain_rating")),
                "is_spam": False,
                "link_count": 0,
                "dofollow_count": 0,
                "links_to_target": 0,
                "anchors": [],
            },
        )
        # Keep the max DA seen for the domain (exports are sometimes inconsistent per row).
        da = _to_float(row.get("domain_authority") or row.get("domain_rating"))
        bucket["domain_authority"] = max(bucket["domain_authority"], da)
        bucket["is_spam"] = bucket["is_spam"] or _to_bool(row.get("is_spam"))
        bucket["link_count"] += 1
        if _to_bool(row.get("follow", row.get("dofollow", True))):
            bucket["dofollow_count"] += 1
        bucket["links_to_target"] += _to_int(row.get("links_to_target"), default=1)
        anchor = row.get("anchor_text") or row.get("anchor") or ""
        bucket["anchors"].append(anchor)
    return domains


def _classify_anchor_over_optimization(anchors: list[str]) -> tuple[bool, str | None, float]:
    """Return (flagged, dominant_anchor, share) for exact-match over-optimization."""
    non_generic = [a.strip() for a in anchors if a and not _is_generic_anchor(a)]
    if not non_generic:
        return False, None, 0.0
    counts: dict[str, int] = defaultdict(int)
    for a in non_generic:
        counts[a.lower()] += 1
    dominant_anchor, count = max(counts.items(), key=lambda kv: kv[1])
    share = count / len(anchors) if anchors else 0.0
    flagged = share >= OVER_OPTIMIZATION_SHARE and len(anchors) >= 3
    return flagged, dominant_anchor, share


def score_domain(bucket: dict) -> dict:
    """Apply the Step 2.3 / 2.4 scoring rules to one aggregated domain record."""
    domain = bucket["domain"]
    da = bucket["domain_authority"]
    link_count = bucket["link_count"]
    dofollow_count = bucket["dofollow_count"]
    links_to_target = bucket["links_to_target"]
    anchors = bucket["anchors"]

    dofollow_ratio = (dofollow_count / link_count) if link_count else 0.0

    toxic_flags: list[str] = []

    high_signals = 0

    if bucket["is_spam"]:
        toxic_flags.append("marked_spam")
        high_signals += 1

    if da < LOW_DA_THRESHOLD:
        toxic_flags.append("low_domain_authority")
        high_signals += 1

    if dofollow_ratio >= 0.95 and links_to_target >= 20:
        toxic_flags.append("near_all_dofollow_high_volume")
        high_signals += 1

    if _is_link_farm_tld(domain):
        toxic_flags.append("link_farm_tld")
        high_signals += 1

    if any(_is_link_selling_anchor(a) for a in anchors):
        toxic_flags.append("link_selling_anchor_text")
        high_signals += 1

    over_optimized, dominant_anchor, anchor_share = _classify_anchor_over_optimization(anchors)
    if over_optimized:
        toxic_flags.append(
            f"exact_match_anchor_over_optimization ({dominant_anchor!r} = {anchor_share:.0%})"
        )

    is_medium_volume = links_to_target > HIGH_VOLUME_THRESHOLD and high_signals == 0

    if high_signals >= 2:
        risk_band = "HIGH"
    elif is_medium_volume:
        risk_band = "MEDIUM"
    else:
        risk_band = "LOW"

    # Quality score: starts at DA (0-100 scale), penalized by toxic signals,
    # rewarded slightly for a healthy dofollow/nofollow mix (all-dofollow at
    # very high volume is itself a signal, handled above).
    score = da
    score -= 15 * high_signals
    if over_optimized:
        score -= 10
    score = max(0.0, min(100.0, score))

    return {
        "domain": domain,
        "domain_authority": da,
        "link_count": link_count,
        "dofollow_count": dofollow_count,
        "links_to_target": links_to_target,
        "quality_score": round(score, 1),
        "risk_band": risk_band,
        "toxic_flags": toxic_flags,
    }


def score_backlinks(records: Iterable[dict]) -> list[dict]:
    """
    Score a collection of raw backlink rows (dicts), returning one ranked
    row per unique referring domain, sorted by quality_score descending.
    """
    domains = _aggregate_by_domain(records)
    scored = [score_domain(bucket) for bucket in domains.values()]
    scored.sort(key=lambda r: (-r["quality_score"], r["domain"]))
    return scored


def write_output(scored: list[dict], path: str, fmt: str) -> None:
    if fmt == "json":
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(scored, fh, indent=2)
    elif fmt == "csv":
        fieldnames = [
            "domain",
            "domain_authority",
            "link_count",
            "dofollow_count",
            "links_to_target",
            "quality_score",
            "risk_band",
            "toxic_flags",
        ]
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for row in scored:
                out_row = dict(row)
                out_row["toxic_flags"] = ";".join(row["toxic_flags"])
                writer.writerow(out_row)
    else:
        raise ValueError(f"Unsupported format: {fmt}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score backlink records for quality/toxicity.")
    parser.add_argument("input_csv", help="Path to a CSV export of backlink records.")
    parser.add_argument("--output", "-o", help="Path to write scored output.")
    parser.add_argument("--format", "-f", choices=["json", "csv"], default="json")
    args = parser.parse_args(argv)

    records = load_records(args.input_csv)
    scored = score_backlinks(records)

    if args.output:
        write_output(scored, args.output, args.format)
        print(f"Wrote {len(scored)} scored domains to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(scored, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
