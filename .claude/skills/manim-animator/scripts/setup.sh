#!/usr/bin/env bash
# Install Manim Community and its system-level build dependencies in the
# sandbox (Ubuntu 22.04 base). Idempotent: safe to run multiple times.
#
# Usage:
#   bash scripts/setup.sh
#
# On success, `manim --version` prints the installed ManimCE version.
set -euo pipefail

# Resolve the skill directory so this script works regardless of cwd.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use sudo only when available and needed (many sandboxes/containers already
# run as root and do not have a `sudo` binary installed at all).
if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    SUDO=()
elif command -v sudo >/dev/null 2>&1; then
    SUDO=(sudo)
else
    echo "[manim/setup] WARNING: not running as root and 'sudo' is not" >&2
    echo "[manim/setup] available; system package installs below may fail." >&2
    SUDO=()
fi

echo "[manim/setup] Checking existing install..."
if python3 -c "import manim" 2>/dev/null; then
    VERSION=$(python3 -c "import manim; print(manim.__version__)")
    echo "[manim/setup] Already installed (manim==${VERSION}). Skipping."
    manim --version || true
    exit 0
fi

echo "[manim/setup] Installing system build dependencies..."
# Pango / Cairo headers are required to build the manimpango and pycairo
# wheels from source. Python.h is required for the same reason. ffmpeg is
# required at runtime to assemble per-frame PNGs into MP4.
if command -v apt-get >/dev/null 2>&1; then
    "${SUDO[@]}" apt-get update -qq
    "${SUDO[@]}" apt-get install -y --no-install-recommends \
        libpango1.0-dev \
        libcairo2-dev \
        pkg-config \
        build-essential \
        python3.11-dev \
        python3-dev \
        ffmpeg
else
    echo "[manim/setup] WARNING: apt-get not found; skipping system package" >&2
    echo "[manim/setup] install. Install the Pango/Cairo/ffmpeg equivalents" >&2
    echo "[manim/setup] for your platform manually before continuing." >&2
fi

echo "[manim/setup] Installing Manim Community and frame-extraction deps via pip..."
# opencv-python-headless powers scripts/extract_frames.py; numpy comes with manim.
"${SUDO[@]}" pip3 install --quiet manim opencv-python-headless

echo "[manim/setup] Verifying installation..."
python3 -c "import manim; print('OK:', manim.__version__)"
manim --version

echo "[manim/setup] Done. LaTeX (texlive-latex-extra / texlive-fonts-extra /"
echo "[manim/setup] texlive-science) is NOT installed by default. Install on"
echo "[manim/setup] demand if a scene uses MathTex or Tex:"
echo "[manim/setup]   sudo apt-get install -y --no-install-recommends \\"
echo "[manim/setup]     texlive-latex-extra texlive-fonts-extra texlive-science"
