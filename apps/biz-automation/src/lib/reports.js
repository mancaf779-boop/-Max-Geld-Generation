function sparkline(values) {
  const bars = "▁▂▃▄▅▆▇█";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  return values
    .map((v) => bars[Math.min(bars.length - 1, Math.floor(((v - min) / range) * (bars.length - 1)))])
    .join("");
}

/**
 * Aggregate invoice/lead/sales data into a single business report.
 * @param {{invoiceSummary?: object, leadSummary?: object, salesData?: Array<{month:string, revenue:number}>}} sources
 * @returns {{generatedAt: string, markdown: string, data: object}}
 */
function generateReport(sources = {}) {
  const generatedAt = new Date().toISOString();
  const { invoiceSummary, leadSummary, salesData = [] } = sources;

  const revenues = salesData.map((d) => d.revenue);
  const totalRevenue = revenues.reduce((a, b) => a + b, 0);
  const trend = revenues.length > 1 ? sparkline(revenues) : "";

  const lines = [];
  lines.push(`# Business Automation Report`);
  lines.push(``);
  lines.push(`Generated: ${generatedAt}`);
  lines.push(``);

  if (invoiceSummary) {
    lines.push(`## Invoices`);
    lines.push(`- Total: ${invoiceSummary.totalInvoices}, Approved: ${invoiceSummary.approvedCount}, Flagged: ${invoiceSummary.flaggedCount}`);
    lines.push(`- Total amount: $${invoiceSummary.totalAmount.toFixed(2)} (approved $${invoiceSummary.approvedAmount.toFixed(2)}, flagged $${invoiceSummary.flaggedAmount.toFixed(2)})`);
    lines.push(``);
  }

  if (leadSummary) {
    lines.push(`## Leads`);
    lines.push(`- Total routed: ${leadSummary.totalLeads}`);
    for (const [team, count] of Object.entries(leadSummary.byTeam ?? {})) {
      lines.push(`  - ${team}: ${count}`);
    }
    lines.push(``);
  }

  if (salesData.length > 0) {
    lines.push(`## Revenue trend`);
    lines.push(`- Months: ${salesData.map((d) => d.month).join(", ")}`);
    lines.push(`- Total: $${totalRevenue.toFixed(2)}`);
    lines.push(`- Trend: ${trend}`);
    lines.push(``);
  }

  return {
    generatedAt,
    markdown: lines.join("\n"),
    data: { invoiceSummary, leadSummary, totalRevenue, revenueTrend: trend },
  };
}

module.exports = { generateReport, sparkline };
