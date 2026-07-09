#!/usr/bin/env node
/**
 * get-analytics-token.cjs — one-time consent for real daily-views in live mode.
 *
 * The daily-views chart reads the YouTube *Analytics* API, which only the
 * channel owner can access (OAuth). Run this once to mint a refresh token, then
 * set it (with the client id/secret) in the server's environment.
 *
 * Prerequisites (Google Cloud Console, same project as your Data API key):
 *   1) Enable "YouTube Analytics API".
 *   2) Credentials -> Create OAuth client ID -> type "Desktop app".
 *   3) Note the client ID + client secret.
 *
 * Run:
 *   YT_OAUTH_CLIENT_ID=xxx YT_OAUTH_CLIENT_SECRET=yyy node get-analytics-token.cjs
 *
 * It prints a URL, you approve access in the browser, and it prints:
 *   export YT_OAUTH_REFRESH_TOKEN="1//0g..."
 * Then start the server with all three YT_OAUTH_* vars set. Node 18+.
 */
const http = require("http");
const crypto = require("crypto");

const CLIENT_ID = process.env.YT_OAUTH_CLIENT_ID || "";
const CLIENT_SECRET = process.env.YT_OAUTH_CLIENT_SECRET || "";
const PORT = Number(process.env.OAUTH_CALLBACK_PORT || 5789);
const REDIRECT = `http://localhost:${PORT}/callback`;
const SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly";
const TOKEN_URL = process.env.YT_OAUTH_TOKEN_URL || "https://oauth2.googleapis.com/token";

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error("Set YT_OAUTH_CLIENT_ID and YT_OAUTH_CLIENT_SECRET (Desktop-app OAuth client).");
  process.exit(1);
}

const state = crypto.randomBytes(8).toString("hex");
const authUrl = "https://accounts.google.com/o/oauth2/v2/auth?" + new URLSearchParams({
  client_id: CLIENT_ID, redirect_uri: REDIRECT, response_type: "code",
  scope: SCOPE, access_type: "offline", prompt: "consent", state,
});

const server = http.createServer(async (req, res) => {
  if (!req.url.startsWith("/callback")) { res.writeHead(404); return res.end(); }
  const u = new URL(req.url, REDIRECT);
  if (u.searchParams.get("state") !== state) { res.writeHead(400); return res.end("state mismatch"); }
  const code = u.searchParams.get("code");
  if (!code) { res.writeHead(400); return res.end("no code (access denied?)"); }
  try {
    const r = await fetch(TOKEN_URL, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        code, client_id: CLIENT_ID, client_secret: CLIENT_SECRET,
        redirect_uri: REDIRECT, grant_type: "authorization_code",
      }),
    });
    const j = await r.json();
    if (!j.refresh_token) {
      res.end("No refresh token returned. Revoke prior access for this app and retry.");
      console.error("Response:", j);
      server.close(); return process.exit(1);
    }
    res.end("Done — refresh token captured. You can close this tab and return to the terminal.");
    console.log("\n✓ Success. Set these in the server environment:\n");
    console.log(`  export YT_OAUTH_CLIENT_ID="${CLIENT_ID}"`);
    console.log(`  export YT_OAUTH_CLIENT_SECRET="${CLIENT_SECRET}"`);
    console.log(`  export YT_OAUTH_REFRESH_TOKEN="${j.refresh_token}"\n`);
    server.close(); process.exit(0);
  } catch (e) {
    res.end("Token exchange failed: " + e.message);
    console.error(e); server.close(); process.exit(1);
  }
});

server.listen(PORT, () => {
  console.log("\n1) Open this URL in your browser and approve access:\n\n" + authUrl + "\n");
  console.log(`2) Waiting for the redirect on ${REDIRECT} …`);
});
