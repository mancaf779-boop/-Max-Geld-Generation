#!/usr/bin/env python3
"""
build_research_brief.py

Formalizes Step 1 (Theme-Based Video Discovery) of the youtube-video-research
skill into a deterministic transform: given a topic and a research type
(company/person/travel/generic), assemble a structured research brief
containing the themes to cover, per-theme query-variant patterns, the target
video count band, and the matching high-density analysis-prompt template
(pulled from the same catalog documented in references/prompt-templates.md).

This does not call any network/video-analysis tool. It is a pure, testable
function that produces the plan a researcher (human or agent) should follow,
per SKILL.md Step 1 and the domain reference docs
(company-research.md, person-research.md, travel-research.md).
"""

from __future__ import annotations

import json
from typing import Any

# Theme catalogs, mirroring SKILL.md's "Theme decomposition examples" table
# and the domain-specific reference docs.
THEMES_BY_TYPE: dict[str, list[str]] = {
    "company": [
        "Industry & macro context",
        "Business model & technology",
        "Financial health & valuation",
        "Customers & partnerships",
        "Bull case & growth catalysts",
        "Bear case & risk factors",
        "Leadership & culture",
    ],
    "person": [
        "Career history",
        "Leadership style",
        "Public controversies",
        "Vision & philosophy",
        "Peer assessments",
    ],
    "travel": [
        "Recent travel vlogs & overview",
        "Food & dining",
        "Budget & cost breakdown",
        "Itinerary & logistics",
        "Local tips & warnings",
        "Accommodation & transport",
    ],
    "generic": [
        "Background & context",
        "Core subject deep-dive",
        "Expert / practitioner perspectives",
        "Critical or opposing viewpoints",
        "Recent developments",
    ],
}

# Analysis-prompt template keys, matching references/prompt-templates.md section titles.
PROMPT_TEMPLATE_KEY_BY_TYPE: dict[str, str] = {
    "company": "ceo_founder_interview",
    "person": "interview_personality_profile",
    "travel": "all_in_one_travel_vlog",
    "generic": "maximum_detail_extraction",
}

PROMPT_TEMPLATES: dict[str, str] = {
    "maximum_detail_extraction": (
        "Extract MAXIMUM detail from this video about {topic}. For every claim the\n"
        "speaker makes, capture their near-exact wording as a direct quote in quotation\n"
        "marks. Include ALL numbers, dates, dollar amounts, percentages, company names,\n"
        "and person names mentioned.\n\n"
        "Structure output as:\n"
        "(A) SPEAKER PROFILE: Name, credentials, disclaimers, sponsors.\n"
        "(B) DIRECT QUOTES: At least 8 verbatim or near-verbatim quotes with topic labels.\n"
        "(C) ALL DATA POINTS: Every number, metric, date, name as a numbered list.\n"
        "(D) KEY ARGUMENTS: Main thesis broken into sub-arguments with supporting quotes.\n"
        "(E) COUNTER-ARGUMENTS / RISKS: Every risk, caveat, or opposing view with quotes.\n"
        "(F) SENTIMENT: Overall stance rating and confidence level.\n\n"
        "Be exhaustive. Length is not a concern — information density is.\n"
        "Do not summarize when you can quote directly."
    ),
    "ceo_founder_interview": (
        "Extract MAXIMUM detail from this interview with the CEO/founder of {topic}.\n"
        "For every strategic claim, capture their near-exact wording as a direct quote.\n"
        "Include ALL numbers, dates, metrics, company names, and person names mentioned.\n\n"
        "Structure output as:\n"
        "(A) SPEAKER PROFILE: Name, title, background, communication style assessment.\n"
        "(B) DIRECT QUOTES: At least 8-10 near-verbatim quotes with topic labels covering:\n"
        "    strategy, metrics, competition, culture, predictions, and any evasive moments.\n"
        "(C) ALL DATA POINTS: Every number, metric, date, partnership, product name as a list.\n"
        "(D) STRATEGIC VISION: Main thesis with supporting quotes.\n"
        "(E) RISKS & RED FLAGS: Contradictions, vague answers, deflections, acknowledged challenges.\n"
        "(F) LEADERSHIP ASSESSMENT: Communication style (visionary/operational/defensive/candid).\n\n"
        "Be exhaustive. Length is not a concern — information density is.\n"
        "Do not summarize when you can quote directly."
    ),
    "interview_personality_profile": (
        "Extract MAXIMUM detail from this interview to build a profile of {topic}.\n"
        "Capture their near-exact wording for every significant statement.\n\n"
        "Structure output as:\n"
        "(A) SUBJECT PROFILE: Name, title, background, interview context.\n"
        "(B) DIRECT QUOTES: At least 8-10 near-verbatim quotes revealing beliefs, values, style.\n"
        "(C) CORE BELIEFS: Values and philosophy articulated, with supporting quotes.\n"
        "(D) PERSONAL ANECDOTES: Stories shared, lessons drawn, with quoted phrasing.\n"
        "(E) INFLUENCES: Mentors, books, experiences credited — with quotes.\n"
        "(F) COMMUNICATION STYLE: How they handle tough questions, humor, vulnerability.\n"
        "(G) AUTHENTICITY ASSESSMENT: Genuine vs. performed moments.\n\n"
        "Be exhaustive. Preserve the subject's voice and distinctive phrasing."
    ),
    "all_in_one_travel_vlog": (
        "Extract MAXIMUM practical detail from this travel vlog about {topic}.\n"
        "For every recommendation, capture the creator's near-exact wording as a quote.\n\n"
        "Structure output as:\n"
        "(A) CREATOR PROFILE: Name, travel style, audience, credibility signals.\n"
        "(B) PLACES VISITED: Name, location, description, creator's quote about each.\n"
        "(C) FOOD & DINING: Every restaurant/food spot with name, dishes, prices, creator's reaction quote.\n"
        "(D) TRANSPORT: Methods, costs, tips — with creator's exact advice quotes.\n"
        "(E) ACCOMMODATION: Details, prices, pros/cons with quotes.\n"
        "(F) BUDGET: Every cost mentioned as a numbered list. Calculate implied daily budget.\n"
        "(G) TIPS & WARNINGS: Practical advice with creator's exact phrasing.\n\n"
        "Be exhaustive. Include ALL prices, names, and locations mentioned."
    ),
}

