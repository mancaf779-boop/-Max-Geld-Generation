# Prompt library

One comprehensive, reusable prompt per task — each covers role → execution →
guidelines → output → guardrails. Read `GUIDELINES.md` first; it applies to all.
Fill the `{{variables}}`, send to the model, parse the strict JSON output.

| Task | File | Output feeds |
|------|------|--------------|
| Global rules (read first) | `GUIDELINES.md` | — |
| Prompt template | `_TEMPLATE.md` | authoring new prompts |
| Social post | `social-post.md` | content workflow |
| Blog / SEO article | `blog-article.md` | CMS / newsletter |
| Content repurposing | `content-repurpose.md` | multi-platform publish |
| Cold outreach sequence | `cold-outreach.md` | email/DM send |
| Lead qualification | `lead-qualify.md` | route/filter node |
| Product description | `product-description.md` | store / listing update |
| Price-change decision | `price-monitor-decision.md` | reprice / alert branch |
| Client audit report | `client-audit-report.md` | DOCX/PDF / email |
| Proposal / quote | `proposal-quote.md` | document / email |
| n8n workflow spec | `n8n-workflow-spec.md` | the build step |

## How to use in an n8n HTTP (Claude) node
1. Copy the prompt body, replace `{{variables}}` with expressions
   (e.g. `{{ $json.topic }}`) or Set-node values.
2. Put it as the `content` of the user message in the JSON body.
3. The prompts return strict minified JSON — parse it in a following Code node.

## Adding a new task prompt
Copy `_TEMPLATE.md`, keep the 7-part structure and the guardrails, add it to the
table above. Use `skill-creator` (claude.ai) if you want to formalize it further.
