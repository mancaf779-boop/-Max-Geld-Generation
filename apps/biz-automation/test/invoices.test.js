const test = require("node:test");
const assert = require("node:assert/strict");
const { processInvoices } = require("../src/lib/invoices");

test("flags duplicate ids, high value, mismatch, and missing fields; approves the clean one", () => {
  const { approved, flagged, summary } = processInvoices([
    { id: "A", vendor: "V", amount: 100, lineItems: [{ desc: "x", qty: 2, unitPrice: 50 }] },
    { id: "B", vendor: "V", amount: 20000, lineItems: [{ desc: "x", qty: 1, unitPrice: 20000 }] },
    { id: "B", vendor: "V", amount: 20000, lineItems: [{ desc: "x", qty: 1, unitPrice: 20000 }] },
    { id: "C", vendor: "V", amount: 500, lineItems: [{ desc: "x", qty: 1, unitPrice: 100 }] },
    { id: "", vendor: "", amount: -5, lineItems: [] },
  ]);

  assert.equal(approved.length, 1);
  assert.equal(approved[0].id, "A");
  assert.equal(flagged.length, 4);
  assert.ok(flagged.find((f) => f.id === "B" && f.reasons.includes("high_value_review")));
  assert.ok(flagged.some((f) => f.reasons.includes("duplicate_id")));
  assert.ok(flagged.find((f) => f.id === "C").reasons.includes("line_item_mismatch"));
  assert.equal(summary.totalInvoices, 5);
});
