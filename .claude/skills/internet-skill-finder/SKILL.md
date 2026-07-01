---
name: internet-skill-finder
description: Search and recommend Agent Skills from verified GitHub repositories. Use when users ask to find, discover, search for, or recommend skills/plugins for specific tasks, domains, or workflows.
---

# Internet Skill Finder

Search 7 verified GitHub repositories for Agent Skills.

## Workflow

### 1. Fetch Skill List

```bash
python3 "$CLAUDE_PROJECT_DIR/.claude/skills/internet-skill-finder/scripts/fetch_skills.py" --search "keyword"
```

If `CLAUDE_PROJECT_DIR` is not set, use the absolute path to this skill's `scripts/fetch_skills.py` directory instead (resolve it relative to this SKILL.md's own location; do not assume a fixed system path).

Options: `--list` (all skills), `--online` (force a real-time fetch, bypassing the cache), `--json` (structured output), `--max-cache-age-hours N` (treat the cache as stale after N hours; default 24), `--cache-file PATH` (use an alternate cache location).

### 2. Deep Dive (if needed)

```bash
python3 scripts/fetch_skills.py --deep-dive REPO SKILL
```

### 3. Present Results

When using cached data, prepend:

> Using cached data (see the reported cache age). Run with `--online` for real-time results, or configure `gh` (GitHub CLI) auth in this environment for automatic refreshes.

Format each match:

```markdown
### [Skill Name]
**Source**: [Repository] | Stars: [Stars]
**Description**: [From SKILL.md]
**GitHub**: [github_url]
```

### 4. No Matches

Suggest creating a custom skill for the task instead (a directory with a `SKILL.md` under `.claude/skills/`), following this repo's existing skill conventions.

## Data Access

The script auto-detects and uses the best available method:

| Priority | Method | Rate Limit | Behavior |
|----------|--------|------------|----------|
| 1 | GitHub CLI (`gh`), if installed and authenticated | 15000/hr | Auto real-time refresh when cache is stale |
| 2 | Offline cache (`references/skills_cache.json`) | Unlimited | Used when `gh` is unavailable or cache is fresh |
| 3 | `GITHUB_TOKEN` / `GH_TOKEN` env var | 5000/hr | Used for authenticated HTTP calls with `--online` |
| 4 | Unauthenticated HTTP | 60/hr | Last resort with `--online` |

JSON output includes `"using_cache": true/false` to indicate the data source. The cache file itself is stamped with `_fetched_at` / `_fetched_at_iso` on every refresh so staleness can be checked with `--rate-limit` (which prints the cache age) or by inspecting those keys directly.

**Cache staleness**: the script auto-refreshes the cache when `gh` auth is available and the cache is older than `--max-cache-age-hours` (default 24h). Without `gh` auth, a stale cache is still used (skills change infrequently) but a warning is printed suggesting `--online`.

## Sources

7 repositories: anthropics/skills, obra/superpowers, vercel-labs/agent-skills, K-Dense-AI/claude-scientific-skills, ComposioHQ/awesome-claude-skills, travisvn/awesome-claude-skills, BehiSecc/awesome-claude-skills
