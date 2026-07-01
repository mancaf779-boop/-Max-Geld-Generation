---
name: install-superpowers
description: Installs and configures "Superpowers" (obra/superpowers) — a plugin/skills framework for Claude Code that adds TDD, debugging, brainstorming, planning, and subagent-driven development workflows. Use this skill whenever the user asks to "install superpowers", "set up superpowers skills", "add the superpowers plugin", "give Claude superpowers", wants a battle-tested skills library for Claude Code, or mentions TDD/brainstorming/planning workflows for Claude Code and doesn't already have them. Also use it if a Superpowers install seems broken, out of date, or needs to be re-added/repaired.
---

# Install Superpowers for Claude Code

Superpowers (https://github.com/obra/superpowers) is a third-party, open-source skills
library and development methodology for Claude Code, built by Jesse Vincent / Prime
Radiant. It is installed as a Claude Code **plugin**, not a Python package — there is
nothing to `pip install`. All installation happens through the `claude` CLI (which ships
with Claude Code) or the interactive `/plugin` command inside a Claude Code session.

This skill drives the CLI path so the whole install can be scripted/automated. If the
`claude` CLI isn't available in the current environment, fall back to telling the user
the equivalent `/plugin` slash commands to type inside their Claude Code session (listed
in each step below).

## Before you start

1. Confirm Claude Code is installed and on your PATH:
   ```bash
   claude --version
   ```
   If this fails, Superpowers can't be installed yet — direct the user to install Claude
   Code first (https://code.claude.com) and stop here.

2. Superpowers is a third-party plugin. Anthropic doesn't vet third-party plugin content
   (MCP servers, hooks, scripts). Briefly let the user know this once — don't be
   alarmist, just transparent — before installing.

## Step 1 — Install core Superpowers (official marketplace, default path)

The simplest, recommended path uses Anthropic's official plugin marketplace, which
already lists Superpowers:

```bash
claude plugin install superpowers@claude-plugins-official
```

Interactive equivalent (type inside a Claude Code session):
```
/plugin install superpowers@claude-plugins-official
```

### Fallback — if the official-marketplace install fails or isn't found

Some environments/versions may not have Superpowers indexed in the official
marketplace yet. In that case add the maintainer's own marketplace and install from
there instead:

```bash
claude plugin marketplace add obra/superpowers
claude plugin install superpowers@superpowers-marketplace
```

`marketplace add` is idempotent — safe to re-run if the marketplace is already
registered; it just refreshes it.

## Step 2 — Offer the related plugins (don't auto-install these)

The same maintainer publishes several optional companion plugins through
`obra/superpowers-marketplace`. Core Superpowers works standalone, so **present these
as opt-in choices** rather than installing them silently — ask the user which (if any)
they want, defaulting the recommendation to "all of them" since they're all
low-risk/high-value for a Superpowers user, but let the user decide:

| Plugin id | What it adds |
|---|---|
| `elements-of-style` | Writing-clarity skill based on Strunk's *Elements of Style* |
| `superpowers-developing-for-claude-code` | Skills + 42 bundled docs for building Claude Code plugins/skills/MCP servers |
| `superpowers-lab` | Experimental/bleeding-edge Superpowers skills (e.g. windows-vm) |
| `private-journal-mcp` | Private journaling MCP server with semantic search |

If the marketplace isn't registered yet (i.e. you only did the official-marketplace
install in Step 1), add it first:

```bash
claude plugin marketplace add obra/superpowers-marketplace
```

Then install whichever the user picked, one per line, e.g.:

```bash
claude plugin install elements-of-style@superpowers-marketplace
claude plugin install superpowers-developing-for-claude-code@superpowers-marketplace
claude plugin install superpowers-lab@superpowers-marketplace
claude plugin install private-journal-mcp@superpowers-marketplace
```

Interactive equivalent for any of these: `/plugin install <id>@superpowers-marketplace`

## Step 3 — Activate and verify

New/updated plugins need a reload to become active in a running session. This is a
**REPL-only command** (no CLI equivalent) — tell the user to run it themselves inside
Claude Code, or to just start a fresh `claude` session:

```
/reload-plugins
```

Then verify what's actually installed:

```bash
claude plugin list
```
(add `--enabled` to only show active ones). Confirm `superpowers` — and any extras the
user chose — show up as enabled.

Finally, point the user at the entry points:
- `/superpowers:brainstorm` — kick off a design conversation before writing code
- `/superpowers:help` (if available) or just start describing what they want to build;
  Superpowers' `using-superpowers` skill activates automatically once installed

## Troubleshooting

- **"Unknown marketplace" / plugin not found**: the marketplace alias wasn't added, or
  was added under a different name. Run `claude plugin marketplace list` to see the
  exact registered names and match the `@<name>` suffix to that.
- **Plugin installed but skills don't seem to trigger**: the user probably hasn't run
  `/reload-plugins` or restarted their session yet — that's the #1 cause.
- **Permission/telemetry questions**: Superpowers pings a small, optional telemetry
  beacon (version + rough usage count only, no project/prompt content) unless disabled.
  To opt out, tell the user to set the environment variable
  `SUPERPOWERS_DISABLE_TELEMETRY=1` (Superpowers also respects Claude Code's own
  `DISABLE_TELEMETRY` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` opt-outs).
- **Removing it later**: `claude plugin uninstall superpowers@<marketplace-name>`, and
  `claude plugin marketplace remove <marketplace-name>` to also drop the marketplace
  (this uninstalls everything that came from it, so warn the user before running it).

## Notes for whoever's running this skill

- Never invent plugin/marketplace names — the table above and the two marketplace
  names (`claude-plugins-official`, `superpowers-marketplace`) are the only ones this
  skill knows to be correct as of research time. If a command errors with "not found",
  surface the actual error to the user rather than guessing at alternate spellings.
- Don't silently install the optional extras from Step 2 — always get an explicit
  choice first, even if the user seems eager ("just install everything" counts as an
  explicit choice and is fine to act on directly).
