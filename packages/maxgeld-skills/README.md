# MaxGeld Skills

**The research-to-execution skill set for coding agents.** Four composable
[agent skills](https://agentskills.io/specification) that take an open-ended
goal from *not knowing* → *knowing* → *a written plan* → *verified action*.

Built for Claude Code (and other skill-aware harnesses). Each skill is a
behavior-shaping reference the agent loads on demand.

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

## Install (Claude Code)

From this repository:

```bash
# Register the marketplace (point at wherever you host this package)
/plugin marketplace add mancaf779-boop/-Max-Geld-Generation

# Install the plugin
/plugin install maxgeld-skills
```

Or, for local development, add the marketplace from a checkout path that
contains `packages/maxgeld-skills/.claude-plugin/marketplace.json`.

Once installed, the skills auto-surface by their `description` when a matching
task appears — you don't invoke them by hand.

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
- **Auto-trigger is only proxy-tested** (description routing), not live
  in-harness. Test real auto-trigger per harness before relying on it.
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

## License & attribution

MaxGeld Skills is © 2026 MaxGeld (mancaf779), released under the
[MIT License](LICENSE). The four skills and the eval are original work.

The *skill-authoring methodology* (RED→GREEN→REFACTOR for process
documentation, the SKILL.md format, rationalization-table / red-flags
bulletproofing) is inspired by the Superpowers project by Jesse Vincent
(MIT-licensed). This package neither includes nor rebrands Superpowers' own
skills; it is a separate, independently-authored library.
