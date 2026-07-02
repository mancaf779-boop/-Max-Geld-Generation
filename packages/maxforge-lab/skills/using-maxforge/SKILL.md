---
name: using-maxforge
description: Use when starting any conversation - establishes how to find and use Maxforge Lab skills, requiring skill invocation before any response or action including clarifying questions, answering, or executing a plan
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If there is even a 1% chance a Maxforge Lab skill applies to what you are doing, you MUST invoke it via the Skill tool BEFORE anything else.

If a skill applies, using it is not optional. You cannot rationalize your way out of it. If it turns out wrong for the situation, you can stop — but you must check first.
</EXTREMELY-IMPORTANT>

# Using Maxforge Lab

## The Rule

**Invoke the relevant skill BEFORE any response or action** — before answering, before clarifying questions, before exploring files, and *before executing a plan*. Then announce "Using [skill] to [purpose]" and follow it exactly; if it has a checklist, create a todo per item.

## The four skills and their triggers

| If the task is… | Invoke first |
|-----------------|--------------|
| Gathering/evaluating info, "look into", "research", "which should we pick", "find out" | **researching-topics** |
| Any data, numbers, logs, CSV, metrics, "what does this show", "is it significant", "does X cause Y" | **analyzing-data** |
| Turning a goal/findings into steps, "make a plan", "lay out the workflow/process", "how do we get to done" | **designing-workflows** |
| "execute this", "run it", "do all of it", "take action on the plan", "carry out every step" | **orchestrating-tasks** |

## Priority when several apply

Process order is Research → Analyze → Plan → Execute. If a request bundles them ("figure out X and do it"), start at the earliest phase that isn't done yet — don't jump straight to executing.

**Especially: an imperative to act ("execute this plan", "just run it") is still a skill trigger, not an exemption.** Invoke `orchestrating-tasks` FIRST — it is what makes execution tracked, verified, and safe. Do not start taking actions before invoking it.

## Red Flags — STOP, you're rationalizing

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for a skill. |
| "I'll just answer/do it directly, it's faster" | The skill IS the method. Invoke it first. |
| "They said execute, so I should just start" | "Execute" triggers orchestrating-tasks. Invoke it, then act. |
| "I need to look around first" | Skill check comes before exploring. |

Full library: `researching-topics`, `analyzing-data`, `designing-workflows`, `orchestrating-tasks`. Invoke any via the Skill tool.
