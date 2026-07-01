#!/usr/bin/env python3
"""
Multi-clip planning helper for the music-prompter skill.

Formalizes the Section 7 "Multi-Clip Continuity Strategy" arithmetic: how to
chunk a long track into per-call clips, how long a beat-aligned crossfade
should be, and whether a written arrangement's timestamp cues actually
line up with the declared clip duration.

CLI usage:
    multiclip_planner.py plan-clips <total_duration_seconds> [--max-clip 180]
    multiclip_planner.py crossfade-duration <bpm> [--beats 2]
    multiclip_planner.py validate-arrangement <file-or-text> <declared_duration_seconds>
"""

import argparse
import re
import sys
from math import ceil
from pathlib import Path

DEFAULT_MAX_CLIP_SECONDS = 180

_TIMESTAMP_RE = re.compile(
    r'\[\s*(\d+):(\d{2})\s*-\s*(\d+):(\d{2})\s*\]'
)


def _mmss_to_seconds(minutes, seconds):
    return int(minutes) * 60 + int(seconds)


def plan_clips(total_duration, max_clip=DEFAULT_MAX_CLIP_SECONDS):
    """
    Split total_duration seconds into a list of clip durations, each
    <= max_clip, as evenly sized as possible (so no clip is awkwardly short).
    """
    if total_duration <= 0:
        raise ValueError("total_duration must be positive")
    if max_clip <= 0:
        raise ValueError("max_clip must be positive")

    if total_duration <= max_clip:
        return [total_duration]

    num_clips = ceil(total_duration / max_clip)
    base = total_duration // num_clips
    remainder = total_duration - base * num_clips

    clips = []
    for i in range(num_clips):
        duration = base + 1 if i < remainder else base
        clips.append(duration)
    return clips


def crossfade_duration(bpm, beats=2):
    """Seconds for a beat-aligned crossfade of `beats` beats at the given BPM."""
    if bpm <= 0:
        raise ValueError("bpm must be positive")
    if beats <= 0:
        raise ValueError("beats must be positive")
    return beats * 60.0 / bpm


def parse_timestamp_sections(prompt_text):
    """Extract [mm:ss - mm:ss] cues from prompt text, in the order they appear."""
    sections = []
    for m in _TIMESTAMP_RE.finditer(prompt_text):
        start = _mmss_to_seconds(m.group(1), m.group(2))
        end = _mmss_to_seconds(m.group(3), m.group(4))
        sections.append((start, end))
    return sections


def validate_arrangement(prompt_text, declared_duration):
    """
    Check that timestamp cues in prompt_text are contiguous, start at 0,
    and the final timestamp matches declared_duration.

    Returns (ok: bool, messages: list[str]).
    """
    sections = parse_timestamp_sections(prompt_text)
    messages = []
    ok = True

    if not sections:
        return True, ["No timestamp cues found; nothing to validate."]

    if sections[0][0] != 0:
        ok = False
        messages.append(f"First section starts at {sections[0][0]}s, expected 0s.")

    for i in range(1, len(sections)):
        prev_end = sections[i - 1][1]
        cur_start = sections[i][0]
        if cur_start != prev_end:
            ok = False
            messages.append(
                f"Gap/overlap between section {i} (ends {prev_end}s) and "
                f"section {i + 1} (starts {cur_start}s)."
            )

    last_end = sections[-1][1]
    if last_end != declared_duration:
        ok = False
        messages.append(
            f"Final timestamp ends at {last_end}s but declared duration is {declared_duration}s."
        )

    for start, end in sections:
        if end <= start:
            ok = False
            messages.append(f"Section [{start}s - {end}s] has non-positive length.")

    if ok:
        messages.append("Arrangement timestamps are contiguous and match the declared duration.")

    return ok, messages


def _resolve_text_arg(value):
    """If value is a path to an existing file, read it; otherwise treat it as raw text."""
    path = Path(value)
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")
    return value


def _build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_plan = sub.add_parser("plan-clips", help="Chunk a long track into per-call clip durations")
    p_plan.add_argument("total_duration", type=int)
    p_plan.add_argument("--max-clip", type=int, default=DEFAULT_MAX_CLIP_SECONDS)

    p_cross = sub.add_parser("crossfade-duration", help="Beat-aligned crossfade duration")
    p_cross.add_argument("bpm", type=float)
    p_cross.add_argument("--beats", type=float, default=2)

    p_val = sub.add_parser("validate-arrangement", help="Validate timestamp cues against declared duration")
    p_val.add_argument("file_or_text")
    p_val.add_argument("declared_duration", type=int)

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "plan-clips":
            clips = plan_clips(args.total_duration, max_clip=args.max_clip)
            print(" ".join(str(c) for c in clips))
        elif args.command == "crossfade-duration":
            print(f"{crossfade_duration(args.bpm, beats=args.beats):.3f}")
        elif args.command == "validate-arrangement":
            text = _resolve_text_arg(args.file_or_text)
            ok, messages = validate_arrangement(text, args.declared_duration)
            for msg in messages:
                print(msg)
            sys.exit(0 if ok else 1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
