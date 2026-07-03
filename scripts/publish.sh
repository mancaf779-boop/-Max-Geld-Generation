#!/usr/bin/env bash
# publish.sh — commit, push the current branch, and refresh the standalone
# MaxForge Lab package branch. Reusable: run it any time you want to publish.
#
# Usage:
#   scripts/publish.sh "your commit message"
#   scripts/publish.sh                       # uses a default message
#
# Optional env vars:
#   STANDALONE_BRANCH   name of the root-level package branch (default: maxforge-lab-standalone)
#   PACKAGE_DIR         directory to split to the standalone branch (default: maxforge-lab)
#   MAXFORGE_REMOTE     if set (e.g. https://github.com/<you>/maxforge-lab.git),
#                       also mirror the package there as 'main'
#
set -euo pipefail

MSG="${1:-chore: publish update}"
STANDALONE_BRANCH="${STANDALONE_BRANCH:-maxforge-lab-standalone}"
PACKAGE_DIR="${PACKAGE_DIR:-maxforge-lab}"

cd "$(git rev-parse --show-toplevel)"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

# Retry a git command up to 4 times with exponential backoff (network hiccups).
retry() {
  local n=1
  until "$@"; do
    if [ "$n" -ge 4 ]; then
      echo "  failed after $n attempts: $*" >&2
      return 1
    fi
    echo "  retry $n ..." >&2
    sleep "$((2 ** n))"
    n=$((n + 1))
  done
}

echo "==> Branch: $CURRENT_BRANCH"

# 1. Commit any pending changes (skip cleanly if there's nothing to commit).
if [ -n "$(git status --porcelain)" ]; then
  echo "==> Committing changes"
  git add -A
  git commit -m "$MSG"
else
  echo "==> No changes to commit"
fi

# 2. Push the current branch.
echo "==> Pushing $CURRENT_BRANCH"
retry git push -u origin "$CURRENT_BRANCH"

# 3. Refresh the standalone package branch (root = $PACKAGE_DIR).
if [ -d "$PACKAGE_DIR" ]; then
  echo "==> Splitting '$PACKAGE_DIR' -> $STANDALONE_BRANCH"
  SPLIT_SHA="$(git subtree split --prefix="$PACKAGE_DIR")"
  echo "    split commit: $SPLIT_SHA"
  retry git push origin "$SPLIT_SHA:refs/heads/$STANDALONE_BRANCH"

  # 4. Optional: mirror the package to a separate repo as 'main'.
  if [ -n "${MAXFORGE_REMOTE:-}" ]; then
    echo "==> Mirroring package to $MAXFORGE_REMOTE (main)"
    retry git push "$MAXFORGE_REMOTE" "$SPLIT_SHA:refs/heads/main"
  fi
else
  echo "==> Skipping standalone split ('$PACKAGE_DIR' not found)"
fi

echo "==> Done."
