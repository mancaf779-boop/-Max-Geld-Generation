#!/usr/bin/env node
/**
 * Maxforge Lab — standalone server
 *
 * One process serves the built front-end (./dist) AND the data API on a single
 * port, so the dashboard shows live data with no separate backend or CORS setup.
 *
 *   GET  /               -> the Maxforge Lab app (SPA)
 *   GET  /api/stats      -> channel stats  (real YouTube data if configured, else demo)
 *   GET  /chart.json     -> daily views    (demo unless real analytics wired in)
 *
 * Configure with env vars (see .env.example):
 *   PORT              port to listen on           (default 8080)
 *   YOUTUBE_API_KEY   YouTube Data API v3 key     (omit -> demo data)
 *   MAXFORGE_CHANNEL  @handle or UC… channel id   (required when a key is set)
 *
 * Node 18+ (uses global fetch). Run:  npm install && npm start
 */
const path = require("path");
const express = require("express");

const PORT = process.env.PORT || 3000;
const API_KEY = process.env.YOUTUBE_API_KEY || "";
const CHANNEL = process.env.MAXFORGE_CHANNEL || "";
const LIVE = Boolean(API_KEY && CHANNEL);
const BASE = process.env.YOUTUBE_BASE_URL || "https://www.googleapis.com/youtube/v3";

// ---------- YouTube Analytics (daily views for the live chart, OAuth) ----------
// The public Data API has no per-day views; the Analytics API does but needs
// OAuth (only the channel owner can read it). Configure a refresh token once
// with:  node get-analytics-token.cjs  (see README). No extra npm deps — the
// token exchange and report call are plain fetch.
const YT_CLIENT_ID = process.env.YT_OAUTH_CLIENT_ID || "";
const YT_CLIENT_SECRET = process.env.YT_OAUTH_CLIENT_SECRET || "";
const YT_REFRESH_TOKEN = process.env.YT_OAUTH_REFRESH_TOKEN || "";
const YT_TOKEN_URL = process.env.YT_OAUTH_TOKEN_URL || "https://oauth2.googleapis.com/token";
const YT_ANALYTICS_URL = process.env.YT_ANALYTICS_BASE_URL || "https://youtubeanalytics.googleapis.com/v2/reports";
const ANALYTICS_ENABLED = Boolean(YT_CLIENT_ID && YT_CLIENT_SECRET && YT_REFRESH_TOKEN);

// ---------- Anthropic (AI Coach / Keywords / Optimize) ----------
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY || "";
const ANTHROPIC_URL = process.env.ANTHROPIC_BASE_URL || "https://api.anthropic.com/v1/messages";
const ANTHROPIC_MODEL = process.env.ANTHROPIC_MODEL || "claude-opus-4-8";
const AI_ENABLED = Boolean(ANTHROPIC_API_KEY);

// ---------- real YouTube Data API ----------
async function api(pathname, params) {
  const url = new URL(BASE + pathname);
  url.searchParams.set("key", API_KEY);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  const res = await fetch(url);
  const json = await res.json();
  if (!res.ok) throw new Error(`YouTube API ${res.status}: ${json?.error?.message || res.statusText}`);
  return json;
}

async function resolveChannel(input) {
  const clean = input.trim();
  const params = { part: "snippet,statistics,contentDetails" };
  if (clean.startsWith("UC") && clean.length === 24) params.id = clean;
  else params.forHandle = clean.startsWith("@") ? clean : "@" + clean;
  const data = await api("/channels", params);
  if (!data.items || !data.items.length) throw new Error(`Kein Kanal gefunden für "${input}".`);
  return data.items[0];
}

async function recentVideos(uploadsPlaylistId, n = 10) {
  const pl = await api("/playlistItems", {
    part: "contentDetails", playlistId: uploadsPlaylistId, maxResults: String(Math.min(n, 50)),
  });
  const ids = (pl.items || []).map((i) => i.contentDetails.videoId).filter(Boolean);
  if (!ids.length) return [];
  const vids = await api("/videos", { part: "snippet,statistics", id: ids.join(",") });
  return (vids.items || []).map((v) => ({
    id: v.id,
    title: v.snippet.title,
    publishedAt: v.snippet.publishedAt,
    views: Number(v.statistics?.viewCount || 0),
    likes: Number(v.statistics?.likeCount || 0),
    comments: Number(v.statistics?.commentCount || 0),
    url: `https://youtube.com/watch?v=${v.id}`,
  }));
}

