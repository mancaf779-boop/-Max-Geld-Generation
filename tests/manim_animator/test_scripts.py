"""Tests for the manim-animator skill's scripts.

manim and ffmpeg are not installed in this environment, so these tests
avoid actually rendering anything or shelling out to real binaries. They
cover:

  * Syntax / importability of every Python script in scripts/ and
    templates/.
  * Pure-Python helper functions (argument validation, path building,
    subtitle timestamp formatting/grouping, scene-name extraction) with
    subprocess and third-party imports (manim, cv2, openai) mocked or
    exercised only through their lazy-import wrappers.
  * finalize_video.sh and setup.sh: shell syntax checks plus
    argument-validation / usage behavior that does not require ffmpeg or
    manim to be installed.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "manim-animator"
SCRIPTS_DIR = SKILL_DIR / "scripts"
TEMPLATES_DIR = SKILL_DIR / "templates"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Structural sanity: the skill was installed where the harness expects it.
# ---------------------------------------------------------------------------

class TestSkillLayout:
    def test_skill_md_exists(self):
        assert (SKILL_DIR / "SKILL.md").exists()

    def test_expected_scripts_exist(self):
        for name in [
            "render_scenes.py",
            "extract_frames.py",
            "generate_subtitles.py",
            "finalize_video.sh",
            "setup.sh",
        ]:
            assert (SCRIPTS_DIR / name).exists(), name

    def test_quickstart_template_exists(self):
        assert (TEMPLATES_DIR / "quickstart.py").exists()

    def test_no_leftover_manus_references(self):
        """The skill was ported from a Manus-specific bundle; make sure the
        rename to be portable/Claude-Code-appropriate actually stuck."""
        for path in SKILL_DIR.rglob("*"):
            if path.is_dir():
                continue
            if path.name in ("LICENSE.txt",):
                continue  # third-party license text must stay verbatim
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert "manus" not in text.lower(), f"Manus reference left in {path}"
            assert "/home/ubuntu" not in text, f"hardcoded sandbox path left in {path}"


# ---------------------------------------------------------------------------
# Every Python script: valid syntax + importable.
# ---------------------------------------------------------------------------

PY_FILES = [
    SCRIPTS_DIR / "render_scenes.py",
    SCRIPTS_DIR / "extract_frames.py",
    SCRIPTS_DIR / "generate_subtitles.py",
    TEMPLATES_DIR / "quickstart.py",
]


class TestPythonSyntax:
    @pytest.mark.parametrize("path", PY_FILES, ids=lambda p: p.name)
    def test_valid_syntax(self, path):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    @pytest.mark.parametrize(
        "path", [p for p in PY_FILES if p.name != "quickstart.py"], ids=lambda p: p.name
    )
    def test_importable_without_manim_or_cv2_or_openai(self, path):
        """quickstart.py legitimately does `from manim import *` at module
        scope (it's a Manim scene file, not a driver script), so it is
        excluded here and exercised separately below. The three driver
        scripts must import cleanly even when manim/cv2/openai are absent,
        since none of them should need those packages just to parse CLI
        args or run their pure-Python helpers."""
        # Ensure a clean re-import each time.
        mod_name = f"_manim_animator_import_check_{path.stem}"
        sys.modules.pop(mod_name, None)
        module = _load_module(mod_name, path)
        assert isinstance(module, types.ModuleType)

    def test_quickstart_requires_manim_at_module_scope(self):
        """quickstart.py is a Manim scene file: it's expected (and
        documented in write_system.md rule 8) to import manim at the top
        of the file. Confirm that's still true so we don't accidentally
        silently break the "imports at top" hard rule."""
        tree = ast.parse((TEMPLATES_DIR / "quickstart.py").read_text())
        top_level_imports = [
            node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        assert any(
            isinstance(node, ast.ImportFrom) and node.module == "manim"
            for node in top_level_imports
        )


# ---------------------------------------------------------------------------
# render_scenes.py: extract_scene_class_names + argument validation.
# ---------------------------------------------------------------------------

@pytest.fixture()
def render_scenes_mod():
    return _load_module("render_scenes", SCRIPTS_DIR / "render_scenes.py")


class TestExtractSceneClassNames:
    def test_finds_scene_subclasses(self, render_scenes_mod):
        src = (
            "from manim import *\n"
            "class Intro(Scene):\n"
            "    def construct(self):\n"
            "        pass\n"
            "class Helper:\n"
            "    pass\n"
            "class ThreeD(ThreeDScene):\n"
            "    def construct(self):\n"
            "        pass\n"
        )
        names = render_scenes_mod.extract_scene_class_names(src)
        assert names == ["Intro", "ThreeD"]

    def test_finds_dotted_base_scene(self, render_scenes_mod):
        src = "import manim\nclass Foo(manim.Scene):\n    pass\n"
        assert render_scenes_mod.extract_scene_class_names(src) == ["Foo"]

    def test_no_scenes_found_returns_empty_list(self, render_scenes_mod):
        src = "x = 1\n"
        assert render_scenes_mod.extract_scene_class_names(src) == []

    def test_syntax_error_returns_empty_list(self, render_scenes_mod):
        src = "def broken(:\n"
        assert render_scenes_mod.extract_scene_class_names(src) == []


class TestRenderOneSceneSubprocessMocking(object):
    """render_one_scene shells out to `manim` and `ffprobe`; mock both so
    the test never needs the real binaries."""

    def test_successful_render_reports_duration(self, render_scenes_mod, tmp_path):
        script_path = tmp_path / "video.py"
        script_path.write_text("from manim import *\nclass A(Scene):\n    pass\n")
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        expected_mp4 = out_dir / "videos" / "video" / "480p15" / "A.mp4"
        expected_mp4.parent.mkdir(parents=True)
        expected_mp4.write_bytes(b"fake mp4 bytes")

        manim_result = subprocess.CompletedProcess(
            args=["manim"], returncode=0, stdout="rendered ok", stderr=""
        )
        ffprobe_result = subprocess.CompletedProcess(
            args=["ffprobe"], returncode=0, stdout="3.500\n", stderr=""
        )

        with patch.object(
            render_scenes_mod.subprocess, "run",
            side_effect=[manim_result, ffprobe_result],
        ) as mock_run:
            report = render_scenes_mod.render_one_scene(script_path, "A", out_dir, 60.0)

        assert mock_run.call_count == 2
        assert report["success"] is True
        assert report["timed_out"] is False
        assert report["duration_seconds"] == 3.5
        assert report["video_path"] == str(expected_mp4.resolve())

    def test_timeout_is_reported_non_fatally(self, render_scenes_mod, tmp_path):
        script_path = tmp_path / "video.py"
        script_path.write_text("from manim import *\nclass A(Scene):\n    pass\n")
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        exc = subprocess.TimeoutExpired(cmd=["manim"], timeout=5, output="", stderr="")
        with patch.object(render_scenes_mod.subprocess, "run", side_effect=exc):
            report = render_scenes_mod.render_one_scene(script_path, "A", out_dir, 5.0)

        assert report["success"] is False
        assert report["timed_out"] is True
        assert report["video_path"] is None
        assert "timed out" in report["log_tail"]

    def test_missing_manim_binary_reported_cleanly(self, render_scenes_mod, tmp_path):
        """This exercises the FileNotFoundError handling added as a
        robustness fix: previously a missing `manim` executable crashed
        the whole batch with an uncaught traceback instead of producing a
        JSON report."""
        script_path = tmp_path / "video.py"
        script_path.write_text("from manim import *\nclass A(Scene):\n    pass\n")
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        with patch.object(
            render_scenes_mod.subprocess, "run", side_effect=FileNotFoundError()
        ):
            report = render_scenes_mod.render_one_scene(script_path, "A", out_dir, 60.0)

        assert report["success"] is False
        assert report["returncode"] == 127
        assert "not found" in report["log_tail"]


class TestRenderScenesMainValidation:
    def _run_main(self, monkeypatch, render_scenes_mod, argv):
        monkeypatch.setattr(sys, "argv", ["render_scenes.py", *argv])
        return render_scenes_mod.main()

    def test_rejects_nonpositive_timeout(self, monkeypatch, render_scenes_mod, tmp_path, capsys):
        script = tmp_path / "video.py"
        script.write_text("from manim import *\n")
        rc = self._run_main(
            monkeypatch, render_scenes_mod,
            ["--code", str(script), "--out", str(tmp_path / "out"), "--timeout", "0"],
        )
        assert rc == 2
        out = json.loads(capsys.readouterr().out)
        assert "timeout" in out["error"]

    def test_rejects_missing_code_file(self, monkeypatch, render_scenes_mod, tmp_path, capsys):
        rc = self._run_main(
            monkeypatch, render_scenes_mod,
            ["--code", str(tmp_path / "nope.py"), "--out", str(tmp_path / "out")],
        )
        assert rc == 2
        out = json.loads(capsys.readouterr().out)
        assert "not found" in out["error"]

    def test_rejects_code_path_that_is_a_directory(self, monkeypatch, render_scenes_mod, tmp_path, capsys):
        a_dir = tmp_path / "im_a_dir"
        a_dir.mkdir()
        rc = self._run_main(
            monkeypatch, render_scenes_mod,
            ["--code", str(a_dir), "--out", str(tmp_path / "out")],
        )
        assert rc == 2
        out = json.loads(capsys.readouterr().out)
        assert "not a file" in out["error"]

    def test_no_scenes_found_reports_error(self, monkeypatch, render_scenes_mod, tmp_path, capsys):
        script = tmp_path / "empty.py"
        script.write_text("x = 1\n")
        rc = self._run_main(
            monkeypatch, render_scenes_mod,
            ["--code", str(script), "--out", str(tmp_path / "out")],
        )
        assert rc == 3
        out = json.loads(capsys.readouterr().out)
        assert out["total_scenes"] == 0


# ---------------------------------------------------------------------------
# extract_frames.py
# ---------------------------------------------------------------------------

@pytest.fixture()
def extract_frames_mod():
    return _load_module("extract_frames", SCRIPTS_DIR / "extract_frames.py")


class TestExtractFramesImportsWithoutCv2:
    def test_module_imports_without_cv2_installed(self, extract_frames_mod):
        """Robustness fix: cv2/numpy imports were moved out of module scope
        so this script (and its CLI argument validation) can be imported
        and tested even where opencv-python is not installed."""
        assert hasattr(extract_frames_mod, "extract_highest_density")
        assert hasattr(extract_frames_mod, "extract_fixed_count")

    def test_import_cv_deps_reports_clean_error_when_missing(self, extract_frames_mod, capsys):
        with patch.dict(sys.modules, {"cv2": None}):
            with pytest.raises(SystemExit) as exc_info:
                extract_frames_mod._import_cv_deps()
        assert exc_info.value.code == 2
        out = json.loads(capsys.readouterr().out)
        assert "opencv-python" in out["error"]


class TestExtractFramesMainValidation:
    def _run_main(self, monkeypatch, extract_frames_mod, argv):
        monkeypatch.setattr(sys, "argv", ["extract_frames.py", *argv])
        return extract_frames_mod.main()

    def test_rejects_missing_video(self, monkeypatch, extract_frames_mod, tmp_path, capsys):
        rc = self._run_main(
            monkeypatch, extract_frames_mod,
            ["--video", str(tmp_path / "nope.mp4"), "--out", str(tmp_path / "frames")],
        )
        assert rc == 2
        out = json.loads(capsys.readouterr().out)
        assert "not found" in out["error"]

    def test_rejects_video_path_that_is_a_directory(self, monkeypatch, extract_frames_mod, tmp_path, capsys):
        a_dir = tmp_path / "vid_dir"
        a_dir.mkdir()
        rc = self._run_main(
            monkeypatch, extract_frames_mod,
            ["--video", str(a_dir), "--out", str(tmp_path / "frames")],
        )
        assert rc == 2
        out = json.loads(capsys.readouterr().out)
        assert "not a file" in out["error"]

    def test_rejects_nonpositive_count_in_fixed_count_mode(
        self, monkeypatch, extract_frames_mod, tmp_path, capsys
    ):
        video = tmp_path / "scene.mp4"
        video.write_bytes(b"fake")
        rc = self._run_main(
            monkeypatch, extract_frames_mod,
            [
                "--video", str(video), "--out", str(tmp_path / "frames"),
                "--mode", "fixed_count", "--count", "0",
            ],
        )
        assert rc == 2
        out = json.loads(capsys.readouterr().out)
        assert "count" in out["error"]


# ---------------------------------------------------------------------------
# generate_subtitles.py: pure helper functions.
# ---------------------------------------------------------------------------

@pytest.fixture()
def subtitles_mod():
    return _load_module("generate_subtitles", SCRIPTS_DIR / "generate_subtitles.py")


class TestFormatSrtTime:
    @pytest.mark.parametrize(
        "seconds, expected",
        [
            (0.0, "00:00:00,000"),
            (1.5, "00:00:01,500"),
            (61.25, "00:01:01,250"),
            (3661.001, "01:01:01,001"),
            (7325.999, "02:02:05,999"),
        ],
    )
    def test_formats_correctly(self, subtitles_mod, seconds, expected):
        assert subtitles_mod.format_srt_time(seconds) == expected


class TestOffsetWords:
    def test_shifts_all_timestamps(self, subtitles_mod):
        words = [
            {"word": "hi", "start": 0.0, "end": 0.4},
            {"word": "there", "start": 0.4, "end": 0.9},
        ]
        shifted = subtitles_mod.offset_words(words, 10.0)
        assert shifted == [
            {"word": "hi", "start": 10.0, "end": 10.4},
            {"word": "there", "start": 10.4, "end": 10.9},
        ]

    def test_zero_offset_is_noop(self, subtitles_mod):
        words = [{"word": "x", "start": 1.0, "end": 2.0}]
        assert subtitles_mod.offset_words(words, 0.0) == words


class TestGroupWords:
    def _words(self, *texts):
        out = []
        t = 0.0
        for w in texts:
            out.append({"word": w, "start": t, "end": t + 0.3})
            t += 0.3
        return out

    def test_splits_on_max_words(self, subtitles_mod):
        words = self._words("one", "two", "three", "four")
        cues = subtitles_mod.group_words(words, max_chars=1000, max_words=2)
        assert [c["text"] for c in cues] == ["one two", "three four"]

    def test_splits_on_max_chars(self, subtitles_mod):
        words = self._words("aaaa", "bbbb", "cccc")
        cues = subtitles_mod.group_words(words, max_chars=9, max_words=100)
        # "aaaa bbbb" is exactly 9 chars, adding "cccc" would exceed it.
        assert [c["text"] for c in cues] == ["aaaa bbbb", "cccc"]

    def test_cue_start_end_span_its_words(self, subtitles_mod):
        words = self._words("a", "b", "c")
        cues = subtitles_mod.group_words(words, max_chars=1000, max_words=3)
        assert len(cues) == 1
        assert cues[0]["start"] == words[0]["start"]
        assert cues[0]["end"] == words[-1]["end"]

    def test_empty_word_list_returns_no_cues(self, subtitles_mod):
        assert subtitles_mod.group_words([], max_chars=42, max_words=8) == []


class TestWriteSrt:
    def test_writes_expected_format(self, subtitles_mod, tmp_path):
        cues = [
            {"text": "Hello world", "start": 0.0, "end": 1.5},
            {"text": "Second cue", "start": 1.5, "end": 3.0},
        ]
        out_path = tmp_path / "out.srt"
        subtitles_mod.write_srt(cues, str(out_path))
        content = out_path.read_text(encoding="utf-8")
        assert "1\n00:00:00,000 --> 00:00:01,500\nHello world" in content
        assert "2\n00:00:01,500 --> 00:00:03,000\nSecond cue" in content


class TestGetDuration:
    def test_parses_ffprobe_output(self, subtitles_mod):
        fake_result = subprocess.CompletedProcess(
            args=["ffprobe"], returncode=0, stdout="4.250\n", stderr=""
        )
        with patch("subprocess.run", return_value=fake_result) as mock_run:
            duration = subtitles_mod.get_duration("fake.wav")
        assert duration == 4.25
        mock_run.assert_called_once()

    def test_missing_ffprobe_raises_clean_runtime_error(self, subtitles_mod):
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            with pytest.raises(RuntimeError, match="ffprobe not found"):
                subtitles_mod.get_duration("fake.wav")

    def test_ffprobe_failure_raises_clean_runtime_error(self, subtitles_mod):
        err = subprocess.CalledProcessError(
            returncode=1, cmd=["ffprobe"], stderr="no such file"
        )
        with patch("subprocess.run", side_effect=err):
            with pytest.raises(RuntimeError, match="ffprobe failed"):
                subtitles_mod.get_duration("fake.wav")

    def test_unparseable_output_raises_clean_runtime_error(self, subtitles_mod):
        fake_result = subprocess.CompletedProcess(
            args=["ffprobe"], returncode=0, stdout="not-a-number\n", stderr=""
        )
        with patch("subprocess.run", return_value=fake_result):
            with pytest.raises(RuntimeError, match="unparseable duration"):
                subtitles_mod.get_duration("fake.wav")


class TestTranscribeClipErrorHandling:
    def test_missing_openai_package_raises_clean_runtime_error(self, subtitles_mod):
        with patch.dict(sys.modules, {"openai": None}):
            with pytest.raises(RuntimeError, match="openai"):
                subtitles_mod.transcribe_clip("fake.wav")

    def test_missing_api_key_raises_clean_runtime_error(self, subtitles_mod, monkeypatch):
        # Provide a fake openai module so we get past the import and hit
        # the API-key check instead.
        fake_openai = types.ModuleType("openai")
        fake_openai.OpenAI = lambda: None
        monkeypatch.setitem(sys.modules, "openai", fake_openai)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            subtitles_mod.transcribe_clip("fake.wav")


class TestGenerateSubtitlesMainValidation:
    def _run_main(self, monkeypatch, subtitles_mod, argv):
        monkeypatch.setattr(sys, "argv", ["generate_subtitles.py", *argv])
        return subtitles_mod.main()

    def test_rejects_missing_audio_file(self, monkeypatch, subtitles_mod, tmp_path, capsys):
        rc = self._run_main(
            monkeypatch, subtitles_mod,
            ["--audio", str(tmp_path / "nope.wav"), "--out", str(tmp_path / "out.srt")],
        )
        assert rc == 2
        err = capsys.readouterr().err
        assert "not found" in err

    def test_rejects_nonpositive_max_chars(self, monkeypatch, subtitles_mod, tmp_path, capsys):
        audio = tmp_path / "a.wav"
        audio.write_bytes(b"fake")
        rc = self._run_main(
            monkeypatch, subtitles_mod,
            [
                "--audio", str(audio), "--out", str(tmp_path / "out.srt"),
                "--max-chars", "0",
            ],
        )
        assert rc == 2
        err = capsys.readouterr().err
        assert "max-chars" in err

    def test_rejects_nonpositive_max_words(self, monkeypatch, subtitles_mod, tmp_path, capsys):
        audio = tmp_path / "a.wav"
        audio.write_bytes(b"fake")
        rc = self._run_main(
            monkeypatch, subtitles_mod,
            [
                "--audio", str(audio), "--out", str(tmp_path / "out.srt"),
                "--max-words", "0",
            ],
        )
        assert rc == 2
        err = capsys.readouterr().err
        assert "max-words" in err


# ---------------------------------------------------------------------------
# Shell scripts: syntax check + argument validation without real binaries.
# ---------------------------------------------------------------------------

FINALIZE_SH = SCRIPTS_DIR / "finalize_video.sh"
SETUP_SH = SCRIPTS_DIR / "setup.sh"


def _bash_available() -> bool:
    try:
        subprocess.run(["bash", "--version"], capture_output=True, check=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


BASH_AVAILABLE = _bash_available()


@pytest.mark.skipif(not BASH_AVAILABLE, reason="bash not available in this environment")
class TestShellScriptSyntax:
    @pytest.mark.parametrize("path", [FINALIZE_SH, SETUP_SH], ids=lambda p: p.name)
    def test_bash_syntax_check(self, path):
        result = subprocess.run(
            ["bash", "-n", str(path)], capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr


@pytest.mark.skipif(not BASH_AVAILABLE, reason="bash not available in this environment")
class TestFinalizeVideoShArgValidation:
    def test_help_flag_exits_zero_with_usage(self):
        result = subprocess.run(
            ["bash", str(FINALIZE_SH), "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Usage" in result.stderr

    def test_wrong_arg_count_exits_nonzero_with_usage(self):
        result = subprocess.run(
            ["bash", str(FINALIZE_SH), "only_one_arg"], capture_output=True, text=True
        )
        assert result.returncode == 2
        assert "Usage" in result.stderr

    def test_missing_video_file_reports_clean_error(self, tmp_path):
        result = subprocess.run(
            ["bash", str(FINALIZE_SH), str(tmp_path / "nope.py"), str(tmp_path), "out.mp4"],
            capture_output=True, text=True,
        )
        assert result.returncode == 2
        assert "not found" in result.stderr

    def test_missing_media_dir_reports_clean_error(self, tmp_path):
        video = tmp_path / "video.py"
        video.write_text("from manim import *\n")
        missing_dir = tmp_path / "does_not_exist"
        result = subprocess.run(
            ["bash", str(FINALIZE_SH), str(video), str(missing_dir), "out.mp4"],
            capture_output=True, text=True,
        )
        assert result.returncode == 2
        assert "not found" in result.stderr


@pytest.mark.skipif(not BASH_AVAILABLE, reason="bash not available in this environment")
class TestSetupShBehavior:
    def test_skips_install_when_manim_already_importable(self):
        """setup.sh's fast path (`python3 -c "import manim"`) should exit 0
        without needing apt/pip/sudo/network access. We can't guarantee
        manim is installed in this environment, so skip if it isn't --
        that combination genuinely requires the real dependency."""
        check = subprocess.run(
            [sys.executable, "-c", "import manim"], capture_output=True
        )
        if check.returncode != 0:
            pytest.skip("manim is not installed in this environment")

        result = subprocess.run(
            ["bash", str(SETUP_SH)], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Already installed" in result.stdout

    def test_does_not_hardcode_sudo_without_guard(self):
        """Regression test for the sandbox robustness fix: setup.sh must
        not call bare `sudo ...` unconditionally, since many containers
        run as root with no `sudo` binary installed at all."""
        content = SETUP_SH.read_text()
        assert "SUDO=" in content
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert not stripped.startswith("sudo "), f"unguarded sudo call: {line!r}"
