#!/usr/bin/env node
/**
 * Driver for the biz-automation app: a dependency-free Node HTTP API that
 * triages invoices, routes leads, and generates/schedules reports.
 *
 * Subcommands:
 *   node driver.js direct   - import lib/ functions directly, no server, no port.
 *                             Fastest check; this is what most PRs touching
 *                             invoices.js/leads.js/reports.js actually need.
 *   node driver.js cli      - run `node src/cli.js report` (one-shot) and
 *                             confirm it writes a report file.
 *   node driver.js server   - launch the real HTTP server on a scratch port,
 *                             drive every route with real payloads (chaining
 *                             invoice + lead output into report generation,
 *                             the way a real orchestration would), confirm
 *                             the scheduler fires on its interval, then kill
 *                             the server cleanly.
 *   node driver.js all      - all three, in the order above. Default.
 *
 * Exit code 0 = all requested checks passed, 1 = something failed (see
 * stderr for which check and why).
 */
const path = require("node:path");
const fs = require("node:fs");
const crypto = require("node:crypto");
const { spawn } = require("node:child_process");

const APP_ROOT = path.join(__dirname, "..", "..", "..");

let failures = 0;
function check(label, cond, detail) {
  if (cond) {
    console.log(`  PASS: ${label}`);
  } else {
    failures += 1;
    console.error(`  FAIL: ${label}${detail ? ` — ${detail}` : ""}`);
  }
}

function runDirect() {
  console.log("== direct invocation ==");
  const { processInvoices } = require(path.join(APP_ROOT, "src/lib/invoices"));
  const { routeLeads } = require(path.join(APP_ROOT, "src/lib/leads"));
  const { generateReport } = require(path.join(APP_ROOT, "src/lib/reports"));

  const invoices = JSON.parse(fs.readFileSync(path.join(APP_ROOT, "data/sample-invoices.json"), "utf8")).invoices;
  const leads = JSON.parse(fs.readFileSync(path.join(APP_ROOT, "data/sample-leads.json"), "utf8")).leads;
  const sales = JSON.parse(fs.readFileSync(path.join(APP_ROOT, "data/sample-sources.json"), "utf8")).salesData;

  const invResult = processInvoices(invoices);
  check("processInvoices flags the duplicate/high-value/mismatched/malformed rows", invResult.flagged.length === 4, `got ${invResult.flagged.length}`);
  check("processInvoices approves the one clean invoice", invResult.approved.length === 1, `got ${invResult.approved.length}`);

  const leadResult = routeLeads(leads);
  check("routeLeads routes the >$50k US lead to enterprise-sales", leadResult.assignments[0].assignedTeam === "enterprise-sales");
  check("routeLeads routes the EU lead to eu-sales", leadResult.assignments[1].assignedTeam === "eu-sales");

  const report = generateReport({ invoiceSummary: invResult.summary, leadSummary: leadResult.summary, salesData: sales });
  check("generateReport produces markdown mentioning all three sections", ["Invoices", "Leads", "Revenue trend"].every((s) => report.markdown.includes(s)));
}

function runCli() {
  console.log("== cli (report --once) ==");
  const reportsDir = path.join(APP_ROOT, "reports");
  const before = fs.existsSync(reportsDir) ? fs.readdirSync(reportsDir).length : 0;
  const result = require("node:child_process").spawnSync("node", ["src/cli.js", "report"], { cwd: APP_ROOT, encoding: "utf8" });
  check("cli exits 0", result.status === 0, `stderr: ${result.stderr}`);
  check("cli prints a Business Automation Report", result.stdout.includes("# Business Automation Report"));
  const after = fs.existsSync(reportsDir) ? fs.readdirSync(reportsDir).length : 0;
  check("cli writes a new report file", after === before + 1, `before=${before} after=${after}`);
}

function waitForHealth(port, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  const poll = async () => {
    while (Date.now() < deadline) {
      try {
        const res = await fetch(`http://localhost:${port}/health`);
        if (res.ok) return true;
      } catch {
        // not up yet
      }
      await new Promise((r) => setTimeout(r, 150));
    }
    return false;
  };
  return poll();
}

async function runServer() {
  console.log("== server (full HTTP smoke test) ==");
  const port = 8901 + Math.floor(Math.random() * 500);
  const apiKey = crypto.randomBytes(16).toString("hex");
  const child = spawn("node", ["src/server.js"], {
    cwd: APP_ROOT,
    env: { ...process.env, PORT: String(port), REPORT_SCHEDULE_MS: "1200", BIZ_AUTOMATION_API_KEY: apiKey },
    stdio: ["ignore", "pipe", "pipe"],
  });
  let out = "";
  child.stdout.on("data", (d) => (out += d));
  child.stderr.on("data", (d) => (out += d));

  try {
    const up = await waitForHealth(port, 8000);
    check("server becomes healthy within 8s", up, out);
    if (!up) return;

    const invoices = JSON.parse(fs.readFileSync(path.join(APP_ROOT, "data/sample-invoices.json"), "utf8"));
    const leads = JSON.parse(fs.readFileSync(path.join(APP_ROOT, "data/sample-leads.json"), "utf8"));
    const base = `http://localhost:${port}`;
    const authHeaders = { "Content-Type": "application/json", "X-API-Key": apiKey };

    const unauthed = await fetch(`${base}/invoices/process`, { method: "POST", body: "{}", headers: { "Content-Type": "application/json" } });
    check("request without X-API-Key is rejected with 401", unauthed.status === 401, `got ${unauthed.status}`);

    const invResp = await (await fetch(`${base}/invoices/process`, { method: "POST", body: JSON.stringify(invoices), headers: authHeaders })).json();
    check("POST /invoices/process flags 4 of 5 rows", invResp.summary.flaggedCount === 4, JSON.stringify(invResp.summary));

    const leadResp = await (await fetch(`${base}/leads/route`, { method: "POST", body: JSON.stringify(leads), headers: authHeaders })).json();
    check("POST /leads/route routes all 5 leads", leadResp.summary.totalLeads === 5);

    const combined = { invoiceSummary: invResp.summary, leadSummary: leadResp.summary, salesData: JSON.parse(fs.readFileSync(path.join(APP_ROOT, "data/sample-sources.json"), "utf8")).salesData };
    const reportResp = await (await fetch(`${base}/reports/generate`, { method: "POST", body: JSON.stringify(combined), headers: authHeaders })).json();
    check("POST /reports/generate chains invoice+lead+sales into one report", reportResp.markdown.includes("Invoices") && reportResp.markdown.includes("Leads") && reportResp.markdown.includes("Revenue trend"));

    const before404 = await fetch(`${base}/reports/does-not-exist`, { headers: authHeaders });
    check("unknown route returns 404", before404.status === 404);

    console.log("  waiting ~1.5s for the report scheduler to tick...");
    await new Promise((r) => setTimeout(r, 1500));
    const latest = await (await fetch(`${base}/reports/latest`, { headers: authHeaders })).json();
    check("scheduler populates /reports/latest on its own", Boolean(latest.generatedAt), JSON.stringify(latest));
  } finally {
    child.kill("SIGTERM");
    await new Promise((r) => setTimeout(r, 300));
    if (!child.killed) child.kill("SIGKILL");
  }
}

async function main() {
  const sub = process.argv[2] || "all";
  if (sub === "direct" || sub === "all") runDirect();
  if (sub === "cli" || sub === "all") runCli();
  if (sub === "server" || sub === "all") await runServer();

  if (failures > 0) {
    console.error(`\n${failures} check(s) failed.`);
    process.exit(1);
  }
  console.log("\nAll checks passed.");
}

main();
