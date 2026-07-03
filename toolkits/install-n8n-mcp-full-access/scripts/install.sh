#!/usr/bin/env bash
#
# install.sh — Registriert den n8n-mcp Server (czlonkowski/n8n-mcp) bei Claude Code.
# Gibt Claude vollen Zugriff auf alle n8n Nodes (Core + Community + AI-Tools),
# um Workflows programmatisch zu bauen, validieren, updaten und auszufuehren.
#
# Nutzung:
#   ./install.sh --url "https://deine-instanz.app.n8n.cloud/api/v1" --key "n8n_api_xxx" [--scope local|project]
#   ./install.sh                     # nur Doku/Validierungs-Tools, ohne n8n API-Zugriff
#
set -euo pipefail

SERVER_NAME="n8n-mcp"
SCOPE="local"
N8N_API_URL=""
N8N_API_KEY=""

usage() {
  cat <<EOF
Usage: $0 [--url <n8n_api_url>] [--key <n8n_api_key>] [--scope local|project]

  --url     n8n API URL, z.B. https://deine-instanz.app.n8n.cloud/api/v1
            (muss auf /api/v1 enden). Ohne diese Option: nur Doku-Tools.
  --key     n8n API Key (Settings -> n8n API -> Create an API Key)
  --scope   local (Standard, nur du) oder project (geteilt via .mcp.json)
  -h        diese Hilfe anzeigen
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url) N8N_API_URL="$2"; shift 2 ;;
    --key) N8N_API_KEY="$2"; shift 2 ;;
    --scope) SCOPE="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unbekannte Option: $1"; usage ;;
  esac
done

if [[ "$SCOPE" != "local" && "$SCOPE" != "project" ]]; then
  echo "Fehler: --scope muss 'local' oder 'project' sein." >&2
  exit 1
fi

if [[ -n "$N8N_API_URL" && "$N8N_API_URL" != */api/v1 ]]; then
  echo "Warnung: --url endet nicht auf /api/v1 (aktuell: $N8N_API_URL)." >&2
  echo "         n8n's REST API erwartet i.d.R. .../api/v1 — bitte pruefen." >&2
fi

# --- Voraussetzungen pruefen ---------------------------------------------
command -v node >/dev/null 2>&1 || { echo "Fehler: Node.js ist nicht installiert (>=18 benoetigt)."; exit 1; }
command -v npx  >/dev/null 2>&1 || { echo "Fehler: npx ist nicht verfuegbar (kommt mit Node.js)."; exit 1; }
command -v claude >/dev/null 2>&1 || {
  echo "Fehler: Claude Code CLI ('claude') ist nicht installiert."
  echo "        Installiere mit: npm install -g @anthropic-ai/claude-code"
  exit 1
}

NODE_MAJOR="$(node --version | sed 's/^v//' | cut -d. -f1)"
if [[ "$NODE_MAJOR" -lt 18 ]]; then
  echo "Fehler: Node.js Version zu alt ($(node --version)). Mindestens v18 benoetigt." >&2
  exit 1
fi

# --- Bestehende Registrierung sauber entfernen (idempotent) --------------
if claude mcp list 2>/dev/null | grep -q "^${SERVER_NAME}"; then
  echo "-> Entferne bestehende ${SERVER_NAME} Registrierung..."
  claude mcp remove "$SERVER_NAME" --scope "$SCOPE" >/dev/null 2>&1 || \
    claude mcp remove "$SERVER_NAME" >/dev/null 2>&1 || true
fi

# --- Neu registrieren ------------------------------------------------------
echo "-> Registriere ${SERVER_NAME} bei Claude Code (scope: ${SCOPE})..."

ARGS=(mcp add "$SERVER_NAME"
  --scope "$SCOPE"
  -e MCP_MODE=stdio
  -e LOG_LEVEL=error
  -e DISABLE_CONSOLE_OUTPUT=true
)

if [[ -n "$N8N_API_URL" && -n "$N8N_API_KEY" ]]; then
  ARGS+=(-e "N8N_API_URL=${N8N_API_URL}" -e "N8N_API_KEY=${N8N_API_KEY}")
  echo "   Modus: VOLLER Zugriff (Doku + Workflow erstellen/aendern/ausfuehren)"
else
  echo "   Modus: NUR Doku/Validierung (kein N8N_API_URL/KEY angegeben)"
  echo "   Fuer vollen Zugriff spaeter erneut mit --url und --key ausfuehren."
fi

# -y (--yes) laesst npx das Paket beim ersten Start ohne Rueckfrage installieren.
# Ohne -y schlaegt der erste `claude mcp list` Health-Check fehl, weil der npx-
# Download beim ersten Mal laenger dauert als der Health-Check-Timeout (Server
# erscheint faelschlich als "Failed to connect"). Siehe references/troubleshooting.md.
ARGS+=(-- npx -y n8n-mcp)

claude "${ARGS[@]}"

echo ""
echo "-> Fertig. Pruefen mit:  claude mcp list"
echo "-> Test in einer Claude Code Session:"
echo '   "Nutze tools_documentation um die verfuegbaren n8n-mcp Tools zu zeigen."'
