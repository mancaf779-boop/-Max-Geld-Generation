const HIGH_VALUE_THRESHOLD = 10000;
const LINE_ITEM_TOLERANCE = 0.01; // 1%

function lineItemTotal(lineItems = []) {
  return lineItems.reduce((sum, li) => sum + (li.qty ?? 0) * (li.unitPrice ?? 0), 0);
}

/**
 * Validate and triage a batch of invoices.
 * @param {Array<object>} invoices
 * @returns {{approved: object[], flagged: object[], summary: object}}
 */
function processInvoices(invoices) {
  if (!Array.isArray(invoices)) {
    throw new TypeError("invoices must be an array");
  }

  const seenIds = new Set();
  const approved = [];
  const flagged = [];

  for (const invoice of invoices) {
    const reasons = [];
    const { id, vendor, amount, lineItems } = invoice;

    if (!id || !vendor || amount === undefined || amount === null) {
      reasons.push("missing_field");
    }
    if (id && seenIds.has(id)) {
      reasons.push("duplicate_id");
    }
    if (id) seenIds.add(id);

    if (typeof amount === "number" && amount <= 0) {
      reasons.push("non_positive_amount");
    }

    if (Array.isArray(lineItems) && lineItems.length > 0 && typeof amount === "number") {
      const computed = lineItemTotal(lineItems);
      const delta = Math.abs(computed - amount);
      if (delta > amount * LINE_ITEM_TOLERANCE) {
        reasons.push("line_item_mismatch");
      }
    }

    if (typeof amount === "number" && amount > HIGH_VALUE_THRESHOLD) {
      reasons.push("high_value_review");
    }

    if (reasons.length > 0) {
      flagged.push({ ...invoice, reasons });
    } else {
      approved.push(invoice);
    }
  }

  const totalAmount = invoices.reduce((sum, inv) => sum + (typeof inv.amount === "number" ? inv.amount : 0), 0);
  const approvedAmount = approved.reduce((sum, inv) => sum + (inv.amount ?? 0), 0);
  const flaggedAmount = flagged.reduce((sum, inv) => sum + (inv.amount ?? 0), 0);

  return {
    approved,
    flagged,
    summary: {
      totalInvoices: invoices.length,
      approvedCount: approved.length,
      flaggedCount: flagged.length,
      totalAmount,
      approvedAmount,
      flaggedAmount,
    },
  };
}

module.exports = { processInvoices, HIGH_VALUE_THRESHOLD, LINE_ITEM_TOLERANCE };
