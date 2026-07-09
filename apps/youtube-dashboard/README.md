# Maxforge Lab — YouTube Dashboard

A mobile **YouTube growth dashboard**: channel stats, trend keywords, an AI
coach, and a video optimizer (German UI). A **Vite + React** front-end built to
static files and served — together with its data/AI APIs — by one self-contained
Node server. No separate backend, no CORS setup.

## Requirements

- **Node.js 18+** (the server uses the built-in `fetch`)

## Quick start

```bash
npm install
npm run serve      # = vite build && node server.cjs  →  http://localhost:3000
```

Or run the steps separately:

```bash
npm run build      # bundle the app into dist/
npm start          # serve dist/ + the APIs on port 3000
```

For front-end development with hot reload use `npm run dev` (Vite on `:5173`);
it proxies data from a running `npm start` server or falls back to demo data.

Out of the box the dashboard runs in **demo mode** with sample numbers. Set the
env vars below to switch on live data and the AI screens.

## Live YouTube data

```bash
export YOUTUBE_API_KEY="your_api_key"    # console.cloud.google.com → "YouTube Data API v3" → API key
export MAXFORGE_CHANNEL="@yourhandle"    # your @handle or a UC… channel id
npm run serve
```

The dashboard flips to **Live-Daten** and shows real subscribers, views, video
count, average views/video, and latest uploads.

### Daily-views chart (live mode)

The per-day trend in the **Analytik** tab reads the YouTube **Analytics** API
(OAuth, owner-only). Get a refresh token once, then set three env vars:

```bash
# Cloud Console: enable "YouTube Analytics API", create an OAuth client ID → "Desktop app".
YT_OAUTH_CLIENT_ID=xxx YT_OAUTH_CLIENT_SECRET=yyy node get-analytics-token.cjs
#   → approve in the browser → prints the three exports below
export YT_OAUTH_CLIENT_ID="xxx" YT_OAUTH_CLIENT_SECRET="yyy" YT_OAUTH_REFRESH_TOKEN="1//0g..."
npm run serve   # banner: "daily chart → LIVE (YouTube Analytics OAuth)"
```

Without these, the chart is hidden in live mode (demo mode still shows a sample
trend). No extra npm packages — the OAuth exchange and report call are plain `fetch`.

## AI features (AI Coach, Schlüsselwörter, Optimieren)

These screens call Claude through the built-in `POST /api/claude` proxy, so the
API key stays server-side (never shipped to the browser, no CORS).

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # console.anthropic.com → API keys
npm run serve
```

Without the key the AI screens show a friendly "disabled" message and the rest
of the app works normally.

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `PORT` | `3000` | Port the server listens on |
| `YOUTUBE_API_KEY` | — | YouTube Data API v3 key. Omit for demo mode. |
| `MAXFORGE_CHANNEL` | — | `@handle` or `UC…` id. Required when a key is set. |
| `ANTHROPIC_API_KEY` | — | Enables the AI screens. Omit to disable them. |
| `ANTHROPIC_MODEL` | `claude-opus-4-8` | Model used for AI calls. |
| `ANTHROPIC_BASE_URL` | `…/v1/messages` | Anthropic endpoint override (gateway/proxy). |
| `YT_OAUTH_CLIENT_ID` / `_SECRET` / `_REFRESH_TOKEN` | — | Enable the live daily-views chart (YouTube Analytics OAuth). |
| `YOUTUBE_BASE_URL`, `YT_OAUTH_TOKEN_URL`, `YT_ANALYTICS_BASE_URL` | Google endpoints | Upstream overrides (proxy/testing). |

## API (served on the same origin)

| Route | Returns |
|---|---|
| `GET /api/stats` | `{ channel: {subscribers, views, videoCount, …}, recentVideos: […] }` |
| `GET /chart.json` | `[{ d: "M/D", v: number }, …]` — real daily views (Analytics OAuth) or demo |
| `POST /api/claude` | Proxies `{model, max_tokens, system, messages}` to Anthropic with the server key |
| `GET /*` | the app (SPA) |

## Layout

```
apps/youtube-dashboard/
  src/                      # React source (main.jsx, VidqApp.jsx, index.css)
  index.html               # Vite entry (Maxforge Lab title + favicon)
  vite.config.js           # + tailwind.config.js, postcss.config.js
  .env.production          # build-time API paths (relative, same-origin)
  server.cjs               # static host + stats / chart / AI proxy
  get-analytics-token.cjs  # one-time OAuth helper for the daily-views chart
  .claude/skills/run-youtube-dashboard/   # skill to launch + screenshot the app
```

## Running / screenshotting for verification

A `run-youtube-dashboard` skill under `.claude/skills/` drives the app in
headless Chromium (Playwright) and screenshots any screen — handy for verifying
a change renders. See its `SKILL.md`.
