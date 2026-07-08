# Maxforge Lab Setup Guide

**Get started with Maxforge Lab in 5 minutes.**

---

## Quick Start (No Install)

Test the skills immediately in a headless session:

```bash
# Try the analyzing-data skill
claude -p "Analyze this: month,price,units | Jan,10,100 | Feb,12,90 | Mar,15,70. Does raising price hurt sales?" \
  --plugin-dir /path/to/maxforge-lab
```

The agent will auto-invoke `analyzing-data`, profile the data, and refuse to call correlation causation. **That's the skill working.**

---

## Installation

### For Claude Code

#### 1. Register the Marketplace

```bash
/plugin marketplace add mancaf779-boop/-Max-Geld-Generation
```

#### 2. Install the Plugin

```bash
/plugin install maxforge-lab
```

#### 3. Verify Installation

```bash
/plugin list
```

You should see `maxforge-lab` in the list. The `using-maxforge` bootstrap hook loads automatically at session start.

### For Local Development

```bash
git clone https://github.com/mancaf779-boop/-Max-Geld-Generation.git
cd -Max-Geld-Generation

# Use with headless commands
claude -p "your question" --plugin-dir .
```

---

## The Four Skills

### 1. **researching-topics** — Know before you act

**When to use:** Gather, evaluate, and synthesize information before deciding.

```bash
claude -p "Research: what are the top 3 factors driving cloud adoption in 2026?" --plugin-dir .
```

**What it enforces:**
- Frame the question clearly
- Gather from independent sources (in parallel)
- Corroborate findings
- State confidence + key assumptions

---

### 2. **analyzing-data** — Insight, not correlation

**When to use:** Profile, clean, analyze any data (CSV, JSON, logs, metrics).

```bash
claude -p "Analyze: Q1 revenue by region. North: $2M, South: $1.5M, East: $3M. Why is East winning?" --plugin-dir .
```

**What it enforces:**
- Profile the data (shape, ranges, outliers)
- Clean with a *stated rule*
- Analyze → validate
- **Correlation ≠ causation** — always

---

### 3. **designing-workflows** — Plan beats improvisation

**When to use:** Turn findings into an ordered, executable plan.

```bash
claude -p "Design a workflow to migrate our database from PostgreSQL to DynamoDB. We have 100GB of data and can afford 4 hours of downtime." --plugin-dir .
```

**What it enforces:**
- Outcome + verification method
- Single-action steps ordered by real dependency
- A **done-criterion per step**
- Parallel markers, checkpoints, failure paths

---

### 4. **orchestrating-tasks** — Execute → verify → done

**When to use:** Turn a plan into concrete tasks and take action.

```bash
claude -p "Execute the database migration plan we designed. Track each step." --plugin-dir .
```

**What it enforces:**
- Execute the step
- **Verify the result** (don't assume)
- Mark done only after verification
- Stop before irreversible or outward-facing moves

---

### 5. **using-maxforge** (Bootstrap) — Make them work together

**What it does:**
- Loads at session start
- Tells the agent which skill applies before acting
- Drives all 4 skills to **reliably auto-trigger**

**Measurement:** Without bootstrap: 2 of 4 fire. With bootstrap: 4 of 4 fire.

---

## Verifying Everything Works

### Test 1: Auto-trigger (Analyze skill)

```bash
claude -p "I have pricing data: Jan $10 (100 units), Feb $12 (90 units), Mar $15 (70 units). \
Does raising price hurt sales?" --plugin-dir .
```

✅ **Expected:** Agent invokes `analyzing-data`, profiles the data, states the correlation, refuses to claim causation.

### Test 2: Cross-domain (Research skill)

```bash
claude -p "Research the key factors companies cite for adopting AI agents in 2026. \
Frame the question, find 3 independent sources, and synthesize." --plugin-dir .
```

✅ **Expected:** Agent frames the question, gathers from multiple sources, states confidence and assumptions.

### Test 3: Full pipeline (All 4 skills)

```bash
claude -p "I need to roll out a new feature to 1000 customers over 30 days. \
Research best practices, analyze our customer segments, design a rollout plan, and give me the first 3 executable steps." --plugin-dir .
```

✅ **Expected:** Agent researches, analyzes, designs a plan with done-criteria, then proposes verification steps.

---

## Troubleshooting

### Skills aren't auto-triggering

**Problem:** I'm asking questions but the skills aren't invoking.

**Solution:**
1. Verify installation: `/plugin list` should show `maxforge-lab`
2. Restart Claude Code
3. Check that `using-maxforge` bootstrap is loaded (it should be automatic)
4. Review [`docs/research-to-execution-workflow.md`](research-to-execution-workflow.md) — your question may not match a skill's trigger

### "Skill not found" error

**Problem:** Getting an error that a skill is missing.

**Solution:**
1. Re-register marketplace: `/plugin marketplace add mancaf779-boop/-Max-Geld-Generation`
2. Re-install: `/plugin install maxforge-lab`
3. Check that your `.claude-plugin/` directory is valid

### Headless command fails

**Problem:** `claude -p "..." --plugin-dir .` returns an error.

**Solution:**
1. Verify you're in the maxforge-lab repo directory
2. Check path: `--plugin-dir` should point to the repository root
3. Ensure Claude CLI is up to date: `claude --version`

---

## What to Expect

### The Good

✅ **Reliable skill invocation** — All 4 fire consistently on matching tasks  
✅ **Cross-domain** — Tested on medical, finance, legal, ML, ops, marketing  
✅ **Model-agnostic** — Holds on both Opus- and Haiku-class  
✅ **Lightweight** — No runtime, no dependencies, plain Markdown  

### The Limitations

⚠️ **Skills enforce process, not judgment** — A weaker model won't gain better judgment; they gain discipline.  
⚠️ **Auto-trigger validated on Claude Code** — Other harnesses need per-harness verification.  
⚠️ **Not a substitute for monitoring** — Always track real usage once deployed.  

---

## Next Steps

- **Develop a new skill?** → See [`CONTRIBUTING.md`](../CONTRIBUTING.md)
- **Understand the pipeline?** → Read [`docs/research-to-execution-workflow.md`](research-to-execution-workflow.md)
- **See the eval evidence?** → Check [`docs/eval-report.md`](eval-report.md)
- **Need custom skills?** → Email mancaf779@gmail.com

---

## Support

- **Bug report:** [Open an issue](https://github.com/mancaf779-boop/-Max-Geld-Generation/issues)
- **General questions:** Check the [README](../README.md)
- **High-end services (Pro/Lab tiers):** mancaf779@gmail.com

---

**Last Updated:** 2026-07-08  
**Version:** 1.0 (Open tier)
