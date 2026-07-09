import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies the backend routes to the standalone server on :3000, so
// `npm run dev` (hot reload) shows real backend data/AI just like the built app.
// Run `node server.cjs` (or `npm start`) in another terminal for live routes;
// without it, these proxy targets are simply unreachable and the app shows demo
// data. Override the target with VITE_BACKEND (e.g. VITE_BACKEND=http://host:3000).
const backend = process.env.VITE_BACKEND || "http://localhost:3000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": { target: backend, changeOrigin: true },
      "/chart.json": { target: backend, changeOrigin: true },
    },
  },
});
