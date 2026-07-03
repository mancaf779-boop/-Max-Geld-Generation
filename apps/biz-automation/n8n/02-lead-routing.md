# n8n Build Prompt — Workflow 2: Lead Routing & Task Creation

Paste this whole file into n8n's AI Workflow Builder to scaffold the workflow.

## Assumptions (swap any line if it doesn't match your setup)

- Leads arrive via a **Typeform** form.
- Owner notifications go out as **Slack DMs**.
- Owner → Slack-user-ID mapping lives in a **Google Sheet** tab
  (`SlackDirectory`) — no paid CRM assumed.

## Context: the biz-automation API

biz-automation is deployed and reachable at `{{BIZ_AUTOMATION_BASE_URL}}` (n8n
environment variable). Every route except `/health` requires header
`X-API-Key: {{BIZ_AUTOMATION_API_KEY}}` (n8n credential) — a request without
it, or with the wrong value, returns `401`.

`POST /leads/route` — body `{ leads: [{ id, source, region, dealSize, product }] }`
→ `{ assignments: [{ leadId, assignedTeam, assignedOwner, notification }], summary: { totalLeads, byTeam } }`.

Routing rules live server-side (deal size / region thresholds, round-robin
owner assignment) — call the API rather than reimplementing them in n8n.

## Workflow

1. **Typeform Trigger** node, bound to your lead-capture form.
2. **Code node**: map Typeform's field IDs to
   `{ id: {{$json.event_id}}, source: "typeform", region, dealSize, product }`
   — fill in your form's actual field-to-value mapping here.
3. **HTTP Request** → `POST {{BIZ_AUTOMATION_BASE_URL}}/leads/route`,
   header `X-API-Key: {{BIZ_AUTOMATION_API_KEY}}`, body
   `{ leads: [<mapped lead from step 2>] }`.
4. **Google Sheets "Lookup row"** on the `SlackDirectory` tab (columns:
   `ownerName`, `slackUserId`) using
   `{{$json.assignments[0].assignedOwner}}` to resolve the Slack user ID.
5. **Slack** node: DM that `slackUserId` with the lead details from
   `{{$json.assignments[0].notification}}`.
6. **Google Sheets "Append row"** to a `Leads` tab:
   `leadId, assignedTeam, assignedOwner, timestamp`.

## Notes

- The `Leads` Google Sheet tab is also read by Workflow 3 (Scheduled
  Reporting) — keep its column names stable if you change this workflow.
- If a lead's `assignedOwner` comes back `null` (empty team roster), branch
  on that before the Slack node — DMing a null user ID will error the
  workflow instead of just skipping the notification.
- Add a `401` check on the HTTP Request node's error output → Slack
  `#ops-alerts`, same as Workflow 1: a `401` means the credential is
  missing/expired, not that the lead payload is malformed.
