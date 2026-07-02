---
name: orchestrating-tasks
description: Use when you have a plan or workflow and must turn every step into concrete tasks and actually execute them - creating the task list, doing the work, taking real actions, verifying each one, and driving to done. Triggers on "execute this", "do all of it", "run the whole thing", "take action on the plan", "turn this into tasks and complete them"
---

# Orchestrating Tasks

## Overview

The gap between a plan and a result is execution discipline. Work rots when tasks are vague, marked "done" without verification, or when one failure quietly derails the rest.

**Core principle:** Every step becomes a tracked task; every task is executed, verified, and closed before the next. Taking action means observing the result of the action, not assuming it.

**Announce at start:** "I'm using the orchestrating-tasks skill to execute this."

**Note:** This works far better with subagents. When available, dispatch each substantial task to a subagent — **REQUIRED SUB-SKILL:** superpowers:subagent-driven-development. For a written code implementation plan, superpowers:executing-plans is the more specific skill.

## The Process

### 1. Turn the plan into a task list
Convert each workflow step into an explicit, tracked task (use your todo tool). One task = one step with a done-criterion. If a step has no observable done-criterion, fix the plan (superpowers:designing-workflows) before executing.

### 2. Sequence and parallelize
Respect the dependency order. Independent tasks may run concurrently — **REQUIRED SUB-SKILL when parallelizing:** superpowers:dispatching-parallel-agents.

### 3. Execute one task at a time
For the active task:
1. Mark it in_progress.
2. Take the concrete action (run the command, write the file, call the API, make the change).
3. **Verify the result against the done-criterion** — read the output, check the state, run the test. Do not mark done on the basis that you "did the step".
4. Mark completed only after verification passes.

### 4. Handle failure without thrashing
When a task fails or verification doesn't pass:
- Follow its stated on-failure path (retry / fallback / stop-and-ask).
- If the cause is unclear, **REQUIRED SUB-SKILL:** superpowers:systematic-debugging — find root cause before re-trying.
- Never pile new fixes on an unexplained failure. Never mark a failed task done.

### 5. Checkpoint with your human partner
Stop at the plan's review points, and stop immediately on any action that is destructive, irreversible, or outward-facing (deploys, deletes, sends, spends) — confirm before acting.

### 6. Verify the whole and report
When all tasks are closed, confirm the overall outcome — **REQUIRED SUB-SKILL:** superpowers:verification-before-completion. Report what was done, what was verified, and anything skipped or still open. Report failures plainly.

## When to STOP and ask

- Instruction ambiguous or a step's done-criterion is missing
- An action is destructive / irreversible / spends money / sends externally
- Verification fails repeatedly (see systematic-debugging; 3+ failures ⇒ question the plan)
- A task reveals the plan is wrong — return to superpowers:designing-workflows

## Quick Reference

| Step | Guardrail |
|------|-----------|
| Tasks | Every workflow step is a tracked task with a done-criterion |
| Sequence | Dependency order honored; parallels dispatched |
| Execute | Action taken, then result observed |
| Verify | Done-criterion checked before marking complete |
| Fail | On-failure path followed; root cause found before retry |
| Report | Done + verified + skipped/open, honestly |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Marking a task done because you ran the step | Verify the observable result first |
| Executing without a task list | Create tracked tasks up front |
| Retrying a failure you don't understand | Root-cause it (systematic-debugging) |
| Taking irreversible action unprompted | Checkpoint with your partner first |
| Claiming success without a final check | verification-before-completion |
| Doing tasks serially when independent | Dispatch parallel agents |

## Integration

- **designing-workflows** / **superpowers:writing-plans** — produce what this skill executes
- **superpowers:subagent-driven-development** — dispatch tasks to subagents (preferred)
- **superpowers:executing-plans** — for a written code implementation plan
- **superpowers:dispatching-parallel-agents** — run independent tasks concurrently
- **superpowers:systematic-debugging** — when a task fails
- **superpowers:verification-before-completion** — final gate before reporting done
- **superpowers:finishing-a-development-branch** — when the execution is a code change
