# Workflow: Research → Analyze → Plan → Execute

**Outcome:** Any open-ended goal ("figure out X and do something about it") is carried
end-to-end — from not knowing, to knowing, to a written plan, to verified action —
using four composable skills. **Verified by:** the goal's success criterion is met and
confirmed by superpowers:verification-before-completion.

This is a step-by-step workflow built with the `designing-workflows` skill. It chains
the four skills added alongside it. Each phase names the skill that owns it and the
observable result that lets the next phase begin.

## The four skills in this pipeline

| Phase | Skill | Answers |
|-------|-------|---------|
| 1 | `researching-topics` | What do we actually know? |
| 2 | `analyzing-data` | What do the numbers/evidence say? |
| 3 | `designing-workflows` | What are the ordered steps to the goal? |
| 4 | `orchestrating-tasks` | Do every step, take action, verify. |

## Steps

1. **Frame the goal**
   - Needs: the user's request.
   - Does: state the goal in one sentence and what "done" looks like. If fuzzy, use
     superpowers:brainstorming to pin it down.
   - Done when: a one-line goal + success criterion is written down.
   - On failure (goal still unclear): stop and ask the human partner.

2. **Research the unknowns** — skill: `researching-topics`
   - Needs: framed goal (step 1).
   - Does: frame the sub-questions, gather from independent sources (parallel via
     superpowers:dispatching-parallel-agents), evaluate, synthesize, cite.
   - Done when: each sub-question is answered with citations, and gaps are listed.
   - On failure (can't find answers): report the gaps as findings; flag assumptions.
   - [parallel-safe] independent sub-questions fan out.

3. **Analyze the evidence** — skill: `analyzing-data`
   - Needs: any datasets/metrics gathered in step 2.
   - Does: pick the analysis type (descriptive/diagnostic/predictive/qualitative),
     profile → clean → analyze → validate → report; chart via `dataviz` if it helps.
   - Done when: the decision-relevant question is answered with uncertainty stated.
   - On failure (dirty/insufficient data): document the limitation; loop back to step 2
     for more data if the decision needs it.
   - Skip if the goal has no data component.

4. **Design the workflow** — skill: `designing-workflows`
   - Needs: research findings (step 2) + analysis conclusions (step 3).
   - Does: define outcome, decompose into single-action steps, order by dependency,
     give each step a done-criterion, mark checkpoints and failure paths.
   - Done when: a numbered plan artifact exists with a done-criterion per step.
   - Checkpoint: human review of the plan before any action is taken.

5. **Execute every task and take action** — skill: `orchestrating-tasks`
   - Needs: the approved plan (step 4).
   - Does: turn each plan step into a tracked task; execute one at a time (or dispatch
     to subagents via superpowers:subagent-driven-development); verify each against its
     done-criterion; handle failures via superpowers:systematic-debugging.
   - Done when: every task is completed and verified.
   - On failure: follow each task's on-failure path; 3+ failures ⇒ return to step 4.

6. **Verify and report**
   - Needs: all tasks closed (step 5).
   - Does: confirm the step-1 success criterion with
     superpowers:verification-before-completion; report done / verified / skipped /
     open, honestly.
   - Done when: the goal's success criterion is confirmed true.

## Checkpoints

- After step 4: human reviews the plan before execution begins.
- Before any destructive, irreversible, or outward-facing action in step 5: confirm.

## Loops (when to go back)

- Step 3 needs more data → step 2.
- Step 5 shows the plan is wrong → step 4.
- Step 6 shows the goal isn't met → re-enter at the phase that fell short.

## Risks / open questions

- Skills authored to Superpowers **format** conventions but not yet run through the
  full RED→GREEN→REFACTOR subagent pressure-testing eval loop the `writing-skills`
  Iron Law requires before upstream deployment. Treat as working drafts; validate with
  `superpowers:writing-skills` before relying on them under pressure or contributing
  them upstream.
- Overlap with existing `writing-plans` / `executing-plans`: the new skills cross-
  reference rather than replace them and point to the more specific skill for code
  implementation work.
