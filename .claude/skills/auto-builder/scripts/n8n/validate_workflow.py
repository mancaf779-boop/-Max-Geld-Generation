#!/usr/bin/env python3
"""Validate an n8n workflow JSON file.

Checks:
  - file is valid JSON with nodes[] and connections{}
  - every node has id/name/type
  - every connection references a node that exists
  - warns on leftover REPLACE_WITH_* credential/id placeholders

Exit code 0 = valid (warnings allowed), 1 = invalid.

Usage: python3 validate_workflow.py my-workflow.json
"""
import json
import sys


def validate(path: str) -> int:
    try:
        with open(path, encoding="utf-8") as f:
            wf = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"INVALID: cannot load JSON — {e}")
        return 1

    errors, warnings = [], []

    nodes = wf.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        print("INVALID: missing or empty 'nodes' array")
        return 1

    names = set()
    for i, node in enumerate(nodes):
        for key in ("id", "name", "type"):
            if not node.get(key):
                errors.append(f"node #{i} missing '{key}'")
        if node.get("name"):
            names.add(node["name"])

    conns = wf.get("connections", {})
    if not isinstance(conns, dict):
        errors.append("'connections' must be an object")
    else:
        for src, outputs in conns.items():
            if src not in names:
                errors.append(f"connection source '{src}' is not a node name")
            for group in outputs.get("main", []):
                for link in group or []:
                    tgt = link.get("node")
                    if tgt not in names:
                        errors.append(f"connection target '{tgt}' is not a node name")

    blob = json.dumps(wf)
    if "REPLACE_WITH_" in blob:
        n = blob.count("REPLACE_WITH_")
        warnings.append(f"{n} 'REPLACE_WITH_*' placeholder(s) — fill these in n8n before running")

    for w in warnings:
        print(f"WARN: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"INVALID: {len(errors)} error(s)")
        return 1

    print(f"VALID: {len(nodes)} nodes, {len(conns)} connection source(s)"
          + (f", {len(warnings)} warning(s)" if warnings else ""))
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 validate_workflow.py <workflow.json>", file=sys.stderr)
        return 2
    return validate(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
