# Contributing to Maxforge Lab

Thanks for your interest in contributing to Maxforge Lab! This guide outlines how to develop, test, and submit new skills or improvements.

---

## Skill Development Workflow

### 1. Understand the Pipeline

Maxforge Lab operates on a **research-to-execution pipeline**:

```
Research (researching-topics)
    ↓
Analyze (analyzing-data)
    ↓
Plan (designing-workflows)
    ↓
Execute (orchestrating-tasks)
```

Every skill reinforces one stage. Review [`docs/research-to-execution-workflow.md`](docs/research-to-execution-workflow.md) before starting.

### 2. Skill Structure

All skills follow the same format:

```markdown
---
name: skill-name
description: One-line description of what the skill does
---

# Skill Title

## When to use this skill

Clear scenarios where an agent should invoke this skill.

## What this skill enforces

The non-negotiable discipline or process this skill maintains.

## How it works

Step-by-step breakdown of the skill's execution.

## Example

Concrete example showing the skill in action.

## Known limitations

Edge cases or scenarios where this skill may not apply.
```

### 3. Create Your Skill

1. **Branch from `maxforge-lab`:**
   ```bash
   git checkout maxforge-lab
   git pull origin maxforge-lab
   git checkout -b skill/your-skill-name
   ```

2. **Add your skill file:**
   - Location: `skills/your-skill-name.md`
   - Follow the structure above
   - Keep descriptions concise but complete

3. **Verify the skill:**
   - Does it solve ONE specific problem?
   - Is every step testable/observable?
   - Are limitations clearly stated?
   - Does it align with one pipeline stage?

### 4. Test Your Skill

**Headless test (no Claude Code needed):**

```bash
claude -p "Your test question here" --plugin-dir .
```

**Check auto-trigger reliability:**
- Does the skill fire when it should?
- Does it stay silent when it shouldn't?
- Measure: at least 4 of 4 invocations on matching scenarios

### 5. Document with an Eval

Add an eval test case to `docs/eval-report.md`:

```markdown
## [Skill Name]

**Test Case:** [What you're testing]
- **Without skill:** [Baseline behavior — how the agent fails]
- **With skill:** [Expected behavior — how the skill fixes it]
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** [Any edge cases or caveats]
```

### 6. Submit a Pull Request

1. Push your branch:
   ```bash
   git push origin skill/your-skill-name
   ```

2. Open a PR against `maxforge-lab` with:
   - **Title:** `Add [skill-name]: [one-line description]`
   - **Description:** Link to the eval test case
   - **Checklist:**
     - [ ] Skill follows the standard format
     - [ ] Tested on at least 4 scenarios
     - [ ] Eval test case documented
     - [ ] No hardcoded secrets or credentials
     - [ ] Contrast ratios checked (WCAG AA)

3. Address review feedback in the same branch

---

## Code Review Standards

### For Skill PRs

- ✅ Clear, testable steps
- ✅ One responsibility per skill
- ✅ Eval test cases included
- ✅ No process creep (stays disciplined)
- ✅ Limitations documented

### For Documentation PRs

- ✅ Clarity and conciseness
- ✅ Examples are runnable
- ✅ Links are valid
- ✅ Tone matches existing docs

### For Site/UI PRs

- ✅ Dark mode colors use CSS variables (not hardcoded hex)
- ✅ Accessibility: focus states, ARIA labels, heading hierarchy
- ✅ Responsive: tested at 320px, 768px, 1440px
- ✅ Performance: LCP < 2.5s, no render-blocking resources

---

## Quality Standards (RED→GREEN→REFACTOR)

We develop skills the hard way:

1. **RED** — Write a test showing how the agent fails *without* the skill
2. **GREEN** — Write the skill; verify the test passes
3. **REFACTOR** — Harden against edge cases; re-verify under pressure

All accepted skills must:
- Pass on **at least 4 different scenarios**
- Hold on **both Opus- and Haiku-class models**
- Show **documented evidence** of the RED→GREEN→REFACTOR loop

---

## Directory Structure

```
maxforge-lab/
├── skills/                          # Core skills (auto-load)
│   ├── researching-topics.md
│   ├── analyzing-data.md
│   ├── designing-workflows.md
│   ├── orchestrating-tasks.md
│   └── using-maxforge.md            # Bootstrap (SessionStart hook)
├── toolkits/                        # Optional, standalone skills
│   ├── install-n8n-mcp-full-access/
│   └── skill-creator-on-demand/
├── docs/
│   ├── index.html                   # Landing site
│   ├── TESTING_CHECKLIST.md         # Test procedures
│   ├── SETUP_GUIDE.md               # Installation & quick start
│   ├── CSS_VARIABLES_REFERENCE.md   # Theme & color system
│   ├── research-to-execution-workflow.md
│   ├── eval-report.md               # All eval test cases
│   └── llms.txt                     # LLM discovery map
├── .claude-plugin/
│   └── marketplace.json             # Plugin manifest
├── README.md
├── CONTRIBUTING.md                  # This file
└── LICENSE
```

---

## Local Development Setup

### Prerequisites

- Claude Code or equivalent skill-aware harness
- Git
- A text editor

### Clone and Install

```bash
git clone https://github.com/mancaf779-boop/-Max-Geld-Generation.git
cd -Max-Geld-Generation

# For local testing (headless)
claude -p "test question" --plugin-dir .

# For Claude Code (register marketplace)
/plugin marketplace add mancaf779-boop/-Max-Geld-Generation
/plugin install maxforge-lab
```

---

## Getting Help

- **Questions about skills?** — Check [`docs/research-to-execution-workflow.md`](docs/research-to-execution-workflow.md)
- **How to test?** — See [`docs/TESTING_CHECKLIST.md`](docs/TESTING_CHECKLIST.md)
- **Setup issues?** — Review [`docs/SETUP_GUIDE.md`](docs/SETUP_GUIDE.md)
- **Report a bug?** — [Open an issue](https://github.com/mancaf779-boop/-Max-Geld-Generation/issues)
- **Work with us?** — Email mancaf779@gmail.com

---

## License

By contributing to Maxforge Lab, you agree that your contributions will be licensed under the MIT License.

---

**Last Updated:** 2026-07-08
