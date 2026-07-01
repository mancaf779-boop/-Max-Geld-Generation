#!/usr/bin/env python3
"""
Fetch skill lists from GitHub repositories.

Priority:
1. GitHub CLI (`gh`) - Best: 15000 req/hr when authenticated, pre-authenticated
   in many CI/dev environments.
2. Offline cache - Fast, no API calls, but can go stale.
3. Personal Token (GITHUB_TOKEN / GH_TOKEN) - 5000 req/hr, user-provided.
4. Unauthenticated HTTP - 60 req/hr, last resort.

Use --online to force a real-time fetch, otherwise a fresh-enough cache is
used automatically and a background-free refresh is triggered when the cache
is missing or older than --max-cache-age-hours (default 24h).
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# GitHub token from environment (fallback auth method)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

# Cache file path (can be overridden with --cache-file)
DEFAULT_CACHE_FILE = Path(__file__).resolve().parent.parent / "references" / "skills_cache.json"

# Default staleness threshold for auto-refresh, in hours.
DEFAULT_MAX_CACHE_AGE_HOURS = 24.0

# Network timeouts, in seconds. Every subprocess/HTTP call in this module is
# bounded so a hung network or an unresponsive `gh` binary cannot hang the
# whole script indefinitely.
GH_CLI_CHECK_TIMEOUT = 5
GH_CLI_API_TIMEOUT = 20
HTTP_TIMEOUT = 15

# All repositories this skill searches.
REPOSITORIES = {
    "anthropics/skills": {"skills_path": "skills", "branch": "main", "type": "skills"},
    "obra/superpowers": {"skills_path": "skills", "branch": "main", "type": "skills"},
    "vercel-labs/agent-skills": {"skills_path": "skills", "branch": "main", "type": "skills"},
    "K-Dense-AI/claude-scientific-skills": {"skills_path": "scientific-skills", "branch": "main", "type": "skills"},
    "ComposioHQ/awesome-claude-skills": {"skills_path": ".", "branch": "master", "type": "skills"},
    "travisvn/awesome-claude-skills": {"branch": "main", "type": "curated_list"},
    "BehiSecc/awesome-claude-skills": {"branch": "main", "type": "curated_list"},
}


def check_gh_cli() -> bool:
    """Check if the gh CLI is available and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=GH_CLI_CHECK_TIMEOUT,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except subprocess.TimeoutExpired:
        print("gh auth status timed out; falling back to HTTP", file=sys.stderr)
        return False


