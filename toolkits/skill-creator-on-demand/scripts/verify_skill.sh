#!/usr/bin/env bash
#
# verify_skill.sh — Prueft einen Skill-Ordner auf Vollstaendigkeit und offensichtliche Fehler.
#
# Nutzung: ./verify_skill.sh <pfad-zum-skill-ordner>
#
set -euo pipefail

TARGET="${1:-}"
[[ -z "$TARGET" ]] && { echo "Usage: $0 <skill-ordner>"; exit 1; }
[[ -d "$TARGET" ]] || { echo "Fehler: $TARGET ist kein Verzeichnis."; exit 1; }

ERRORS=0
warn()  { echo "  [WARNUNG] $1"; }
fail()  { echo "  [FEHLER]  $1"; ERRORS=$((ERRORS+1)); }
ok()    { echo "  [OK]      $1"; }

echo "Pruefe Skill: $TARGET"
echo "---"

SKILL_MD="$TARGET/SKILL.md"
if [[ ! -f "$SKILL_MD" ]]; then
  fail "SKILL.md fehlt."
else
  ok "SKILL.md vorhanden."

  if ! head -1 "$SKILL_MD" | grep -q '^---$'; then
    fail "SKILL.md beginnt nicht mit YAML-Frontmatter ('---')."
  else
    ok "YAML-Frontmatter-Start gefunden."
  fi

  if ! grep -q '^name:' "$SKILL_MD"; then
    fail "Frontmatter-Feld 'name' fehlt."
  else
    ok "Feld 'name' vorhanden."
  fi

  if ! grep -q '^description:' "$SKILL_MD"; then
    fail "Frontmatter-Feld 'description' fehlt."
  else
    DESC_LEN=$(grep '^description:' "$SKILL_MD" | wc -c)
    if [[ "$DESC_LEN" -lt 80 ]]; then
      warn "description ist sehr kurz (${DESC_LEN} Zeichen). Trigger-Erkennung braucht i.d.R. konkrete Beispielphrasen."
    else
      ok "Feld 'description' vorhanden und ausreichend detailliert."
    fi
  fi
fi

if [[ -d "$TARGET/scripts" ]]; then
  SCRIPT_COUNT=$(find "$TARGET/scripts" -type f | wc -l)
  if [[ "$SCRIPT_COUNT" -eq 0 ]]; then
    warn "scripts/ Ordner ist leer."
  else
    ok "scripts/ enthaelt $SCRIPT_COUNT Datei(en)."
    while IFS= read -r -d '' f; do
      if [[ "$f" == *.sh && ! -x "$f" ]]; then
        warn "Nicht ausfuehrbar: $f (chmod +x fehlt)"
      fi
    done < <(find "$TARGET/scripts" -type f -print0)
  fi
fi

echo "---"
# Grober Secret-Scan: haeufige Muster fuer hartcodierte Keys/Tokens
if grep -rEIn '(api[_-]?key|token|secret|password)\s*[:=]\s*["\047][A-Za-z0-9_\-]{12,}["\047]' "$TARGET" >/dev/null 2>&1; then
  fail "Moeglicher hartcodierter Secret/API-Key gefunden — bitte pruefen und durch Platzhalter/ENV-Variable ersetzen:"
  grep -rEIn '(api[_-]?key|token|secret|password)\s*[:=]\s*["\047][A-Za-z0-9_\-]{12,}["\047]' "$TARGET" | sed 's/^/            /'
else
  ok "Kein offensichtlicher hartcodierter Secret gefunden."
fi

echo "---"
if [[ "$ERRORS" -eq 0 ]]; then
  echo "Ergebnis: OK — Skill ist strukturell vollstaendig."
  exit 0
else
  echo "Ergebnis: $ERRORS Fehler gefunden — bitte beheben."
  exit 1
fi
