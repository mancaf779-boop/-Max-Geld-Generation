# n8n Build Prompt — Workflow 3: Scheduled Reporting

Paste this whole file into n8n's AI Workflow Builder to scaffold the workflow.

## Assumptions (swap any line if it doesn't match your setup)

- The report is emailed daily to a stakeholder distribution list.
- The source data is the `Invoices` and `Leads` Google Sheet tabs written
  by Workflows 1 and 2 (see `01-invoice-intake-triage.md` and
  `02-lead-routing.md`).
- Raw reports are archived to Google Drive.

## Context: the biz-automation API

biz-automation is deployed and reachable at `{{BIZ_AUTOMATION_BASE_URL}}` (n8n
environment variable). Every route except `/health` requires header
`X-API-Key: {{BIZ_AUTOMATION_API_KEY}}` (n8n credential) — a request without
it, or with the wrong value, returns `401`.

`POST /reports/generate` — body `{}` (uses server-side sample data) or
`{ invoiceSummary, leadSummary, salesData }` → `{ generatedAt, markdown, data }`.
`GET /reports/latest` returns the same shape as the last generated report.

## Workflow

1. **Schedule Trigger**: daily at 08:00.
2. **Google Sheets "Get many rows"** on the `Invoices` and `Leads` tabs,
   filtered to the prior 24h (on `processedAt` / `timestamp`).
3. **Code node**: reduce those rows into
   `{ invoiceSummary: { totalInvoices, approvedCount, flaggedCount, totalAmount, approvedAmount, flaggedAmount }, leadSummary: { totalLeads, byTeam } }`
   — matching the API's own summary schema — plus a `salesData` array
   (`[{ month, revenue }]`) from wherever your revenue numbers live.
4. **HTTP Request** → `POST {{BIZ_AUTOMATION_BASE_URL}}/reports/generate`,
   header `X-API-Key: {{BIZ_AUTOMATION_API_KEY}}`, body from step 3.
5. **Markdown** node: convert `{{$json.markdown}}` to HTML.
6. **Send Email** node: to your stakeholder distribution list, subject
   `Business Automation Report — {{$json.generatedAt}}`.
7. **Google Drive "Upload"**: archive the raw markdown as
   `report-{{$json.generatedAt}}.md`.

## Notes

- Alternative to steps 2–4: if the biz-automation server itself is running
  with `REPORT_SCHEDULE_MS` set, it already regenerates a report on its
  own interval — you can skip the Sheets aggregation entirely and just
  `GET {{BIZ_AUTOMATION_BASE_URL}}/reports/latest` (still needs the
  `X-API-Key` header). Use this simpler path unless you specifically need
  the report to reflect Sheet edits made after the server last ran.
- If `GET /reports/latest` is called before the server has generated its
  first report, it returns `404` with `{"error": "no report generated yet"}`
  — branch on that rather than treating it as a hard failure on a fresh
  deploy.
