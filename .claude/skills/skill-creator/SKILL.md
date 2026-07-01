---
name: skill-creator
description: Guide for creating or updating Claude Code Skills (SKILL.md packages under .claude/skills/). For any request to create, package, or improve a skill, MUST first read this skill and follow its workflow instead of hand-rolling a SKILL.md from scratch.
license: Complete terms in LICENSE.txt
---

# Skill Creator

This skill provides guidance for creating effective Claude Code Skills.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks — they transform Claude from a general-purpose agent into a specialized agent equipped with procedural knowledge no model can fully possess on its own.

Claude Code auto-discovers skills at `.claude/skills/<skill-name>/SKILL.md` (project-level) or `~/.claude/skills/<skill-name>/SKILL.md` (user-level, available in every project).

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share it with everything else Claude needs: the system prompt, conversation history, other skills' metadata, and the actual user request.

**Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
.claude/skills/skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── templates/        - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields Claude reads to decide when the skill gets used, so be clear and comprehensive about what the skill does and when it applies.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Bundled Resources (optional)

- **`scripts/`** - Executable code for repetitive or deterministic tasks (e.g., `rotate_pdf.py`). Token efficient, can run without loading into context.
- **`references/`** - Documentation loaded as needed (schemas, API docs, policies). Keeps SKILL.md lean. For large files (>10k words), include grep patterns in SKILL.md.
- **`templates/`** - Output assets not loaded into context (logos, fonts, boilerplate code).

**Avoid duplication**: Information lives in SKILL.md OR references, not both.

**Do NOT include**: README.md, CHANGELOG.md, or other auxiliary documentation. Skills are for AI agents, not users.

### Progressive Disclosure

Three-level loading system:
1. **Metadata** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<500 lines)
3. **Bundled resources** - As needed

Keep SKILL.md under 500 lines. When splitting content to references, clearly describe when to read them.

**Key principle:** Keep the core workflow in SKILL.md; move variant-specific details to reference files.

## Skill Creation Process

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, templates)
3. Initialize the skill (run `init_skill.py`)
4. Edit the skill (implement resources and write SKILL.md)
5. Validate the skill (run `quick_validate.py`)
6. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

### Step 1: Understand the Skill

Skip only when usage patterns are already clearly understood. Gather concrete examples: "What functionality should this skill support?", "Can you give examples of how it would be used?" Avoid asking too many questions at once.

### Step 2: Plan the Reusable Contents

| Resource Type | When to Use                     | Example                               |
| ------------- | ------------------------------- | ------------------------------------- |
| `scripts/`    | Code rewritten repeatedly       | `rotate_pdf.py` for PDF rotation      |
| `templates/`  | Same boilerplate each time      | HTML/React starter for webapp builder |
| `references/` | Documentation needed repeatedly | Database schemas for a BigQuery skill |

### Step 3: Initialize the Skill

Skip only if the skill already exists and iteration/packaging is needed.

```bash
python3 .claude/skills/skill-creator/scripts/init_skill.py <skill-name>
```

By default this creates the skill under `.claude/skills/<skill-name>/` relative to the current directory. Pass `--base <path>` to target a different location (e.g. `~/.claude/skills` for a user-level skill), or set the `SKILLS_BASE_PATH` environment variable.

The script:
- Validates `<skill-name>` is hyphen-case (lowercase letters, digits, hyphens; no leading/trailing/double hyphens; max 64 chars)
- Creates the skill directory
- Generates a SKILL.md template with proper frontmatter and TODO placeholders
- Creates example resource directories: `scripts/`, `references/`, and `templates/` with example files to customize or delete

### Step 4: Edit the Skill

Remember the skill is being created for another instance of Claude to use. Include information that would be beneficial and non-obvious.

Consult these references based on your skill's needs:
- **Multi-step processes**: `references/workflows.md` — sequential workflows and conditional logic
- **Output formats or quality standards**: `references/output-patterns.md` — template and example patterns
- **Progressive disclosure**: `references/progressive-disclosure-patterns.md` — splitting content across files

Begin with the `scripts/`, `references/`, and `templates/` files identified in Step 2. Test added scripts by running them. Delete any unused example files from initialization.

**Writing SKILL.md:** Always use imperative/infinitive form.
- `name`: hyphen-case identifier matching the directory name.
- `description`: primary trigger mechanism. Must state what the skill does AND when to use it, e.g. "Document creation and editing with tracked changes. Use for: creating .docx files, modifying content, working with tracked changes."

### Step 5: Validate the Skill

```bash
python3 .claude/skills/skill-creator/scripts/quick_validate.py <skill-name>
```

Pass `--base <path>` or set `SKILLS_BASE_PATH` if the skill isn't under `.claude/skills` relative to the current directory. You can also pass an absolute path directly. If validation fails, fix the errors and re-run.

### Step 6: Iterate

After using the skill on real tasks, notice struggles or inefficiencies, identify how SKILL.md or bundled resources should change, implement, and re-validate.
