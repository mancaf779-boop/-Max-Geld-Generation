---
name: run-biz-automation
description: Build, start, and drive the biz-automation app — a dependency-free Node HTTP API for invoice triage, lead routing, and scheduled report generation. Use when asked to run, start, test, or smoke-test biz-automation, hit its API, generate a report, or verify the report scheduler.
---

biz-automation is a plain Node.js HTTP API (no framework, no npm install
needed) with three workflows — invoice triage, lead routing, report
generation/scheduling — sharing one process. Drive it via
`.claude/skills/run-biz-automation/driver.js`, which covers all three ways
a change here gets exercised: direct library calls, the CLI, and the real
HTTP server. All paths below are relative to `apps/biz-automation/`
(this skill's unit root), not the repo root.

## Prerequisites

None beyond Node itself — the app and driver use only Node's stdlib
(`node:http`, `node:child_process`, global `fetch`). Node 18+ required
for global `fetch`; this was built and verified on Node 22.

```bash
node --version   # must be >= 18
```

## Build

No build step, no `npm install` — there are zero dependencies.

## Run (agent path)

```bash
cd apps/biz-automation

# Fastest: import lib/ functions directly, no server, no port.
# Covers most PRs that touch src/lib/invoices.js, leads.js, or reports.js.
node .claude/skills/run-biz-automation/driver.js direct

# Runs `node src/cli.js report` and confirms it writes a report file.
node .claude/skills/run-biz-automation/driver.js cli

# Launches the real HTTP server on a scratch port, POSTs real payloads to
# every route (chaining invoice + lead output into report generation, the
# way a real orchestration would), confirms the scheduler fires on its own,
# then kills the server. Takes ~2s (most of it a deliberate wait for one
# scheduler tick).
node .claude/skills/run-biz-automation/driver.js server

# All three in sequence (default if no subcommand given):
node .claude/skills/run-biz-automation/driver.js all
```

Exit code 0 = every check passed; 1 = see stderr for which `FAIL:` line
and why. Each subcommand prints a `PASS:`/`FAIL:` line per assertion —
read those, not just the exit code, to see what was actually verified.

| subcommand | what it checks |
|---|---|
| `direct` | `processInvoices`/`routeLeads`/`generateReport` called directly against the sample data in `data/`. |
| `cli` | `node src/cli.js report` exits 0, prints the report, and writes a new file under `reports/` (gitignored — generated output, not source). |
| `server` | Full HTTP round trip on every route (`/health`, `/invoices/process`, `/leads/route`, `/reports/generate`, `/reports/latest`, an unknown route → 404), plus a live scheduler tick. |

## Run (human path)

```bash
cd apps/biz-automation
PORT=8080 node src/server.js
# → "biz-automation listening on :8080". Ctrl-C to stop.

curl -X POST localhost:8080/invoices/process -H 'Content-Type: application/json' -d @data/sample-invoices.json
curl -X POST localhost:8080/leads/route -H 'Content-Type: application/json' -d @data/sample-leads.json
curl -X POST localhost:8080/reports/generate -H 'Content-Type: application/json' -d '{}'   # falls back to data/sample-sources.json
curl localhost:8080/reports/latest

# scheduled reports (writes data/../reports every REPORT_SCHEDULE_MS):
REPORT_SCHEDULE_MS=3600000 PORT=8080 node src/server.js

# CLI, one-shot or on a schedule:
node src/cli.js report                    # writes reports/report-<ts>.md, prints it
node src/cli.js report --schedule 3600000 # foreground loop, Ctrl-C to stop
```

## Test

```bash
node --test   # NOT `node --test test/` — passing the dir path as an arg
              # makes Node try to `require()` it as a module and throw
              # MODULE_NOT_FOUND. Bare `--test` auto-discovers test/.
```

2 suites pass (`test/invoices.test.js`, `test/leads.test.js`). These are a
sanity check on the pure logic — `driver.js server`/`cli` are what actually
prove the app runs.

## Gotchas

- **`node --test test/` fails with `MODULE_NOT_FOUND`** on this Node
  version (v22.22.2) — it tries to resolve `test/` as a module specifier,
  not a directory to scan. Run bare `node --test`; it auto-discovers
  `test/**/*.test.js` from the cwd.
- **`POST /reports/generate` with an empty body (`{}`) falls back to
  `data/sample-sources.json`**, it does not error. `Object.keys(body).length
  === 0` is the check in `src/server.js` — if you add a source field named
  after nothing (e.g. `{}` with a stray key), you'll silently stop getting
  the sample fallback.
- **The scheduler check in `driver.js server` needs a real ~1.5s wait.**
  `REPORT_SCHEDULE_MS=1200` is set for the smoke test specifically so one
  tick fits inside a short timeout — don't shorten the wait below the
  interval or you'll get a flaky `FAIL: scheduler populates /reports/latest`
  even though the scheduler is fine.
- **`reports/` is gitignored** (`apps/*/reports/` in the repo-root
  `.gitignore`) — it's generated output from the CLI/scheduler, not source.
  Don't `git add -f` it back in.

## Troubleshooting

- **`Error: Cannot find module '.../test'` when running tests**: you ran
  `node --test test/`. Drop the path argument — see Gotchas.
- **`driver.js server` reports `FAIL: server becomes healthy within 8s`**:
  something on the box is already bound to the port the driver picked
  (`8901 + random(0..500)`) — rerun; the driver picks a new random port
  each time so a collision is transient, not a real failure of the app.
- **`EADDRINUSE` running the human-path server manually**: an earlier
  `node src/server.js` from a previous session is still running — find it
  with `ps aux | grep src/server.js` and kill it; the driver always kills
  its own child on exit, but a manually-backgrounded one won't clean
  itself up.
