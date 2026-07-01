#!/usr/bin/env python3
"""Extract representative frames from a Manim scene video.

Distilled from manim-generator's `extract_frames_from_video`. Two modes:

  * highest_density  — sample up to 30 evenly-spaced frames, keep the one
                       with the highest non-black pixel density. Best for
                       a single "representative" frame on a dark Manim bg.
  * fixed_count      — sample N evenly-spaced frames, keep all. Best for a
                       temporal sequence the agent wants to review in order.

Usage
-----
    python3 scripts/extract_frames.py \\
        --video path/to/Scene.mp4 \\
        --out   path/to/frames_dir/ \\
        [--mode highest_density|fixed_count] \\
        [--count 3]

Output
------
    JSON document on stdout listing absolute paths to the saved PNG frames.
    Files are named <video-stem>_frame_01.png, ..._frame_NN.png.

Requires: opencv-python, numpy.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# NOTE: cv2/numpy are intentionally NOT imported at module scope. Importing
# them lazily (inside the functions that need them) means this module can
# still be imported and its pure argument-parsing / validation logic can be
# unit-tested in environments where opencv-python is not installed.
BLACK_PIXEL_THRESHOLD = 30
DEFAULT_MAX_SAMPLE_FRAMES = 30


def _import_cv_deps() -> tuple[Any, Any]:
    """Import cv2/numpy on demand, with a clean error if missing."""
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError:
        print(
            json.dumps(
                {
                    "error": "opencv-python and numpy are required. "
                             "`pip3 install opencv-python numpy`"
                }
            )
        )
        sys.exit(2)
    return cv2, np


def extract_highest_density(video_path: Path) -> list:
    cv2, np = _import_cv_deps()
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total == 0:
        cap.release()
        return []

    indices = np.linspace(
        0, total - 1, min(DEFAULT_MAX_SAMPLE_FRAMES, total), dtype=int
    )
    best_frame = None
    best_density = -1.0
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        density = float((gray > BLACK_PIXEL_THRESHOLD).sum()) / float(gray.size)
        if density > best_density:
            best_density = density
            best_frame = frame.copy()
    cap.release()
    return [best_frame] if best_frame is not None else []


def extract_fixed_count(video_path: Path, count: int) -> list:
    cv2, np = _import_cv_deps()
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total == 0:
        cap.release()
        return []
    indices = np.linspace(0, total - 1, min(count, total), dtype=int)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if ok:
            frames.append(frame.copy())
    cap.release()
    return frames


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument(
        "--mode",
        choices=["highest_density", "fixed_count"],
        default="highest_density",
    )
    ap.add_argument("--count", type=int, default=3)
    args = ap.parse_args()

    if args.mode == "fixed_count" and args.count <= 0:
        print(json.dumps({"error": f"--count must be positive, got {args.count}"}))
        return 2

    video_path = Path(args.video).resolve()
    out_dir = Path(args.out).resolve()

    if not video_path.exists():
        print(json.dumps({"error": f"video not found: {video_path}"}))
        return 2

    if not video_path.is_file():
        print(json.dumps({"error": f"--video is not a file: {video_path}"}))
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "highest_density":
        frames = extract_highest_density(video_path)
    else:
        frames = extract_fixed_count(video_path, args.count)

    if not frames:
        print(json.dumps({"error": "no frames extracted", "frames": []}))
        return 3

    cv2, _np = _import_cv_deps()
    saved: list[str] = []
    stem = video_path.stem
    for i, frame in enumerate(frames, start=1):
        out_path = out_dir / f"{stem}_frame_{i:02d}.png"
        ok = cv2.imwrite(str(out_path), frame)
        if ok:
            saved.append(str(out_path))

    print(json.dumps({"frames": saved, "mode": args.mode, "count": len(saved)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
