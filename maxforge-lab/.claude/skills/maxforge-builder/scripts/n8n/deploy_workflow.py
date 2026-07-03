#!/usr/bin/env python3
"""Deploy (create) an n8n workflow to a live instance via its public REST API,
and optionally activate it.

Requires:
  N8N_BASE_URL   e.g. https://your-instance.app.n8n.cloud  (no trailing /api)
  N8N_API_KEY    from n8n Settings -> n8n API -> Create API Key

Usage:
  python3 deploy_workflow.py my-workflow.json            # create only
  python3 deploy_workflow.py my-workflow.json --activate # create + activate

Uses only the Python standard library (urllib) — no extra dependencies.
Note: credentials referenced by the workflow must already exist in the target
n8n instance; the API imports the workflow but not its secrets.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def _api(base: str, key: str, path: str, method: str = "GET", payload=None):
    url = base.rstrip("/") + "/api/v1" + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-N8N-API-KEY", key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise SystemExit(f"n8n API {method} {path} failed: HTTP {e.code} — {detail}")
    except urllib.error.URLError as e:
        raise SystemExit(f"n8n API {method} {path} failed: {e.reason}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Deploy an n8n workflow via REST API.")
    ap.add_argument("workflow", help="Path to the workflow JSON.")
    ap.add_argument("--activate", action="store_true", help="Activate after creating.")
    ns = ap.parse_args()

    base = os.environ.get("N8N_BASE_URL")
    key = os.environ.get("N8N_API_KEY")
    if not base or not key:
        print("error: set N8N_BASE_URL and N8N_API_KEY environment variables.",
              file=sys.stderr)
        print("If you don't have API access, use Import from File in the n8n UI.",
              file=sys.stderr)
        return 2

    with open(ns.workflow, encoding="utf-8") as f:
        wf = json.load(f)

    # The create endpoint accepts name/nodes/connections/settings.
    payload = {
        "name": wf.get("name", "Imported workflow"),
        "nodes": wf["nodes"],
        "connections": wf.get("connections", {}),
        "settings": wf.get("settings", {"executionOrder": "v1"}),
    }
    created = _api(base, key, "/workflows", "POST", payload)
    wf_id = created.get("id")
    print(f"Created workflow: id={wf_id} name={created.get('name')!r}")

    if ns.activate and wf_id is not None:
        _api(base, key, f"/workflows/{wf_id}/activate", "POST")
        print(f"Activated workflow {wf_id}.")

    print(f"Open it at: {base.rstrip('/')}/workflow/{wf_id}")
    if "REPLACE_WITH_" in json.dumps(wf):
        print("NOTE: workflow still contains REPLACE_WITH_* placeholders — "
              "attach real credentials in the n8n UI before it will run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
