# <Task name>

**Use for:** <when to reach for this prompt>
**Feeds:** <which workflow node / where the output goes>
**Variables:** `{{var_a}}`, `{{var_b}}`

---

You are <ROLE>. Your objective is to <OBJECTIVE>.

Inputs:
- <var_a>: {{var_a}}
- <var_b>: {{var_b}}

Execution steps:
1. <step>
2. <step>
3. <step>

Guidelines:
- <task-specific quality rule>
- Do NOT invent facts, numbers, or names. Omit or flag anything unverified.
- Do NOT promise guaranteed results.

Before answering, self-check: <what to verify>.

Return ONLY valid minified JSON (no markdown, no fences) with exactly:
{"field_a":"...","field_b":"...","assumptions":"anything you assumed, or empty"}
