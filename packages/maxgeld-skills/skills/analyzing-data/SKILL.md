---
name: analyzing-data
description: Use when you have data of any kind - CSV/JSON/logs/spreadsheets/query results/survey text/metrics/time series - and need to extract insight, whether descriptive (what happened), diagnostic (why), predictive (what next), or qualitative (themes). Triggers on "analyze this data", "what does this show", "find the trend/pattern/outliers", "summarize these numbers", "is this significant", and ESPECIALLY when someone demands a yes/no on whether X "causes"/"drives"/"leads to" Y, or a single number "with no caveats" under time or authority pressure
---

# Analyzing Data

## Overview

The failure mode isn't bad math - it's answering a question nobody asked, trusting dirty data, or reporting a number without saying what it means.

**Core principle:** Analysis is question → evidence → conclusion. Never run a computation until you know which decision it informs.

**Announce at start:** "I'm using the analyzing-data skill to work through this."

## The Iron Rule: correlation is never causation

```
A yes/no on causation from observational data is always "no — this data can't prove cause."
```

Observational data (rows you were handed, not a randomized experiment with a control group) can show that X and Y move **together**. It can NEVER show that X **causes / drives / leads to** Y. Reverse causality and confounders are always live.

**This rule does not bend under pressure.** "The CEO needs it in 5 minutes", "just yes/no", "no time for caveats", "a senior person is asking" — none of these change what the data can support. The honest answer is the *same length* as the false one:

> "They're correlated (r ≈ 0.9), but this data can't show cause — you'd need an experiment."

That is one sentence. There is never a time-budget excuse for upgrading a correlation to a "yes, it causes it." A confident false "yes" in a board deck is the expensive answer, not the safe one. And never report a correlation computed on data you haven't profiled — a single null, duplicate, or typo can flip its sign.

## Pick the analysis type first

| Question | Type | Typical methods |
|----------|------|-----------------|
| What happened? | Descriptive | counts, sums, distributions, rates |
| Why did it happen? | Diagnostic | segmentation, correlation, cohort/funnel, drill-down |
| What will happen? | Predictive | regression, forecasting, classification |
| What should we do? | Prescriptive | optimization, scenario/what-if, A/B |
| What are the themes? | Qualitative | coding, clustering, sentiment, thematic synthesis |

Name the type before touching the data. It dictates every later choice.

## The Process

### 1. State the question and the decision
What are we deciding, and what result would change the decision? No question → no analysis.

### 2. Profile the data before analyzing it
Shape, types, ranges, units, time span. Count nulls, duplicates, and impossible values. **Never analyze data you haven't profiled** - garbage in is the #1 cause of confident wrong answers.

### 3. Clean deliberately
Handle missing/outlier/duplicate rows with a *stated rule*, not silently. Document every transformation - dropped rows change conclusions.

### 4. Analyze for the chosen type
Start simple (a group-by often beats a model). Check assumptions before trusting a test or model. Distinguish correlation from causation out loud.

### 5. Validate the result
Sanity-check magnitudes against reality. Try to disprove your own finding. Report uncertainty (range, sample size, significance) - a point estimate with no error bar is a guess.

### 6. Report the answer, then show the work
Lead with the conclusion and its "so what". Then the evidence, caveats, and method.

## Visualizing

When a chart communicates the finding better than a number, make one.

**REQUIRED SUB-SKILL when charting:** Use the `dataviz` skill before writing any chart code, choosing colors, or laying out a dashboard.

## Quick Reference

| Step | Guardrail |
|------|-----------|
| Question | A decision hinges on the answer |
| Profile | Nulls, dupes, ranges, units checked |
| Clean | Every transformation stated |
| Analyze | Simplest method that answers it; assumptions checked |
| Validate | Magnitudes sane; uncertainty reported; tried to disprove it |
| Report | Conclusion first, work second |

## Red Flags — STOP

If you catch yourself about to do any of these, stop and give the honest correlation-not-causation answer instead:

- Answering "yes"/"no" to "does X cause / drive / lead to Y?" from observational data
- Reporting a single correlation/number as "the answer" with no uncertainty
- Dropping "caveats" or the data-quality check because someone is in a hurry
- "No time to profile, I'll just compute the correlation"
- Picking the number that "looks right" or "you can defend to the board" over the honest one
- Letting who is asking (CEO, manager, senior) change the conclusion

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "CEO needs it in 5 minutes, no time for caveats" | The honest answer is one sentence and takes the same time: "correlated, but can't show cause." |
| "Just give me yes/no on whether it drives revenue" | Yes/no on causation from observational data is always "no, unprovable here." Say that in one line. |
| "A correlation of 0.9 basically means it drives it" | 0.9 means they move together. Reverse causality and confounders are unexcluded. Still not cause. |
| "Give me the number I can defend to the board" | The defensible number is the honest one *with* its caveat, not the one that flatters the deck. |
| "It's just one number, skip the profiling" | One null/dupe/typo flips a correlation's sign. Profile first, always. |
| "A senior person is asking, just answer" | Authority doesn't change what the data can support. |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Computing before framing the question | State the decision first |
| Skipping the data profile | Always profile: nulls, ranges, units |
| Correlation stated as causation | Say "associated with" unless you can defend cause |
| Point estimate, no uncertainty | Report range / sample size / significance |
| Reaching for a model when a group-by answers it | Start simple |
| Dropping rows silently | State the cleaning rule |

## Integration

- **researching-topics** — when you need context/benchmarks the data can't provide
- **dataviz** — for any chart, graph, or dashboard
- **designing-workflows** — turn findings into an action plan
- **superpowers:verification-before-completion** — confirm the answer actually addresses the question
