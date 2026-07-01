#!/usr/bin/env python3
"""
Skill Initializer - Creates a new Claude Code skill from a template.

Usage:
    init_skill.py <skill-name> [--base <path>]

Examples:
    init_skill.py my-new-skill
    init_skill.py my-api-helper --base ~/.claude/skills

Skills are created at <base>/<skill-name>/. The base path defaults to
"./.claude/skills" (relative to the current working directory), and can be
overridden with --base or the SKILLS_BASE_PATH environment variable.
"""

import argparse
import os
import re
import sys
from pathlib import Path


SKILL_NAME_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')


SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: Complete and informative explanation of what the skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Structuring This Skill

[TODO: Choose the structure that best fits this skill's purpose. Common patterns:

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Structure: ## Overview -> ## Workflow Decision Tree -> ## Step 1 -> ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when the skill offers different operations/capabilities
- Structure: ## Overview -> ## Quick Start -> ## Task Category 1 -> ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Structure: ## Overview -> ## Guidelines -> ## Specifications -> ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when the skill provides multiple interrelated features
- Structure: ## Overview -> ## Core Capabilities -> ### 1. Feature -> ### 2. Feature...

Patterns can be mixed and matched. Delete this entire "Structuring This Skill" section when done.]

## [TODO: Replace with the first main section based on chosen structure]

[TODO: Add content here — code samples, decision trees, concrete examples, references to scripts/templates/references as needed.]

## Resources

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.
Appropriate for: automation, data processing, or any deterministic operation.
Note: scripts may run without being loaded into context, but can still be read by Claude for patching or environment adjustments.

### references/
Documentation intended to be loaded into context to inform Claude's process and thinking.
Appropriate for: in-depth documentation, API references, schemas, or detailed guides.

### templates/
Files not intended to be loaded into context, but used within the output Claude produces.
Appropriate for: document templates, boilerplate code, images, icons, fonts.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""Example helper script for {skill_name}.

This is a placeholder script that can be executed directly.
Replace with actual implementation or delete if not needed.
"""


def main():
    print("This is an example script for {skill_name}")
    # TODO: Add actual script logic here.


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

## When Reference Docs Are Useful

- Comprehensive API documentation
- Detailed workflow guides
- Complex multi-step processes
- Information too lengthy for the main SKILL.md
- Content only needed for specific use cases

## Structure Suggestions

### API Reference Example
- Overview, Authentication, Endpoints with examples, Error codes, Rate limits

### Workflow Guide Example
- Prerequisites, Step-by-step instructions, Common patterns, Troubleshooting, Best practices
"""

EXAMPLE_TEMPLATE = """# Example Template File

This placeholder represents where template files would be stored.
Replace with actual template files (templates, images, fonts, etc.) or delete if not needed.

Template files are NOT intended to be loaded into context, but rather used within
the output Claude produces.

## Common Template Types

- Templates: .pptx, .docx, boilerplate directories
- Images: .png, .jpg, .svg, .gif
- Fonts: .ttf, .otf, .woff, .woff2
- Boilerplate code: Project directories, starter files
- Icons: .ico, .svg
- Data files: .csv, .json, .xml, .yaml

Note: This is a text placeholder. Actual templates can be any file type.
"""


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def validate_skill_name(skill_name):
    """Return an error message if skill_name is invalid, else None."""
    if not skill_name:
        return "Skill name cannot be empty."
    if len(skill_name) > 64:
        return f"Skill name is too long ({len(skill_name)} characters). Maximum is 64."
    if not SKILL_NAME_RE.match(skill_name):
        return (
            f"Invalid skill name '{skill_name}'. Must be hyphen-case: lowercase "
            "letters, digits, and single hyphens only (no leading/trailing/double hyphens)."
        )
    return None


def default_base_path():
    env = os.environ.get("SKILLS_BASE_PATH")
    if env:
        return Path(env)
    return Path.cwd() / ".claude" / "skills"


def init_skill(skill_name, base_path):
    """
    Initialize a new skill directory with template SKILL.md.

    Returns:
        Path to created skill directory, or None if error.
    """
    error = validate_skill_name(skill_name)
    if error:
        print(f"❌ Error: {error}")
        return None

    skill_dir = Path(base_path) / skill_name

    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Created skill directory: {skill_dir}")
    except OSError as e:
        print(f"❌ Error creating directory: {e}")
        return None

    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)

    skill_md_path = skill_dir / 'SKILL.md'
    try:
        skill_md_path.write_text(skill_content)
        print("✅ Created SKILL.md")

        scripts_dir = skill_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        example_script = scripts_dir / 'example.py'
        example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
        example_script.chmod(0o755)
        print("✅ Created scripts/example.py")

        references_dir = skill_dir / 'references'
        references_dir.mkdir(exist_ok=True)
        example_reference = references_dir / 'api_reference.md'
        example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
        print("✅ Created references/api_reference.md")

        templates_dir = skill_dir / 'templates'
        templates_dir.mkdir(exist_ok=True)
        example_template = templates_dir / 'example_template.txt'
        example_template.write_text(EXAMPLE_TEMPLATE)
        print("✅ Created templates/example_template.txt")
    except OSError as e:
        print(f"❌ Error creating skill files: {e}")
        return None

    print(f"\n✅ Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to complete the TODO items and update the description")
    print("2. Customize or delete the example files in scripts/, references/, and templates/")
    print("3. Run quick_validate.py when ready to check the skill structure")

    return skill_dir


def main():
    parser = argparse.ArgumentParser(description="Initialize a new Claude Code skill.")
    parser.add_argument("skill_name", help="Hyphen-case skill identifier, e.g. 'data-analyzer'")
    parser.add_argument(
        "--base",
        default=None,
        help="Base directory to create the skill under (default: ./.claude/skills, "
             "or $SKILLS_BASE_PATH if set)",
    )
    args = parser.parse_args()

    base_path = Path(args.base) if args.base else default_base_path()

    print(f"\U0001f680 Initializing skill: {args.skill_name}")
    print(f"   Location: {base_path / args.skill_name}\n")

    result = init_skill(args.skill_name, base_path)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
