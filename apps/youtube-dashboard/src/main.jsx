import React from "react";
import ReactDOM from "react-dom/client";
import { SpeedInsights } from "@vercel/speed-insights/react";
import "./index.css";
import MaxforgeLabApp from "./VidqApp.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <MaxforgeLabApp />
    <SpeedInsights />
  </React.StrictMode>
);
