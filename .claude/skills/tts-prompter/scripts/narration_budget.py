#!/usr/bin/env python3
"""
Narration budget helper for the tts-prompter skill.

Sizes narration text against a fixed time budget (per Section 4 of SKILL.md)
and decides how to reconcile a measured overrun after TTS generation.

CLI usage:
    narration_budget.py max-units <language_code> <budget_seconds> [--safety 0.85]
    narration_budget.py count <text> --language-code <language_code>
    narration_budget.py fits <language_code> <budget_seconds> <text>
    narration_budget.py reconcile <actual_seconds> <budget_seconds>

Library usage:
    from narration_budget import load_catalog, max_text_units, count_units, fits, reconcile
"""

import argparse
import re
import sys
from pathlib import Path

DEFAULT_CATALOG_PATH = Path(__file__).resolve().parent.parent / "references" / "language_catalog.md"
DEFAULT_SAFETY_FACTOR = 0.85

_TABLE_ROW_RE = re.compile(
    r'^\|\s*(?P<language>[^|]+?)\s*\|\s*(?P<code>[\w-]+)\s*\|\s*(?P<unit>chars|words)\s*\|\s*(?P<rate>[\d.]+)\s*\|\s*$',
    re.MULTILINE,
)


class UnknownLanguageError(KeyError):
    pass


def load_catalog(path=None):
    """Parse the language catalog markdown table into {bcp47_code: (unit, rate)}."""
    path = Path(path) if path else DEFAULT_CATALOG_PATH
    text = path.read_text(encoding="utf-8")
    catalog = {}
    for match in _TABLE_ROW_RE.finditer(text):
        code = match.group("code")
        unit = match.group("unit")
        rate = float(match.group("rate"))
        catalog[code] = (unit, rate)
    return catalog


def _lookup(language_code, catalog=None):
    catalog = catalog if catalog is not None else load_catalog()
    if language_code not in catalog:
        raise UnknownLanguageError(f"Unknown language code: {language_code!r}")
    return catalog[language_code]


def count_units(text, unit):
    """Count units in text: non-whitespace characters for 'chars', tokens for 'words'."""
    if unit == "chars":
        return len(re.sub(r"\s+", "", text))
    if unit == "words":
        return len(text.split())
    raise ValueError(f"Unknown unit type: {unit!r}")


def max_text_units(language_code, budget_seconds, safety=DEFAULT_SAFETY_FACTOR, catalog=None):
    """Maximum number of units (chars or words) of narration that fit in budget_seconds."""
    if budget_seconds < 0:
        raise ValueError("budget_seconds must be non-negative")
    _unit, rate = _lookup(language_code, catalog)
    return rate * budget_seconds * safety


def fits(language_code, budget_seconds, text, safety=DEFAULT_SAFETY_FACTOR, catalog=None):
    """Whether text's unit count is within the budget for language_code."""
    unit, _rate = _lookup(language_code, catalog)
    limit = max_text_units(language_code, budget_seconds, safety=safety, catalog=catalog)
    return count_units(text, unit) <= limit


def reconcile(actual_seconds, budget_seconds):
    """
    Decide how to reconcile a measured narration duration against its budget,
    per the ladder in SKILL.md Section 4.

    Returns a dict: {"action": str, "overrun_pct": float, "detail": str}
    """
    if budget_seconds <= 0:
        raise ValueError("budget_seconds must be positive")

    overrun_pct = (actual_seconds - budget_seconds) / budget_seconds * 100

    if overrun_pct < 0:
        return {
            "action": "extend_with_held_frame",
            "overrun_pct": overrun_pct,
            "detail": "Narration is under budget; extend the clip with a brief held frame.",
        }
    if overrun_pct <= 5:
        return {
            "action": "none",
            "overrun_pct": overrun_pct,
            "detail": "Within tolerance; no action needed.",
        }
    if overrun_pct <= 12:
        return {
            "action": "trim_silence_then_atempo",
            "overrun_pct": overrun_pct,
            "detail": "Trim leading/trailing silence first; if still over, apply ffmpeg atempo <= 1.12x.",
        }
    if overrun_pct <= 20:
        return {
            "action": "regenerate",
            "overrun_pct": overrun_pct,
            "detail": "Regenerate once; TTS output duration varies between calls.",
        }
    return {
        "action": "rewrite_shorter",
        "overrun_pct": overrun_pct,
        "detail": "Overrun too large to fix in post; rewrite the narration text shorter and re-plan.",
    }


def _build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_max = sub.add_parser("max-units", help="Compute max narration units for a budget")
    p_max.add_argument("language_code")
    p_max.add_argument("budget_seconds", type=float)
    p_max.add_argument("--safety", type=float, default=DEFAULT_SAFETY_FACTOR)

    p_count = sub.add_parser("count", help="Count units in a piece of text")
    p_count.add_argument("text")
    p_count.add_argument("--language-code", required=True)

    p_fits = sub.add_parser("fits", help="Check whether text fits within a budget")
    p_fits.add_argument("language_code")
    p_fits.add_argument("budget_seconds", type=float)
    p_fits.add_argument("text")

    p_rec = sub.add_parser("reconcile", help="Decide reconciliation action for a measured duration")
    p_rec.add_argument("actual_seconds", type=float)
    p_rec.add_argument("budget_seconds", type=float)

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "max-units":
            print(f"{max_text_units(args.language_code, args.budget_seconds, safety=args.safety):.1f}")
        elif args.command == "count":
            unit, _rate = _lookup(args.language_code)
            print(count_units(args.text, unit))
        elif args.command == "fits":
            print("yes" if fits(args.language_code, args.budget_seconds, args.text) else "no")
        elif args.command == "reconcile":
            result = reconcile(args.actual_seconds, args.budget_seconds)
            print(f"{result['action']} (overrun {result['overrun_pct']:.1f}%): {result['detail']}")
    except (UnknownLanguageError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