# Target video-count bands, per SKILL.md ("12-20 videos for deep research, 8-12 for standard").
VIDEO_COUNT_BANDS = {
    "standard": {"videos_per_theme": "2-3", "total_min": 8, "total_max": 12},
    "deep": {"videos_per_theme": "2-3", "total_min": 12, "total_max": 20},
}

VALID_TYPES = tuple(THEMES_BY_TYPE.keys())


class UnsupportedResearchTypeError(ValueError):
    pass


def _query_variants(topic: str, theme: str, research_type: str) -> list[str]:
    """
    Build 2-3 query variant strings for a theme, following SKILL.md's query
    construction rules: always include "YouTube", vary content type, include
    the entity name.
    """
    theme_lower = theme.lower()
    if research_type == "company" and "bear" in theme_lower:
        return [
            f"{topic} risks concerns analysis YouTube",
            f"{topic} stock bearish case YouTube",
            f"{topic} problems criticism YouTube",
        ]
    if research_type == "company" and "bull" in theme_lower:
        return [
            f"{topic} growth catalysts bull case YouTube",
            f"{topic} CEO vision keynote YouTube",
        ]
    if research_type == "person":
        return [
            f"{topic} {theme_lower} interview YouTube",
            f"{topic} podcast appearance YouTube",
        ]
    if research_type == "travel":
        return [
            f"{topic} {theme_lower} YouTube",
            f"{topic} travel guide {theme_lower} YouTube",
        ]
    # company (non bull/bear themes) and generic
    return [
        f"{topic} {theme_lower} interview YouTube",
        f"{topic} {theme_lower} analysis YouTube",
        f"{topic} {theme_lower} deep dive YouTube",
    ]


def build_research_brief(
    topic: str,
    research_type: str = "generic",
    depth: str = "standard",
) -> dict[str, Any]:
    """
    Assemble a structured research brief for a YouTube-video research task.

    Args:
        topic: the entity/subject being researched (company name, person name,
            destination, or any topic string). Must be non-empty.
        research_type: one of "company", "person", "travel", "generic".
        depth: "standard" (8-12 videos) or "deep" (12-20 videos).

    Returns a dict with: topic, research_type, depth, themes (list of
    {theme, query_variants, videos_per_theme}), target_video_count
    ({min, max}), and analysis_prompt (the high-density prompt template with
    {topic} substituted in).

    Raises:
        ValueError: if topic is empty.
        UnsupportedResearchTypeError: if research_type is not recognized.
    """
    if not topic or not topic.strip():
        raise ValueError("topic is required")

    research_type = (research_type or "generic").strip().lower()
    if research_type not in VALID_TYPES:
        raise UnsupportedResearchTypeError(
            f"unsupported research_type: {research_type!r}. Valid types: {', '.join(VALID_TYPES)}"
        )

    depth = (depth or "standard").strip().lower()
    if depth not in VIDEO_COUNT_BANDS:
        depth = "standard"

    topic = topic.strip()
    themes = THEMES_BY_TYPE[research_type]

    theme_entries = []
    for theme in themes:
        theme_entries.append(
            {
                "theme": theme,
                "query_variants": _query_variants(topic, theme, research_type),
                "videos_per_theme": VIDEO_COUNT_BANDS[depth]["videos_per_theme"],
            }
        )

    prompt_key = PROMPT_TEMPLATE_KEY_BY_TYPE[research_type]
    analysis_prompt = PROMPT_TEMPLATES[prompt_key].format(topic=topic)

    band = VIDEO_COUNT_BANDS[depth]

    return {
        "topic": topic,
        "research_type": research_type,
        "depth": depth,
        "themes": theme_entries,
        "target_video_count": {"min": band["total_min"], "max": band["total_max"]},
        "bear_bull_balance_required": research_type == "company",
        "analysis_prompt_template_key": prompt_key,
        "analysis_prompt": analysis_prompt,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Build a YouTube video-research brief.")
    parser.add_argument("topic")
    parser.add_argument("--type", dest="research_type", default="generic", choices=VALID_TYPES)
    parser.add_argument("--depth", default="standard", choices=list(VIDEO_COUNT_BANDS.keys()))
    parser.add_argument("--output", "-o", help="Write JSON brief to this path instead of stdout.")
    args = parser.parse_args(argv)

    try:
        brief = build_research_brief(args.topic, research_type=args.research_type, depth=args.depth)
    except (ValueError, UnsupportedResearchTypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output_json = json.dumps(brief, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output_json)
    else:
        print(output_json)
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
