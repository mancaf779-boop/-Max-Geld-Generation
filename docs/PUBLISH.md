# Publishing with `scripts/publish.sh`

One command to commit, push your working branch, and refresh the standalone
MaxForge Lab package branch. Run it any time you've made changes.

## Basic use
```bash
scripts/publish.sh "describe what changed"
```
This will:
1. Commit any pending changes (skips if there's nothing to commit).
2. Push the current branch to `origin`.
3. Re-split `maxforge-lab/` to the root and push it to the
   `maxforge-lab-standalone` branch (clean, package-only root).

## Mirror to a separate repo (optional)
If you have a dedicated repo for the brand package, set `MAXFORGE_REMOTE` and the
script also pushes the package there as `main`:
```bash
MAXFORGE_REMOTE="https://github.com/<you>/maxforge-lab.git" \
  scripts/publish.sh "publish package"
```
> Requires your local git to have push rights to that repo (e.g. you're logged in
> with `gh` or a credential helper). This is the piece a scoped Claude session
> can't do for you — from your own machine it just works.

## Config knobs (env vars)
| Var | Default | Meaning |
|-----|---------|---------|
| `STANDALONE_BRANCH` | `maxforge-lab-standalone` | name of the package branch |
| `PACKAGE_DIR` | `maxforge-lab` | directory split to the standalone branch |
| `MAXFORGE_REMOTE` | _(unset)_ | if set, mirror the package to that repo's `main` |

## First-time setup for a separate repo
1. Create an empty `maxforge-lab` repo on GitHub (no README/license).
2. Run once with `MAXFORGE_REMOTE` set (as above). Done — future runs keep it in sync.
