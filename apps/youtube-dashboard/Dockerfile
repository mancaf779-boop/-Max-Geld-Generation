# Maxforge Lab — YouTube dashboard. Multi-stage: build the Vite front-end, then
# serve dist/ + the data/AI APIs from the self-contained Node server.
#
#   docker build -t maxforge-lab .
#   docker run --rm -p 3000:3000 maxforge-lab                 # demo mode
#   docker run --rm -p 3000:3000 --env-file .env maxforge-lab # live data / AI
#   docker run --rm -p 8080:8080 -e PORT=8080 maxforge-lab    # custom port

# ---- build stage: bundle the front-end ----
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- runtime stage: serve app + APIs ----
FROM node:20-alpine AS runtime
ENV NODE_ENV=production
WORKDIR /app
# only production deps (express) are needed to run server.cjs
COPY --chown=node:node package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY --chown=node:node server.cjs get-analytics-token.cjs ./
COPY --chown=node:node --from=build /app/dist ./dist
# drop root
USER node
EXPOSE 3000
# Liveness only: hit the static SPA root, not /api/stats — that route is
# rate-limited and (in live mode) depends on the YouTube API, so a transient
# 429/500 there could wrongly mark the container unhealthy.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
  CMD wget -qO- "http://localhost:${PORT:-3000}/" >/dev/null 2>&1 || exit 1
CMD ["node", "server.cjs"]
