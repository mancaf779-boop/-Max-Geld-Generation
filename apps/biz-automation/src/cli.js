#!/usr/bin/env node
const fs = require("node:fs");
const path = require("node:path");

const { generateReport } = require("./lib/reports");
const { createScheduler } = require("./lib/scheduler");

const DATA_DIR = path.join(__dirname, "..", "data");
const OUT_DIR = path.join(__dirname, "..", "reports");

function sampleSources() {
  return JSON.parse(fs.readFileSync(path.join(DATA_DIR, "sample-sources.json"), "utf8"));
}

function writeReport(report) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const file = path.join(OUT_DIR, `report-${report.generatedAt.replace(/[:.]/g, "-")}.md`);
  fs.writeFileSync(file, report.markdown);
  return file;
}

function runOnce() {
  const report = generateReport(sampleSources());
  const file = writeReport(report);
  console.log(report.markdown);
  console.log(`\nWritten to ${file}`);
}

function runSchedule(intervalMs) {
  console.log(`Scheduling report generation every ${intervalMs}ms. Ctrl-C to stop.`);
  const scheduler = createScheduler((n) => {
    const report = generateReport(sampleSources());
    const file = writeReport(report);
    console.log(`[run ${n}] wrote ${file}`);
  }, intervalMs);
  scheduler.start();
}

function main(argv) {
  const [command, ...rest] = argv;
  if (command !== "report") {
    console.error("usage: cli.js report [--once | --schedule <ms>]");
    process.exit(1);
  }
  const scheduleIdx = rest.indexOf("--schedule");
  if (scheduleIdx !== -1) {
    const ms = Number(rest[scheduleIdx + 1]);
    if (!ms || ms <= 0) {
      console.error("--schedule requires a positive millisecond value");
      process.exit(1);
    }
    runSchedule(ms);
    return;
  }
  runOnce();
}

main(process.argv.slice(2));
