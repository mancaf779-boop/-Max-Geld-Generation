#!/usr/bin/env python3
"""Generic executor: run a local artifact, auto-detecting its runtime.

Supports Python (.py), Node (.js/.mjs), and shell (.sh) scripts. Streams the
child's stdout/stderr and returns its exit code.

Usage:
  python3 run.py path/to/script.py
  python3 run.py path/to/script.js -- --flag value     # args after -- go to the script
  python3 run.py path/to/script.sh --dry-run           # print the command, don't run

For n8n workflow JSON, use scripts/n8n/deploy_workflow.py instead.
"""
import argparse
import os
import shutil
import subprocess
import sys

RUNNERS = {
    ".py": ["python3"],
    ".js": ["node"],
    ".mjs": ["node"],
    ".sh": ["bash"],
}


def main() -> int:
    # Split on the first literal "--": everything after it is passed to the
    # target script verbatim, so run.py's own flags work in any position.
    argv = sys.argv[1:]
    if "--" in argv:
        sep = argv.index("--")
        own, extra = argv[:sep], argv[sep + 1:]
    else:
        own, extra = argv, []

    ap = argparse.ArgumentParser(description="Run a local script, auto-detecting runtime.")
    ap.add_argument("artifact", help="Path to the script to run.")
    ap.add_argument("--dry-run", action="store_true", help="Print the command instead of running.")
    ns = ap.parse_args(own)

    path = ns.artifact
    if not os.path.isfile(path):
        print(f"error: not a file: {path}", file=sys.stderr)
        return 2

    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        print("This looks like an n8n workflow. Use scripts/n8n/deploy_workflow.py "
              "or Import from File in n8n.", file=sys.stderr)
        return 2
    if ext not in RUNNERS:
        print(f"error: unsupported extension {ext!r} (supported: {', '.join(RUNNERS)})",
              file=sys.stderr)
        return 2

    runner = RUNNERS[ext]
    if shutil.which(runner[0]) is None:
        print(f"error: {runner[0]} is not installed / not on PATH.", file=sys.stderr)
        return 127

    cmd = runner + [path] + extra

    if ns.dry_run:
        print("would run:", " ".join(cmd))
        return 0

    print(f"$ {' '.join(cmd)}", flush=True)
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