async function liveStats() {
  const ch = await resolveChannel(CHANNEL);
  const s = ch.statistics;
  return {
    fetchedAt: new Date().toISOString(),
    channel: {
      id: ch.id,
      title: ch.snippet.title,
      handle: ch.snippet.customUrl || null,
      thumbnail: ch.snippet.thumbnails?.default?.url || null,
      subscribers: Number(s.subscriberCount || 0),
      subscribersHidden: s.hiddenSubscriberCount === true,
      views: Number(s.viewCount || 0),
      videoCount: Number(s.videoCount || 0),
    },
    recentVideos: await recentVideos(ch.contentDetails.relatedPlaylists.uploads, 10),
  };
}

// ---------- demo data (same contract) ----------
const DEMO_TITLES = [
  "Ich habe YouTube 30 Tage mit KI automatisiert",
  "Diese 3 Tools verändern deinen Kanal 2026",
  "So findest du virale Themen (Schritt für Schritt)",
  "Mein Setup für tägliche Uploads",
  "Warum 99% aller Kanäle scheitern",
];
function demoStats() {
  const base = Date.now();
  return {
    fetchedAt: new Date().toISOString(),
    channel: {
      id: "UC_demo", title: "Maxforge Lab Demo", handle: "@maxforgelab", thumbnail: null,
      subscribers: 1284, subscribersHidden: false, views: 96540, videoCount: 42,
    },
    recentVideos: DEMO_TITLES.map((title, i) => ({
      id: "demo" + i, title, publishedAt: new Date(base - i * 3456e5).toISOString(),
      views: Math.round(2000 + Math.random() * 18000), likes: Math.round(80 + Math.random() * 1200),
      comments: Math.round(5 + Math.random() * 300), url: "#",
    })),
  };
}
function demoChart() {
  const out = [], today = new Date();
  for (let i = 27; i >= 0; i--) {
    const d = new Date(today); d.setDate(today.getDate() - i);
    out.push({ d: i === 27 || i === 0 ? `${d.getMonth() + 1}/${d.getDate()}` : "",
      v: Math.round(1500 + Math.random() * 4500 + (27 - i) * 120) });
  }
  return out;
}

// ---------- real daily views via the YouTube Analytics API ----------
let accessToken = null, accessExp = 0, refreshPromise = null;
async function getAccessToken() {
  if (accessToken && Date.now() < accessExp - 60_000) return accessToken;
  if (refreshPromise) return refreshPromise; // coalesce concurrent refreshes
  refreshPromise = (async () => {
    try {
      const r = await fetch(YT_TOKEN_URL, {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          client_id: YT_CLIENT_ID, client_secret: YT_CLIENT_SECRET,
          refresh_token: YT_REFRESH_TOKEN, grant_type: "refresh_token",
        }),
      });
      const j = await r.json();
      if (!r.ok || !j.access_token) throw new Error(`OAuth token: ${j.error_description || j.error || r.status}`);
      accessToken = j.access_token;
      accessExp = Date.now() + (Number(j.expires_in) || 3600) * 1000;
      return accessToken;
    } finally {
      refreshPromise = null;
    }
  })();
  return refreshPromise;
}

const isoDate = (d) => d.toISOString().slice(0, 10);
async function dailyViews(days = 28) {
  const end = new Date(), start = new Date();
  start.setDate(end.getDate() - (days - 1));
  const token = await getAccessToken();
  const url = new URL(YT_ANALYTICS_URL);
  url.searchParams.set("ids", "channel==MINE");
  url.searchParams.set("startDate", isoDate(start));
  url.searchParams.set("endDate", isoDate(end));
  url.searchParams.set("metrics", "views");
  url.searchParams.set("dimensions", "day");
  url.searchParams.set("sort", "day");
  const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  const j = await r.json();
  if (!r.ok) throw new Error(`Analytics API ${r.status}: ${j?.error?.message || r.statusText}`);
  const points = (j.rows || []).map((row) => {
    if (!row || !row[0]) return null;
    const parts = String(row[0]).split("-");
    if (parts.length < 3) return null;
    const [, m, d] = parts;
    return { d: `${Number(m)}/${Number(d)}`, v: Number(row[1] || 0) };
  }).filter(Boolean);
  // label only first + last (matches the dashboard's chart style)
  return points.map((p, i) => ({ ...p, d: i === 0 || i === points.length - 1 ? p.d : "" }));
}

