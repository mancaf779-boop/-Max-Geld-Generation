# Manus API v1 — Legacy Reference (deprecated)

**Do not use v1 for new integrations.** It is deprecated in favor of v2 (see the main
`SKILL.md` and `v2-endpoints.md`). This file exists only to help maintain an
already-existing v1 integration. The v1 OpenAPI spec was intentionally **not** copied
into this skill's `references/` — if you need the raw spec, it's still in the original
Manus docs bundle (`docs/v1/openapi.json`) or at https://open.manus.ai/docs/v1.

## Base URL and auth

Base URL: `https://api.manus.ai` (same host as v2, different path prefix: `/v1/...`).

Auth header is **different from v2**: use `API_KEY: <your-api-key>` (not
`x-manus-api-key`, and not a `Bearer` scheme).

```bash
curl -H "API_KEY: your-api-key" https://api.manus.ai/v1/tasks
```

## Endpoints

### Tasks
- `POST /v1/tasks` — create a task. Body: `{"prompt": "...", "agent_profile": "...", "project_id": "..."}` (v1 uses flat `prompt` string, not v2's `message.content`/`message` object).
- `GET /v1/tasks` — list tasks. Query params: `after` (cursor, ID of last task), `limit` (default 100, 1-1000), `order` (`asc`|`desc`, default `desc`), `orderBy` (`created_at`|`updated_at`), `query` (search title/body), `status` (array of `pending`|`running`|`completed`|`failed`), `createdAfter`/`createdBefore` (unix timestamps), `project_id`.
- `GET /v1/tasks/{task_id}` — get task detail. Supports `?convert=true` to convert `.pptx` outputs.
- `PUT /v1/tasks/{task_id}` — update task metadata: `title`, `enableShared`, `enableVisibleInTaskList`.
- `DELETE /v1/tasks/{task_id}` — permanently delete a task.

Note the v1 task status enum (`pending`|`running`|`completed`|`failed`) differs from
v2's (`running`|`stopped`|`waiting`|`error`) — do not assume they map 1:1 when porting
code.

### Projects
- `POST /v1/projects` — `{"name": "...", "instruction": "..."}` (`name` required).
  ```bash
  curl -X POST "https://api.manus.ai/v1/projects" \
    -H "Content-Type: application/json" \
    -H "API_KEY: your-api-key" \
    -d '{"name": "Research Project", "instruction": "Always summarize key findings first"}'
  ```
  Response: `{"id": "proj_abc123", "name": "...", "instruction": "...", "created_at": 1699900000}`.
- `GET /v1/projects` — list, query param `limit` (default 100, 1-1000). Response: `{"data": [Project, ...]}`.

### Files
- `POST /v1/files` — creates a file record + presigned S3 URL. `PUT` the file bytes to
  the returned URL. Reference the file later via `file_id` in a task's attachments.
- `GET /v1/files` — list the 10 most recently uploaded files.
- `GET /v1/files/{file_id}` — file detail/status.
- `DELETE /v1/files/{file_id}` — delete file record + S3 object.

### Webhooks
- `POST /v1/webhooks` — register a webhook URL.
- `DELETE /v1/webhooks/{webhook_id}` — remove a webhook.

v1 webhooks fire **three** event types (v2 only fires two — no `task_progress` in v2):
1. `task_created` — once, on task creation.
2. `task_progress` — zero or more times, plan/step updates (`progress_detail.progress_type`, e.g. `"plan_update"`; `progress_detail.message`).
3. `task_stopped` — once, on completion or when input is needed (`stop_reason`: `finish`|`ask`; `attachments`: `[{file_name, url, size_bytes}]`).

Payload envelope differs slightly by field nesting; check `task_detail` vs
`progress_detail` per event type in the original `docs/v1/webhooks.mdx` if porting a
handler.

### Connectors, data integrations, OpenAI compatibility
v1 also documented `connectors/*`, `data-integrations/*` (e.g. Similarweb), and an
OpenAI-compatible Responses API shim. These were not carried into this skill's v2
reference because v2 superseded them with `connector.list`/`message.connectors` and
native structured output; consult the original bundle's `docs/v1/connectors/`,
`docs/v1/data-integrations/`, and `docs/v1/openai-compatibility/` directories if you
must maintain code that depends on them.

## Migration notes (v1 -> v2)

- Auth header: `API_KEY` -> `x-manus-api-key` (or OAuth2 `Authorization: Bearer`).
- Path prefix: `/v1/...` -> `/v2/...`; RPC-style names (`task.create`, `task.list`, ...)
  replace REST-style paths (`POST /tasks`, `GET /tasks/{id}`, ...).
- Task creation body: flat `{"prompt": "..."}` -> `{"message": {"content": "..."}}`.
- Response envelope: v2 wraps everything in `{"ok": bool, "request_id": "...", ...}`
  and errors as `{"ok": false, "error": {"code", "message"}}`; v1 responses are
  unwrapped.
- Webhooks: v1's `task_progress` event has no v2 equivalent — poll
  `task.listMessages` in v2 if you need intermediate progress detail.
