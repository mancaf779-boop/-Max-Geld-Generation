import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / ".claude" / "skills" / "music-prompter" / "scripts" / "multiclip_planner.py"


@pytest.fixture(scope="module")
def mp():
    spec = importlib.util.spec_from_file_location("multiclip_planner", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["multiclip_planner"] = module
    spec.loader.exec_module(module)
    return module


class TestPlanClips:
    def test_short_track_is_single_clip(self, mp):
        assert mp.plan_clips(60) == [60]

    def test_exactly_at_max_is_single_clip(self, mp):
        assert mp.plan_clips(180) == [180]

    def test_splits_long_track_into_even_chunks(self, mp):
        clips = mp.plan_clips(260)
        assert sum(clips) == 260
        assert all(c <= 180 for c in clips)
        assert len(clips) == 2
        assert max(clips) - min(clips) <= 1

    def test_splits_respect_custom_max_clip(self, mp):
        clips = mp.plan_clips(100, max_clip=30)
        assert sum(clips) == 100
        assert all(c <= 30 for c in clips)

    def test_zero_or_negative_duration_raises(self, mp):
        with pytest.raises(ValueError):
            mp.plan_clips(0)
        with pytest.raises(ValueError):
            mp.plan_clips(-10)

    def test_zero_max_clip_raises(self, mp):
        with pytest.raises(ValueError):
            mp.plan_clips(60, max_clip=0)


class TestCrossfadeDuration:
    def test_120_bpm_two_beats_is_one_second(self, mp):
        assert mp.crossfade_duration(120, beats=2) == pytest.approx(1.0)

    def test_default_beats_is_two(self, mp):
        assert mp.crossfade_duration(120) == pytest.approx(1.0)

    def test_60_bpm_one_beat_is_one_second(self, mp):
        assert mp.crossfade_duration(60, beats=1) == pytest.approx(1.0)

    def test_invalid_bpm_raises(self, mp):
        with pytest.raises(ValueError):
            mp.crossfade_duration(0)

    def test_invalid_beats_raises(self, mp):
        with pytest.raises(ValueError):
            mp.crossfade_duration(120, beats=0)


class TestParseTimestampSections:
    def test_extracts_sections_in_order(self, mp):
        text = "[0:00 - 0:12] Intro\n[0:12 - 0:24] Verse\n[0:24 - 1:00] Chorus"
        assert mp.parse_timestamp_sections(text) == [(0, 12), (12, 24), (24, 60)]

    def test_no_sections_returns_empty(self, mp):
        assert mp.parse_timestamp_sections("no timestamps here") == []


class TestValidateArrangement:
    def test_contiguous_matching_duration_passes(self, mp):
        text = "[0:00 - 0:12] Intro\n[0:12 - 0:36] Verse\n[0:36 - 1:00] Outro"
        ok, messages = mp.validate_arrangement(text, 60)
        assert ok is True

    def test_no_timestamps_passes_trivially(self, mp):
        ok, messages = mp.validate_arrangement("just a plain prompt, no cues", 60)
        assert ok is True

    def test_gap_between_sections_fails(self, mp):
        text = "[0:00 - 0:10] A\n[0:15 - 0:30] B"
        ok, messages = mp.validate_arrangement(text, 30)
        assert ok is False
        assert any("Gap/overlap" in m for m in messages)

    def test_does_not_start_at_zero_fails(self, mp):
        text = "[0:05 - 0:30] A"
        ok, messages = mp.validate_arrangement(text, 30)
        assert ok is False
        assert any("expected 0s" in m for m in messages)

    def test_final_timestamp_mismatch_fails(self, mp):
        text = "[0:00 - 0:30] A"
        ok, messages = mp.validate_arrangement(text, 45)
        assert ok is False
        assert any("declared duration is 45" in m for m in messages)

    def test_reads_from_file(self, mp, tmp_path):
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text("[0:00 - 1:00] Full track")
        # validate_arrangement itself takes text, not a path; the CLI resolves files.
        from multiclip_planner import _resolve_text_arg
        text = _resolve_text_arg(str(prompt_file))
        ok, _messages = mp.validate_arrangement(text, 60)
        assert ok is True


def test_cli_plan_clips(mp, capsys):
    sys.argv = ["multiclip_planner.py", "plan-clips", "260"]
    mp.main()
    out = capsys.readouterr().out.strip()
    values = [int(v) for v in out.split()]
    assert sum(values) == 260


def test_cli_validate_arrangement_exits_nonzero_on_failure(mp):
    sys.argv = ["multiclip_planner.py", "validate-arrangement", "[0:00 - 0:10] A", "20"]
    with pytest.raises(SystemExit) as exc_info:
        mp.main()
    assert exc_info.value.code == 1
