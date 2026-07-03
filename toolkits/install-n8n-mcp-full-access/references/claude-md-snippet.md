## n8n-mcp Workflow-Building Konventionen

Beim Bauen oder Aendern von n8n-Workflows ueber n8n-mcp immer in dieser Reihenfolge vorgehen:

1. **`tools_documentation`** zuerst aufrufen, falls unklar ist, welches Tool passt.
2. **`search_nodes`** um passende Nodes zu finden (`source: 'verified'` fuer gepruefte Community-Nodes bevorzugen, `includeExamples: true` fuer Referenz-Configs).
3. **`get_node`** im Modus `detail: 'standard'` pruefen, bevor ein Node in den Workflow eingebaut wird — spart Fehlversuche durch falsche Properties.
4. Workflow mit **`n8n_create_workflow`** anlegen (oder **`n8n_update_partial_workflow`** fuer punktuelle Aenderungen an bestehenden Workflows — deutlich token-effizienter als volles Replace).
5. Vor dem Live-Schalten: Validierungs-Tools nutzen, Workflow **nicht** automatisch veroeffentlichen, sondern dem User zur Pruefung vorlegen.
6. `execute_workflow` nutzt standardmaessig die **produktive** (veroeffentlichte) Version. Fuer Tests an der unveroeffentlichten Version den manuellen Ausfuehrungsmodus explizit anfordern.

Komplexe Workflows in Etappen bauen (erst Happy Path, danach Fehlerbehandlung/Branches ergaenzen) statt alles in einem Schritt zu beschreiben.
