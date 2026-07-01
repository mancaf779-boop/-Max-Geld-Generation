"""Tests for the youtube-video-research skill's scripts/build_research_brief.py."""

import importlib.util
from pathlib import Path

import pytest

SKILL_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / ".claude"
    / "skills"
    / "youtube-video-research"
    / "scripts"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "build_research_brief", SKILL_SCRIPTS_DIR / "build_research_brief.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def brb():
    return _load_module()


def test_company_brief_has_expected_themes(brb):
    brief = brb.build_research_brief("Stripe", research_type="company")
    theme_names = [t["theme"] for t in brief["themes"]]
    assert "Bull case & growth catalysts" in theme_names
    assert "Bear case & risk factors" in theme_names
    assert brief["bear_bull_balance_required"] is True


def test_person_brief_themes(brb):
    brief = brb.build_research_brief("Jane Doe", research_type="person")
    theme_names = [t["theme"] for t in brief["themes"]]
    assert "Career history" in theme_names
    assert brief["bear_bull_balance_required"] is False


def test_travel_brief_themes(brb):
    brief = brb.build_research_brief("Kyoto", research_type="travel")
    theme_names = [t["theme"] for t in brief["themes"]]
    assert any("Budget" in t for t in theme_names)


def test_generic_type_is_default(brb):
    brief = brb.build_research_brief("Quantum computing")
    assert brief["research_type"] == "generic"
    assert len(brief["themes"]) >= 4


def test_deep_depth_widens_target_video_count(brb):
    standard = brb.build_research_brief("Stripe", research_type="company", depth="standard")
    deep = brb.build_research_brief("Stripe", research_type="company", depth="deep")
    assert standard["target_video_count"]["max"] < deep["target_video_count"]["max"]
    assert deep["target_video_count"] == {"min": 12, "max": 20}
    assert standard["target_video_count"] == {"min": 8, "max": 12}


def test_query_variants_include_youtube_and_topic(brb):
    brief = brb.build_research_brief("Acme Corp", research_type="company")
    for theme in brief["themes"]:
        for variant in theme["query_variants"]:
            assert "YouTube" in variant
            assert "Acme Corp" in variant


def test_bear_case_theme_uses_critical_query_angle(brb):
    brief = brb.build_research_brief("Acme Corp", research_type="company")
    bear_theme = next(t for t in brief["themes"] if "Bear case" in t["theme"])
    joined = " ".join(bear_theme["query_variants"]).lower()
    assert "risk" in joined or "bearish" in joined or "criticism" in joined


def test_analysis_prompt_is_populated_with_topic(brb):
    brief = brb.build_research_brief("Acme Corp", research_type="company")
    assert "Acme Corp" in brief["analysis_prompt"]
    assert "DIRECT QUOTES" in brief["analysis_prompt"]


def test_analysis_prompt_differs_by_research_type(brb):
    company = brb.build_research_brief("X", research_type="company")
    travel = brb.build_research_brief("X", research_type="travel")
    assert company["analysis_prompt"] != travel["analysis_prompt"]
    assert company["analysis_prompt_template_key"] == "ceo_founder_interview"
    assert travel["analysis_prompt_template_key"] == "all_in_one_travel_vlog"


def test_empty_topic_raises(brb):
    with pytest.raises(ValueError):
        brb.build_research_brief("")


def test_whitespace_only_topic_raises(brb):
    with pytest.raises(ValueError):
        brb.build_research_brief("   ")


def test_unsupported_research_type_raises(brb):
    with pytest.raises(brb.UnsupportedResearchTypeError):
        brb.build_research_brief("Topic", research_type="astrology")


def test_unknown_depth_falls_back_to_standard(brb):
    brief = brb.build_research_brief("Topic", depth="extreme")
    assert brief["depth"] == "standard"


def test_topic_is_stripped_of_whitespace(brb):
    brief = brb.build_research_brief("  Stripe  ", research_type="company")
    assert brief["topic"] == "Stripe"


def test_cli_main_writes_json_file(tmp_path, brb):
    out = tmp_path / "brief.json"
    rc = brb.main(["Stripe", "--type", "company", "--output", str(out)])
    assert rc == 0
    import json

    data = json.loads(out.read_text())
    assert data["topic"] == "Stripe"


def test_cli_main_returns_nonzero_on_empty_topic(brb, capsys):
    rc = brb.main([""])
    assert rc == 1
