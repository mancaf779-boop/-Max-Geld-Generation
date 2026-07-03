# n8n Build Prompt — Workflow 1: Invoice Intake & Triage

Paste this whole file into n8n's AI Workflow Builder to scaffold the workflow.

## Assumptions (swap any line if it doesn't match your setup)

- Invoices arrive as **CSV attachments to an `invoices@` inbox** (Gmail/IMAP).
- Flagged invoices get reviewed in **Slack** (`#ap-review`).
- The audit trail is a **Google Sheet** (tab: `Invoices`) — no paid CRM/ERP assumed.

## Context: the biz-automation API

biz-automation is deployed and reachable at `{{BIZ_AUTOMATION_BASE_URL}}` (n8n
environment variable). Every route except `/health` requires header
`X-API-Key: {{BIZ_AUTOMATION_API_KEY}}` (n8n credential) — a request without
it, or with the wrong value, returns `401`.

`POST /invoices/process` — body `{ invoices: [{ id, vendor, amount, dueDate, lineItems: [{desc, qty, unitPrice}] }] }`
→ `{ approved: [...], flagged: [{...invoice, reasons: [...]}], summary: { totalInvoices, approvedCount, flaggedCount, totalAmount, approvedAmount, flaggedAmount } }`.

Flag reasons: `missing_field`, `duplicate_id`, `non_positive_amount`,
`line_item_mismatch`, `high_value_review`.

Call the API for all validation/triage logic — do not reimplement the
invoice rules in a Code node.

## Workflow

1. **Email Trigger (IMAP)** on `invoices@yourcompany.com`, filter: has
   attachment, attachment type `.csv`.
2. **Spreadsheet File** node: parse the CSV attachment into JSON rows.
3. **Code node**: reshape rows into
   `{ invoices: [{ id, vendor, amount, dueDate, lineItems }] }` — map your
   CSV's actual column names to these fields here. This is the one place
   column-name differences get absorbed.
4. **HTTP Request** → `POST {{BIZ_AUTOMATION_BASE_URL}}/invoices/process`,
   header `X-API-Key: {{BIZ_AUTOMATION_API_KEY}}`, body from step 3.
5. **IF**: `{{$json.summary.flaggedCount}} > 0`
   - **True branch**: Split Out on `flagged` → **Slack** node posting to
     `#ap-review`, one message per invoice, including `id`, `vendor`,
     `amount`, `reasons`.
   - **False/approved branch**: pass straight through to step 6.
6. **Merge** both branches → **Google Sheets** "Append row" to the
   `Invoices` tab: `id, vendor, amount, status (approved/flagged), reasons, processedAt`.
7. **Error Trigger workflow** → Slack `#ops-alerts` on any node failure in
   this workflow; include the HTTP status code from the biz-automation
   call. A `401` there means the `X-API-Key` credential is missing or
   expired, not that the invoice data is bad — check the credential first.

## Notes

- The `Invoices` Google Sheet tab is also read by Workflow 3 (Scheduled
  Reporting) — keep its column names (`id, vendor, amount, status, reasons,
  processedAt`) stable if you change this workflow.
- Retry the HTTP Request node 2–3 times on 5xx/timeout before falling
  through to the error-alert branch; do not retry on `401` (retrying
  won't fix a bad credential).
