import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / ".claude" / "skills" / "tts-prompter" / "scripts" / "narration_budget.py"


@pytest.fixture(scope="module")
def nb():
    spec = importlib.util.spec_from_file_location("narration_budget", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["narration_budget"] = module
    spec.loader.exec_module(module)
    return module


def test_catalog_loads_and_has_expected_entries(nb):
    catalog = nb.load_catalog()
    assert len(catalog) > 50
    assert catalog["en-US"] == ("words", 2.1)
    assert catalog["ja-JP"] == ("chars", 4.2)
    assert catalog["th-TH"] == ("chars", 7.2)


def test_unknown_language_raises(nb):
    with pytest.raises(nb.UnknownLanguageError):
        nb.max_text_units("xx-XX", 10)


class TestCountUnits:
    def test_words(self, nb):
        assert nb.count_units("this is four words", "words") == 4

    def test_chars_ignores_whitespace(self, nb):
        assert nb.count_units("私 たち は", "chars") == 4

    def test_unknown_unit_raises(self, nb):
        with pytest.raises(ValueError):
            nb.count_units("text", "syllables")


class TestMaxTextUnits:
    def test_matches_formula(self, nb):
        # en-US: words, rate 2.1
        result = nb.max_text_units("en-US", 10, safety=0.85)
        assert result == pytest.approx(2.1 * 10 * 0.85)

    def test_default_safety_factor(self, nb):
        result = nb.max_text_units("en-US", 10)
        assert result == pytest.approx(2.1 * 10 * nb.DEFAULT_SAFETY_FACTOR)

    def test_negative_budget_raises(self, nb):
        with pytest.raises(ValueError):
            nb.max_text_units("en-US", -5)

    def test_zero_budget_gives_zero(self, nb):
        assert nb.max_text_units("en-US", 0) == 0


class TestFits:
    def test_short_text_fits(self, nb):
        assert nb.fits("en-US", 10, "just a few words here") is True

    def test_long_text_does_not_fit(self, nb):
        long_text = " ".join(["word"] * 100)
        assert nb.fits("en-US", 5, long_text) is False


class TestReconcile:
    def test_under_budget(self, nb):
        result = nb.reconcile(9, 10)
        assert result["action"] == "extend_with_held_frame"

    def test_within_tolerance(self, nb):
        result = nb.reconcile(10.3, 10)
        assert result["action"] == "none"

    def test_boundary_at_5_percent_is_none(self, nb):
        result = nb.reconcile(10.5, 10)
        assert result["action"] == "none"

    def test_moderate_overrun_trims_then_atempo(self, nb):
        result = nb.reconcile(11, 10)
        assert result["action"] == "trim_silence_then_atempo"

    def test_large_overrun_regenerates(self, nb):
        result = nb.reconcile(11.5, 10)
        assert result["action"] == "regenerate"

    def test_extreme_overrun_rewrites(self, nb):
        result = nb.reconcile(13, 10)
        assert result["action"] == "rewrite_shorter"

    def test_zero_budget_raises(self, nb):
        with pytest.raises(ValueError):
            nb.reconcile(5, 0)


def test_cli_max_units(nb, capsys):
    sys.argv = ["narration_budget.py", "max-units", "en-US", "10"]
    nb.main()
    out = capsys.readouterr().out.strip()
    assert float(out) == pytest.approx(2.1 * 10 * 0.85, abs=0.05)


def test_cli_unknown_language_exits_nonzero(nb):
    sys.argv = ["narration_budget.py", "max-units", "xx-XX", "10"]
    with pytest.raises(SystemExit) as exc_info:
        nb.main()
    assert exc_info.value.code == 1
