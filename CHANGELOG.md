# Changelog

All notable changes to Maxforge Lab are documented here.

## [1.0.0] — 2026-07-02

Initial release.

### Skills
- **researching-topics** — frame the question, gather from independent sources
  (in parallel), evaluate credibility, synthesize, cite, and state confidence +
  the key assumption you're betting on.
- **analyzing-data** — descriptive / diagnostic / predictive / prescriptive /
  qualitative analysis with profile → clean → analyze → validate → report
  guardrails, and a hard correlation-is-not-causation rule.
- **designing-workflows** — turn a goal + findings into an ordered, verifiable
  step-by-step workflow with per-step done-criteria, checkpoints, and failure
  paths.
- **orchestrating-tasks** — turn a plan into tracked tasks and execute them,
  verifying each result and stopping before any irreversible or outward-facing
  action.
- **using-maxforge** (bootstrap) — loads at session start via a hook and makes
  the other four reliably auto-trigger.

### Bootstrap / hooks
- `skills/using-maxforge/SKILL.md` + `hooks/` (SessionStart hook + cross-platform
  `run-hook.cmd` launcher). Without a bootstrap, bare skills auto-trigger
  inconsistently (measured 2 of 4 in Claude Code); with it, all four fire.

### Docs
- `docs/research-to-execution-workflow.md` — the end-to-end pipeline that chains
  the four skills (Research → Analyze → Plan → Execute).
- `docs/eval-report.md` — the RED→GREEN→REFACTOR eval campaign (~30 subagent
  runs across max-pressure, cross-domain, and weaker-model rounds).

### Validation
- Two skills (`analyzing-data`, `researching-topics`) had real
  under-pressure failures that were caught, refactored, and re-verified.
- All four validated across multiple domains on both Opus- and Haiku-class
  models, and confirmed to auto-trigger live in Claude Code with the bootstrap.
  See `docs/eval-report.md` for the full record and known limitations.
