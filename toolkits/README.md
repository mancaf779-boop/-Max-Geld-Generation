# Toolkits

Standalone, self-contained Claude Code skills kept alongside — but **not part
of** — the Maxforge Lab plugin. They live here (rather than under `skills/`) so
they don't auto-load with the plugin; install the ones you want by copying them
into `~/.claude/skills/` or a project `.claude/skills/`.

These skills are written in German.

## What's here

### `install-n8n-mcp-full-access/`
Installs the community **`czlonkowski/n8n-mcp`** server (via `npx -y n8n-mcp`)
so Claude Code gets full n8n node documentation + workflow-building tools
(`search_nodes`, `n8n_create_workflow`, …). This is a **stdio** MCP server (a
local subprocess), distinct from n8n's native HTTP/OAuth connector which only
*executes* existing workflows.

- `scripts/install.sh` — idempotent registration via `claude mcp add`.
- `references/troubleshooting.md`, `references/claude-md-snippet.md`.

Run it on a machine that can reach both npm and your n8n instance's `/api/v1`.

### `skill-creator-on-demand/`
A meta-skill that scaffolds new skills from a template.

- `scripts/new_skill.sh` — scaffold a new skill dir from `reference/template/`.
- `scripts/verify_skill.sh` — check structure, frontmatter, and scan for
  obvious hardcoded secrets.
- `reference/` — best practices, skill ideas, and the template.

## Verified in this environment

- The n8n-mcp stdio server was installed with `install.sh` and confirmed
  **connected** via `claude mcp list` — its offline documentation tools work.
  Its *workflow* tools call your n8n API, which is only reachable from a
  machine whose network can reach that host (not this sandbox — egress to the
  n8n Cloud host is blocked here by policy).
- Both skills pass `skill-creator-on-demand/scripts/verify_skill.sh`.
- `new_skill.sh` scaffolds correctly (placeholder substitution across all
  files, not just `*.md`).

## Fixes applied vs. the originals

- `install.sh` now registers with `npx -y n8n-mcp` (not `npx n8n-mcp`): without
  `-y`, the first `claude mcp list` health check fails while npx downloads the
  package on first run. Documented in `references/troubleshooting.md`.
- `new_skill.sh` now substitutes `__SKILL_NAME__` in every file, not only
  `*.md` — previously `scripts/main.sh` kept the raw placeholder.
- Fixed a broken absolute path in the n8n `SKILL.md` (`cat` of the CLAUDE.md
  snippet now uses a repo-relative path).
