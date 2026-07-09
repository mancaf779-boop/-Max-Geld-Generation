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
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY server.cjs get-analytics-token.cjs ./
COPY --from=build /app/dist ./dist
# drop root
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
  CMD wget -qO- "http://localhost:${PORT:-3000}/api/stats" >/dev/null 2>&1 || exit 1
CMD ["node", "server.cjs"]
