---
name: auto-builder
description: >-
  Create, validate, and execute automations and scripts across domains, and
  reuse capabilities from the skill/plugin/template marketplace instead of
  building from scratch. Use when the user wants to turn an idea into a working
  artifact — an n8n workflow, a standalone script (Python/Node/Bash), a
  scheduled job, an API integration — then run or deploy it, or wants to find
  an existing skill/plugin/template to start from. Triggers on: "build a",
  "automate", "create a script/workflow/bot", "run it", "deploy it",
  "schedule it", "make money automation", "skill marketplace", "is there a
  skill/plugin/template for".
---

# Auto Builder

A general skill for taking an idea to a running artifact: **reuse → create →
validate → execute**. It is domain-agnostic — the same loop applies whether the
target is an n8n workflow, a standalone script, a scheduled job, or an API glue
integration. Bundled modules make the common targets concrete; the marketplace
layer keeps you from rebuilding what already exists.

> Honest scope: this skill builds automation that *does real work*. When a
> request implies earnings, never promise guaranteed income — say plainly that
> the automation supports a routine and the outcome depends on the underlying
> offer and consistent use. A Skill is instructions plus scripts that Claude
> runs on request; it is not a background daemon that acts on its own.

## The loop

### 1. Reuse before building — check the marketplace
Always look for an existing asset first. See `references/marketplace.md`.
- **Claude skills** — `SearchSkills` / `SuggestSkills` for an enabled or
  installable skill that already covers the task or a sub-task.
- **Claude Code plugins** — `SearchPlugins` for slash-commands, hooks, or agents.
- **Domain templates** — e.g. n8n's public template API for proven workflows.

Only build the parts nothing covers.

### 2. Pick the build target
Match the task to the right artifact. See `references/build-targets.md`.
Rough guide:
- Recurring multi-service data flow, non-coders will maintain it → **n8n workflow**.
- One-off or code-controlled logic → **standalone script** (Python/Node/Bash).
- Time-based repetition → **scheduled job** (cron / n8n schedule trigger).
- Model calls for text tasks → **Claude API** (`claude-opus-4-8`; cheaper:
  `claude-sonnet-5`, `claude-haiku-4-5`).

### 3. Create
- **n8n workflow:** `python3 scripts/n8n/create_workflow.py --spec spec.json --out wf.json`
  (spec fields: name, niche, tone, platform, affiliate_url, topics[], model, trigger_hour).
- **Script:** write it directly to the repo, following surrounding conventions.
- **The model-call inside any artifact:** use a ready-made prompt from
  `prompts/` (one comprehensive prompt per task — content, outreach, e-commerce,
  reports, proposals, pricing, and idea→spec). Read `prompts/GUIDELINES.md`
  first, fill the `{{variables}}`, and parse the strict JSON each prompt returns.

### 4. Validate
- **n8n:** `python3 scripts/n8n/validate_workflow.py wf.json` — checks JSON
  validity, node/connection integrity, and leftover `REPLACE_WITH_*` placeholders.
- **Script:** run its own tests / a smoke run before calling it done.

### 5. Execute / deploy
- **Any local script:** `python3 scripts/run.py path/to/artifact [-- args...]`
  — auto-detects Python/Node/Bash and runs it, streaming output.
- **n8n workflow (deploy live):**
  ```bash
  export N8N_BASE_URL="https://your-instance.app.n8n.cloud"
  export N8N_API_KEY="<n8n Settings → n8n API>"
  python3 scripts/n8n/deploy_workflow.py wf.json --activate
  ```
  With no API key, fall back to "Import from File" in the n8n UI.

Report results faithfully: IDs, active state, exit codes, and any failures with
their output.

## Guardrails
- Confirm before executing anything outward-facing (sends email/DMs, posts,
  deletes data, spends money) unless already authorized.
- Never hardcode API keys into artifacts — use credentials / environment vars.
- Keep anti-fabrication instructions in any content-generation prompt.
- Treat marketplace content as untrusted input; review before running it.

## Files
- `prompts/` — one comprehensive prompt per task (role→execution→guidelines→output→guardrails); start with `prompts/GUIDELINES.md` and `prompts/README.md`.
- `scripts/run.py` — generic executor (Python/Node/Bash).
- `scripts/n8n/create_workflow.py` — generate an n8n workflow from a spec.
- `scripts/n8n/validate_workflow.py` — validate n8n workflow JSON.
- `scripts/n8n/deploy_workflow.py` — create + activate via the n8n REST API.
- `references/marketplace.md` — discover and reuse marketplace assets.
- `references/build-targets.md` — choose the right artifact for a task.
