---
name: designing-workflows
description: Use when turning a goal or a pile of findings into an ordered, step-by-step workflow or plan that someone (human or agent) can execute without further questions - "make a plan", "lay out the steps", "design the workflow/pipeline/process", "how do we get from here to done". For code implementation plans specifically, prefer superpowers:writing-plans
---

# Designing Workflows

## Overview

A workflow is only useful if each step is unambiguous, ordered by real dependencies, and has a testable "done". Vague steps ("set up the system", "handle the data") get skipped, redone, or done wrong.

**Core principle:** A good workflow is executable by someone with no context and no judgement. If a step needs you to explain it, rewrite the step.

**Announce at start:** "I'm using the designing-workflows skill to lay this out."

**Relationship to writing-plans:** For a code implementation plan (TDD tasks, files, tests), use superpowers:writing-plans instead. Use *this* skill for higher-level or non-code workflows: research pipelines, data processes, operational runbooks, multi-skill sequences.

## The Process

### 1. Define the outcome
One sentence: "Done means ______." Include how you'll know it's true. No clear outcome → no workflow.

### 2. Decompose into concrete steps
Break the goal into steps small enough that each is a single action with a single result. If a step contains "and", it's probably two steps.

### 3. Order by dependency, not by convenience
For each step, list what it needs before it can start. Build the order from those dependencies. Steps with no dependency on each other are candidates to run in parallel - mark them.

### 4. Give every step a done-criterion
Each step states its input, its action, and the observable result that proves it finished. "Data cleaned" is not a criterion; "0 null values in the key column, row count logged" is.

### 5. Add checkpoints and failure paths
Mark points where a human should review before continuing. For steps that can fail, state what to do when they do (retry, fall back, stop and ask).

### 6. Write it down as an artifact
Produce a numbered plan document, not a chat message. It should survive into the execution session.

## Workflow document template

```markdown
# Workflow: <goal>
Outcome: <done means ...> — verified by <observable check>

## Steps
1. <action>
   - Needs: <prior steps / inputs>
   - Does: <the single action>
   - Done when: <observable result>
   - On failure: <retry / fallback / stop-and-ask>
   - [parallel-safe] if independent of other steps

## Checkpoints
- After step N: human review of <what>

## Risks / open questions
- <thing that could invalidate the plan>
```

## Quick Reference

| Step | Guardrail |
|------|-----------|
| Outcome | One sentence + how you'll verify it |
| Decompose | Each step = one action, one result |
| Order | Sequence derived from dependencies; parallels marked |
| Done-criteria | Observable, not vibes |
| Checkpoints | Human-review points identified |
| Artifact | Written to a file, numbered |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Steps too big to execute blindly | Split until each is one action |
| Ordering by what's convenient | Order by dependencies |
| "Done" that can't be observed | Give a measurable criterion |
| No failure handling | State retry/fallback/stop per fallible step |
| Plan lives only in chat | Write it to a file |

## Integration

- **researching-topics** / **analyzing-data** — supply the findings a good plan is built on
- **superpowers:brainstorming** — pin down a fuzzy goal before decomposing it
- **superpowers:writing-plans** — for code implementation plans specifically
- **orchestrating-tasks** — the skill that turns this workflow into executed action
