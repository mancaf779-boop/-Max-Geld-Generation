#!/usr/bin/env node
/**
 * driver.mjs — drive the running Maxforge Lab dashboard headlessly and screenshot it.
 *
 * The app is a Vite + React SPA (mobile-shaped dashboard). This driver loads
 * it in the pre-installed Playwright Chromium, optionally clicks a sequence of
 * on-screen labels (tabs / buttons), takes a full-page screenshot, and prints
 * any console/page errors so a failed render is visible without eyeballing.
 *
 * Usage (from the apps/youtube-dashboard/ dir, with the dev server already running):
 *   node .claude/skills/run-youtube-dashboard/driver.mjs <out.png> [clickLabel ...]
 *
 * A click arg is on-screen text by default; prefix with `css=` to target by
 * CSS selector instead (needed for icon-only buttons, e.g. the settings gear).
 *
 * Examples:
 *   node .claude/skills/run-youtube-dashboard/driver.mjs home.png
 *   node .claude/skills/run-youtube-dashboard/driver.mjs analytik.png "Analytik"
 *   node .claude/skills/run-youtube-dashboard/driver.mjs settings.png "css=button:has(svg.lucide-settings)"
 *
 * Env:
 *   URL  — app URL (default http://localhost:5173/)
 */
import { chromium } from "playwright-core";
import { existsSync, readdirSync } from "node:fs";

// Pre-installed Playwright Chromium; the versioned dir (chromium-<rev>) varies,
// so resolve it instead of hardcoding.
function findChrome() {
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH || "/opt/pw-browsers";
  const dir = readdirSync(root).find((n) => /^chromium-\d+$/.test(n));
  const p = dir && `${root}/${dir}/chrome-linux/chrome`;
  if (!p || !existsSync(p)) throw new Error(`Chromium not found under ${root}`);
  return p;
}

const URL = process.env.URL || "http://localhost:5173/";
const OUT = process.argv[2] || "shot.png";
const clicks = process.argv.slice(3);

const browser = await chromium.launch({
  executablePath: findChrome(),
  args: ["--no-sandbox"],
});
const page = await browser.newPage({
  viewport: { width: 430, height: 900 }, // app is capped at max-w-[430px]
  deviceScaleFactor: 2,
});

const errors = [];
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
page.on("pageerror", (e) => errors.push("PAGEERROR: " + e.message));

await page.goto(URL, { waitUntil: "networkidle" });
await page.waitForTimeout(800); // let live-data fetch + chart animation settle

for (const label of clicks) {
  try {
    const target = label.startsWith("css=")
      ? page.locator(label.slice(4))
      : page.getByText(label, { exact: false });
    await target.first().click({ timeout: 5000 });
    await page.waitForTimeout(700);
  } catch (e) {
    console.log(`click "${label}" failed: ${e.message.split("\n")[0]}`);
  }
}

await page.screenshot({ path: OUT, fullPage: true });
console.log("saved " + OUT);
// Favicon 404 is expected and harmless; anything else is a real problem.
const real = errors.filter((e) => !/favicon/i.test(e));
console.log("console errors: " + (real.length ? "\n  " + real.join("\n  ") : "none"));
await browser.close();
