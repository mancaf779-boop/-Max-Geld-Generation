---
name: install-n8n-mcp-full-access
description: Installiert und konfiguriert den vollständigen n8n-mcp Server (czlonkowski/n8n-mcp) für Claude Code, der Zugriff auf alle 2000+ n8n Nodes (Core + Community + AI-Nodes) gibt, um n8n-Workflows programmatisch zu bauen, validieren, aktualisieren und auszuführen. Nutze diesen Skill, wenn der User sagt "installiere n8n mcp", "gib mir Zugriff auf alle n8n plugins/nodes", "verbinde Claude Code mit n8n", "baue mir einen n8n Workflow", oder wenn eine bestehende n8n-mcp Installation kaputt/veraltet ist und neu aufgesetzt werden muss.
---

# n8n-MCP Full Access installieren

Dieser Skill installiert den Community-MCP-Server **czlonkowski/n8n-mcp** (nicht den nativen n8n Instance-Level-MCP-Connector, der nur Workflows *ausführt*). Dieser Server gibt Claude Code vollen Zugriff auf **alle n8n Node-Definitionen** (816 Core-Nodes + 1247 Community-Nodes, davon 1113 verifiziert, inkl. 265 AI-fähige Tool-Varianten), sodass Claude komplette Workflows von Grund auf bauen, validieren und deployen kann — nicht nur bestehende Workflows ausführen.

## Wann diesen Skill nutzen vs. den nativen n8n-Connector

| | Community n8n-mcp (dieser Skill) | Natives n8n Instance-Level-MCP |
|---|---|---|
| Zweck | Workflows **bauen/editieren** mit voller Node-Doku | Bestehende Workflows **ausführen/abfragen** |
| Node-Wissen | Alle 2000+ Nodes mit Properties, Beispielen, Docs | Keine Node-Doku |
| Client | Claude Code / Claude Desktop (CLI-Config) | Claude.ai, Claude Desktop, ChatGPT (OAuth) |
| Setup | `claude mcp add` + API-Key | Toggle in n8n Settings + OAuth-Connect |

Für "ich will mit Claude Code ganze Workflows bauen" → dieser Skill.
Für "ich will einen bestehenden Workflow aus dem Chat heraus anstoßen" → nativer Connector (siehe Chat-Verlauf).

## Voraussetzungen prüfen

```bash
node --version   # muss >= 18 sein
npx --version
claude --version # Claude Code CLI muss installiert sein
```

Falls Claude Code fehlt: `npm install -g @anthropic-ai/claude-code`

## Schritt 1: n8n API-Key holen

Der User muss das manuell in seiner n8n-Instanz tun (Cloud oder self-hosted):

1. n8n öffnen → Profilname unten links → **Settings**
2. Im linken Menü: **n8n API**
3. **Create an API Key** klicken, Label z.B. `mcp` vergeben, speichern
4. Key kopieren (wird nur einmal angezeigt!)
5. Die API-URL notieren — Format: `https://<deine-instanz>.app.n8n.cloud/api/v1` (Cloud) oder `http://localhost:5678/api/v1` (lokal/self-hosted)

Ohne Key funktioniert der Server auch (nur Doku/Validierungs-Tools), aber Workflows erstellen/aktualisieren/ausführen braucht den Key.

## Schritt 2: Installation ausführen

Nutze `scripts/install.sh` aus diesem Skill-Ordner:

```bash
./scripts/install.sh --url "https://deine-instanz.app.n8n.cloud/api/v1" --key "n8n_api_xxxxxxxx" --scope local
```

Parameter:
- `--url` — n8n API URL (Pflicht für vollen Funktionsumfang, sonst nur Doku-Tools)
- `--key` — n8n API-Key (Pflicht für vollen Funktionsumfang)
- `--scope` — `local` (nur du, Standard) oder `project` (Team, landet in `.mcp.json` im Projekt-Root)

Das Skript ist idempotent — bei bereits vorhandener `n8n-mcp` Config wird sie erst entfernt und sauber neu angelegt.

## Schritt 3: Verifizieren

```bash
claude mcp list
```

`n8n-mcp` sollte als "connected" erscheinen. Dann in einer Claude Code Session testen:

```
Nutze das n8n-mcp Tool tools_documentation um zu prüfen, welche Tools verfügbar sind, und liste danach meine bestehenden n8n Workflows mit n8n_list_workflows auf.
```

Bei Fehlern: API-URL muss auf `/api/v1` enden, Key muss gültig sein (n8n zeigt ihn sonst als abgelaufen/falsch formatiert an — besonders bei n8n Cloud gab es JWT-Format-Stolperfallen, siehe `references/troubleshooting.md`).

## Schritt 4: Best-Practice-Workflow-Instruktionen speichern (empfohlen)

Damit Claude Code bei jedem Workflow-Bau die Tool-Reihenfolge kennt (erst `tools_documentation`, dann `search_nodes`, dann `n8n_create_workflow`), die Datei `references/claude-md-snippet.md` an das Projekt-`CLAUDE.md` anhängen:

```bash
cat references/claude-md-snippet.md >> CLAUDE.md
```

## Danach: Workflows bauen lassen

Sobald verbunden, kannst du Claude Code direkt Workflows beschreiben lassen, z.B.:

```
Baue einen n8n Workflow: Webhook empfängt Lead-Daten → E-Mail mit Hunter.io validieren →
bei gültiger Mail personalisierte Nachricht mit Claude generieren → über SMTP versenden →
Status in einer n8n Data Table aktualisieren.
```

Claude Code nutzt dann die n8n-mcp Tools, um passende Nodes zu suchen (`search_nodes`), deren Properties zu prüfen (`get_node`), den Workflow zusammenzubauen (`n8n_create_workflow`) und zu validieren, bevor er live geschaltet wird.
