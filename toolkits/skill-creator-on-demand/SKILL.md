---
name: skill-creator-on-demand
description: Erstellt auf Zuruf komplette, funktionierende Claude Code Skills (SKILL.md + Scripts + Referenzdateien) fuer beliebige Aufgaben — analog zu install-superpowers und install-n8n-mcp-full-access. Nutze diesen Skill, wenn der User sagt "erstelle mir einen Skill fuer X", "baue einen Skill der Y kann", "ich brauche eine Automatisierung fuer Z", oder allgemein einen wiederkehrenden Workflow in einen wiederverwendbaren, selbst-triggernden Skill verwandeln will. Deckt sowohl reine Anleitungs-Skills als auch Skills mit ausfuehrbaren Scripts (bash/python/node) ab.
---

# Skill-Creator: On-Demand Skills bauen

Dieser Skill verwandelt eine Anforderung ("ich brauche X") in einen kompletten, sofort nutzbaren Claude Code Skill nach demselben Muster wie deine bestehenden Skills (`install-superpowers`, `install-n8n-mcp-full-access`).

## Ablauf

### 1. Anforderung klaeren (falls noetig)
Bevor gebaut wird, kurz pruefen:
- **Trigger**: Welche Formulierungen soll der Skill erkennen? (Fuer die `description` im Frontmatter entscheidend — Claude Code matcht Skills primaer ueber diesen Text, nicht ueber den Namen.)
- **Aktion**: Reine Anleitung (Markdown-Steps) oder braucht es ein ausfuehrbares Script?
- **Abhaengigkeiten**: API-Keys, CLI-Tools, Netzwerkzugriff noetig?

Bei eindeutigen Anfragen ("baue mir einen Skill der meine Sales-Zahlen aus meiner Funnel-Plattform zieht") direkt bauen, ohne nachzufragen — sinnvolle Annahmen treffen und im SKILL.md dokumentieren.

### 2. Skill-Ordner anlegen
```bash
./scripts/new_skill.sh --name <skill-name> --dest ~/.claude/skills
```
Das erzeugt aus `reference/template/` ein Grundgeruest:
```
<skill-name>/
├── SKILL.md              # Frontmatter + Anleitung
├── scripts/
│   └── main.sh            # Platzhalter fuer ausfuehrbare Logik
└── references/
    └── notes.md            # Platz fuer Detailwissen, das nicht ins SKILL.md muss
```

### 3. SKILL.md ausfuellen
Regeln aus `reference/best_practices.md` befolgen — insbesondere:
- **description** ist das Wichtigste im ganzen Skill. Muss konkrete Trigger-Phrasen und Anwendungsfaelle enthalten, keine vage Ein-Satz-Zusammenfassung.
- Scripts sind bevorzugt gegenueber langen Inline-Bash-Bloecken im SKILL.md — haelt den Skill wartbar.
- Idempotenz: Skripte sollten mehrfach ausfuehrbar sein, ohne kaputtzugehen (siehe `install.sh` Pattern aus n8n-mcp-Skill: bestehende Config erst entfernen, dann neu anlegen).
- Troubleshooting-Wissen in eine separate `references/troubleshooting.md` auslagern statt das Haupt-SKILL.md aufzublaehen.

### 4. Testen
```bash
./scripts/verify_skill.sh ~/.claude/skills/<skill-name>
```
Prueft: gueltiges YAML-Frontmatter, `name` und `description` vorhanden, Scripts ausfuehrbar (`chmod +x`), keine hartcodierten Secrets im Klartext.

### 5. Skill aktivieren
Skill-Ordner nach `~/.claude/skills/` (oder Projekt-`.claude/skills/`) kopieren. Claude Code liest Skills automatisch beim naechsten Start ein — kein Neustart des gesamten Systems noetig.

## Was dieser Skill NICHT tut

- Er kopiert keine proprietaeren Anthropic-Marketplace-Plugins (small-business:*, sales:*, etc.) — die sind serverseitig in Claude.ai/Cowork gebunden und nicht als Dateien exportierbar.
- Er erstellt keine MCP-Connector-Authentifizierung (OAuth-Flows) — dafuer bleibt der Weg ueber Claude.ai Settings > Connectors bzw. `claude mcp add` mit API-Keys (siehe `install-n8n-mcp-full-access` Skill als Beispiel).

Was er tut: dir fuer **jeden konkreten Anwendungsfall aus deinem Business** (Funnel-Reporting, Content-Batch-Produktion, Release-Checks, Monitoring, etc.) einen echten, lauffaehigen Skill nach demselben Qualitaetsstandard bauen wie die bereits vorhandenen.

## Beispiel-Anwendungsfaelle

Siehe `reference/skill_ideas.md` fuer eine Liste konkreter Skill-Vorschlaege (Funnel-Reporting, Content-Batch-Generierung, Release-/Update-Checks, Checkout-Monitoring etc.) — auf Zuruf wird jeder davon vollstaendig gebaut, nicht nur skizziert.
