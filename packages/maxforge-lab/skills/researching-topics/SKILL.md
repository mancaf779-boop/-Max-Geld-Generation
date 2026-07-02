---
name: researching-topics
description: Use when you need to gather, evaluate, and synthesize information on a question or topic before acting - literature reviews, competitive/market scans, technical spikes, fact-finding, "look into X", "find out how Y works", or any decision that depends on evidence you don't yet have. Also when pressured to give a confident answer with "no hedging / no caveats / no gaps" and tempted to drop your confidence level or the key assumption you're betting on
---

# Researching Topics

## Overview

Research fails when you collect links instead of answers, trust the first source, or stop before you've closed the actual question.

**Core principle:** Research is answering a specific question with evidence you can cite and defend - not accumulating tabs.

**Announce at start:** "I'm using the researching-topics skill to investigate this."

## Confidence and the key assumption are part of the answer, not hedging

Lead with a clear recommendation - commit to it. But a confident recommendation ALWAYS carries two things in **one line**: your confidence level, and the key assumption you're betting on.

```
"Use X. Confident. The one thing I'm assuming is <assumption>; if that's false, reconsider."
```

**This survives "no hedging / no caveats / no gaps" pressure.** Waffling (refusing to commit, listing every possibility, "it depends") is what the person is rightly rejecting - drop that. The one-line confidence + assumption is the opposite: it's what lets them *act* on your answer and know when to revisit it. Dropping it doesn't make you more decisive, it makes you less trustworthy. Stating "I'm confident; I'm betting on X" is not a caveat - it's the deliverable.

## When to Use

- A decision depends on facts you don't have ("which library", "is X feasible", "what's the market")
- Someone asks you to "look into", "find out", "research", or "understand" something
- You're about to analyze data or plan work but don't yet understand the domain

**Don't use for:** Questions you can answer from the codebase directly (search it), or trivial lookups (just look it up).

## The Process

### 1. Frame the question
Write the ONE question you must answer, plus the sub-questions that would settle it. Vague question → vague research. If you can't state what a good answer looks like, you're not ready to search.

### 2. Gather in parallel
Cast wide, from independent sources. When the search has independent branches, fan them out.

**REQUIRED SUB-SKILL when subagents are available:** Use superpowers:dispatching-parallel-agents to run independent searches concurrently and return synthesis, not raw dumps.

### 3. Evaluate every source
For each claim ask: Who says it? When? What's their incentive? Is it corroborated? Primary source beats a summary of a summary. Flag anything you can't corroborate as *unverified*.

### 4. Synthesize, don't list
Answer the framed question in prose. Group findings by claim, not by source. Note where sources agree, disagree, and are silent.

### 5. Cite and expose gaps
Every non-obvious claim gets a source. State explicitly what you could NOT find and what confidence you have. Unknowns are findings.

## Quick Reference

| Step | Output |
|------|--------|
| Frame | The question + what a good answer looks like |
| Gather | Sources from independent origins (parallel) |
| Evaluate | Credibility + corroboration per claim |
| Synthesize | Answer to the question, grouped by claim |
| Cite | Sources + explicit list of gaps/unknowns |

## Red Flags — STOP

- Omitting your confidence level or key assumption because someone said "no hedging/caveats/gaps"
- Presenting an unverified claim as established fact to sound more decisive
- Answering a fuzzy question you never framed
- Reporting sources you found without answering the actual question

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "They said no caveats, so I'll drop the confidence/assumption line" | That line is one sentence and it's what lets them act. It's the deliverable, not a caveat. Drop the waffle, keep it. |
| "Being confident means stating it as flat fact" | Confidence is committing to a recommendation *and* naming what you're betting on. Flat false certainty is just guessing loudly. |
| "No time to corroborate, the first source is probably right" | One independent check is cheap; a confident wrong answer is expensive. |
| "Stating what I couldn't verify makes me look unsure" | It makes you trustworthy. Unknowns are findings. |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Collecting links, calling it research | Answer the question in your own words with citations |
| Trusting the first / top result | Corroborate from an independent source |
| Reporting only what you found | Report what you couldn't find too |
| Burying the answer in a source dump | Lead with the answer; sources support it |
| Researching a fuzzy question | Frame the exact question first |

## Integration

- **superpowers:dispatching-parallel-agents** — fan out independent searches
- **analyzing-data** — when the answer requires crunching numbers, not just reading
- **designing-workflows** — feed findings into a plan
- **superpowers:verification-before-completion** — confirm the question is actually answered before you stop
