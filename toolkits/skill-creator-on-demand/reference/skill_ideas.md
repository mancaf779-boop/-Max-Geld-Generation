# Skill-Ideen

Konkrete Kandidaten-Typen, die sich mit `new_skill.sh` sofort scaffolden und
dann voll ausbauen lassen. Auf Zuruf ("baue mir Skill Nr. 3") wird jeder davon
komplett fertiggestellt, nicht nur skizziert. Die Beispiele sind bewusst
generisch gehalten — ersetze sie durch deine eigenen Anwendungsfälle.

1. **funnel-report** — Zieht Verkaufszahlen/Conversion aus deiner Funnel-/Shop-Plattform (API oder CSV-Export) und baut einen Tages-/Wochenreport.
2. **pin-batch** — Generiert eine Serie von Social-Media-/Pinterest-Designs (Canva-Connector oder HTML/SVG-Templates) im eigenen Brand-Design.
3. **release-check** — Prüft regelmäßig auf neue Commits/Releases in einem Repo und verbundenen SDKs, fasst Breaking Changes zusammen.
4. **plugin-sync** — Hält installierte Claude-Code-Plugins aktuell, erkennt Versions-Drift.
5. **checkout-monitor** — Testet regelmäßig einen Checkout-/Kauf-Flow end-to-end, meldet kaputte Links/Preise.
6. **n8n-workflow-backup** — Exportiert regelmäßig alle n8n-Workflows als JSON-Backup (nutzt n8n-mcp oder REST API direkt), versioniert in Git.
7. **toolkit-extend** — Erweitert ein bestehendes Plugin/Toolkit um neue Agents/Commands nach Bedarf.

Jede Idee lässt sich sofort umsetzen:
```bash
./scripts/new_skill.sh --name funnel-report
```
Danach SKILL.md + main.sh mit der konkreten Logik füllen — sag einfach, welchen davon ich zuerst voll ausbauen soll.
