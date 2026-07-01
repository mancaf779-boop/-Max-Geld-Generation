#!/usr/bin/env python3
"""Transcribe per-scene narration audio with OpenAI Whisper API (word-level
timestamps) and produce a single SRT subtitle file for the concatenated video.

This script is the subtitle counterpart of ``finalize_video.sh``.  It takes
the same ordered list of per-scene audio clips, transcribes each one via the
Whisper API, offsets timestamps so they are relative to the concatenated
timeline, and writes a single ``.srt`` file ready to be muxed into the final
MP4.

Usage
-----
    python3 scripts/generate_subtitles.py \
        --audio scene1.wav scene2.wav scene3.wav \
        --out   output/subtitles.srt \
        [--max-chars 42] \
        [--max-words 8]

The ``--audio`` clips MUST be in the same scene order used by
``finalize_video.sh`` so that subtitle timestamps align with the video.

Output
------
A standard SRT file whose cues are grouped by ``--max-chars`` (default 42)
or ``--max-words`` (default 8), whichever limit is hit first.  Each cue
corresponds to a short phrase, not a full sentence, to keep on-screen text
readable.

Requirements
------------
- ``openai`` Python package (``pip install openai``)
- ``OPENAI_API_KEY`` environment variable set in the environment
- ``ffprobe`` (part of the ffmpeg toolchain) on PATH, used to measure each
  clip's duration for timeline offsetting
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def transcribe_clip(audio_path: str) -> list[dict]:
    """Return word-level timestamps for one audio file via Whisper API.

    Each element: {"word": str, "start": float, "end": float}
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is required for subtitle generation. "
            "Install it with: pip install openai"
        ) from exc

    import os

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set; "
            "cannot call the Whisper transcription API."
        )

    client = OpenAI()
    with open(audio_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
    # resp.words is a list of objects with .word, .start, .end
    return [{"word": w.word, "start": w.start, "end": w.end} for w in resp.words]


def offset_words(words: list[dict], offset: float) -> list[dict]:
    """Shift all timestamps by *offset* seconds."""
    return [
        {"word": w["word"], "start": round(w["start"] + offset, 3),
         "end": round(w["end"] + offset, 3)}
        for w in words
    ]


def get_duration(audio_path: str) -> float:
    """Return duration in seconds via ffprobe."""
    import subprocess

    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
            capture_output=True, text=True, check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "ffprobe not found on PATH; install ffmpeg to measure audio "
            "clip durations."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"ffprobe failed on {audio_path!r}: {exc.stderr.strip()}"
        ) from exc

    try:
        return float(out.stdout.strip())
    except ValueError as exc:
        raise RuntimeError(
            f"ffprobe returned an unparseable duration for {audio_path!r}: "
            f"{out.stdout!r}"
        ) from exc


def group_words(words: list[dict], max_chars: int, max_words: int) -> list[dict]:
    """Group consecutive words into subtitle cues.

    A new cue starts when adding the next word would exceed *max_chars*
    (including spaces) or *max_words*, whichever limit is hit first.

    Returns a list of cue dicts: {"text": str, "start": float, "end": float}
    """
    cues: list[dict] = []
    buf_words: list[dict] = []
    buf_text = ""

    for w in words:
        candidate = (buf_text + " " + w["word"]).strip() if buf_text else w["word"]
        if buf_words and (len(candidate) > max_chars or len(buf_words) >= max_words):
            cues.append({
                "text": buf_text,
                "start": buf_words[0]["start"],
                "end": buf_words[-1]["end"],
            })
            buf_words = [w]
            buf_text = w["word"]
        else:
            buf_words.append(w)
            buf_text = candidate

    if buf_words:
        cues.append({
            "text": buf_text,
            "start": buf_words[0]["start"],
            "end": buf_words[-1]["end"],
        })
    return cues


def format_srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(cues: list[dict], out_path: str) -> None:
    """Write cues to an SRT file."""
    lines: list[str] = []
    for i, cue in enumerate(cues, 1):
        lines.append(str(i))
        lines.append(f"{format_srt_time(cue['start'])} --> {format_srt_time(cue['end'])}")
        lines.append(cue["text"])
        lines.append("")
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Transcribe per-scene audio and produce a timeline-aligned SRT file.",
    )
    p.add_argument(
        "--audio", nargs="+", required=True,
        help="Per-scene audio files in scene order",
    )
    p.add_argument(
        "--out", required=True,
        help="Output SRT file path",
    )
    p.add_argument(
        "--max-chars", type=int, default=42,
        help="Max characters per subtitle cue (default 42)",
    )
    p.add_argument(
        "--max-words", type=int, default=8,
        help="Max words per subtitle cue (default 8)",
    )
    args = p.parse_args()

    if args.max_chars <= 0:
        print(f"ERROR: --max-chars must be positive, got {args.max_chars}", file=sys.stderr)
        return 2
    if args.max_words <= 0:
        print(f"ERROR: --max-words must be positive, got {args.max_words}", file=sys.stderr)
        return 2

    all_words: list[dict] = []
    timeline_offset = 0.0

    for audio_path in args.audio:
        if not Path(audio_path).exists():
            print(f"ERROR: audio file not found: {audio_path}", file=sys.stderr)
            return 2

        try:
            print(f"[subtitles] Transcribing {audio_path} ...")
            words = transcribe_clip(audio_path)
            print(f"[subtitles]   -> {len(words)} words")

            all_words.extend(offset_words(words, timeline_offset))
            timeline_offset += get_duration(audio_path)
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    if not all_words:
        print("[subtitles] WARNING: no words transcribed; writing empty SRT.")
        Path(args.out).write_text("", encoding="utf-8")
        return 0

    cues = group_words(all_words, args.max_chars, args.max_words)
    write_srt(cues, args.out)

    print(f"[subtitles] Done: {len(cues)} cues written to {args.out}")
    print(f"[subtitles] Total timeline: {timeline_offset:.2f}s")

    # Also write the raw word-level JSON alongside the SRT for debugging.
    json_path = str(Path(args.out).with_suffix(".json"))
    Path(json_path).write_text(
        json.dumps(all_words, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print(f"[subtitles] Word-level JSON: {json_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
