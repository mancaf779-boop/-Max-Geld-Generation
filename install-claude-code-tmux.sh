#!/bin/bash

set -euo pipefail

SESSION_NAME="${1:-claude-code}"
ATTACH="${2:-true}"

echo "Setting up Claude Code in tmux session: $SESSION_NAME"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "Session '$SESSION_NAME' already exists. Attaching..."
  tmux attach-session -t "$SESSION_NAME"
  exit 0
fi

tmux new-session -d -s "$SESSION_NAME" -c "$HOME"

tmux send-keys -t "$SESSION_NAME" "echo 'Installing Claude Code CLI...' && curl -fsSL https://claude.ai/install | sh" Enter

tmux send-keys -t "$SESSION_NAME" "claude" Enter

sleep 2

if [ "$ATTACH" = "true" ]; then
  tmux attach-session -t "$SESSION_NAME"
fi
