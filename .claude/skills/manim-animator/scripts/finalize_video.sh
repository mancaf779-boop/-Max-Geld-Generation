#!/usr/bin/env bash
# Re-render every Scene in a Manim script at high quality (1080p60) and
# concatenate the per-scene MP4s into one final video, in source order.
#
# Distilled from manim-generator's `render_and_concat`, minus auto-play.
#
# Usage:
#   bash scripts/finalize_video.sh <video.py> <media_dir> <final_output.mp4>
#
# Example:
#   bash scripts/finalize_video.sh output/video.py output/ output/final.mp4
#
# On success, prints the absolute path of the final mp4 on the last line.

set -euo pipefail

usage() {
    echo "Usage: $0 <video.py> <media_dir> <final_output.mp4>" >&2
    echo "" >&2
    echo "Example:" >&2
    echo "  bash scripts/finalize_video.sh output/video.py output/ output/final.mp4" >&2
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

if [[ $# -ne 3 ]]; then
    usage
    exit 2
fi

if [[ ! -f "$1" ]]; then
    echo "[finalize] ERROR: video.py not found: $1" >&2
    exit 2
fi

if [[ ! -d "$2" ]]; then
    echo "[finalize] ERROR: media_dir not found: $2" >&2
    echo "[finalize] (run scripts/render_scenes.py first to create it)" >&2
    exit 2
fi

for bin in manim ffmpeg python3; do
    if ! command -v "${bin}" >/dev/null 2>&1; then
        echo "[finalize] ERROR: required command not found on PATH: ${bin}" >&2
        exit 2
    fi
done

SCRIPT_FILE="$(realpath "$1")"
MEDIA_DIR="$(realpath "$2")"
FINAL_OUT="$3"
case "$FINAL_OUT" in
    /*) ;;                                 # already absolute
    *)  FINAL_OUT="$(pwd)/$FINAL_OUT" ;;   # make absolute
esac

# Make sure the destination directory for the final file exists.
mkdir -p "$(dirname "${FINAL_OUT}")"

SCRIPT_STEM="$(basename "${SCRIPT_FILE}" .py)"
HQ_DIR="${MEDIA_DIR}/videos/${SCRIPT_STEM}/1080p60"

echo "[finalize] Script:   ${SCRIPT_FILE}"
echo "[finalize] Media:    ${MEDIA_DIR}"
echo "[finalize] Out:      ${FINAL_OUT}"

# --- Stage 1: high-quality render of every Scene ---
echo "[finalize] Stage 1/2: rendering all scenes at -qh (1080p60)..."
manim -qh --write_all --media_dir "${MEDIA_DIR}" "${SCRIPT_FILE}"

if [[ ! -d "${HQ_DIR}" ]]; then
    echo "[finalize] ERROR: expected directory not found: ${HQ_DIR}" >&2
    exit 3
fi

# --- Stage 2: build ffmpeg concat manifest in source order ---
# Extract Scene class names in the order they appear in the script.
SCENES=$(python3 - "${SCRIPT_FILE}" <<'PY'
import ast, sys
src = open(sys.argv[1], encoding="utf-8").read()
tree = ast.parse(src)
bases = {"Scene","ThreeDScene","MovingCameraScene","ZoomedScene",
         "LinearTransformationScene","VectorScene","GraphScene",
         "SpecialThreeDScene"}
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for b in node.bases:
            name = getattr(b, "id", None) or getattr(b, "attr", None)
            if name in bases:
                print(node.name)
                break
PY
)

if [[ -z "${SCENES}" ]]; then
    echo "[finalize] ERROR: no Scene classes found in ${SCRIPT_FILE}" >&2
    exit 4
fi

CONCAT_LIST="${MEDIA_DIR}/ffmpeg_concat_list.txt"
: > "${CONCAT_LIST}"
MISSING=0
while IFS= read -r SCENE; do
    MP4="${HQ_DIR}/${SCENE}.mp4"
    if [[ -f "${MP4}" ]]; then
        echo "file '$(realpath "${MP4}")'" >> "${CONCAT_LIST}"
    else
        echo "[finalize] WARNING: missing rendered file for ${SCENE}: ${MP4}" >&2
        MISSING=$((MISSING + 1))
    fi
done <<< "${SCENES}"

if [[ ! -s "${CONCAT_LIST}" ]]; then
    echo "[finalize] ERROR: concat manifest is empty (${MISSING} missing)." >&2
    exit 5
fi

echo "[finalize] Stage 2/2: concatenating with ffmpeg..."
ffmpeg -y -hide_banner -loglevel error \
    -f concat -safe 0 -i "${CONCAT_LIST}" -c copy "${FINAL_OUT}"

rm -f "${CONCAT_LIST}"

echo "[finalize] Done."
echo "${FINAL_OUT}"
