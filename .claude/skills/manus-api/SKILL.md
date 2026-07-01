---
name: manus-api
description: Programmatically create and manage Manus AI agent tasks via the Manus REST API - kick off autonomous research/build/automation jobs, poll for results, and register webhooks, instead of using the Manus web UI by hand. Use when the user wants to automate Manus, call the Manus API, or have Claude Code delegate a job to a Manus agent.
---

# Manus API

[Manus](https://manus.im) is a third-party autonomous AI agent platform: you give it a
prompt, it plans and executes a multi-step job (research, data analysis, building a
website, writing a report, etc.) in the background and returns results/files. The Manus
**API** lets you drive that agent programmatically — useful here for "money generation"
workflows where Claude Code wants to delegate an open-ended job (e.g. "research
competitor pricing," "build a landing page," "compile a market report") to a Manus agent
running asynchronously, then pull the results back in.

**Version policy: use v2 for everything new.** v1 (`/v1/...`, header `API_KEY`) is
deprecated and only documented here for maintaining existing v1 integrations — see
`references/v1-legacy.md`. Everything below is v2.

## Authentication

Base URL: `https://api.manus.ai`. Every v2 request needs exactly one auth header
(confirmed in `references/openapi_v2.json` under `components.securitySchemes`):

| Header | Value | Use case |
| --- | --- | --- |
| `x-manus-api-key` | your API key | your own scripts/integrations (this skill's default) |
| `Authorization` | `Bearer {access_token}` | third-party OAuth2 apps acting for a team user |

Get an API key from the Manus webapp: Settings -> API Integration -> Create API Key (up
to 50 keys/account, shown only once). Store it as the `MANUS_API_KEY` environment
variable — `scripts/manus_client.py` reads it from there by default.

Responses use an envelope: success is `{"ok": true, ...}`, failure is
`{"ok": false, "request_id": ..., "error": {"code": ..., "message": ...}}`. Rate limits
are per-user (shared across all your keys), e.g. `task.create`/`task.sendMessage` are
10/min, most GET endpoints are 100/min — see `references/v2-endpoints.md` for the full
table. A 429 returns `error.code: "rate_limited"`; back off with jitter and prefer
webhooks over polling in production.

## Quick start

```bash
export MANUS_API_KEY="sk-..."
python3 .claude/skills/manus-api/scripts/manus_client.py   # runs the built-in demo
```

Or from Python, using the helper client directly:

```python
import sys, time
sys.path.insert(0, ".claude/skills/manus-api/scripts")
from manus_client import ManusClient

client = ManusClient()  # reads MANUS_API_KEY from env

# Kick off an autonomous job
task = client.create_task(
    "Research the top 5 project management tools for a 5-person startup "
    "and summarize pricing in a markdown table."
)
task_id = task["task_id"]
print("Started:", task["task_url"])

# Poll until it finishes (production code should use webhooks instead - see below)
while True:
    detail = client.get_task(task_id)
    if detail["status"] in ("stopped", "error"):
        break
    time.sleep(5)

messages = client.list_messages(task_id, order="desc", limit=10)
print(messages)
```

To continue a conversation instead of starting a new task, call
`client.send_message(task_id, "follow-up instructions")`. To stop a runaway task, call
`client.stop_task(task_id)`.

## Webhooks (recommended for production)

Polling is fine for scripts, but production integrations should register a webhook so
Manus pushes `task_created` / `task_stopped` events to your endpoint instead:

```python
webhook = client.create_webhook("https://yourapp.example.com/manus-webhook")
```

Your endpoint must respond `2xx` within 10 seconds. Verify payload signatures using the
RSA public key from `client.get_webhook_public_key()` (RSA-SHA256) — see
`references/v2-endpoints.md` for the payload schema and verification notes.

## Reference material

- `references/v2-endpoints.md` — condensed, scannable reference for every v2 endpoint
  (method, path, params, example request/response, rate limit). Start here for anything
  beyond the quick start.
- `references/openapi_v2.json` — the authoritative machine-readable OpenAPI spec. Grep
  this for exact field names/types/enums when `v2-endpoints.md` isn't precise enough —
  it is ground truth over any prose summary, including this file.
- `references/v1-legacy.md` — v1 (deprecated) endpoint reference, only for maintaining
  existing v1 integrations. New work should not use v1.
- `scripts/manus_client.py` — `ManusClient` Python class wrapping the v2 REST API
  (`requests`-based, reads `MANUS_API_KEY` from env). Methods: `create_task`,
  `get_task`, `list_tasks`, `list_messages`, `send_message`, `confirm_action`,
  `stop_task`, `delete_task`, `update_task`, `create_webhook`, `list_webhooks`,
  `delete_webhook`, `get_webhook_public_key`. Raises `ManusAPIError` (with the response
  body in the message) on any non-2xx response.

## Key gotchas

- `task.create` defaults `agent_profile` to `manus-1.6`; `task.sendMessage` does **not**
  default it — omit the field to keep the task's current profile.
- Use `task_id: "agent-default-main_task"` as a shortcut to message the account's
  default IM agent instead of creating a new task.
- If the agent asks a plain question (`waiting_for_event_type: messageAskUser`), reply
  with `send_message`. For an action confirmation (e.g. "send this email?"), use
  `confirm_action` with the `event_id` from the task's `status_update` event instead.
- `webhook.create`, `webhook.list`, `webhook.delete`, `usage.*`, `agent.*`, and
  `website.*` endpoints are **API-key only** — they reject OAuth2 bearer tokens.
