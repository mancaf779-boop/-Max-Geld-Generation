#!/usr/bin/env python3
"""
Clip plan validator for the video-generator skill.

Validates the Phase 3 per-clip field dependencies and builds the mandatory
"BGM Emotional Arc Blueprint" from a list of clip dicts, so both can be
checked mechanically instead of by inspection.

Expected clip dict shape (only the fields this script cares about):
    {
        "duration": 4 | 6 | 8,
        "inter_clip_boundary": "continuous" | "scene_cut",
        "first_keyframe_reuse": "yes" | "no",
        "last_keyframe_required": "yes" | "no",
        "bgm_cue": <any hashable/JSON-comparable value, or None>,
    }

CLI usage:
    clip_plan_validator.py validate <clips.json>
    clip_plan_validator.py emotional-arc <clips.json>
"""

import argparse
import json
import sys
from pathlib import Path

VALID_DURATIONS = {4, 6, 8}


def validate_clip_plan(clips):
    """
    Validate field dependencies across a list of clip dicts.

    Returns (ok: bool, messages: list[str]).
    """
    ok = True
    messages = []

    if not clips:
        return True, ["No clips to validate."]

    for i, clip in enumerate(clips):
        duration = clip.get("duration")
        if duration not in VALID_DURATIONS:
            ok = False
            messages.append(f"Clip {i}: duration {duration!r} must be one of {sorted(VALID_DURATIONS)}.")

        if clip.get("inter_clip_boundary") == "continuous":
            if i == len(clips) - 1:
                ok = False
                messages.append(f"Clip {i}: inter_clip_boundary=continuous but it is the last clip.")
            else:
                next_clip = clips[i + 1]
                if next_clip.get("first_keyframe_reuse") != "yes":
                    ok = False
                    messages.append(
                        f"Clip {i}: inter_clip_boundary=continuous requires clip {i + 1} "
                        f"to have first_keyframe_reuse=yes, got {next_clip.get('first_keyframe_reuse')!r}."
                    )

        if clip.get("first_keyframe_reuse") == "yes":
            if i == 0:
                ok = False
                messages.append(f"Clip {i}: first_keyframe_reuse=yes but there is no previous clip.")
            else:
                prev_clip = clips[i - 1]
                if prev_clip.get("last_keyframe_required") != "yes":
                    ok = False
                    messages.append(
                        f"Clip {i}: first_keyframe_reuse=yes requires clip {i - 1} "
                        f"to have last_keyframe_required=yes, got {prev_clip.get('last_keyframe_required')!r}."
                    )

    if ok:
        messages.append("Clip plan is internally consistent.")
    return ok, messages


def _format_timestamp(total_seconds):
    minutes, seconds = divmod(int(total_seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"


def build_emotional_arc(clips):
    """
    Compute [start-end] time segments per clip and merge consecutive clips
    sharing an identical bgm_cue into a single row.

    Returns a list of dicts: {"start": int, "end": int, "bgm_cue": ...}
    """
    rows = []
    cursor = 0
    for clip in clips:
        duration = clip.get("duration", 0)
        start, end = cursor, cursor + duration
        bgm_cue = clip.get("bgm_cue")

        if rows and rows[-1]["bgm_cue"] == bgm_cue:
            rows[-1]["end"] = end
        else:
            rows.append({"start": start, "end": end, "bgm_cue": bgm_cue})

        cursor = end
    return rows


def format_emotional_arc_table(rows):
    lines = ["| Time Segment | BGM Cue |", "|---|---|"]
    for row in rows:
        segment = f"[{_format_timestamp(row['start'])}-{_format_timestamp(row['end'])}]"
        lines.append(f"| `{segment}` | `{row['bgm_cue']}` |")
    return "\n".join(lines)


def _load_clips(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate field dependencies across clips")
    p_validate.add_argument("clips_json")

    p_arc = sub.add_parser("emotional-arc", help="Build the merged BGM emotional arc table")
    p_arc.add_argument("clips_json")

    args = parser.parse_args()

    try:
        clips = _load_clips(args.clips_json)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error reading {args.clips_json}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "validate":
        ok, messages = validate_clip_plan(clips)
        for msg in messages:
            print(msg)
        sys.exit(0 if ok else 1)
    elif args.command == "emotional-arc":
        rows = build_emotional_arc(clips)
        print(format_emotional_arc_table(rows))


if __name__ == "__main__":
    main()
