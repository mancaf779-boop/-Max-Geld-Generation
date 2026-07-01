#!/usr/bin/env python3
"""
Quick validation script for Claude Code skills.

Usage:
    quick_validate.py <skill-name> [--base <path>]
    quick_validate.py <path-to-skill-dir>

Examples:
    quick_validate.py my-skill
    quick_validate.py .claude/skills/my-skill
    quick_validate.py my-skill --base ~/.claude/skills
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata'}
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
RECOMMENDED_MAX_BODY_LINES = 500


def default_base_path():
    env = os.environ.get("SKILLS_BASE_PATH")
    if env:
        return Path(env)
    return Path.cwd() / ".claude" / "skills"


def resolve_skill_path(skill_path_or_name, base_path):
    """Resolve a skill name or path to an absolute/relative skill directory path."""
    path = Path(skill_path_or_name)
    if path.is_absolute() or path.exists():
        return path
    return Path(base_path) / skill_path_or_name


def validate_skill(skill_path):
    """Validate a skill directory. Returns (ok: bool, messages: list[str])."""
    messages = []
    ok = True

    def fail(msg):
        nonlocal ok
        ok = False
        messages.append(f"❌ {msg}")

    def warn(msg):
        messages.append(f"⚠️  {msg}")

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        fail(f"SKILL.md not found at {skill_md}")
        return ok, messages

    content = skill_md.read_text()
    if not content.startswith('---'):
        fail("No YAML frontmatter found (SKILL.md must start with '---')")
        return ok, messages

    match = re.match(r'^---\n(.*?)\n---\n?(.*)$', content, re.DOTALL)
    if not match:
        fail("Invalid frontmatter format (missing closing '---')")
        return ok, messages

    frontmatter_text, body = match.group(1), match.group(2)

    if yaml is None:
        fail("PyYAML is not installed; cannot parse frontmatter")
        return ok, messages

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        fail(f"Invalid YAML in frontmatter: {e}")
        return ok, messages

    if not isinstance(frontmatter, dict):
        fail("Frontmatter must be a YAML dictionary")
        return ok, messages

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        fail(
            f"Unexpected key(s) in frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    if 'name' not in frontmatter:
        fail("Missing 'name' in frontmatter")
    if 'description' not in frontmatter:
        fail("Missing 'description' in frontmatter")

    name = frontmatter.get('name', '')
    if name is None:
        name = ''
    if not isinstance(name, str):
        fail(f"Name must be a string, got {type(name).__name__}")
    else:
        name = name.strip()
        if not name:
            fail("Name cannot be empty")
        else:
            if not re.match(r'^[a-z0-9-]+$', name):
                fail(f"Name '{name}' should be hyphen-case (lowercase letters, digits, hyphens only)")
            if name.startswith('-') or name.endswith('-') or '--' in name:
                fail(f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens")
            if len(name) > MAX_NAME_LENGTH:
                fail(f"Name is too long ({len(name)} characters). Maximum is {MAX_NAME_LENGTH}.")
            if name != skill_path.name:
                warn(f"Name '{name}' does not match directory name '{skill_path.name}'")

    description = frontmatter.get('description', '')
    if description is None:
        description = ''
    if not isinstance(description, str):
        fail(f"Description must be a string, got {type(description).__name__}")
    else:
        description = description.strip()
        if not description:
            fail("Description cannot be empty")
        else:
            if '<' in description or '>' in description:
                fail("Description cannot contain angle brackets (< or >)")
            if len(description) > MAX_DESCRIPTION_LENGTH:
                fail(f"Description is too long ({len(description)} characters). Maximum is {MAX_DESCRIPTION_LENGTH}.")

    body_lines = [line for line in body.splitlines()]
    if len(body_lines) > RECOMMENDED_MAX_BODY_LINES:
        warn(
            f"SKILL.md body is {len(body_lines)} lines; recommended max is "
            f"{RECOMMENDED_MAX_BODY_LINES}. Consider moving details to references/."
        )

    if ok:
        messages.append("✅ Skill is valid!")
    return ok, messages


def main():
    parser = argparse.ArgumentParser(description="Validate a Claude Code skill directory.")
    parser.add_argument("skill", help="Skill name or path to the skill directory")
    parser.add_argument(
        "--base",
        default=None,
        help="Base directory to resolve a bare skill name against (default: ./.claude/skills, "
             "or $SKILLS_BASE_PATH if set)",
    )
    args = parser.parse_args()

    base_path = Path(args.base) if args.base else default_base_path()
    resolved_path = resolve_skill_path(args.skill, base_path)

    print(f"\U0001f50d Validating skill at: {resolved_path}")
    ok, messages = validate_skill(resolved_path)
    print("\n".join(messages))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
