#!/usr/bin/env bash
# Renders a guide HTML file to dist/<name>.pdf using headless Chromium.
# Usage: ./build-pdf.sh [file.html]   (default: fokus-os-50plus.html)
set -euo pipefail
cd "$(dirname "$0")"
SRC="${1:-fokus-os-50plus.html}"
OUT="../dist/$(basename "${SRC%.html}").pdf"
CHROME="${CHROME:-$(command -v chromium || command -v chromium-browser || command -v google-chrome || echo /opt/pw-browsers/chromium)}"
if [ -d "$CHROME" ]; then
  CHROME="$(find "$CHROME" -maxdepth 3 -type f \( -name chrome -o -name chromium \) | head -1)"
fi
mkdir -p ../dist
"$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
  --print-to-pdf="$OUT" "file://$(pwd)/$SRC"
echo "PDF written to $OUT"
