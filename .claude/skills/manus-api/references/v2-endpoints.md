# Manus API v2 — Endpoint Reference

Base URL: `https://api.manus.ai`. Auth: `x-manus-api-key: <key>` header (API key) or
`Authorization: Bearer <access_token>` (OAuth2). This file is condensed from the prose
`.mdx` docs and cross-checked against `openapi_v2.json` (trust the JSON spec if
anything here looks off — grep it by path, e.g. `"/v2/task.create"`).

Response envelope: `{"ok": true, "request_id": "...", ...}` on success,
`{"ok": false, "request_id": "...", "error": {"code": "...", "message": "..."}}` on
failure. List endpoints paginate with `cursor` / `next_cursor` / `has_more`.

## Tasks

### `POST /v2/task.create` — 10/min
Start a new autonomous agent task. OAuth scope: `create_task` or `manage_all_tasks`.

Request body:
```json
{
  "message": {"content": "Research X and summarize as a table", "connectors": [], "enable_skills": [], "force_skills": []},
  "project_id": "proj_abc",
  "locale": "en",
  "interactive_mode": false,
  "hide_in_task_list": false,
  "share_visibility": "private",
  "agent_profile": "manus-1.6",
  "structured_output_schema": {"type": "object", "properties": {...}}
}
```
Only `message.content` is required. `agent_profile` enum: `manus-1.6` (default),
`manus-1.6-lite`, `manus-1.6-max`. `share_visibility` enum: `private` (default), `team`,
`public`.

Response:
```json
{"ok": true, "request_id": "req_...", "task_id": "task_abc123", "task_title": "...", "task_url": "https://manus.im/app/task_abc123", "share_visibility": "private"}
```
`share_url` is only present when `share_visibility != "private"`.

File attachments go in `message.content` as an array of `ContentPart` objects
referencing `file_id` (from `file.upload`, ≤512 MB), `file_url` (Manus downloads it,
≤20 MB), or `file_data` (inline base64, ≤20 MB decoded).

### `GET /v2/task.detail` — 100/min
Params: `task_id` (required; supports shortcut `agent-default-main_task`).
Returns a `Task` object: `id`, `status` (`running`|`stopped`|`waiting`|`error`),
`created_at`, `updated_at`, `task_type` (`standard`|`project`|`agent_subtask`),
`share_visibility`, `title`, `credit_usage`, `task_url`, `created_by_api_key`.
Status/metadata only — use `task.listMessages` for conversation history.

### `GET /v2/task.list` — 100/min
Params: `limit` (default 20, max 100), `cursor`, `order` (`asc`|`desc`, default
`desc`), `scope` (`all`|`standard`|`project`|`agent_subtask`), `agent_id` (required if
`scope=agent_subtask`; shortcut `agent-default`), `project_id` (required if
`scope=project`). Response: `{"data": [Task, ...], "has_more": bool, "next_cursor": "..."}`.

### `GET /v2/task.listMessages` — 100/min
Params: `task_id` (required), `order`, `limit`, `cursor`. Poll this after
`task.create`/`task.sendMessage`. Watch `status_update` events:
`running` → keep polling, `stopped` → read results, `waiting` → reply via
`task.sendMessage` (plain question, `waiting_for_event_type: messageAskUser`) or
`task.confirmAction` (action confirmation), `error` → read error. If the task used
`structured_output_schema`, a `structured_output_result` event appears once it stops.

### `POST /v2/task.sendMessage` — 10/min
Body: `{"task_id": "...", "message": {"content": "..."}, "agent_profile": "...", "structured_output_schema": {...}}`.
`task_id` and `message` required. Shortcut `task_id: "agent-default-main_task"` messages
the default IM agent. Unlike `task.create`, omitting `agent_profile` keeps the current
profile (it does **not** reset to `manus-1.6`). New `structured_output_schema` replaces
any previously armed one; omitting it leaves the existing arm state unchanged.

### `POST /v2/task.confirmAction` — 40/min
Body: `{"task_id": "...", "event_id": "...", "input": {...}}`. `task_id` and `event_id`
required; `event_id` is the task's `waiting_for_event_id` from its `status_update`
event, and `input`'s shape comes from that event's `confirm_input_schema`. Do **not**
use this for `messageAskUser` waits — use `task.sendMessage` instead.

