import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / ".claude" / "skills" / "video-generator" / "scripts" / "clip_plan_validator.py"


@pytest.fixture(scope="module")
def cpv():
    spec = importlib.util.spec_from_file_location("clip_plan_validator", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["clip_plan_validator"] = module
    spec.loader.exec_module(module)
    return module


class TestValidateClipPlan:
    def test_empty_plan_is_ok(self, cpv):
        ok, messages = cpv.validate_clip_plan([])
        assert ok is True

    def test_simple_valid_plan(self, cpv):
        clips = [
            {"duration": 4, "inter_clip_boundary": "scene_cut", "first_keyframe_reuse": "no", "last_keyframe_required": "no"},
            {"duration": 6, "inter_clip_boundary": "scene_cut", "first_keyframe_reuse": "no", "last_keyframe_required": "no"},
        ]
        ok, messages = cpv.validate_clip_plan(clips)
        assert ok is True

    def test_invalid_duration_rejected(self, cpv):
        clips = [{"duration": 5, "inter_clip_boundary": "scene_cut", "first_keyframe_reuse": "no", "last_keyframe_required": "no"}]
        ok, messages = cpv.validate_clip_plan(clips)
        assert ok is False
        assert any("duration" in m for m in messages)

    def test_continuous_boundary_requires_next_reuse(self, cpv):
        clips = [
            {"duration": 4, "inter_clip_boundary": "continuous", "first_keyframe_reuse": "no", "last_keyframe_required": "yes"},
            {"duration": 4, "inter_clip_boundary": "scene_cut", "first_keyframe_reuse": "no", "last_keyframe_required": "no"},
        ]
        ok, messages = cpv.validate_clip_plan(clips)
        assert ok is False
        assert any("requires clip 1" in m for m in messages)

    def test_continuous_boundary_satisfied(self, cpv):
        clips = [
            {"duration": 4, "inter_clip_boundary": "continuous", "first_keyframe_reuse": "no", "last_keyframe_required": "yes"},
            {"duration": 4, "inter_clip_boundary": "scene_cut", "first_keyframe_reuse": "yes", "last_keyframe_required": "no"},
        ]
        ok, messages = cpv.validate_clip_plan(clips)
        assert ok is True

    def test_continuous_boundary_on_last_clip_fails(self, cpv):
        clips = [{"duration": 4, "inter_clip_boundary": "continuous", "first_keyframe_reuse": "no", "last_keyframe_required": "no"}]
        ok, messages = cpv.validate_clip_plan(clips)
        assert ok is False
        assert any("last clip" in m for m in messages)

    def test_first_keyframe_reuse_on_first_clip_fails(self, cpv):
        clips = [{"duration": 4, "inter_clip_boundary": "scene_cut", "first_keyframe_reuse": "yes", "last_keyframe_required": "no"}]
        ok, messages = cpv.validate_clip_plan(clips)
        assert ok is False
        assert any("no previous clip" in m for m in messages)

    def test_first_keyframe_reuse_requires_prev_last_keyframe(self, cpv):
        clips = [
            {"duration": 4, "inter_clip_boundary": "scene_cut", "first_keyframe_reuse": "no", "last_keyframe_required": "no"},
            {"duration": 4, "inter_clip_boundary": "scene_cut", "first_keyframe_reuse": "yes", "last_keyframe_required": "no"},
        ]
        ok, messages = cpv.validate_clip_plan(clips)
        assert ok is False
        assert any("requires clip 0" in m for m in messages)


class TestBuildEmotionalArc:
    def test_merges_identical_consecutive_cues(self, cpv):
        clips = [
            {"duration": 4, "bgm_cue": "sparse/calm"},
            {"duration": 4, "bgm_cue": "sparse/calm"},
            {"duration": 6, "bgm_cue": "full/energetic"},
        ]
        rows = cpv.build_emotional_arc(clips)
        assert rows == [
            {"start": 0, "end": 8, "bgm_cue": "sparse/calm"},
            {"start": 8, "end": 14, "bgm_cue": "full/energetic"},
        ]

    def test_no_merge_when_cues_differ(self, cpv):
        clips = [
            {"duration": 4, "bgm_cue": "a"},
            {"duration": 4, "bgm_cue": "b"},
        ]
        rows = cpv.build_emotional_arc(clips)
        assert len(rows) == 2

    def test_empty_clips_gives_empty_arc(self, cpv):
        assert cpv.build_emotional_arc([]) == []

    def test_format_table_contains_timestamps(self, cpv):
        rows = cpv.build_emotional_arc([{"duration": 70, "bgm_cue": "x"}])
        table = cpv.format_emotional_arc_table(rows)
        assert "00:00" in table
        assert "01:10" in table


def test_cli_validate_success(cpv, tmp_path, capsys):
    clips_file = tmp_path / "clips.json"
    clips_file.write_text(json.dumps([
        {"duration": 4, "inter_clip_boundary": "scene_cut", "first_keyframe_reuse": "no", "last_keyframe_required": "no"},
    ]))
    sys.argv = ["clip_plan_validator.py", "validate", str(clips_file)]
    with pytest.raises(SystemExit) as exc_info:
        cpv.main()
    assert exc_info.value.code == 0


def test_cli_validate_failure_exits_nonzero(cpv, tmp_path):
    clips_file = tmp_path / "clips.json"
    clips_file.write_text(json.dumps([{"duration": 5}]))
    sys.argv = ["clip_plan_validator.py", "validate", str(clips_file)]
    with pytest.raises(SystemExit) as exc_info:
        cpv.main()
    assert exc_info.value.code == 1


def test_cli_missing_file_exits_nonzero(cpv, tmp_path):
    sys.argv = ["clip_plan_validator.py", "validate", str(tmp_path / "missing.json")]
    with pytest.raises(SystemExit) as exc_info:
        cpv.main()
    assert exc_info.value.code == 1
