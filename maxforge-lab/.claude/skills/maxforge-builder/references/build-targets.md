# Choosing the build target

Match the task to the smallest artifact that fits. Don't reach for a heavy
target when a simple one works.

| If the task is… | Build… | Why |
|---|---|---|
| A recurring flow across several apps that a non-coder will maintain | **n8n workflow** | Visual, credential-managed, easy to tweak without code |
| One-off transformation or code-controlled logic | **Standalone script** (Python/Node/Bash) | Fastest to write and run; full control |
| Time-based repetition | **Scheduled job** | cron for scripts, or an n8n Schedule Trigger inside a workflow |
| A webhook-driven reaction (form submit, GitHub event, payment) | **n8n workflow** with a Webhook trigger, or a small web handler | Event in → action out |
| Text generation / summarize / classify / extract | **Claude API call** | Use `claude-opus-4-8`; cheaper: `claude-sonnet-5`, `claude-haiku-4-5`. Put the call in whichever host above fits |
| Multi-step agentic work with tools and its own workspace | **Claude Agent / Managed Agent** | When the model must plan and act, not just transform |

## Decision shortcuts
- **Will the user edit it themselves without code?** → n8n workflow.
- **Does it need tight logic, tests, or libraries?** → script.
- **Is it just "call the model on a schedule"?** → schedule trigger + one Claude call.
- **Does it already exist?** → check `references/marketplace.md` first.

## After choosing
1. Create the artifact (bundled scripts for n8n; write code directly otherwise).
2. Validate (n8n validator, or the script's own tests / a smoke run).
3. Execute (`scripts/run.py` for scripts; `scripts/n8n/deploy_workflow.py` or UI
   import for n8n).
4. Report the outcome honestly — including failures and their output.
