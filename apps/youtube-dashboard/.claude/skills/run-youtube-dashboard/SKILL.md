---
name: run-youtube-dashboard
description: Build, run, and screenshot the Maxforge Lab YouTube dashboard — a Vite + React mobile YouTube-analytics dashboard served by a self-contained Node server. Use when asked to run, start, launch, serve, drive, or screenshot the app, or to verify a change renders (dashboard, live data, AI Coach, keywords, optimize, settings screens).
---

# Run the Maxforge Lab YouTube dashboard

A **Vite + React single-page app** (mobile-shaped dashboard, German UI, Tailwind
+ Recharts + lucide-react), built to static files and served — together with its
data/AI APIs — by one self-contained Node server (`server.cjs`). It runs headless
and is driven with the pre-installed Playwright Chromium via
**`.claude/skills/run-youtube-dashboard/driver.mjs`**, which loads the app,
optionally clicks on-screen labels, screenshots, and reports console errors.

The dashboard has two data modes:
- **Demo-Daten** — sample numbers served by `server.cjs` when no credentials are
  set. This is the default; `/api/stats` returns `{ demo: true, ... }`.
- **Live-Daten** — real data when the YouTube / Anthropic env vars are set (see
  below). `/api/stats` (channel), `/chart.json` (daily views), `/api/claude`
  (AI proxy) are all served by the same process, same origin.

**All paths below are relative to the app project root (`apps/youtube-dashboard/`).**
The driver's full path from there is `.claude/skills/run-youtube-dashboard/driver.mjs`.

## Prerequisites

- Node 18+ (tested on v22) and npm. No `apt-get` packages needed.
- Playwright Chromium is pre-installed at `/opt/pw-browsers/chromium-*`
  (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`). The driver auto-detects the
  versioned path — do **not** run `playwright install`.

## Setup

```bash
npm install     # react, recharts, lucide-react, vite, express, playwright-core (driver)
```

## Run (agent path)

One server hosts the built app + APIs on `:3000`. Build, launch in the
background, then drive.

```bash
# 1) Build + serve (= vite build && node server.cjs) on :3000
npm run serve                      # run in background
#   (or, if dist is already built: node server.cjs)

# 2) Drive it — screenshot the home dashboard
node .claude/skills/run-youtube-dashboard/driver.mjs home.png
```

Verify the server is up before driving:

```bash
curl -s -o /dev/null -w "app %{http_code}\n" http://localhost:3000/            # 200
curl -s -o /dev/null -w "stats %{http_code}\n" http://localhost:3000/api/stats # 200
```

**Driver usage:** `node .claude/skills/run-youtube-dashboard/driver.mjs <out.png> [clickLabel ...]`
Each `clickLabel` is on-screen text on a tab/button; the driver clicks them in
order before screenshotting. Prefix with `css=` to target by CSS selector
instead (for icon-only buttons). The driver targets `http://localhost:3000/` by
default; override with `URL=…`. Screenshots land wherever you point `<out.png>`.

```bash
node .claude/skills/run-youtube-dashboard/driver.mjs analytik.png "Analytik"  # analytics tiles + channel-views chart
node .claude/skills/run-youtube-dashboard/driver.mjs alle.png "Alle"          # all dashboard sections at once
# Settings/Datenquelle: reach it via the gear icon (target the button by CSS):
node .claude/skills/run-youtube-dashboard/driver.mjs settings.png "css=button:has(svg.lucide-settings)"
```

The driver prints `console errors: none` on a clean render. **Read the PNG** — a
blank frame is a failure to launch.

### Live data (optional)

All same-origin on the one server; set env vars and restart:

```bash
# Channel stats (dashboard flips to Live-Daten):
export YOUTUBE_API_KEY="your_key"   # Google Cloud → "YouTube Data API v3" → API key
export MAXFORGE_CHANNEL="@yourhandle"

# AI screens (AI Coach / Keywords / Optimize) via the server-side proxy:
export ANTHROPIC_API_KEY="sk-ant-..."

# Daily-views chart (Analytik tab) via YouTube Analytics OAuth:
YT_OAUTH_CLIENT_ID=x YT_OAUTH_CLIENT_SECRET=y node get-analytics-token.cjs  # one-time
export YT_OAUTH_CLIENT_ID=x YT_OAUTH_CLIENT_SECRET=y YT_OAUTH_REFRESH_TOKEN=z

npm run serve   # banner shows which of data / chart / AI are LIVE
```

For verification without real credentials, the upstreams are override-able via
`YOUTUBE_BASE_URL`, `YT_OAUTH_TOKEN_URL`, `YT_ANALYTICS_BASE_URL`, and
`ANTHROPIC_BASE_URL` — point them at a local mock returning the same shapes.

## Run (human path)

`npm run serve`, open `http://localhost:3000/`, Ctrl-C to stop. Useless
headless — use the agent path above. For front-end hot reload use `npm run dev`
(Vite on `:5173`, which proxies `/api` and `/chart.json` to a `server.cjs`
running on `:3000`).

## Gotchas

- **One server, same origin.** The built app and all APIs are served by
  `server.cjs` on `:3000` — no separate backend, and no CORS needed by default
  (a blanket `Access-Control-Allow-Origin: *` was intentionally removed; set
  `CORS_ORIGIN` only for a specific cross-origin front-end).
- **`server.cjs` / `get-analytics-token.cjs` are `.cjs`.** `package.json` has
  `"type": "module"` (Vite needs it), which makes Node treat `.js` as ESM; the
  `require(...)`-based server stays `.cjs` to remain CommonJS.
- **Demo vs Live badge.** `/api/stats` demo responses carry `demo: true`; the UI
  keys the "Live-Daten"/"Demo-Daten" badge off that, not just channel presence.
- **Config persistence uses a `localStorage` fallback.** The `store` helper
  prefers the artifact-host `window.storage` but falls back to `localStorage` in
  a normal browser, so the Datenquelle settings persist.
- **Settings via the gear icon.** The "Datenquelle verbinden" text link only
  shows in Demo mode; in Live mode target the gear button by CSS:
  `css=button:has(svg.lucide-settings)` (lucide renders `svg.lucide-<name>`).
- **Chromium path is versioned** (`chromium-1194` today). The driver globs
  `/opt/pw-browsers/chromium-*/chrome-linux/chrome`; don't hardcode the revision.
- **`/favicon.ico`** is an inline SVG in `index.html` (no 404 noise).
- **AI screens need `ANTHROPIC_API_KEY`.** Without it, `/api/claude` returns a
  friendly 503 and those screens show a "disabled" message — their UI still
  renders, so don't treat that as a broken build.

## Troubleshooting

- **App shows "Demo-Daten" when you expected live** → the relevant env vars
  aren't set, or the server was started before they were exported. Check the
  startup banner (`data source` / `daily chart` / `AI features`) and
  `curl http://localhost:3000/api/stats` (live responses have no `demo` flag).
- **`require is not defined in ES module scope`** → you renamed `server.cjs` to
  `.js`; it must stay `.cjs` under `"type": "module"`.
- **`429` from `/api/claude` or `/api/stats`** → the per-IP rate limiter
  (`RATE_LIMIT_PER_MIN`, default 60). Raise it or set `RATE_LIMIT_PER_MIN=0` to
  disable for local testing.
- **Driver: `Chromium not found under /opt/pw-browsers`** → the pre-installed
  browser moved; check `ls /opt/pw-browsers` and `echo $PLAYWRIGHT_BROWSERS_PATH`.
- **Driver: `click "X" failed`** → the label isn't on the current screen. The
  driver still screenshots; open the PNG to see the actual state.
