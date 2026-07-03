---
name: run-maxforge-lab
description: Build, load, and drive the Maxforge Lab Claude Code plugin (maxforge-lab) — run its SessionStart hook, launch a headless Claude Code session with the plugin loaded, and verify that skills (researching-topics, analyzing-data, designing-workflows, orchestrating-tasks, using-maxforge) actually auto-trigger. Use when asked to run, test, smoke-test, or verify this plugin/skill package, or to check that the auto-trigger bootstrap works.
---

Maxforge Lab isn't an app with a GUI or a server — it's a Claude Code plugin
(a SessionStart hook + five skills, no runtime, no build step). "Running" it
means loading it into a real headless Claude Code session and observing two
things: the hook fires and injects the `using-maxforge` bootstrap, and the
agent actually invokes the right `maxforge-lab:<skill>` for a matching prompt.
Drive it with `.claude/skills/run-maxforge-lab/driver.py` — all paths below
are relative to the repo root.

## Prerequisites

Nothing to install. The plugin is plain Markdown + one bash hook script.
You need the `claude` CLI on PATH (it already is, in this environment) and
Python 3 (also already present — the driver only uses the stdlib).

```bash
which claude python3   # both must resolve; nothing else is required
```

## Build

No build step. `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`
at the repo root make this directory a loadable plugin as-is.

## Run (agent path)

Two subcommands, cheapest first:

```bash
# 1. Fast, free: run the SessionStart hook directly, no API calls.
python3 .claude/skills/run-maxforge-lab/driver.py check

# 2. Real end-to-end: launch a headless session with the plugin loaded,
#    stream-parse tool_use events, and confirm the right skill fires.
python3 .claude/skills/run-maxforge-lab/driver.py smoke \
  "Analyze this: month,price,units | Jan,10,100 | Feb,12,90 | Mar,15,70. Does raising price hurt sales?" \
  analyzing-data --timeout 60
```

`smoke` takes `"<prompt>" [expected_skill_substring] [--timeout SECONDS]`. It
runs `claude -p "<prompt>" --plugin-dir <repo-root> --output-format stream-json --verbose`,
reads the JSONL stream line by line, and **stops the session as soon as it
sees a `Skill` tool_use whose name starts with `maxforge-lab:`** (matching
`expected_skill_substring` if given) — it does not wait for the full turn to
finish. Exit code 0 = PASS, 1 = FAIL. Every `tool_use` seen along the way is
printed, so you can see exactly what the agent reached for.

| subcommand | what it does |
|---|---|
| `check` | Runs `hooks/session-start` directly via `bash`, parses its JSON, confirms `additionalContext`/`hookSpecificOutput` contains the `using-maxforge` bootstrap. No network, no model call. |
| `smoke <prompt> [skill] [--timeout N]` | Launches a real `claude -p --plugin-dir .` session and verifies the hook fired *and* the expected skill auto-triggered. Default timeout 60s. |

To try a different skill trigger, swap the prompt/expected pair, e.g.:

```bash
python3 .claude/skills/run-maxforge-lab/driver.py smoke \
  "Look into whether Rust or Go is the better choice for a new CLI tool in 2026" \
  researching-topics --timeout 30
```

## Run (human path)

The Quickstart from the README — same idea, but you read the whole reply
instead of stopping early:

```bash
claude -p "Analyze this: month,price,units | Jan,10,100 | Feb,12,90 | Mar,15,70. Does raising price hurt sales?" \
  --plugin-dir .
```

## Test

There is no separate test suite — the `smoke` subcommand above **is** the
test: it's the only way to verify "does the hook fire and does the right
skill auto-trigger" outside of a live conversation. Run `check` then one
`smoke` call per skill you touched before calling a change to
`hooks/session-start`, any `SKILL.md` frontmatter, or `.claude-plugin/*.json`
done.

## Gotchas

- **`hooks/run-hook.cmd` has no shebang — it's a Windows/Unix polyglot**
  (`: << 'CMDBLOCK' ... CMDBLOCK` skips the batch half on Unix). Running it
  with `subprocess.run([path, ...])` in Python fails with `Exec format
  error` because Python calls `execve` directly and there's no interpreter
  line. Interactive `bash` gets away with `./hooks/run-hook.cmd` because on
  `ENOEXEC` bash silently re-execs the file under `/bin/sh` — a courtesy
  Python's `subprocess` doesn't extend. Always invoke it as
  `bash hooks/run-hook.cmd session-start`, matching what
  `driver.py check` does.
- **Don't let `smoke` wait for full completion on research-shaped prompts.**
  A prompt that triggers `researching-topics` makes the agent dispatch real
  parallel subagents and `WebSearch` calls and can run for many minutes to
  a final answer. The driver deliberately stops the moment it observes the
  `Skill` tool_use — that's the entire signal you need (auto-trigger
  worked), and it's what keeps the smoke test fast. Don't "improve" this by
  waiting for the `result` event.
- **`--plugin-dir .` must point at the repo root, not the skill dir.** The
  driver resolves it via `git rev-parse --show-toplevel`, not `cwd`, so it
  works no matter where you invoke it from.

## Troubleshooting

- **`OSError: [Errno 8] Exec format error` on `run-hook.cmd`**: you (or code
  you wrote) called it directly via `subprocess`/`execve` instead of through
  a shell. Prefix with `bash`.
- **`smoke` reports FAIL: hook fired, but no maxforge-lab skill … was
  invoked**: either the prompt doesn't actually match any skill's
  `description` trigger phrases, or the timeout is too short for a slower
  model — try a prompt closer to the skill's own examples (see each
  `skills/*/SKILL.md` frontmatter) or raise `--timeout`.
- **`smoke` reports FAIL: never observed a SessionStart hook event**: the
  plugin didn't load — check you passed `--plugin-dir <repo-root>` (the
  driver does this for you) and that `.claude-plugin/plugin.json` still
  parses as valid JSON.
