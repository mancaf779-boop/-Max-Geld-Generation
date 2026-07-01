#!/usr/bin/env python3
"""Render every Scene in a Manim script at low quality, with per-scene
timeout, and return a structured JSON report.

This script is distilled from manim-generator's `run_manim_multiscene`
function, adapted for direct CLI use by an agent:
  * No LiteLLM, no Rich, no base64 framing.
  * Failures are non-fatal; per-scene success/failure is reported.
  * Stdout is a single JSON document for easy parsing by the agent.

Usage
-----
    python3 scripts/render_scenes.py \\
        --code output/video.py \\
        --out  output/ \\
        [--timeout 120]

Output
------
    {
      "success": bool,                # all scenes rendered successfully
      "success_rate": float,          # percent of scenes that rendered
      "scenes_rendered": int,
      "total_scenes": int,
      "scenes": [
        {
          "name":     "MyScene",
          "success":  true|false,
          "timed_out": false,
          "returncode": 0,
          "video_path": ".../480p15/MyScene.mp4"  | null,
          "duration_seconds": 8.23  | null,
          "log_tail":  "last ~40 lines of stdout+stderr"
        },
        ...
      ]
    }

The rendered videos live at:
    <out>/videos/<script_stem>/480p15/<Scene>.mp4

and are NOT deleted afterwards, so downstream steps (frame extraction,
finalization) can reuse them.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from pathlib import Path


LOW_QUALITY_FOLDER = "480p15"


def extract_scene_class_names(source: str) -> list[str]:
    """Return names of classes that inherit (directly or by name) from a
    Manim Scene base class. Falls back to empty list on syntax errors."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    manim_scene_bases = {
        "Scene",
        "ThreeDScene",
        "MovingCameraScene",
        "ZoomedScene",
        "LinearTransformationScene",
        "VectorScene",
        "GraphScene",
        "SpecialThreeDScene",
    }
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id in manim_scene_bases:
                    names.append(node.name)
                    break
                if isinstance(base, ast.Attribute) and base.attr in manim_scene_bases:
                    names.append(node.name)
                    break
    return names


def render_one_scene(
    script_path: Path,
    scene_name: str,
    output_dir: Path,
    timeout: float,
) -> dict:
    """Run `manim -ql` for a single Scene. Return per-scene report dict."""
    cmd = [
        "manim",
        "-ql",
        "--disable_caching",
        "--media_dir",
        str(output_dir),
        str(script_path),
        scene_name,
    ]

    timed_out = False
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
        stdout = proc.stdout
        stderr = proc.stderr
        returncode = proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        returncode = -1
    except FileNotFoundError:
        # `manim` is not installed / not on PATH. Report cleanly instead of
        # letting the traceback abort the whole batch.
        stdout = ""
        stderr = (
            "ERROR: 'manim' executable not found on PATH. "
            "Run scripts/setup.sh first."
        )
        returncode = 127

    # Compose a compact tail for the agent to read.
    tail_src = f"--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}"
    tail_lines = tail_src.splitlines()
    log_tail = "\n".join(tail_lines[-40:]) if len(tail_lines) > 40 else tail_src
    if timed_out:
        log_tail += f"\n<!> Scene {scene_name} timed out after {timeout:.0f} seconds"

    # Locate the rendered mp4 if succeeded.
    video_path: str | None = None
    if returncode == 0 and not timed_out:
        expected = (
            output_dir
            / "videos"
            / script_path.stem
            / LOW_QUALITY_FOLDER
            / f"{scene_name}.mp4"
        )
        if expected.exists():
            video_path = str(expected.resolve())

    # Measure rendered clip duration via ffprobe when available.
    duration_seconds: float | None = None
    if video_path is not None:
        try:
            dur_out = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries",
                 "format=duration", "-of",
                 "default=noprint_wrappers=1:nokey=1", video_path],
                capture_output=True, text=True, timeout=10,
            )
            duration_seconds = round(float(dur_out.stdout.strip()), 3)
        except Exception:
            pass  # non-fatal; duration will be null

    return {
        "name": scene_name,
        "success": (returncode == 0 and not timed_out and video_path is not None),
        "timed_out": timed_out,
        "returncode": returncode,
        "video_path": video_path,
        "duration_seconds": duration_seconds,
        "log_tail": log_tail,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Render every Manim scene at low quality.")
    p.add_argument("--code", required=True, help="Path to video.py")
    p.add_argument(
        "--out",
        required=True,
        help="Media output directory (Manim uses <out>/videos/<stem>/480p15/)",
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Per-scene timeout in seconds (default 120)",
    )
    args = p.parse_args()

    if args.timeout <= 0:
        print(json.dumps({"error": f"--timeout must be positive, got {args.timeout}"}))
        return 2

    script_path = Path(args.code).resolve()
    output_dir = Path(args.out).resolve()

    if not script_path.exists():
        print(json.dumps({"error": f"code file not found: {script_path}"}))
        return 2

    if not script_path.is_file():
        print(json.dumps({"error": f"--code is not a file: {script_path}"}))
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)

    source = script_path.read_text(encoding="utf-8")
    scene_names = extract_scene_class_names(source)

    if not scene_names:
        print(
            json.dumps(
                {
                    "success": False,
                    "success_rate": 0.0,
                    "scenes_rendered": 0,
                    "total_scenes": 0,
                    "scenes": [],
                    "error": "no Scene subclasses found (syntax error or empty file)",
                }
            )
        )
        return 3

    scene_reports: list[dict] = []
    for name in scene_names:
        scene_reports.append(
            render_one_scene(script_path, name, output_dir, args.timeout)
        )

    rendered = sum(1 for s in scene_reports if s["success"])
    total = len(scene_reports)
    report = {
        "success": rendered == total,
        "success_rate": round(100.0 * rendered / total, 2) if total else 0.0,
        "scenes_rendered": rendered,
        "total_scenes": total,
        "scenes": scene_reports,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if rendered == total else 1


if __name__ == "__main__":
    sys.exit(main())