### `POST /v2/task.stop` — 40/min
Body: `{"task_id": "..."}`. Sets status to `stopped`; resumable later via
`task.sendMessage`.

### `POST /v2/task.delete` — 40/min
Body: `{"task_id": "..."}`. Permanently deletes; agent-subtasks cannot be deleted.
Response includes `id` and `deleted: true`.

### `POST /v2/task.update` — 40/min
Body: `{"task_id": "...", "title": "...", "share_visibility": "...", "enable_visible_in_task_list": bool}`.
Only `task_id` required.

## Projects

### `POST /v2/project.create` — 40/min
Body: `{"name": "...", "instruction": "..."}` (`name` required). `instruction` is
auto-prepended to every task in the project. Response: `{"project": Project}`.

### `GET /v2/project.list` — 100/min
No params. Response: `{"data": [Project, ...]}`.

## Files

### `POST /v2/file.upload` — 40/min
Body: `{"filename": "report.pdf"}`. Response: `{"file": File, "upload_url": "...", "upload_expires_at": <unix ts>}`.
Two-step flow: call this to get a presigned S3 `upload_url`, then `PUT` the raw file
bytes to that URL within 3 minutes. Max 512 MB/file, 10 GB total/account. Files auto-
delete after 48 hours. Blocked extensions: `.exe`, `.sh`, `.bat`, `.dmg`, etc. Use the
returned `file.id` as `file_id` in a task message's content.

### `GET /v2/file.detail` — 100/min · `POST /v2/file.delete` — 40/min
Params/body: `file_id`.

## Webhooks — API key only (reject OAuth2 tokens)

### `POST /v2/webhook.create` — 40/min
Body: `{"url": "https://..."}` — `url` is the only field the spec defines (no `events`
filter; every webhook receives both `task_created` and `task_stopped`). Must be HTTPS,
publicly reachable, and respond 2xx within 10s (Manus sends a test request first).
Response: `{"webhook": Webhook}` (`id`, `url`, `status`: `active`|`inactive`, `created_at`).

### `GET /v2/webhook.list` — 100/min
No params. Response: `{"data": [Webhook, ...]}`.

### `POST /v2/webhook.delete` — 40/min
Body: `{"webhook_id": "..."}`.

### `GET /v2/webhook.publicKey` — cacheable, rarely changes
No params. Response: `{"public_key": "<PEM RSA public key>", "algorithm": "RSA-SHA256"}`.
Use to verify webhook payload signatures (see `webhooks-security.mdx` in the original
bundle for the signature verification algorithm if needed).

**Event payloads** (POSTed to your `url`):
- `task_created`: `{"event_id", "event_type": "task_created", "task_detail": {"task_id", "task_title", "task_url"}}`
- `task_stopped`: `{"event_id", "event_type": "task_stopped", "task_detail": {"task_id", "task_title", "task_url", "message", "attachments": [{"file_name","url","size_bytes"}], "stop_reason": "finish"|"ask", "structured_output": {"success","value","error"}}}`

## Agents, Skills, Connectors, Browser (API key only except `skill.list`/`connector.list`)

- `GET /v2/agent.list`, `GET /v2/agent.detail`, `POST /v2/agent.update` — 100/40/100 per min. Manage custom IM agents.
- `GET /v2/skill.list` — 100/min. Skill IDs for `message.enable_skills` / `force_skills`.
- `GET /v2/connector.list` — 100/min. Connector IDs for `message.connectors`.
- `GET /v2/browser.onlineList` — 100/min. Lists online browser clients.

## Usage — API key only

- `GET /v2/usage.list`, `GET /v2/usage.teamStatistic`, `GET /v2/usage.teamLog` — 600/min each.

## Website — API key only

- `GET /v2/website.status`, `GET /v2/website.listCheckpoints` — 100/min.
- `POST /v2/website.publish`, `POST /v2/website.update` — 40/min.
Manage websites built by Manus tasks (status, checkpoint history, publish, update).

## Rate limit error

```json
{"ok": false, "request_id": "req_abc123", "error": {"code": "rate_limited", "message": "Rate limit exceeded. Please retry after a short backoff."}}
```
Back off exponentially with jitter; prefer webhooks over polling `task.listMessages` in
production; cache `webhook.publicKey`.
