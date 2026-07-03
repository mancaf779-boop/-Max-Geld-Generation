#!/usr/bin/env bash
#
# new_skill.sh — Scaffoldet einen neuen Claude Code Skill aus dem Template.
#
# Nutzung:
#   ./new_skill.sh --name mein-skill-name --dest ~/.claude/skills [--force]
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")/reference/template"

NAME=""
DEST="$HOME/.claude/skills"
FORCE=0

usage() {
  cat <<EOF
Usage: $0 --name <skill-name> [--dest <verzeichnis>] [--force]

  --name    Skill-Name in kebab-case, z.B. funnel-report
  --dest    Zielverzeichnis (Standard: ~/.claude/skills)
  --force   Ueberschreiben, falls Skill-Ordner schon existiert
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="$2"; shift 2 ;;
    --dest) DEST="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage ;;
    *) echo "Unbekannte Option: $1"; usage ;;
  esac
done

[[ -z "$NAME" ]] && { echo "Fehler: --name ist Pflicht."; usage; }

if [[ ! "$NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "Fehler: --name muss kebab-case sein (nur a-z, 0-9, Bindestriche), z.B. 'mein-skill-name'." >&2
  exit 1
fi

TARGET="$DEST/$NAME"

if [[ -d "$TARGET" && "$FORCE" -ne 1 ]]; then
  echo "Fehler: $TARGET existiert bereits. Mit --force ueberschreiben." >&2
  exit 1
fi

mkdir -p "$DEST"
rm -rf "$TARGET"
cp -r "$TEMPLATE_DIR" "$TARGET"

# Platzhalter im Template durch tatsaechlichen Namen ersetzen.
# Alle Dateien, nicht nur *.md — sonst bleibt __SKILL_NAME__ z.B. in
# scripts/main.sh unersetzt stehen.
if [[ "$(uname)" == "Darwin" ]]; then
  SED_INPLACE=(-i '')
else
  SED_INPLACE=(-i)
fi
find "$TARGET" -type f -exec sed "${SED_INPLACE[@]}" "s/__SKILL_NAME__/${NAME}/g" {} +

chmod +x "$TARGET/scripts/main.sh" 2>/dev/null || true

echo "-> Skill-Geruest erstellt: $TARGET"
echo ""
echo "Naechste Schritte:"
echo "  1. $TARGET/SKILL.md ausfuellen (description = wichtigster Teil!)"
echo "  2. $TARGET/scripts/main.sh mit echter Logik fuellen"
echo "  3. Verifizieren:  ./verify_skill.sh $TARGET"
