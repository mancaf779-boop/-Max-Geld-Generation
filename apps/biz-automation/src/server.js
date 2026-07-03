const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const { processInvoices } = require("./lib/invoices");
const { routeLeads } = require("./lib/leads");
const { generateReport } = require("./lib/reports");
const { createScheduler } = require("./lib/scheduler");

const PORT = Number(process.env.PORT || 8080);
const REPORT_SCHEDULE_MS = process.env.REPORT_SCHEDULE_MS ? Number(process.env.REPORT_SCHEDULE_MS) : null;
const DATA_DIR = path.join(__dirname, "..", "data");

let latestReport = null;

function readJson(body) {
  if (!body) return {};
  return JSON.parse(body);
}

function sampleSources() {
  return JSON.parse(fs.readFileSync(path.join(DATA_DIR, "sample-sources.json"), "utf8"));
}

function send(res, status, payload) {
  const body = JSON.stringify(payload, null, 2);
  res.writeHead(status, { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) });
  res.end(body);
}

function collectBody(req) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (chunk) => (data += chunk));
    req.on("end", () => resolve(data));
    req.on("error", reject);
  });
}

const startedAt = Date.now();

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  try {
    if (req.method === "GET" && url.pathname === "/health") {
      return send(res, 200, { status: "ok", uptimeMs: Date.now() - startedAt, schedulerRunning: scheduler.isRunning() });
    }

    if (req.method === "POST" && url.pathname === "/invoices/process") {
      const { invoices } = readJson(await collectBody(req));
      return send(res, 200, processInvoices(invoices ?? []));
    }

    if (req.method === "POST" && url.pathname === "/leads/route") {
      const { leads, roster } = readJson(await collectBody(req));
      return send(res, 200, routeLeads(leads ?? [], { roster }));
    }

    if (req.method === "POST" && url.pathname === "/reports/generate") {
      const body = readJson(await collectBody(req));
      const sources = Object.keys(body).length > 0 ? body : sampleSources();
      latestReport = generateReport(sources);
      return send(res, 200, latestReport);
    }

    if (req.method === "GET" && url.pathname === "/reports/latest") {
      if (!latestReport) return send(res, 404, { error: "no report generated yet" });
      return send(res, 200, latestReport);
    }

    return send(res, 404, { error: `no route for ${req.method} ${url.pathname}` });
  } catch (err) {
    return send(res, 400, { error: err.message });
  }
});

const scheduler = createScheduler(async () => {
  latestReport = generateReport(sampleSources());
}, REPORT_SCHEDULE_MS ?? 3600000);

if (REPORT_SCHEDULE_MS) {
  scheduler.start();
}

server.listen(PORT, () => {
  console.log(`biz-automation listening on :${PORT}`);
  if (REPORT_SCHEDULE_MS) {
    console.log(`report scheduler running every ${REPORT_SCHEDULE_MS}ms`);
  }
});

module.exports = { server, scheduler };
