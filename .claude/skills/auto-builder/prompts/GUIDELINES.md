# Global prompting guidelines

These apply to **every** prompt in this library. Each task prompt assumes them.

## Structure every prompt follows
1. **Role** — who the model is acting as.
2. **Objective** — the single outcome to produce.
3. **Inputs** — `{{variables}}` the caller fills in.
4. **Execution steps** — the ordered method, not just the ask.
5. **Guidelines** — quality rules specific to the task.
6. **Output** — exact format; strict minified JSON when the result feeds automation.
7. **Self-check** — the model verifies its own output before returning.

## Non-negotiable guardrails (bake into every prompt)
- **No fabrication.** Never invent statistics, studies, quotes, names, prices, or
  reviews. If a fact isn't provided, either omit it or mark it clearly as an
  assumption the user must verify.
- **No guaranteed-income / guaranteed-outcome claims.** Describe benefits honestly;
  never promise money, rankings, or results.
- **No secrets in output.** Never echo API keys, tokens, or credentials.
- **Stay on-brand and truthful.** Match the requested tone; don't overhype.
- **Ask-free automation.** When run headless (in a workflow), do not ask the user
  questions — make a reasonable choice and note assumptions in an `assumptions`
  field where the schema allows.

## Quality levers
- Prefer **specific and concrete** over generic. One vivid example beats three vague ones.
- Lead with the **outcome/hook**; put supporting detail after.
- Keep to the requested length; being clear matters more than being long.
- For JSON output: return **only** minified JSON, no markdown fences, no preamble.

## Model note
Default model `claude-opus-4-8` for best quality; `claude-sonnet-5` or
`claude-haiku-4-5` to cut cost. These prompts are model-agnostic.
