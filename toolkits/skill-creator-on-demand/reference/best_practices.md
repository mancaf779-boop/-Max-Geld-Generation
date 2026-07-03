# Best Practices für Claude Code Skills

## Die `description` entscheidet alles
Claude Code / Claude wählt Skills anhand der `description` im Frontmatter aus, nicht anhand des `name`. Faustregeln:
- Konkrete Trigger-Phrasen einbauen: "Nutze diesen Skill wenn der User sagt X, Y, Z"
- Abgrenzung zu ähnlichen Skills nennen (wann NICHT triggern)
- Lieber zu lang/detailliert als zu vage — ein Ein-Satz-Description wie "Hilft bei Automatisierung" triggert nie zuverlässig

Schlecht: `description: Hilft bei n8n`
Gut: `description: Installiert den n8n-mcp Server für vollen Node-Zugriff. Nutze bei "installiere n8n mcp", "baue mir einen n8n Workflow", oder wenn eine bestehende Installation kaputt ist.`

## Struktur
```
skill-name/
├── SKILL.md          # Pflicht: Frontmatter + kurze Anleitung
├── scripts/           # Ausführbare Logik, keine langen Bash-Blöcke im SKILL.md
└── references/        # Detailwissen, Troubleshooting — wird nur bei Bedarf gelesen
```

Das Haupt-SKILL.md sollte kurz und scanbar bleiben. Alles, was nur in Edge Cases gebraucht wird, gehört in `references/`.

## Idempotenz
Jedes Setup-Script sollte mehrfach ausführbar sein, ohne kaputtzugehen. Pattern: bestehenden Zustand prüfen/entfernen, dann sauber neu anlegen (siehe `install.sh` in `install-n8n-mcp-full-access`).

## Secrets
Nie API-Keys/Tokens hartcodiert ins SKILL.md oder Scripts schreiben. Immer als Parameter/Umgebungsvariable übergeben lassen. `verify_skill.sh` scannt grob danach, ersetzt aber keine sorgfältige manuelle Prüfung.

## Wann Script vs. reine Anleitung
- **Nur Anleitung (kein Script)**: Wenn der Skill hauptsächlich Wissen/Prozess vermittelt, das der User oder Claude selbst ausführt (z.B. "wie schreibe ich gute UX-Copy")
- **Mit Script**: Wenn es wiederholbare, mechanische Schritte gibt (Installation, API-Calls, Datei-Generierung) — dann Script bauen statt Claude die Befehle jedes Mal neu tippen zu lassen
