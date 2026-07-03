# Deploying biz-automation

biz-automation is a single Docker container (`Dockerfile` in this
directory) — no database, no external services. It refuses to start
without `BIZ_AUTOMATION_API_KEY` set (see `src/server.js`), so every
option below sets that as a **secret**, never a committed value.

> **Note on verification:** the Dockerfile itself wasn't build-tested in
> the environment that authored it — outbound access to Docker Hub is
> blocked there by network policy, so `docker build` couldn't run. It
> follows the standard `node:22-alpine` + stdlib-only pattern (no native
> deps, no build step), so it should build cleanly, but run the first
> build yourself and sanity-check `curl <url>/health` before relying on
> it. If something doesn't build, tell me the error and I'll fix the
> Dockerfile directly.

This repo is a monorepo — biz-automation lives at `apps/biz-automation/`,
not the repo root. Each platform below needs to be told that.

## Railway

```bash
npm install -g @railway/cli
railway login
cd apps/biz-automation
railway init                          # creates/links a Railway project
railway up                            # builds from the Dockerfile here, deploys
railway variables --set "BIZ_AUTOMATION_API_KEY=$(openssl rand -hex 32)"
railway variables --set "REPORT_SCHEDULE_MS=3600000"   # optional
railway domain                        # prints the public URL to use as BIZ_AUTOMATION_BASE_URL
```

`railway.json` in this directory already sets the Dockerfile builder and
`/health` as the healthcheck path.

## Render

1. Push this repo to GitHub (already done if you're reading this from
   the repo).
2. In the Render dashboard: **New → Blueprint**, point it at this repo.
   Render reads `apps/biz-automation/render.yaml` automatically because
   of its `rootDir: apps/biz-automation`.
3. Render will create the service and ask you to fill in the one
   `sync: false` env var — set `BIZ_AUTOMATION_API_KEY` there (Render's
   dashboard, not the yaml file).
4. Render assigns the public URL — that's your `BIZ_AUTOMATION_BASE_URL`.

Or via the CLI:

```bash
render blueprint launch   # from the repo root, picks up render.yaml
```

## Fly.io

```bash
curl -L https://fly.io/install.sh | sh
fly auth login
cd apps/biz-automation
fly launch --no-deploy --copy-config   # uses fly.toml already in this dir; pick a unique app name if "biz-automation" is taken
fly secrets set BIZ_AUTOMATION_API_KEY=$(openssl rand -hex 32)
fly deploy
fly status   # prints the public URL — that's your BIZ_AUTOMATION_BASE_URL
```

## Your own VPS / server (Docker Compose)

```bash
# on the server, with Docker + Docker Compose installed:
git clone <this-repo-url>
cd <repo>/apps/biz-automation
cp .env.example .env
# edit .env: set BIZ_AUTOMATION_API_KEY=$(openssl rand -hex 32)
docker compose up -d --build
curl http://localhost:8080/health
```

Put this behind whatever reverse proxy/TLS termination you already run
(Caddy, nginx, Traefik) to get an `https://` URL — the container itself
only speaks plain HTTP on `PORT` (default 8080).

## After deploying, anywhere

Whatever URL you get back is `{{BIZ_AUTOMATION_BASE_URL}}` in the three
n8n prompts under `../n8n/`. The key you set above is
`{{BIZ_AUTOMATION_API_KEY}}` — store it as an n8n credential, sent as the
`X-API-Key` header on every HTTP Request node.

```bash
curl https://<your-url>/health   # no key needed
curl -X POST https://<your-url>/invoices/process \
  -H "X-API-Key: <your key>" -H 'Content-Type: application/json' \
  -d @data/sample-invoices.json
```