def gh_api(endpoint: str) -> dict | list | None:
    """Make a GitHub API request via the gh CLI, with a bounded timeout."""
    try:
        result = subprocess.run(
            ["gh", "api", endpoint],
            capture_output=True,
            text=True,
            timeout=GH_CLI_API_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        print(f"gh api {endpoint} timed out after {GH_CLI_API_TIMEOUT}s", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("gh CLI not found", file=sys.stderr)
        return None

    if result.returncode != 0:
        print(f"gh api {endpoint} failed: {result.stderr.strip()}", file=sys.stderr)
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"gh api {endpoint} returned invalid JSON: {exc}", file=sys.stderr)
        return None


def http_api(url: str) -> dict | list | None:
    """Make a GitHub API request via HTTP (with optional token), with a bounded timeout."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "claude-code-internet-skill-finder")
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 403 or e.code == 429:
            print(f"Rate limited fetching {url} (HTTP {e.code})", file=sys.stderr)
        elif e.code == 404:
            print(f"Not found: {url}", file=sys.stderr)
        else:
            print(f"HTTP error {e.code} fetching {url}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"Network error fetching {url}: {e.reason}", file=sys.stderr)
        return None
    except TimeoutError:
        print(f"Timed out fetching {url} after {HTTP_TIMEOUT}s", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON from {url}: {e}", file=sys.stderr)
        return None


# Global flag for which API method to use
USE_GH_CLI = False


def api_request(endpoint: str) -> dict | list | None:
    """Make an API request using the best available method."""
    if USE_GH_CLI:
        return gh_api(endpoint)
    return http_api(f"https://api.github.com/{endpoint}")


def load_cache(cache_file: Path) -> dict | None:
    """Load cached skills data. Returns None if missing or unreadable."""
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: could not read cache at {cache_file}: {e}", file=sys.stderr)
        return None


def cache_age_hours(cache_file: Path) -> float | None:
    """Return the age of the cache file in hours, or None if it doesn't exist."""
    if not cache_file.exists():
        return None
    return (time.time() - cache_file.stat().st_mtime) / 3600.0


def is_cache_stale(cache_file: Path, max_age_hours: float) -> bool:
    """A cache is stale if it doesn't exist or is older than max_age_hours."""
    age = cache_age_hours(cache_file)
    return age is None or age > max_age_hours


def save_cache(data: dict, cache_file: Path) -> None:
    """Save skills data to cache, tagging it with a fetch timestamp."""
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {"_fetched_at": time.time(), "_fetched_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        payload.update(data)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"Cache updated at {cache_file}", file=sys.stderr)
    except OSError as e:
        print(f"Warning: could not save cache to {cache_file}: {e}", file=sys.stderr)


def _repo_entries(all_repos: dict) -> dict:
    """Return only the repository entries from a cache payload, excluding metadata keys."""
    return {k: v for k, v in all_repos.items() if not k.startswith("_")}


def check_rate_limit() -> dict:
    """Check current rate limit status."""
    data = api_request("rate_limit")
    if data:
        core = data.get("rate", {})
        return {"remaining": core.get("remaining", 0), "limit": core.get("limit", 0)}
    return {"remaining": 0, "limit": 0}


def fetch_repo_info(owner: str, repo: str) -> dict | None:
    data = api_request(f"repos/{owner}/{repo}")
    if data:
        return {"stars": data.get("stargazers_count", 0), "description": data.get("description", ""), "url": data.get("html_url", "")}
    return None


def fetch_readme(owner: str, repo: str, branch: str) -> str:
    data = api_request(f"repos/{owner}/{repo}/contents/README.md?ref={branch}")
    if data and data.get("encoding") == "base64":
        try:
            return base64.b64decode(data["content"]).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as e:
            print(f"Could not decode README for {owner}/{repo}: {e}", file=sys.stderr)
    return ""


def parse_readme_skills(readme_content: str) -> list:
    skills = []
    patterns = [
        r'\[([^\]]+)\]\((https://github\.com/[^)]+)\)\s*[-–—:]\s*(.+?)(?=\n|$)',
        r'\*\s*\[([^\]]+)\]\((https://github\.com/[^)]+)\)',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, readme_content, re.MULTILINE):
            name = match.group(1).strip()
            url = match.group(2).strip()
            desc = match.group(3).strip() if len(match.groups()) > 2 else ""
            if any(x in url.lower() for x in ['badge', 'shields.io', 'profile', 'twitter', 'linkedin']):
                continue
            # Only treat it as a "skill" link if it points at a specific
            # path within a repo (a tree/blob path, or at least owner/repo/subpath),
            # not a bare owner/repo landing page.
            is_specific_path = "/tree/" in url or "/blob/" in url or url.count("/") >= 6
            skills.append(
                {
                    "name": name,
                    "description": desc[:200],
                    "github_url": url,
                    "import_url": url if is_specific_path else "",
                    "source": "readme",
                }
            )
    return skills


def fetch_skill_directories(owner: str, repo: str, skills_path: str, branch: str) -> list | None:
    data = api_request(f"repos/{owner}/{repo}/git/trees/{branch}?recursive=1")
    if not data or "tree" not in data:
        return None
    skills = set()
    prefix = f"{skills_path}/" if skills_path != "." else ""
    for item in data["tree"]:
        path = item["path"]
        if skills_path == ".":
            if path.endswith("/SKILL.md") and path.count("/") == 1:
                skills.add(path.split("/")[0])
        else:
            if path.startswith(prefix) and path.endswith("/SKILL.md"):
                parts = path[len(prefix):].split("/")
                if len(parts) == 2:
                    skills.add(parts[0])
    return sorted(skills)


def generate_github_url(owner: str, repo: str, skill_name: str, skills_path: str, branch: str) -> str:
    """Build the canonical GitHub URL for a skill directory (used as the 'import' link)."""
    if skills_path == ".":
        return f"https://github.com/{owner}/{repo}/tree/{branch}/{skill_name}"
    return f"https://github.com/{owner}/{repo}/tree/{branch}/{skills_path}/{skill_name}"


def fetch_online(cache_file: Path) -> dict:
    """Fetch fresh data from GitHub API for every configured repository."""
    print("Fetching real-time data from GitHub...", file=sys.stderr)
    result = {}

    for repo_key, config in REPOSITORIES.items():
        owner, repo = repo_key.split("/")
        branch = config["branch"]

        repo_info = fetch_repo_info(owner, repo)
        if not repo_info:
            print(f"  skipped {repo_key} (could not fetch repo info)", file=sys.stderr)
            continue

        print(f"  fetched {repo_key} (stars={repo_info['stars']})", file=sys.stderr)

        if config["type"] == "curated_list":
            readme = fetch_readme(owner, repo, branch)
            result[repo_key] = {
                "stars": repo_info["stars"], "description": repo_info["description"],
                "url": repo_info["url"], "type": "curated_list",
                "skills": parse_readme_skills(readme) if readme else []
            }
        else:
            skills_path = config["skills_path"]
            skill_names = fetch_skill_directories(owner, repo, skills_path, branch) or []
            skills = []
            for name in skill_names:
                github_url = generate_github_url(owner, repo, name, skills_path, branch)
                skills.append({"name": name, "github_url": github_url, "import_url": github_url})
            result[repo_key] = {
                "stars": repo_info["stars"], "description": repo_info["description"],
                "url": repo_info["url"], "type": "skills", "skills": skills
            }

    if result:
        save_cache(result, cache_file)
    return result


def search_skills(keyword: str, all_repos: dict) -> list:
    keyword_lower = keyword.lower()
    matches = []
    for repo_key, repo_data in _repo_entries(all_repos).items():
        for skill in repo_data.get("skills", []):
            if keyword_lower in skill["name"].lower() or keyword_lower in skill.get("description", "").lower():
                matches.append({**skill, "repository": repo_key, "stars": repo_data["stars"], "repo_type": repo_data["type"]})
    return matches


def deep_dive(repo_key: str, skill_name: str) -> dict:
    """Fetch SKILL.md content for a specific skill."""
    if repo_key not in REPOSITORIES:
        return {"error": f"Unknown repository: {repo_key}"}
    config = REPOSITORIES[repo_key]
    if config["type"] == "curated_list":
        return {"error": f"{repo_key} is a curated list - visit github_url directly"}

    owner, repo = repo_key.split("/")
    skills_path = config["skills_path"]
    branch = config["branch"]

    endpoint = f"repos/{owner}/{repo}/contents/{skills_path}/{skill_name}/SKILL.md?ref={branch}" if skills_path != "." else f"repos/{owner}/{repo}/contents/{skill_name}/SKILL.md?ref={branch}"

    data = api_request(endpoint)
    if not data:
        return {"error": "Could not fetch SKILL.md"}

    if data.get("encoding") != "base64":
        return {"error": "Could not decode SKILL.md"}

    try:
        content = base64.b64decode(data["content"]).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as e:
        return {"error": f"Could not decode SKILL.md: {e}"}

    description = ""
    in_fm = False
    for line in content.split("\n"):
        if line.strip() == "---":
            in_fm = not in_fm
            if not in_fm:
                break
        elif in_fm and line.startswith("description:"):
            description = line.replace("description:", "").strip().strip('"\'')

    github_url = generate_github_url(owner, repo, skill_name, skills_path, branch)
    return {
        "name": skill_name,
        "repository": repo_key,
        "description": description,
        "content": content,
        "github_url": github_url,
        "import_url": github_url,
    }


def format_stars(count: int) -> str:
    return f"{count/1000:.1f}k".replace(".0k", "k") if count >= 1000 else str(count)


def main():
    global USE_GH_CLI

    parser = argparse.ArgumentParser(description="Claude Code Skill Finder")
    parser.add_argument("--list", "-l", action="store_true", help="List all skills")
    parser.add_argument("--search", "-s", help="Search skills by keyword")
    parser.add_argument("--deep-dive", "-d", nargs=2, metavar=("REPO", "SKILL"), help="Fetch SKILL.md")
    parser.add_argument("--online", "-o", action="store_true", help="Force a real-time fetch, bypassing the cache")
    parser.add_argument("--rate-limit", "-r", action="store_true", help="Check rate limit")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON")
    parser.add_argument("--cache-file", type=Path, default=DEFAULT_CACHE_FILE, help="Path to the skills cache JSON file")
    parser.add_argument(
        "--max-cache-age-hours",
        type=float,
        default=DEFAULT_MAX_CACHE_AGE_HOURS,
        help=f"Auto-refresh the cache if older than this many hours (default: {DEFAULT_MAX_CACHE_AGE_HOURS})",
    )
    args = parser.parse_args()

    cache_file: Path = args.cache_file

    # Determine API method.
    gh_available = check_gh_cli()
    if gh_available:
        USE_GH_CLI = True
        print("Using GitHub CLI (gh) - up to 15000 req/hr when authenticated", file=sys.stderr)
    elif GITHUB_TOKEN:
        print("Using GITHUB_TOKEN - up to 5000 req/hr", file=sys.stderr)
    else:
        print("No GitHub auth available (using cache, or 60 req/hr unauthenticated if --online)", file=sys.stderr)

    if args.rate_limit:
        rate = check_rate_limit()
        print(f"Rate limit: {rate['remaining']}/{rate['limit']}")
        print(f"Cache: {'available' if cache_file.exists() else 'not found'} at {cache_file}")
        age = cache_age_hours(cache_file)
        if age is not None:
            print(f"Cache age: {age:.1f} hours")
        return

    if args.deep_dive:
        repo, skill = args.deep_dive
        result = deep_dive(repo, skill)
        if args.json:
            print(json.dumps(result, indent=2))
        elif "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"\n=== {result['name']} ({result['repository']}) ===\n")
            print(f"Description: {result['description']}\n")
            print(f"GitHub: {result['import_url']}\n")
            print("--- SKILL.md ---\n")
            print(result['content'][:3000])
            if len(result['content']) > 3000:
                print(f"\n... ({len(result['content'])} chars total)")
        return

    # Decide whether to use the cache or fetch fresh data:
    #   --online always forces a fresh fetch.
    #   Otherwise, use the cache if it exists and isn't stale;
    #   if it's missing or stale, try a fresh fetch and fall back to
    #   whatever cache we have (even if stale) if that fetch fails.
    using_cache = False
    cache_stale = is_cache_stale(cache_file, args.max_cache_age_hours)

    if args.online:
        all_repos = fetch_online(cache_file)
        if not all_repos:
            print("Online fetch failed, falling back to cache...", file=sys.stderr)
            all_repos = load_cache(cache_file) or {}
            using_cache = True
    elif gh_available and cache_stale:
        # We have working auth and the cache is stale (or missing): refresh it.
        all_repos = fetch_online(cache_file)
        if not all_repos:
            print("Refresh failed, falling back to existing cache...", file=sys.stderr)
            all_repos = load_cache(cache_file) or {}
            using_cache = True
    else:
        all_repos = load_cache(cache_file)
        using_cache = True
        if all_repos and cache_stale:
            print(
                f"Warning: cache is older than {args.max_cache_age_hours}h and no GitHub auth is "
                "available to refresh it automatically. Pass --online to force a refresh.",
                file=sys.stderr,
            )
        if not all_repos:
            print("No cache available, attempting an online fetch...", file=sys.stderr)
            all_repos = fetch_online(cache_file) or {}
            using_cache = False

    if not all_repos:
        print("No data available.")
        return

    repo_entries = _repo_entries(all_repos)

    if args.search:
        matches = search_skills(args.search, all_repos)
        if args.json:
            print(json.dumps({"using_cache": using_cache, "results": matches}, indent=2))
        else:
            print(f"\n=== Skills matching '{args.search}' ({len(matches)} found) ===\n")
            for skill in matches:
                tag = " [README]" if skill.get("source") == "readme" else ""
                print(f"- {skill['name']} ({skill['repository']} stars={format_stars(skill['stars'])}){tag}")
                if skill.get("description"):
                    print(f"  {skill['description'][:100]}")
                print(f"  GitHub: {skill.get('import_url') or skill['github_url']}\n")
            if matches:
                print("Use --deep-dive REPO SKILL for the full description")
    else:
        if args.json:
            print(json.dumps({"using_cache": using_cache, "repositories": repo_entries}, indent=2))
        else:
            total_skills = sum(len(r.get("skills", [])) for r in repo_entries.values() if r["type"] == "skills")
            total_readme = sum(len(r.get("skills", [])) for r in repo_entries.values() if r["type"] == "curated_list")
            print(f"\n=== All Skills ({total_skills} + {total_readme} from READMEs) ===\n")

            for repo_key, repo_data in repo_entries.items():
                stars = format_stars(repo_data['stars'])
                if repo_data["type"] == "curated_list":
                    print(f"## {repo_key} (stars={stars}) - CURATED ({len(repo_data.get('skills', []))})")
                    for skill in repo_data.get("skills", [])[:5]:
                        desc = f" - {skill['description'][:40]}..." if skill.get('description') else ""
                        print(f"   - {skill['name']}{desc}")
                    if len(repo_data.get("skills", [])) > 5:
                        print(f"   ... +{len(repo_data['skills']) - 5} more")
                else:
                    print(f"## {repo_key} (stars={stars}) - {len(repo_data.get('skills', []))} skills")
                    for skill in repo_data.get("skills", []):
                        print(f"   - {skill['name']}")
                print()

            print("Use --search KEYWORD | --deep-dive REPO SKILL | --online")


if __name__ == "__main__":
    main()
