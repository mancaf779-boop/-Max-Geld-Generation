FROM node:22-alpine

WORKDIR /app

# No dependencies to install — the app uses only Node's stdlib — but
# COPY package.json first anyway so `npm ci` stays a no-op cache layer
# if a real dependency is ever added later.
COPY --chown=node:node package.json ./
COPY --chown=node:node src ./src
COPY --chown=node:node data ./data

ENV PORT=8080
EXPOSE 8080

# BIZ_AUTOMATION_API_KEY has no default on purpose — the app refuses to
# start without it (see src/server.js). Set it at deploy time as a secret,
# never bake it into the image.

# The server only reads files at runtime (data/*.json) — never writes —
# so it can safely run as the non-root "node" user the base image ships.
USER node

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD node -e "fetch('http://localhost:'+(process.env.PORT||8080)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["node", "src/server.js"]
