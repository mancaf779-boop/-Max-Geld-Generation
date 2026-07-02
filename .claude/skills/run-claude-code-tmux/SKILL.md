---
name: run-claude-code-tmux
description: Install and run Claude Code in a tmux session
---

# Run Claude Code in tmux

This skill launches Claude Code (the CLI tool) in a persistent tmux session. The script handles session creation, installation, and optional attachment, making it easy to run Claude in the background or in a dedicated terminal.

## Prerequisites

- `tmux` installed (`apt-get install tmux` on Ubuntu/Debian)
- `curl` for downloading the Claude Code installer
- Internet access to `https://claude.ai`

## Run (Agent Path)

The driver script is `./install-claude-code-tmux.sh`. Launch it with:

```bash
./install-claude-code-tmux.sh [session-name] [attach]
```

**Parameters:**
- `session-name` (optional, default: `claude-code`): Name for the tmux session
- `attach` (optional, default: `true`): Whether to attach to the session after launching

**Examples:**

Create a session named `my-claude` and attach to it:
```bash
./install-claude-code-tmux.sh my-claude
```

Create a detached session (runs in background):
```bash
./install-claude-code-tmux.sh my-claude false
```

Reattach to an existing session:
```bash
./install-claude-code-tmux.sh my-claude
```

**Inside the tmux session:**
- The Claude Code CLI will launch automatically after installation
- Use standard Claude Code commands (e.g., `/help`, `/model`, etc.)
- Detach from the session with `Ctrl-B D` (then `Ctrl-B d` to detach)
- Kill the session when done: `tmux kill-session -t <session-name>`

## Run (Human Path)

For interactive use without scripting:

```bash
# Simple launch with defaults
./install-claude-code-tmux.sh

# Then interact with Claude Code as normal
# Quit with Ctrl-C to exit Claude and return to shell
# Session persists in background
```

## How It Works

1. Checks if a tmux session with the given name already exists
2. If it exists, reattaches to it
3. If not, creates a new session and:
   - Installs Claude Code via the official installer
   - Launches the Claude Code CLI
   - Optionally attaches to the session for interactive use

## Gotchas

- **First run takes time:** The installation script downloads and installs Claude Code, which may take 30-60 seconds depending on network speed
- **Installation output:** The curl installer output is sent to the tmux session; you won't see it in your terminal until you attach
- **Interactive prompts:** Claude Code may show configuration prompts (theme selection) on first run; respond in the tmux session
- **Session reuse:** The script cleverly reuses existing sessions — if you run it twice with the same name, it just reattaches rather than reinstalling

## Troubleshooting

**"command not found: tmux"**
- Install tmux: `apt-get update && apt-get install -y tmux`

**Session seems frozen or unresponsive**
- Attach to check status: `./install-claude-code-tmux.sh my-claude`
- Check session activity: `tmux list-windows -t my-claude`
- Kill and restart if needed: `tmux kill-session -t my-claude && ./install-claude-code-tmux.sh my-claude`

**Claude Code CLI not starting after installation**
- The install script may be slow. Wait 30+ seconds and attach to the session to see progress
- Check tmux pane for errors: `tmux send-keys -t my-claude 'echo "Check logs above"' Enter`

**Need to update Claude Code**
- Kill the session: `tmux kill-session -t my-claude`
- Run the script again to reinstall: `./install-claude-code-tmux.sh my-claude`
