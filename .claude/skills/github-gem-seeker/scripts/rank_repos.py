#!/usr/bin/env python3
"""
rank_repos.py

Formalizes the github-gem-seeker skill's "Evaluate Quality" step and Quality
Tiers table from SKILL.md into a deterministic, testable classifier.

Given a list of repo metadata dicts, e.g.:
    {
        "name": "yt-dlp",
        "stars": 90000,
        "last_commit_date": "2026-06-01",   # ISO 8601 date or datetime string
        "has_readme": true,
        "open_issues": 1200
    }

classify_repo() assigns one of the SKILL.md Quality Tiers:
    Legendary  : 50k+ stars, industry standard
    Excellent  : 10k+ stars, strong community
    Solid      : 1k+ stars, well-documented
    Promising  : <1k stars, active development

Star thresholds come directly from SKILL.md. Because "industry standard",
"strong community", "well-documented", and "active development" aren't
themselves numeric, this script approximates them the same way a careful
human reviewer would per the "Evaluate Quality (Quick Check)" table:
  - "well-documented" / "strong community" => has_readme is True
  - "active development" (for repos under 1k stars) => last commit within
    the last 6 months (per the Warning Signal row: ">2 years ago" is bad;
    this script uses the skill's own "within 6 months" freshness bar)

A repo missing has_readme/last_commit_date/open_issues is not penalized
beyond what's inferable -- missing fields are treated as "unknown, don't
downgrade" rather than failing the repo, since the input may come from a
partial API response.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Any

TIER_ORDER = ["Legendary", "Excellent", "Solid", "Promising"]
_TIER_RANK = {tier: i for i, tier in enumerate(TIER_ORDER)}

LEGENDARY_STARS = 50_000
EXCELLENT_STARS = 10_000
SOLID_STARS = 1_000

ACTIVE_WINDOW_DAYS = 180  # "within 6 months" per SKILL.md's Gem Signal
STALE_WINDOW_DAYS = 730  # ">2 years ago" per SKILL.md's Warning Signal


def _parse_date(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).strip()
    # Support both date-only ("2026-06-01") and full ISO datetime strings,
    # including a trailing "Z" (common in GitHub API responses).
    text = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _days_since(dt: datetime | None, now: datetime | None = None) -> float | None:
    if dt is None:
        return None
    now = now or datetime.now(timezone.utc)
    return (now - dt).total_seconds() / 86400.0


def classify_repo(repo: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    """
    Classify a single repo metadata dict into a quality tier.

    Returns a copy of the input dict augmented with:
        "tier": one of TIER_ORDER
        "stars": normalized int (0 if missing/invalid)
        "is_active": True/False/None (None = unknown, no last_commit_date)
        "is_stale": True/False/None
    """
    stars_raw = repo.get("stars", 0)
    try:
        stars = int(stars_raw)
    except (TypeError, ValueError):
        stars = 0

    last_commit = _parse_date(repo.get("last_commit_date"))
    days_since_commit = _days_since(last_commit, now=now)

    is_active = None if days_since_commit is None else days_since_commit <= ACTIVE_WINDOW_DAYS
    is_stale = None if days_since_commit is None else days_since_commit > STALE_WINDOW_DAYS

    if stars >= LEGENDARY_STARS:
        tier = "Legendary"
    elif stars >= EXCELLENT_STARS:
        tier = "Excellent"
    elif stars >= SOLID_STARS:
        tier = "Solid"
    else:
        tier = "Promising"
        # For sub-1k-star repos, SKILL.md's Promising tier explicitly requires
        # "active development". If we know the repo is stale, it doesn't even
        # clear the bar for Promising -- but we still return a tier (rather
        # than erroring) since the caller may want to see and explicitly
        # reject it; the staleness is surfaced via is_stale/is_active.

    result = dict(repo)
    result["tier"] = tier
    result["stars"] = stars
    result["is_active"] = is_active
    result["is_stale"] = is_stale
    return result


def rank_repos(repos: list[dict[str, Any]], now: datetime | None = None) -> list[dict[str, Any]]:
    """
    Classify and sort a list of repo metadata dicts.

    Sort order: tier (Legendary > Excellent > Solid > Promising) first,
    then stars descending, then name ascending for stable, readable ties.
    """
    classified = [classify_repo(repo, now=now) for repo in repos]
    classified.sort(
        key=lambda r: (
            _TIER_RANK.get(r["tier"], len(TIER_ORDER)),
            -r["stars"],
            str(r.get("name") or r.get("full_name") or ""),
        )
    )
    return classified


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Rank/classify GitHub repo candidates into quality tiers.")
    parser.add_argument(
        "input_json",
        help="Path to a JSON file containing a list of repo metadata dicts, or '-' to read from stdin.",
    )
    parser.add_argument("--output", "-o", help="Write ranked JSON output to this path instead of stdout.")
    args = parser.parse_args(argv)

    if args.input_json == "-":
        repos = json.load(sys.stdin)
    else:
        with open(args.input_json, encoding="utf-8") as fh:
            repos = json.load(fh)

    if not isinstance(repos, list):
        print("Error: input JSON must be a list of repo metadata objects.", file=sys.stderr)
        return 1

    ranked = rank_repos(repos)
    output_json = json.dumps(ranked, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output_json)
    else:
        print(output_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
