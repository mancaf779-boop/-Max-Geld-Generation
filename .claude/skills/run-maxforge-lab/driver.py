#!/usr/bin/env python3
"""Driver for the Maxforge Lab Claude Code plugin.

This is not an app with a GUI or a server — it's a plugin: a SessionStart
hook plus five skills. "Running" it means loading it into a real headless
Claude Code session and observing that (a) the hook fires and injects the
using-maxforge bootstrap, and (b) the agent actually invokes the right
maxforge-lab:<skill> in response to a matching prompt.

Usage:
    driver.py check
        Run the SessionStart hook script directly (no API calls) and
        verify its JSON shape. Fast, free, good first sanity check.

    driver.py smoke "<prompt>" [expected_skill] [--timeout SECONDS]
        Launch `claude -p --plugin-dir <repo>` with the given prompt,
        stream-parse the JSONL output, and stop as soon as the agent
        either invokes a maxforge-lab:<skill> (PASS) or the timeout
        elapses without one (FAIL). Prints every tool_use seen along
        the way. Exits 0 on PASS, 1 on FAIL.

        expected_skill, if given, is matched as a substring of the
        invoked skill name (e.g. "analyzing-data").

        Default timeout is 60s. Skills like researching-topics dispatch
        real web-search subagents and can run for many minutes to full
        completion — the driver does not wait for that; it only waits
        long enough to observe the Skill tool_use event, then kills the
        session. That's enough to prove auto-trigger is working.

Examples (run from the repo root):
    .claude/skills/run-maxforge-lab/driver.py check
    .claude/skills/run-maxforge-lab/driver.py smoke \\
        "Analyze this: month,price,units | Jan,10,100 | Feb,12,90 | Mar,15,70. Does raising price hurt sales?" \\
        analyzing-data
"""
import json
import os
import subprocess
import sys
import time

REPO_ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], cwd=os.path.dirname(__file__),
    capture_output=True, text=True, check=True,
).stdout.strip()


def cmd_check():
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=REPO_ROOT)
    hook = os.path.join(REPO_ROOT, "hooks", "run-hook.cmd")
    result = subprocess.run(
        ["bash", hook, "session-start"], cwd=REPO_ROOT, env=env,
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        print(f"FAIL: hook exited {result.returncode}\nstderr: {result.stderr}")
        return 1
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"FAIL: hook did not print valid JSON: {e}\nstdout: {result.stdout[:500]}")
        return 1
    ctx = (
        payload.get("hookSpecificOutput", {}).get("additionalContext")
        or payload.get("additional_context")
        or payload.get("additionalContext")
        or ""
    )
    if "using-maxforge" not in ctx or "EXTREMELY_IMPORTANT" not in ctx:
        print(f"FAIL: hook JSON present but missing expected bootstrap markers.\nGot: {json.dumps(payload)[:500]}")
        return 1
    print("PASS: hook emits valid JSON with the using-maxforge bootstrap injected.")
    print(f"  keys: {list(payload.keys())}")
    print(f"  additionalContext length: {len(ctx)} chars")
    return 0


def cmd_smoke(prompt, expected_skill=None, timeout=60):
    args = [
        "claude", "-p", prompt,
        "--plugin-dir", REPO_ROOT,
        "--output-format", "stream-json",
        "--verbose",
    ]
    print(f"$ (cd {REPO_ROOT} && {' '.join(args[:3])} ... --plugin-dir . --output-format stream-json --verbose)")
    proc = subprocess.Popen(
        args, cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    deadline = time.time() + timeout
    hook_seen = False
    matched_skill = None
    try:
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = d.get("type")
            if t == "system" and d.get("subtype") in ("hook_started", "hook_response"):
                hook_seen = True
            elif t == "assistant":
                for block in d.get("message", {}).get("content", []):
                    if block.get("type") == "tool_use":
                        name = block.get("name")
                        inp = block.get("input", {})
                        print(f"  TOOL_USE {name} {json.dumps(inp)[:160]}")
                        if name == "Skill":
                            skill = inp.get("skill", "")
                            if skill.startswith("maxforge-lab:"):
                                if expected_skill is None or expected_skill in skill:
                                    matched_skill = skill
                                    raise StopIteration
    except StopIteration:
        pass
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    if not hook_seen:
        print("FAIL: never observed a SessionStart hook event in the stream.")
        return 1
    if matched_skill is None:
        print(f"FAIL: hook fired, but no maxforge-lab skill matching {expected_skill!r} was invoked within {timeout}s.")
        return 1
    print(f"PASS: hook fired and agent invoked '{matched_skill}'.")
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    sub = argv[0]
    if sub == "check":
        return cmd_check()
    if sub == "smoke":
        rest = argv[1:]
        timeout = 60
        if "--timeout" in rest:
            i = rest.index("--timeout")
            timeout = int(rest[i + 1])
            del rest[i:i + 2]
        if not rest:
            print("usage: driver.py smoke \"<prompt>\" [expected_skill] [--timeout N]")
            return 1
        prompt = rest[0]
        expected = rest[1] if len(rest) > 1 else None
        return cmd_smoke(prompt, expected, timeout)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
