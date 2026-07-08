<<<<<<< HEAD
# Maxforge Lab

**AI tooling, forged for business.** Maxforge Lab builds and hardens
production-grade agent capabilities — from packaged skills to bespoke,
high-end AI solutions for teams that need results they can trust.

This repository is the Lab's flagship open toolkit: **the research-to-execution
skill set for coding agents.** Four composable
[agent skills](https://agentskills.io/specification) that take an open-ended
goal from *not knowing* → *knowing* → *a written plan* → *verified action*.

Built for Claude Code (and other skill-aware harnesses). Each skill is a
behavior-shaping reference the agent loads on demand — and every one ships with
a documented eval so you know it works before you bet a workflow on it.

> **Working with Maxforge Lab.** The skills here are free and MIT-licensed. If
> you need custom skills, agent workflows tuned to your domain, or a hardened
> deployment on your own model stack, that's the Lab's high-end engagement tier
> — reach out at mancaf779@gmail.com.

---

## The four skills

| Skill | Use it when… | What it enforces |
|-------|--------------|------------------|
| **researching-topics** | You need to gather, evaluate, and synthesize information before acting | Frame the question → gather from independent sources (in parallel) → corroborate → synthesize → cite → **state confidence + the key assumption you're betting on** (even under "no hedging" pressure) |
| **analyzing-data** | You have data of any kind and need insight (descriptive, diagnostic, predictive, prescriptive, qualitative) | Profile → clean (with a stated rule) → analyze → validate → report; **correlation is never causation, and that rule does not bend under pressure** |
| **designing-workflows** | You're turning a goal + findings into an ordered, executable plan | Outcome + how it's verified, single-action steps ordered by dependency, a **done-criterion per step**, parallel markers, checkpoints, and failure paths |
| **orchestrating-tasks** | You have a plan and must execute every step and take action | Every step becomes a tracked task; **execute → verify the result → then mark done**; stop before any destructive / irreversible / outward-facing action |

They chain into one pipeline — see [`docs/research-to-execution-workflow.md`](docs/research-to-execution-workflow.md):

> **Research → Analyze → Plan → Execute**

Plus a fifth, invisible skill — **`using-maxforge`** — the bootstrap that makes the other four
*reliably auto-trigger*. It loads at session start via a hook and tells the agent to invoke the
right skill before acting. Without a bootstrap, bare skills fire inconsistently (measured: 2 of 4);
with it, all four fire. See the eval report for the numbers.

## Quickstart (try it in 30 seconds)

No install needed — load the plugin into a one-off headless session:

```bash
claude -p "Analyze this: month,price,units | Jan,10,100 | Feb,12,90 | Mar,15,70. Does raising price hurt sales?" \
  --plugin-dir .
```

The agent auto-invokes `analyzing-data`, profiles the data, and refuses to call correlation
causation — that's the skill working.

## Install (Claude Code)

```bash
# Register the marketplace (point at wherever you host this package)
/plugin marketplace add mancaf779-boop/-Max-Geld-Generation

# Install the plugin
/plugin install maxforge-lab
```

Or, for local development, add the marketplace from your checkout — the plugin
lives at the repository root (`.claude-plugin/marketplace.json`).

The `using-maxforge` SessionStart hook loads automatically once the plugin is installed, so the
skills auto-trigger on matching tasks — you don't invoke them by hand.

## How it works

The skills are plain Markdown with YAML frontmatter (`name` + `description`).
The agent reads the descriptions to decide which skill applies to the task in
front of it, then loads the full skill body when it acts. There is no runtime,
no dependency, and nothing to configure.

## Quality — this was tested, not vibes

These skills were developed and hardened with a RED→GREEN→REFACTOR eval loop
(watch an agent fail without the skill, write the skill, close the loopholes),
run with real subagents under pressure. Full record in
[`docs/eval-report.md`](docs/eval-report.md). Highlights:

- **~30 subagent runs** across paired baseline/treatment, maximum-pressure,
  cross-domain, and weaker-model rounds.
- Two skills had **real under-pressure failures** (giving a false causal "yes";
  dropping the confidence/assumption line under "no caveats" pressure). Both
  were caught, refactored, and re-verified.
- All four held across **multiple domains** (medical, product, finance, legal,
  competitive intel, ops, ML, marketing) and on **both Opus- and Haiku-class
  models**.

### Known limitations (read before shipping a product on these)

- The skills enforce **process/honesty discipline** reliably, including on a
  weaker model — but they do **not** upgrade a weaker model's *substantive
  judgment*. Choose your model tier where answer quality matters.
- **Auto-trigger is validated live on Claude Code** with the bootstrap (all
  four fire). Other harnesses (Cursor, Codex, Copilot CLI) need their own
  per-harness confirmation.
- Nothing here replaces monitoring real usage once deployed.

## Interoperates with Superpowers (optional)

These skills cross-reference several skills from the
[Superpowers](https://github.com/obra/superpowers) library
(e.g. `superpowers:dispatching-parallel-agents`,
`superpowers:subagent-driven-development`,
`superpowers:systematic-debugging`,
`superpowers:verification-before-completion`) for the heavy lifting they name
as optional sub-skills. If Superpowers is also installed, those references
light up; if not, the skills still stand on their own — the cross-references
degrade to plain guidance.

## Work with Maxforge Lab

| Tier | What you get | For |
|------|--------------|-----|
| **Open** (free, MIT) | This toolkit: the 4 skills + bootstrap, docs, and eval. Use it, fork it, ship it. | Teams who want a solid, tested starting point |
| **Pro** | A curated pack of domain-tuned skills + the bootstrap, packaged and version-managed for your stack, with the eval harness to keep them honest as models change | Businesses standardizing how their agents work |
| **Lab** (high-end) | Bespoke skills and agent workflows built and pressure-tested for your domain, wired into your model stack and harness, with an eval suite and a hardening SLA | Companies betting real workflows on agents |

Every tier ships with an eval — you see the RED→GREEN→REFACTOR evidence, not
just claims. Start a conversation: **mancaf779@gmail.com**.

## License & attribution

Maxforge Lab is © 2026 Maxforge Lab (mancaf779), released under the
[MIT License](LICENSE). The five skills and the eval are original work.

The *skill-authoring methodology* (RED→GREEN→REFACTOR for process
documentation, the SKILL.md format, rationalization-table / red-flags
bulletproofing) is inspired by the Superpowers project by Jesse Vincent
(MIT-licensed). This package neither includes nor rebrands Superpowers' own
skills; it is a separate, independently-authored library.
=======
# Superpowers

Superpowers is a complete software development methodology for your coding agents, built on top of a set of composable skills and some initial instructions that make sure your agent uses them.


## We're Hiring!

We're hiring someone to help out full time with Superpowers community and code work. 
You can read about the job at https://primeradiant.com/jobs/superpowers-community-engineer/
If this sounds like someone you know, definitely send them our way.

## Quickstart

Give your agent Superpowers: [Claude Code](#claude-code), [Antigravity](#antigravity), [Codex App](#codex-app), [Codex CLI](#codex-cli), [Cursor](#cursor), [Factory Droid](#factory-droid), [GitHub Copilot CLI](#github-copilot-cli), [Kimi Code](#kimi-code), [OpenCode](#opencode), [Pi](#pi).

## How it works

It starts from the moment you fire up your coding agent. As soon as it sees that you're building something, it *doesn't* just jump into trying to write code. Instead, it steps back and asks you what you're really trying to do. 

Once it's teased a spec out of the conversation, it shows it to you in chunks short enough to actually read and digest. 

After you've signed off on the design, your agent puts together an implementation plan that's clear enough for an enthusiastic junior engineer with poor taste, no judgement, no project context, and an aversion to testing to follow. It emphasizes true red/green TDD, YAGNI (You Aren't Gonna Need It), and DRY. 

Next up, once you say "go", it launches a *subagent-driven-development* process, having agents work through each engineering task, inspecting and reviewing their work, and continuing forward. It's not uncommon for your agent to work autonomously for a couple hours at a time without deviating from the plan you put together.

There's a bunch more to it, but that's the core of the system. And because the skills trigger automatically, you don't need to do anything special. Your coding agent just has Superpowers.

## Commercial Services

If you're using Superpowers in enterprise and could benefit from commercial support, additional tooling, or managed spending, please don't hesitate to drop us a line at sales@primeradiant.com.

## Installation

Installation differs by harness. If you use more than one, install Superpowers separately for each one.

### Claude Code

Superpowers is available via the [official Claude plugin marketplace](https://claude.com/plugins/superpowers)

#### Official Marketplace

- Install the plugin from Anthropic's official marketplace:

  ```bash
  /plugin install superpowers@claude-plugins-official
  ```

#### Superpowers Marketplace

The Superpowers marketplace provides Superpowers and some other related plugins for Claude Code.

- Register the marketplace:

  ```bash
  /plugin marketplace add obra/superpowers-marketplace
  ```

- Install the plugin from this marketplace:

  ```bash
  /plugin install superpowers@superpowers-marketplace
  ```

### Antigravity

Install Superpowers as a plugin from this repository:

```bash
agy plugin install https://github.com/obra/superpowers
```

Antigravity runs the plugin's session-start hook, so Superpowers is active from
the first message. Reinstall with the same command to update.

### Codex App

Superpowers is available via the [official Codex plugin marketplace](https://github.com/openai/plugins).

- In the Codex app, click on Plugins in the sidebar.
- You should see `Superpowers` in the Coding section.
- Click the `+` next to Superpowers and follow the prompts.

### Codex CLI

Superpowers is available via the [official Codex plugin marketplace](https://github.com/openai/plugins).

- Open the plugin search interface:

  ```bash
  /plugins
  ```

- Search for Superpowers:

  ```bash
  superpowers
  ```

- Select `Install Plugin`.

### Cursor

- In Cursor Agent chat, install from marketplace:

  ```text
  /add-plugin superpowers
  ```

- Or search for "superpowers" in the plugin marketplace.

### Factory Droid

- Register the marketplace:

  ```bash
  droid plugin marketplace add https://github.com/obra/superpowers
  ```

- Install the plugin:

  ```bash
  droid plugin install superpowers@superpowers
  ```

### GitHub Copilot CLI

- Register the marketplace:

  ```bash
  copilot plugin marketplace add obra/superpowers-marketplace
  ```

- Install the plugin:

  ```bash
  copilot plugin install superpowers@superpowers-marketplace
  ```

### Kimi Code

Superpowers is available in Kimi Code's plugin marketplace.

- Open Kimi Code's plugin manager:

  ```text
  /plugins
  ```

- Go to `Marketplace` > `Superpowers` and install it.

- Or install directly from this repository:

  ```text
  /plugins install https://github.com/obra/superpowers
  ```

- Detailed docs: [docs/README.kimi.md](docs/README.kimi.md)

### OpenCode

OpenCode uses its own plugin install; install Superpowers separately even if you
already use it in another harness.

- Tell OpenCode:

  ```
  Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md
  ```

- Detailed docs: [docs/README.opencode.md](docs/README.opencode.md)

### Pi

Install Superpowers as a Pi package from this repository:

```bash
pi install git:github.com/obra/superpowers
```

For local development, run Pi with this checkout loaded as a temporary package:

```bash
pi -e /path/to/superpowers
```

The Pi package loads the Superpowers skills and a small extension that injects the `using-superpowers` bootstrap at session startup and again after compaction. Pi has native skills, so no compatibility `Skill` tool is required. Subagent and task-list tools remain optional Pi companion packages.

## The Basic Workflow

1. **brainstorming** - Activates before writing code. Refines rough ideas through questions, explores alternatives, presents design in sections for validation. Saves design document.

2. **using-git-worktrees** - Activates after design approval. Creates isolated workspace on new branch, runs project setup, verifies clean test baseline.

3. **writing-plans** - Activates with approved design. Breaks work into bite-sized tasks (2-5 minutes each). Every task has exact file paths, complete code, verification steps.

4. **subagent-driven-development** or **executing-plans** - Activates with plan. Dispatches fresh subagent per task with two-stage review (spec compliance, then code quality), or executes in batches with human checkpoints.

5. **test-driven-development** - Activates during implementation. Enforces RED-GREEN-REFACTOR: write failing test, watch it fail, write minimal code, watch it pass, commit. Deletes code written before tests.

6. **requesting-code-review** - Activates between tasks. Reviews against plan, reports issues by severity. Critical issues block progress.

7. **finishing-a-development-branch** - Activates when tasks complete. Verifies tests, presents options (merge/PR/keep/discard), cleans up worktree.

**The agent checks for relevant skills before any task.** Mandatory workflows, not suggestions.

## What's Inside

### Skills Library

**Testing**
- **test-driven-development** - RED-GREEN-REFACTOR cycle (includes testing anti-patterns reference)

**Debugging**
- **systematic-debugging** - 4-phase root cause process (includes root-cause-tracing, defense-in-depth, condition-based-waiting techniques)
- **verification-before-completion** - Ensure it's actually fixed

**Collaboration** 
- **brainstorming** - Socratic design refinement
- **writing-plans** - Detailed implementation plans
- **executing-plans** - Batch execution with checkpoints
- **dispatching-parallel-agents** - Concurrent subagent workflows
- **requesting-code-review** - Pre-review checklist
- **receiving-code-review** - Responding to feedback
- **using-git-worktrees** - Parallel development branches
- **finishing-a-development-branch** - Merge/PR decision workflow
- **subagent-driven-development** - Fast iteration with two-stage review (spec compliance, then code quality)

**Meta**
- **writing-skills** - Create new skills following best practices (includes testing methodology)
- **using-superpowers** - Introduction to the skills system

## Philosophy

- **Test-Driven Development** - Write tests first, always
- **Systematic over ad-hoc** - Process over guessing
- **Complexity reduction** - Simplicity as primary goal
- **Evidence over claims** - Verify before declaring success

Read [the original release announcement](https://blog.fsck.com/2025/10/09/superpowers/).

## Contributing

The general contribution process for Superpowers is below. Keep in mind that we don't generally accept contributions of new skills and that any updates to skills must work across all of the coding agents we support.

1. Fork the repository
2. Switch to the 'dev' branch
3. Create a branch for your work
4. Follow the `writing-skills` skill for creating and testing new and modified skills
5. Submit a PR, being sure to fill in the pull request template.

Skill-behavior tests use the drill eval harness from [superpowers-evals](https://github.com/prime-radiant-inc/superpowers-evals/), cloned into `evals/` — see `evals/README.md` for setup. Plugin-infrastructure tests live at `tests/` and run via the relevant `run-*.sh` or `npm test`.

See `skills/writing-skills/SKILL.md` for the complete guide.

## Updating

Superpowers updates are somewhat coding-agent dependent, but are often automatic.

## License

MIT License - see LICENSE file for details

## Visual companion telemetry

Because skills and plugins don't provide any feedback to creators, we have no idea how many of you are using Superpowers. By default, the Prime Radiant logo on brainstorming's optional visual companion feature is loaded from our website. It includes the version of Superpowers in use. It does not include any details about your project, prompt, or coding agent. We don't see your clicks or anything about what you're building. This helps us have a rough idea of how many folks are using Superpowers and which version of Superpowers they're using. It's 100% optional. To disable this, set the environment variable `SUPERPOWERS_DISABLE_TELEMETRY` to any true value. Superpowers also honors Claude Code's `DISABLE_TELEMETRY` and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` opt-outs.

## Community

Superpowers is built by [Jesse Vincent](https://blog.fsck.com) and the rest of the folks at [Prime Radiant](https://primeradiant.com).

- **Discord**: [Join us](https://discord.gg/35wsABTejz) for community support, questions, and sharing what you're building with Superpowers
- **Issues**: https://github.com/obra/superpowers/issues
- **Release announcements**: [Sign up](https://primeradiant.com/superpowers/) to get notified about new versions
>>>>>>> 3548a5c... Add Superpowers skills for Claude Code
