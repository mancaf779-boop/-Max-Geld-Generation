---
name: run-youtube-dashboard
description: Build, run, and screenshot the Maxforge Lab YouTube dashboard — a Vite + React mobile YouTube-analytics dashboard with an optional Node/Express stats backend. Use when asked to run, start, launch, serve, drive, or screenshot the app, or to verify a change renders (dashboard, live data, AI Coach, keywords, optimize, settings screens).
---

# Run the Maxforge Lab YouTube dashboard

Maxforge Lab (this app) is a **Vite + React single-page app** (mobile-shaped dashboard, German UI,
Tailwind + Recharts + lucide-react). It runs headless and is driven with the
pre-installed Playwright Chromium via **`.claude/skills/run-youtube-dashboard/driver.mjs`**,
which loads the app, optionally clicks on-screen labels, screenshots, and reports
console errors.

The dashboard has two data modes:
- **Demo-Daten** — hardcoded sample numbers (no backend). This is the default
  when no data source is reachable.
- **Live-Daten** — fetched from a backend exposing `/api/stats` (channel stats)
  and optionally `/chart.json` (daily views). `backend/mock-server.cjs` serves
  that exact contract for local runs; `backend/youtube-stats.cjs` serves the
  real thing with a YouTube API key.

**All paths below are relative to the app project root (`apps/youtube-dashboard/`).** The driver's
full path from there is `.claude/skills/run-youtube-dashboard/driver.mjs`.

## Prerequisites

- Node 18+ (tested on v22) and npm. No `apt-get` packages needed.
- Playwright Chromium is pre-installed at `/opt/pw-browsers/chromium-*`
  (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`). The driver auto-detects the
  versioned path — do **not** run `playwright install`.

## Setup

```bash
npm install          # installs react, recharts, lucide-react, vite,
                     # playwright-core (driver), express + googleapis (backend)
```

## Run (agent path)

Three steps: start the backend, start the app, drive it. Start both servers in
the background.

```bash
# 1) Backend — mock (no credentials). Serves /api/stats + /chart.json on :3000.
node backend/mock-server.cjs        # run in background

# 2) App — Vite dev server on :5173. Reads VITE_STATS_URL/VITE_CHART_URL from .env
#    and auto-connects to the backend on load.
npm run dev                         # run in background

# 3) Drive it — screenshot the home dashboard (should show "Live-Daten · 42 Videos")
node .claude/skills/run-youtube-dashboard/driver.mjs home.png
```

Verify the servers are up before driving:

```bash
curl -s -o /dev/null -w "vite %{http_code}\n" http://localhost:5173/      # 200
curl -s -o /dev/null -w "mock %{http_code}\n" http://localhost:3000/api/stats  # 200
```

**Driver usage:** `node .claude/skills/run-youtube-dashboard/driver.mjs <out.png> [clickLabel ...]`
Each `clickLabel` is on-screen text on a tab/button; the driver clicks them in
order before screenshotting. Prefix with `css=` to target by CSS selector
instead (for icon-only buttons). Screenshots land wherever you point `<out.png>`.

```bash
node .claude/skills/run-youtube-dashboard/driver.mjs analytik.png "Analytik"   # live stats + channel-views chart + recent videos
node .claude/skills/run-youtube-dashboard/driver.mjs alle.png "Alle"          # all dashboard sections at once
# Settings/Datenquelle: reach it via the gear icon (the "Datenquelle verbinden"
# text link only exists in Demo mode, so target the gear button by CSS):
node .claude/skills/run-youtube-dashboard/driver.mjs settings.png "css=button:has(svg.lucide-settings)"
```

The driver prints `console errors: none` on a clean render. **Read the PNG** —
a blank frame or Demo-Daten badge when you expected Live-Daten is a failure.

### Real YouTube data instead of the mock

Same `/api/stats` contract, so it's a drop-in for the mock backend:

```bash
export YOUTUBE_API_KEY="your_key"   # Google Cloud → enable "YouTube Data API v3" → API key
node backend/youtube-stats.cjs @yourhandle --serve   # serves :3000, no app change needed
```

Daily-views `chart.json` comes from `backend/youtube-analytics.cjs`, which needs
an OAuth consent flow (`client_secret.json`) — see the header comment in that file.

## Run (human path)

`npm run dev`, open `http://localhost:5173/` in a browser, Ctrl-C to stop. With
`backend/mock-server.cjs` also running it shows Live-Daten; otherwise Demo-Daten.
Useless headless — use the agent path above.

## Gotchas

- **Backend scripts are `.cjs`, not `.js`.** `package.json` has
  `"type": "module"` (Vite needs it), which makes Node treat `.js` as ESM and
  the `require(...)`-based backend scripts fail with *"require is not defined in
  ES module scope."* They were renamed to `.cjs` to stay CommonJS.
- **Config persistence needed a `localStorage` fallback.** The app's `store`
  helper originally only used `window.storage`, which exists **only inside the
  Anthropic artifact host** — in a normal browser it's `undefined`, so the
  Datenquelle settings never persisted and the app was stuck in Demo-Daten. A
  `localStorage` fallback was added in `src/VidqApp.jsx`.
- **`.env` is read only at Vite startup.** `VITE_STATS_URL` / `VITE_CHART_URL`
  drive the auto-connect. If you change `.env`, restart `npm run dev`.
- **Backend must be up *before* the app loads** to get Live-Daten. The fetch
  failure is caught and swallowed (falls back to Demo-Daten silently). If you
  start the backend late, click the refresh (↻) icon in the app header, or just
  re-run the driver.
- **The "Datenquelle verbinden" text link is Demo-mode only.** In Live-Daten
  mode the home screen shows the green "Live-Daten" badge in its place, so to
  reach Settings you must click the **gear icon** — target it by CSS:
  `css=button:has(svg.lucide-settings)`. (lucide-react renders icons as
  `svg.lucide-<name>`.)
- **CORS is already handled** — both backends send `Access-Control-Allow-Origin: *`,
  so `:5173 → :3000` works.
- **Chromium path is versioned** (`chromium-1194` today). The driver globs
  `/opt/pw-browsers/chromium-*/chrome-linux/chrome`; don't hardcode the revision.
- **The `/favicon.ico` 404** was silenced by adding an inline SVG icon in
  `index.html`. Chromium's console text for it is a generic
  *"Failed to load resource… 404"* with no URL, so it can't be filtered by name.
- **AI Coach / Schlüsselwörter / Optimieren call `api.anthropic.com` directly**
  from the browser. They need an API key and hit CORS, so they don't function in
  a local run — but their screens render fine. Don't treat their failure as a
  broken build.

## Troubleshooting

- **App shows "Demo-Daten — Datenquelle verbinden" instead of live numbers** →
  backend not reachable. Check `curl http://localhost:3000/api/stats` returns
  JSON with a `channel` object; confirm `.env` points at it; restart `npm run dev`
  if you edited `.env`.
- **`require is not defined in ES module scope`** when starting a backend script
  → you're running a `.js` copy. Use the `.cjs` files in `backend/`.
- **Driver: `Chromium not found under /opt/pw-browsers`** → the pre-installed
  browser is missing/moved; check `ls /opt/pw-browsers` and
  `echo $PLAYWRIGHT_BROWSERS_PATH`.
- **Driver: `click "X" failed`** → the label text isn't on the current screen
  (e.g. clicking "Analytik" but the tab row scrolled). The driver still
  screenshots; open the PNG to see the actual state.
