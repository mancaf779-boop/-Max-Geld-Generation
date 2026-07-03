# Troubleshooting — n8n-mcp

## "Invalid API Key" trotz frisch generiertem Key (v.a. n8n Cloud)

n8n Cloud liefert Keys teils im JWT-Format. Typische Ursachen:
- Key wurde nicht vollstaendig kopiert (JWTs sind lang, Copy-Button nutzen statt manuell markieren)
- `N8N_API_URL` zeigt auf die falsche Domain (Cloud-Instanzen: `https://<subdomain>.app.n8n.cloud/api/v1`, NICHT die allgemeine `n8n.cloud` Domain)
- Key wurde in einer anderen n8n-Instanz/Workspace generiert als in `N8N_API_URL` referenziert

Fix: Key in n8n loeschen, neu erstellen, direkt per Copy-Button kopieren, `install.sh` erneut mit frischen Werten ausfuehren.

## "list_workflows" liefert leere Liste, obwohl Workflows existieren

- Pruefen, ob der API-Key auf denselben Workspace zeigt wie die UI, in der die Workflows sichtbar sind
- Bei self-hosted: `N8N_API_URL` muss exakt auf `/api/v1` enden, kein trailing slash danach

## Connection refused / Timeout

- Bei self-hosted lokal: laeuft n8n wirklich auf dem angegebenen Port (Standard 5678)?
- Bei self-hosted remote: Firewall/Reverse-Proxy blockiert eventuell `/api/v1` Pfad
- `curl -H "X-N8N-API-KEY: <key>" <N8N_API_URL>/workflows` zum isolierten Testen der API selbst, unabhaengig vom MCP-Server

## Erster `claude mcp list` zeigt "Failed to connect", zweiter "Connected"

Beim allerersten Start muss `npx` das `n8n-mcp` Paket erst herunterladen. Dieser
Download dauert laenger als der Health-Check-Timeout, deshalb schlaegt der erste
`claude mcp list` fehl — obwohl mit der Config alles stimmt. Fix: `install.sh`
registriert den Server bewusst mit `npx -y n8n-mcp` (nicht `npx n8n-mcp`), und
nach einmaligem Herunterladen (Paket ist dann im npx-Cache) verbindet der Server
zuverlaessig. Einfach `claude mcp list` ein zweites Mal ausfuehren, oder vorab
einmal `npx -y n8n-mcp </dev/null` laufen lassen, um den Cache zu waermen.

## Server erscheint nicht in `claude mcp list`

- Scope pruefen: `local` Registrierungen sind nur im aktuellen User-Kontext sichtbar, `project` nur wenn du dich im richtigen Projektordner befindest (`.mcp.json`)
- `claude mcp list --scope project` bzw. `--scope local` explizit gegenpruefen

## Von `local` auf `project` Scope wechseln (Team-Sharing)

```bash
claude mcp remove n8n-mcp --scope local
./scripts/install.sh --url "..." --key "..." --scope project
```

`--scope local` beim Remove ist wichtig: ein scope-loses `claude mcp remove
n8n-mcp` kann eine gleichnamige Registrierung in einem anderen Scope treffen.
Immer den Scope angeben, den du wirklich entfernen willst.

Achtung: Bei `--scope project` landet der API-Key in `.mcp.json` im Projekt-Root — **niemals in ein oeffentliches Repo committen**. Fuer Teams stattdessen Umgebungsvariablen-Referenzen statt Klartext-Keys pruefen, sobald n8n-mcp das unterstuetzt.