// ---------- server ----------
const app = express();
app.use((req, res, next) => { res.set("Access-Control-Allow-Origin", "*"); next(); });
app.use(express.json({ limit: "1mb" }));

// AI proxy: the browser posts {model, max_tokens, system, messages} here; the
// server adds the API key + version headers and forwards to Anthropic. Keeps the
// key server-side and avoids the browser-CORS block on api.anthropic.com.
app.post("/api/claude", async (req, res) => {
  if (!AI_ENABLED) {
    return res.status(503).json({
      error: { message: "AI features disabled — set ANTHROPIC_API_KEY on the server to enable." },
    });
  }
  try {
    const b = req.body || {};
    const payload = {
      // Model is server-controlled (ANTHROPIC_MODEL, default claude-opus-4-8);
      // the client's model field is intentionally ignored so the deployment,
      // not the browser, decides model/cost.
      model: ANTHROPIC_MODEL,
      max_tokens: Math.min(Math.max(Number(b.max_tokens) || 1024, 1), 4096),
      messages: Array.isArray(b.messages) ? b.messages : [],
    };
    if (b.system) payload.system = b.system;
    const r = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify(payload),
    });
    const data = await r.json();
    res.status(r.status).json(data);
  } catch (e) {
    res.status(502).json({ error: { message: e.message } });
  }
});

let cache = null, cacheTime = 0;
app.get("/api/stats", async (req, res) => {
  try {
    if (!LIVE) return res.json(demoStats());
    if (!cache || Date.now() - cacheTime > 60_000) {
      try {
        cache = await liveStats(); cacheTime = Date.now();
      } catch (e) {
        if (!cache) throw e; // no cache to fall back on
        console.error("stats refresh failed, serving stale cache:", e.message);
      }
    }
    res.json(cache);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Daily views: real (YouTube Analytics, OAuth) when configured; else demo
// points in demo mode, or an empty array in live mode (the app hides the chart
// rather than show fake numbers next to real stats).
let chartCache = null, chartCacheTime = 0;
app.get("/chart.json", async (req, res) => {
  if (!ANALYTICS_ENABLED) return res.json(LIVE ? [] : demoChart());
  try {
    if (!chartCache || Date.now() - chartCacheTime > 600_000) { // 10 min cache
      try {
        chartCache = await dailyViews(28); chartCacheTime = Date.now();
      } catch (e) {
        if (!chartCache) throw e; // no cache to fall back on
        console.error("chart refresh failed, serving stale cache:", e.message);
      }
    }
    res.json(chartCache);
  } catch (e) {
    console.error("chart.json:", e.message);
    res.json([]); // don't break the dashboard — just hide the chart
  }
});

app.use(express.static(path.join(__dirname, "dist")));
// SPA fallback: non-API routes return index.html. But a path with a file
// extension is a missing static asset — 404 it instead of returning HTML, so
// the browser doesn't choke on "<" while parsing a would-be .js/.css.
app.get(/^(?!\/api\/|\/chart\.json).*/, (req, res) => {
  if (path.extname(req.path)) return res.status(404).end();
  res.sendFile(path.join(__dirname, "dist", "index.html"));
});

app.listen(PORT, () => {
  console.log(`\n  Maxforge Lab  →  http://localhost:${PORT}`);
  console.log(`  data source   →  ${LIVE ? `LIVE (YouTube: ${CHANNEL})` : "DEMO (set YOUTUBE_API_KEY + MAXFORGE_CHANNEL for live)"}`);
  console.log(`  daily chart   →  ${ANALYTICS_ENABLED ? "LIVE (YouTube Analytics OAuth)" : (LIVE ? "hidden (run get-analytics-token.cjs for real daily views)" : "DEMO")}`);
  console.log(`  AI features   →  ${AI_ENABLED ? `ON (model: ${ANTHROPIC_MODEL})` : "OFF (set ANTHROPIC_API_KEY to enable AI Coach / Keywords / Optimize)"}\n`);
});
