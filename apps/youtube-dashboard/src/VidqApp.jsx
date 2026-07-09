import React, { useState, useEffect, useRef } from "react";
import {
  Menu, ChevronDown, ChevronUp, MoreVertical, Home, Search, Youtube,
  Signal, BatteryCharging, Moon, BellOff, Clapperboard, SquarePen,
  ListFilter, Rocket, Sparkles, X, Send, ArrowLeft, Loader2, TrendingUp,
  Copy, Check, RefreshCw, Settings, Video, Wifi, WifiOff,
} from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, ResponsiveContainer,
} from "recharts";

const C = {
  bg: "#08080C", card: "#141419", cardAlt: "#1B1B22", blue: "#2B6BF7",
  green: "#3FD77F", text: "#FFFFFF", sub: "#8B8B94", faint: "#3A3A42",
};

const MODEL = "claude-sonnet-4-6";

const chartData = [
  { d: "6/5", v: 22 }, { d: "", v: 18 }, { d: "", v: 20 }, { d: "", v: 24 },
  { d: "", v: 21 }, { d: "", v: 26 }, { d: "", v: 45 }, { d: "", v: 33 },
  { d: "", v: 40 }, { d: "", v: 28 }, { d: "", v: 24 }, { d: "", v: 55 },
  { d: "", v: 30 }, { d: "", v: 26 }, { d: "", v: 24 }, { d: "", v: 27 },
  { d: "", v: 25 }, { d: "", v: 30 }, { d: "", v: 28 }, { d: "", v: 26 },
  { d: "", v: 34 }, { d: "", v: 58 }, { d: "", v: 40 }, { d: "", v: 30 },
  { d: "", v: 36 }, { d: "", v: 52 }, { d: "", v: 66 }, { d: "7/2", v: 100 },
];

const TABS = ["Alle", "Optimierung", "Forschung", "Analytik"];

// ---------- Anthropic API helper ----------
// Calls the app's own backend proxy (same origin) instead of api.anthropic.com
// directly — the server injects the API key, so it never ships to the browser
// and there is no CORS problem. Override the endpoint with VITE_CLAUDE_URL.
const CLAUDE_URL = (import.meta.env?.VITE_CLAUDE_URL || "/api/claude").trim();
async function callClaude(messages, system, maxTokens = 1000) {
  const res = await fetch(CLAUDE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: maxTokens,
      system,
      messages,
    }),
  });
  const data = await res.json();
  if (data.error) throw new Error(data.error.message || data.error);
  return (data.content || [])
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("\n")
    .trim();
}

// ---------- Persistent storage helper ----------
// Prefers the artifact-host window.storage bridge, falls back to
// localStorage in a normal browser so config survives reloads.
const store = {
  async get(key) {
    try {
      if (typeof window !== "undefined" && window.storage) {
        const r = await window.storage.get(key);
        return r ? JSON.parse(r.value) : null;
      }
      if (typeof localStorage !== "undefined") {
        const r = localStorage.getItem(key);
        return r ? JSON.parse(r) : null;
      }
    } catch (e) {}
    return null;
  },
  async set(key, value) {
    try {
      if (typeof window !== "undefined" && window.storage) {
        await window.storage.set(key, JSON.stringify(value));
      } else if (typeof localStorage !== "undefined") {
        localStorage.setItem(key, JSON.stringify(value));
      }
    } catch (e) {}
  },
};

// Default data source from build-time env (Vite). Lets the app auto-connect
// to a running youtube-stats.js --serve backend without touching Settings.
const ENV_CONFIG = {
  statsUrl: (import.meta.env?.VITE_STATS_URL || "").trim(),
  chartUrl: (import.meta.env?.VITE_CHART_URL || "").trim(),
};

// Robustly parse JSON from an LLM reply that may wrap it in ```json fences or
// surrounding prose. Falls back to extracting the first balanced [...] / {...}.
function parseLooseJSON(raw) {
  let s = String(raw ?? "").trim();
  if (!s) throw new Error("leere Antwort");
  s = s.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "").trim();
  try { return JSON.parse(s); } catch (e) {}
  const start = s.search(/[[{]/);
  const close = s[start] === "[" ? "]" : "}";
  const end = s.lastIndexOf(close);
  if (start !== -1 && end > start) return JSON.parse(s.slice(start, end + 1));
  throw new Error("keine gültige JSON-Antwort");
}

function scoreColor(s) {
  if (s >= 55) return C.green;
  if (s >= 35) return "#E8B23A";
  return "#E2554A";
}

// Kompakte Zahl: 1234 -> "1,2k", 2.1M -> "2,1M"
function compact(n) {
  if (n >= 1e6) return (n / 1e6).toFixed(n >= 1e7 ? 0 : 1).replace(".", ",") + "M";
  if (n >= 1e3) return (n / 1e3).toFixed(n >= 1e4 ? 0 : 1).replace(".", ",") + "k";
  return String(n);
}

// Meilenstein-Bereich für den Fortschrittsbalken (0->0..1, 6->5..10, ...)
function bracket(n) {
  const M = [0, 1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000,
    25000, 50000, 100000, 250000, 500000, 1000000, 5000000, 10000000];
  let min = 0, max = 1;
  for (let i = 0; i < M.length; i++) {
    if (M[i] <= n) min = M[i];
    if (M[i] > n) { max = M[i]; break; }
  }
  if (n >= M[M.length - 1]) { min = M[M.length - 1]; max = min * 2; }
  return { min, max };
}

// ================= Drawer =================
function Drawer({ open, onClose, go, conversations, openConv }) {
  const [toolsOpen, setToolsOpen] = useState(true);
  const items = [
    { icon: Home, label: "Startseite", to: "home", active: true },
    { icon: Clapperboard, label: "Optimieren", to: "optimize" },
    { icon: SquarePen, label: "Neuer Chat", to: "newchat" },
    { icon: ListFilter, label: "Schlüsselwörter", to: "keywords" },
  ];
  return (
    <>
      <div onClick={onClose} className="fixed inset-0 z-40 transition-opacity duration-300"
        style={{ background: "rgba(0,0,0,0.55)", opacity: open ? 1 : 0, pointerEvents: open ? "auto" : "none" }} />
      <div className="fixed top-0 left-0 z-50 h-full flex flex-col transition-transform duration-300"
        style={{ width: "84%", maxWidth: 360, background: "#0C0C12",
          transform: open ? "translateX(0)" : "translateX(-100%)", boxShadow: "8px 0 40px rgba(0,0,0,0.5)" }}>
        <div className="flex justify-end px-4 pt-4">
          <button onClick={onClose} className="p-2" style={{ color: C.sub }}><X size={22} /></button>
        </div>
        <div className="px-3 mt-2 flex flex-col gap-1">
          {items.map((it) => {
            const Icon = it.icon;
            return (
              <button key={it.label} onClick={() => { go(it.to); onClose(); }}
                className="flex items-center gap-4 px-4 py-3.5 rounded-2xl text-left"
                style={{ background: it.active ? "#1E1E27" : "transparent" }}>
                <Icon size={24} /><span className="text-[19px] font-medium">{it.label}</span>
              </button>
            );
          })}
          <button onClick={() => { go("upgrade"); onClose(); }}
            className="flex items-center gap-4 px-4 py-3.5 rounded-2xl text-left">
            <Rocket size={24} style={{ color: C.blue }} />
            <span className="text-[19px] font-medium" style={{ color: C.blue }}>Upgrade</span>
          </button>
        </div>

        <button onClick={() => setToolsOpen((v) => !v)}
          className="flex items-center gap-2 px-7 py-4 mt-2" style={{ color: C.sub }}>
          <span className="text-[17px]">Weitere Tools</span>
          {toolsOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>

        {toolsOpen && (
          <div className="px-7 flex-1 overflow-y-auto no-scrollbar">
            <div className="text-[17px] mb-4" style={{ color: C.sub }}>Verlauf</div>
            {conversations.length === 0 ? (
              <div className="text-center px-2 mt-8">
                <div className="text-[20px] font-bold mb-2">Noch keine Gespräche</div>
                <div className="text-[15px] leading-relaxed" style={{ color: C.sub }}>
                  Beginnen Sie mit AI Coach zu chatten, um Ihren Verlauf hier anzuzeigen
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-1">
                {conversations.map((c) => (
                  <button key={c.id} onClick={() => { openConv(c.id); onClose(); }}
                    className="text-left px-3 py-2.5 rounded-xl truncate text-[15px]"
                    style={{ color: C.text, background: "transparent" }}>
                    {c.title}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="mt-auto px-5 py-5 flex items-center gap-3 border-t" style={{ borderColor: C.faint }}>
          <div className="w-11 h-11 rounded-full bg-gradient-to-br from-stone-500 to-stone-700 shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="text-[16px] font-medium truncate">mancaf779@gmail.com</div>
            <div className="text-[14px]" style={{ color: C.sub }}>Free</div>
          </div>
          <button onClick={() => { go("upgrade"); onClose(); }}
            className="w-11 h-11 rounded-full flex items-center justify-center shrink-0"
            style={{ background: "#12213F", border: `1.5px solid ${C.blue}` }}>
            <Sparkles size={20} style={{ color: C.blue }} />
          </button>
        </div>
      </div>
    </>
  );
}

// ================= Reusable header =================
function ScreenHeader({ title, onBack, right }) {
  return (
    <div className="flex items-center px-4 py-3 gap-3 shrink-0">
      <button onClick={onBack} className="w-11 h-11 rounded-full flex items-center justify-center"
        style={{ background: C.card }}><ArrowLeft size={22} /></button>
      <span className="flex-1 text-[20px] font-bold truncate">{title}</span>
      {right}
    </div>
  );
}

// ================= AI Coach =================
function CoachScreen({ onBack, conv, onUpdate }) {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);
  const msgs = conv?.messages || [];

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [msgs, busy]);

  const suggestions = [
    "Wie finde ich ein virales Video-Thema?",
    "Verbessere meinen Titel für mehr Klicks",
    "Wie oft sollte ich hochladen?",
  ];

  async function send(text) {
    const content = (text ?? input).trim();
    if (!content || busy) return;
    setInput("");
    const nextMsgs = [...msgs, { role: "user", content }];
    onUpdate({ ...conv, messages: nextMsgs, title: conv.title === "Neuer Chat" ? content.slice(0, 40) : conv.title });
    setBusy(true);
    try {
      const reply = await callClaude(
        nextMsgs.map((m) => ({ role: m.role, content: m.content })),
        "Du bist der AI Coach von Maxforge Lab – ein erfahrener Experte für YouTube-Wachstum, SEO, Titel, Thumbnails, Content-Strategie und den Aufbau von Kanälen im deutschsprachigen Raum. Antworte immer auf Deutsch, konkret, umsetzbar und motivierend. Halte dich kurz und nutze bei Bedarf Aufzählungen."
      );
      onUpdate({ ...conv, messages: [...nextMsgs, { role: "assistant", content: reply || "Entschuldigung, da ist etwas schiefgelaufen." }],
        title: conv.title === "Neuer Chat" ? content.slice(0, 40) : conv.title });
    } catch (e) {
      onUpdate({ ...conv, messages: [...nextMsgs, { role: "assistant", content: "Verbindung fehlgeschlagen. Bitte erneut versuchen." }] });
    }
    setBusy(false);
  }

  return (
    <div className="flex flex-col h-full">
      <ScreenHeader title="AI Coach" onBack={onBack}
        right={<div className="w-9 h-9 rounded-full flex items-center justify-center" style={{ background: C.blue }}><Sparkles size={18} /></div>} />
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 pb-4 no-scrollbar">
        {msgs.length === 0 && (
          <div className="mt-8">
            <div className="flex flex-col items-center text-center mb-8">
              <div className="w-16 h-16 rounded-full flex items-center justify-center mb-4" style={{ background: C.blue }}>
                <Sparkles size={30} />
              </div>
              <div className="text-[22px] font-bold">Frag den AI Coach</div>
              <div className="text-[15px] mt-1" style={{ color: C.sub }}>Dein persönlicher YouTube-Wachstumsexperte</div>
            </div>
            <div className="flex flex-col gap-2">
              {suggestions.map((s) => (
                <button key={s} onClick={() => send(s)}
                  className="text-left px-4 py-3 rounded-2xl text-[15px]"
                  style={{ background: C.card, border: `1px solid ${C.faint}` }}>{s}</button>
              ))}
            </div>
          </div>
        )}
        {msgs.map((m, i) => (
          <div key={i} className={`flex mb-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className="max-w-[82%] px-4 py-2.5 rounded-2xl text-[15px] leading-relaxed whitespace-pre-wrap"
              style={{ background: m.role === "user" ? C.blue : C.card,
                borderBottomRightRadius: m.role === "user" ? 6 : 18,
                borderBottomLeftRadius: m.role === "user" ? 18 : 6 }}>
              {m.content}
            </div>
          </div>
        ))}
        {busy && (
          <div className="flex justify-start mb-3">
            <div className="px-4 py-3 rounded-2xl" style={{ background: C.card }}>
              <Loader2 size={18} className="animate-spin" style={{ color: C.sub }} />
            </div>
          </div>
        )}
      </div>
      <div className="px-3 pb-4 pt-2 shrink-0">
        <div className="flex items-center gap-2 px-3 py-2 rounded-full" style={{ background: C.card, border: `1px solid ${C.faint}` }}>
          <input value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Nachricht an AI Coach…" className="flex-1 bg-transparent outline-none text-[16px] px-2" style={{ color: C.text }} />
          <button onClick={() => send()} disabled={busy || !input.trim()}
            className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
            style={{ background: input.trim() ? C.blue : C.faint }}>
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

// ================= Keywords =================
function KeywordsScreen({ onBack }) {
  const [topic, setTopic] = useState("");
  const [busy, setBusy] = useState(false);
  const [results, setResults] = useState([]);
  const [err, setErr] = useState("");

  async function research(t) {
    const q = (t ?? topic).trim();
    if (!q || busy) return;
    setBusy(true); setErr(""); setResults([]);
    try {
      const raw = await callClaude(
        [{ role: "user", content: `Erstelle 8 realistische YouTube-Keyword-Ideen zum Thema "${q}" für den deutschsprachigen Markt. Gib NUR ein JSON-Array zurück, ohne Erklärung, ohne Markdown-Backticks. Format pro Objekt: {"keyword":"string (deutsch, suchtauglich)","score":Zahl 0-100 (SEO-Chance),"vph":"z.B. 42,1k","searches":"z.B. 88,3k","trend":"z.B. +120%"}. Realistische, variierende Werte.` }],
        "Du bist ein YouTube-SEO-Tool. Du gibst ausschließlich valides JSON zurück.",
        1500
      );
      const parsed = parseLooseJSON(raw);
      setResults(Array.isArray(parsed) ? parsed : []);
    } catch (e) {
      setErr("Konnte keine Keywords laden. Bitte erneut versuchen.");
    }
    setBusy(false);
  }

  const chips = ["youtube ai", "geld verdienen online", "lernen tipps", "krypto 2026"];

  return (
    <div className="flex flex-col h-full">
      <ScreenHeader title="Schlüsselwörter" onBack={onBack} />
      <div className="px-4 pb-4 flex-1 overflow-y-auto no-scrollbar">
        <div className="flex items-center gap-2 px-3 py-2 rounded-full mb-3" style={{ background: C.card, border: `1px solid ${C.faint}` }}>
          <Search size={18} style={{ color: C.sub }} />
          <input value={topic} onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && research()}
            placeholder="Thema oder Keyword…" className="flex-1 bg-transparent outline-none text-[16px]" style={{ color: C.text }} />
          <button onClick={() => research()} disabled={busy}
            className="px-4 py-1.5 rounded-full text-[14px] font-semibold" style={{ background: C.blue }}>
            {busy ? <Loader2 size={16} className="animate-spin" /> : "Suchen"}
          </button>
        </div>

        {results.length === 0 && !busy && (
          <div className="flex flex-wrap gap-2 mb-6">
            {chips.map((c) => (
              <button key={c} onClick={() => { setTopic(c); research(c); }}
                className="px-3 py-1.5 rounded-full text-[14px]" style={{ background: C.card, color: C.sub }}>{c}</button>
            ))}
          </div>
        )}

        {err && <div className="text-[14px] mt-4" style={{ color: "#E2554A" }}>{err}</div>}

        {busy && (
          <div className="flex flex-col items-center justify-center py-16" style={{ color: C.sub }}>
            <Loader2 size={28} className="animate-spin mb-3" />
            <span className="text-[15px]">Analysiere „{topic}"…</span>
          </div>
        )}

        <div className="flex flex-col gap-3">
          {results.map((k, i) => (
            <div key={i} className="rounded-2xl p-4" style={{ background: C.card }}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-[22px] font-bold shrink-0" style={{ color: scoreColor(k.score) }}>{k.score}</span>
                  <span className="text-[18px] font-semibold truncate">{k.keyword}</span>
                </div>
                <span className="text-[15px] font-medium shrink-0" style={{ color: C.sub }}>{k.vph} VPH</span>
              </div>
              <div className="mt-1 flex items-center gap-2 text-[14px]" style={{ color: C.sub }}>
                <span>{k.searches} Suchen</span>
                <span className="inline-flex items-center gap-1" style={{ color: C.green }}>
                  <TrendingUp size={14} />{k.trend}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ================= Optimize =================
function OptimizeScreen({ onBack }) {
  const [topic, setTopic] = useState("");
  const [busy, setBusy] = useState(false);
  const [out, setOut] = useState(null);
  const [err, setErr] = useState("");
  const [copied, setCopied] = useState("");

  async function run() {
    const q = topic.trim();
    if (!q || busy) return;
    setBusy(true); setErr(""); setOut(null);
    try {
      const raw = await callClaude(
        [{ role: "user", content: `Optimiere ein YouTube-Video zum Thema "${q}" für den deutschsprachigen Markt. Gib NUR valides JSON zurück (keine Backticks): {"titles":["5 klickstarke Titel"],"description":"SEO-Beschreibung 2-3 Sätze mit Keywords","tags":["12 relevante Tags"]}.` }],
        "Du bist ein YouTube-Optimierungstool. Du gibst ausschließlich valides JSON zurück.",
        1500
      );
      setOut(parseLooseJSON(raw));
    } catch (e) {
      setErr("Optimierung fehlgeschlagen. Bitte erneut versuchen.");
    }
    setBusy(false);
  }

  function copy(text, id) {
    if (!navigator.clipboard) return; // no clipboard (insecure context) → no false checkmark
    navigator.clipboard.writeText(text).then(() => {
      setCopied(id); setTimeout(() => setCopied(""), 1200);
    }).catch(() => {});
  }

  return (
    <div className="flex flex-col h-full">
      <ScreenHeader title="Optimieren" onBack={onBack} />
      <div className="px-4 pb-4 flex-1 overflow-y-auto no-scrollbar">
        <div className="text-[15px] mb-3" style={{ color: C.sub }}>
          Gib dein Video-Thema ein und erhalte optimierte Titel, Beschreibung und Tags.
        </div>
        <div className="flex items-center gap-2 px-3 py-2 rounded-full mb-4" style={{ background: C.card, border: `1px solid ${C.faint}` }}>
          <input value={topic} onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run()}
            placeholder="z.B. YouTube mit KI automatisieren" className="flex-1 bg-transparent outline-none text-[16px] px-2" style={{ color: C.text }} />
          <button onClick={run} disabled={busy} className="px-4 py-1.5 rounded-full text-[14px] font-semibold" style={{ background: C.blue }}>
            {busy ? <Loader2 size={16} className="animate-spin" /> : "Los"}
          </button>
        </div>

        {err && <div className="text-[14px]" style={{ color: "#E2554A" }}>{err}</div>}
        {busy && (
          <div className="flex flex-col items-center justify-center py-16" style={{ color: C.sub }}>
            <Loader2 size={28} className="animate-spin mb-3" /><span className="text-[15px]">Optimiere…</span>
          </div>
        )}

        {out && (
          <div className="flex flex-col gap-5">
            <div>
              <div className="text-[15px] font-bold mb-2" style={{ color: C.sub }}>TITEL-IDEEN</div>
              <div className="flex flex-col gap-2">
                {(out.titles || []).map((t, i) => (
                  <button key={i} onClick={() => copy(t, "t" + i)}
                    className="flex items-center justify-between gap-3 text-left px-4 py-3 rounded-2xl text-[15px]" style={{ background: C.card }}>
                    <span>{t}</span>
                    {copied === "t" + i ? <Check size={16} style={{ color: C.green }} /> : <Copy size={16} style={{ color: C.sub }} />}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <div className="text-[15px] font-bold mb-2" style={{ color: C.sub }}>BESCHREIBUNG</div>
              <button onClick={() => copy(out.description, "desc")}
                className="w-full text-left px-4 py-3 rounded-2xl text-[15px] leading-relaxed" style={{ background: C.card }}>
                {out.description}
                <span className="flex justify-end mt-2">
                  {copied === "desc" ? <Check size={16} style={{ color: C.green }} /> : <Copy size={16} style={{ color: C.sub }} />}
                </span>
              </button>
            </div>
            <div>
              <div className="text-[15px] font-bold mb-2" style={{ color: C.sub }}>TAGS</div>
              <div className="flex flex-wrap gap-2">
                {(out.tags || []).map((tag, i) => (
                  <span key={i} className="px-3 py-1.5 rounded-full text-[13px]" style={{ background: C.card, color: C.sub }}>{tag}</span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ================= Upgrade =================
function UpgradeScreen({ onBack }) {
  const feats = [
    "Unbegrenzte Keyword-Recherchen",
    "AI Coach ohne Limit",
    "Erweiterte Wettbewerbs-Analyse",
    "Best Time to Post",
    "Titel- & Thumbnail-A/B-Ideen",
  ];
  return (
    <div className="flex flex-col h-full">
      <ScreenHeader title="Upgrade" onBack={onBack} />
      <div className="px-5 pb-6 flex-1 overflow-y-auto no-scrollbar">
        <div className="rounded-3xl p-6 mb-6" style={{ background: "linear-gradient(160deg,#12213F,#0C0C12)", border: `1px solid ${C.blue}` }}>
          <Rocket size={34} style={{ color: C.blue }} />
          <div className="text-[26px] font-bold mt-3">Maxforge Lab Pro</div>
          <div className="text-[15px] mt-1" style={{ color: C.sub }}>Alles freischalten und schneller wachsen.</div>
          <div className="text-[34px] font-bold mt-4">9,99€<span className="text-[16px] font-normal" style={{ color: C.sub }}> / Monat</span></div>
        </div>
        <div className="flex flex-col gap-3 mb-8">
          {feats.map((f) => (
            <div key={f} className="flex items-center gap-3 text-[16px]">
              <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0" style={{ background: C.blue }}>
                <Check size={14} />
              </div>{f}
            </div>
          ))}
        </div>
        <button className="w-full py-4 rounded-full text-[17px] font-semibold" style={{ background: C.blue }}>
          Jetzt upgraden
        </button>
      </div>
    </div>
  );
}

// ================= Dashboard =================
function StatCard({ label, value }) {
  const { min, max } = bracket(value);
  const pct = Math.max(0, Math.min(1, (value - min) / (max - min)));
  const disp = compact(value);
  return (
    <div className="flex-1 flex flex-col items-center px-2">
      <span className="text-[13px] font-medium tracking-wide mb-3" style={{ color: C.sub }}>{label}</span>
      <span className="leading-none font-bold" style={{ fontSize: disp.length >= 5 ? 44 : 68 }}>{disp}</span>
      <div className="w-full mt-6">
        <div className="h-[6px] w-full rounded-full" style={{ background: C.faint }}>
          <div className="h-full rounded-full" style={{ width: `${pct * 100}%`, background: C.blue }} />
        </div>
        <div className="flex justify-between mt-2 text-[13px]" style={{ color: C.sub }}>
          <span>{compact(min)}</span><span>{compact(max)}</span>
        </div>
      </div>
    </div>
  );
}

function Dashboard({ openMenu, go, tab, setTab, stats, chart, loading, onRefresh }) {
  const live = !!stats?.channel;
  const subs = stats?.channel?.subscribers ?? 0;
  const views = stats?.channel?.views ?? 6;
  const videoCount = stats?.channel?.videoCount ?? 0;
  const subsHidden = stats?.channel?.subscribersHidden;
  const recent = stats?.recentVideos || [];
  const showTrend = tab === "Alle" || tab === "Forschung";
  const showPeers = tab === "Alle" || tab === "Forschung";
  const showOptimize = tab === "Alle" || tab === "Optimierung";
  const showAnalytics = tab === "Alle" || tab === "Analytik";
  return (
    <div className="flex-1 overflow-y-auto no-scrollbar pb-32">
      <div className="flex items-center px-4 py-3 gap-3">
        <button onClick={openMenu} className="w-11 h-11 rounded-full flex items-center justify-center" style={{ background: C.card }}>
          <Menu size={22} />
        </button>
        <div className="flex-1 flex justify-center">
          <div className="flex items-center gap-2 px-4 py-2 rounded-full" style={{ background: C.card }}>
            <div className="relative">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-rose-400 to-amber-700" />
              <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center" style={{ background: "#FF0000" }}>
                <Youtube size={9} color="#fff" />
              </div>
            </div>
            <span className="font-semibold text-[15px] max-w-[140px] truncate">{stats?.channel?.title || "Dein Kanal"}</span>
            <ChevronDown size={18} style={{ color: C.sub }} />
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={onRefresh} className="w-11 h-11 rounded-full flex items-center justify-center" style={{ background: C.card }}>
            <RefreshCw size={19} className={loading ? "animate-spin" : ""} style={{ color: C.sub }} />
          </button>
          <button onClick={() => go("settings")} className="w-11 h-11 rounded-full flex items-center justify-center" style={{ background: C.card }}>
            <Settings size={19} style={{ color: C.sub }} />
          </button>
        </div>
      </div>

      <div className="px-4">
        <div className="rounded-3xl flex items-stretch py-6" style={{ background: C.card }}>
          <StatCard label="ABONNENTEN" value={subsHidden ? 0 : subs} />
          <div className="w-px my-2" style={{ background: C.faint }} />
          <StatCard label="ANSICHTEN" value={views} />
        </div>
        <div className="flex items-center justify-center gap-2 mt-2 text-[13px]">
          {live ? (
            <span className="inline-flex items-center gap-1.5" style={{ color: C.green }}>
              <Wifi size={13} /> Live-Daten · {videoCount} Videos
            </span>
          ) : (
            <button onClick={() => go("settings")} className="inline-flex items-center gap-1.5" style={{ color: C.sub }}>
              <WifiOff size={13} /> Demo-Daten — Datenquelle verbinden
            </button>
          )}
        </div>
      </div>

      <div className="flex gap-3 px-4 py-5 overflow-x-auto no-scrollbar">
        {TABS.map((t) => {
          const active = t === tab;
          return (
            <button key={t} onClick={() => setTab(t)}
              className="px-6 py-3 rounded-full text-[16px] font-medium whitespace-nowrap transition-colors"
              style={{ background: active ? C.blue : C.card, color: active ? "#fff" : C.sub }}>{t}</button>
          );
        })}
      </div>

      {showTrend && (
        <div className="px-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="text-[22px] font-bold">Trend-Keyword</span>
              <span style={{ color: C.sub }} className="text-[15px]">• vor 4T</span>
            </div>
            <MoreVertical size={22} style={{ color: C.sub }} />
          </div>
          <button onClick={() => go("keywords")} className="w-full text-left rounded-3xl p-5" style={{ background: C.card }}>
            <div className="flex items-start justify-between">
              <div className="flex items-baseline gap-3">
                <span className="text-[26px] font-bold" style={{ color: C.green }}>62</span>
                <span className="text-[24px] font-semibold">youtube ai</span>
              </div>
              <span className="text-[19px] font-semibold" style={{ color: C.sub }}>120,2k VPH</span>
            </div>
            <div className="mt-1 text-[16px]" style={{ color: C.sub }}>
              135,5k Suchen <span style={{ color: C.green }} className="font-medium">+313%</span>
            </div>
            <div className="h-[220px] mt-4 -mx-1">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 8, left: 8, bottom: 0 }}>
                  <XAxis dataKey="d" tick={{ fill: C.sub, fontSize: 14 }} axisLine={false} tickLine={false} interval={0} />
                  <YAxis hide domain={[0, 110]} />
                  <Line type="monotone" dataKey="v" stroke={C.blue} strokeWidth={3} dot={false}
                    activeDot={{ r: 6, fill: C.blue, stroke: "#fff", strokeWidth: 2 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </button>
        </div>
      )}

      {showOptimize && (
        <div className="px-4 mt-7">
          <div className="text-[22px] font-bold mb-3">Optimieren</div>
          <button onClick={() => go("optimize")} className="w-full text-left rounded-3xl p-5 flex items-center gap-4" style={{ background: C.card }}>
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0" style={{ background: C.blue }}>
              <Clapperboard size={24} />
            </div>
            <div>
              <div className="text-[17px] font-semibold">Video optimieren</div>
              <div className="text-[14px]" style={{ color: C.sub }}>Titel, Beschreibung & Tags generieren</div>
            </div>
          </button>
        </div>
      )}

      {showAnalytics && (
        <div className="px-4 mt-7">
          <div className="text-[22px] font-bold mb-3">Analytik</div>
          <div className="grid grid-cols-2 gap-3">
            {(live
              ? [["Abonnenten", subsHidden ? "—" : compact(subs)], ["Ansichten", compact(views)],
                 ["Videos", compact(videoCount)], ["Ø Views/Video", videoCount ? compact(Math.round(views / videoCount)) : "—"]]
              : [["Impressionen", "124"], ["CTR", "4,8%"], ["Watch Time", "2,1 Std"], ["Ø Ansichtsdauer", "0:42"]]
            ).map(([l, v]) => (
              <div key={l} className="rounded-2xl p-4" style={{ background: C.card }}>
                <div className="text-[13px]" style={{ color: C.sub }}>{l}</div>
                <div className="text-[24px] font-bold mt-1">{v}</div>
              </div>
            ))}
          </div>

          {chart && chart.length > 0 && (
            <div className="rounded-3xl p-5 mt-3" style={{ background: C.card }}>
              <div className="text-[15px] font-semibold mb-1">Kanal-Views</div>
              <div className="text-[13px] mb-2" style={{ color: C.sub }}>
                {compact(chart.reduce((a, b) => a + (b.v || 0), 0))} gesamt im Zeitraum
              </div>
              <div className="h-[180px] -mx-1">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chart} margin={{ top: 8, right: 8, left: 8, bottom: 0 }}>
                    <XAxis dataKey="d" tick={{ fill: C.sub, fontSize: 13 }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
                    <YAxis hide />
                    <Line type="monotone" dataKey="v" stroke={C.green} strokeWidth={3} dot={false}
                      activeDot={{ r: 5, fill: C.green, stroke: "#fff", strokeWidth: 2 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {live && recent.length > 0 && (
            <div className="mt-4">
              <div className="text-[15px] font-bold mb-2" style={{ color: C.sub }}>LETZTE VIDEOS</div>
              <div className="flex flex-col gap-2">
                {recent.slice(0, 5).map((v) => (
                  <div key={v.id} className="flex items-center gap-3 rounded-2xl p-3" style={{ background: C.card }}>
                    <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0" style={{ background: C.cardAlt }}>
                      <Video size={17} style={{ color: C.sub }} />
                    </div>
                    <span className="flex-1 text-[14px] truncate">{v.title}</span>
                    <span className="text-[14px] font-semibold shrink-0" style={{ color: C.sub }}>{compact(v.views)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {showPeers && (
        <div className="px-4 mt-7">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-[22px] font-bold">Vorgeschlagene Teilnehmer</span>
            <span style={{ color: C.sub }} className="text-[15px]">• vor 4T</span>
          </div>
          <div className="flex gap-4 overflow-x-auto no-scrollbar pb-2">
            {[{ name: "FORREST'S AUTO REVIEWS", auto: true },{ name: "Tech Deutsch", auto: false },{ name: "AI Kanal", auto: false }].map((ch, i) => (
              <div key={i} className="rounded-3xl p-6 flex flex-col items-center justify-center shrink-0" style={{ background: C.card, width: 190, height: 180 }}>
                <div className="w-24 h-24 rounded-full flex items-center justify-center" style={{ background: "#000", border: `1px solid ${C.faint}` }}>
                  {ch.auto ? (
                    <span className="text-[13px] font-black italic text-center leading-tight" style={{ color: "#E23434" }}>FORREST'S<br />AUTO</span>
                  ) : (<div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600" />)}
                </div>
                <span className="text-[13px] mt-3 text-center" style={{ color: C.sub }}>{ch.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ================= Settings / Datenquelle =================
function SettingsScreen({ onBack, config, onSave }) {
  const [statsUrl, setStatsUrl] = useState(config.statsUrl || "");
  const [chartUrl, setChartUrl] = useState(config.chartUrl || "");
  const [saved, setSaved] = useState(false);

  function save() {
    onSave({ statsUrl: statsUrl.trim(), chartUrl: chartUrl.trim() });
    setSaved(true); setTimeout(() => setSaved(false), 1500);
  }

  const field = (label, val, set, ph) => (
    <div className="mb-5">
      <div className="text-[14px] font-semibold mb-2" style={{ color: C.sub }}>{label}</div>
      <input value={val} onChange={(e) => set(e.target.value)} placeholder={ph}
        className="w-full px-4 py-3 rounded-2xl text-[15px] outline-none"
        style={{ background: C.card, color: C.text, border: `1px solid ${C.faint}` }} />
    </div>
  );

  return (
    <div className="flex flex-col h-full">
      <ScreenHeader title="Datenquelle" onBack={onBack} />
      <div className="px-4 pb-6 flex-1 overflow-y-auto no-scrollbar">
        <div className="text-[15px] leading-relaxed mb-5" style={{ color: C.sub }}>
          Verbinde deine YouTube-Daten. Der Maxforge&nbsp;Lab Server liefert die Statistiken
          standardmäßig unter <span style={{ color: C.text }}>/api/stats</span>. Eigene URL
          eintragen oder leer lassen = Standardquelle.
        </div>
        {field("Statistik-URL (Abos, Views, Videos)", statsUrl, setStatsUrl, "https://dein-server.de/api/stats")}
        {field("Chart-URL (tägliche Views, optional)", chartUrl, setChartUrl, "https://dein-server.de/chart.json")}
        <button onClick={save} className="w-full py-3.5 rounded-full text-[16px] font-semibold mt-2"
          style={{ background: saved ? C.green : C.blue }}>
          {saved ? "Gespeichert ✓" : "Speichern & laden"}
        </button>
        <div className="text-[13px] mt-6 leading-relaxed" style={{ color: C.sub }}>
          Hinweis: Der Server muss CORS erlauben (macht der --serve-Modus automatisch). Die Statistik-URL
          liefert JSON mit einem <span style={{ color: C.text }}>channel</span>-Objekt, die Chart-URL ein
          Array aus <span style={{ color: C.text }}>{`{ d, v }`}</span>.
        </div>
      </div>
    </div>
  );
}

// ================= App root =================
export default function MaxforgeLabApp() {
  const [screen, setScreen] = useState("home");
  const [tab, setTab] = useState("Forschung");
  const [drawer, setDrawer] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [config, setConfig] = useState(ENV_CONFIG);
  const [liveStats, setLiveStats] = useState(null);
  const [liveChart, setLiveChart] = useState(null);
  const [loading, setLoading] = useState(false);
  const requestSeq = useRef(0);

  async function loadLive(cfg) {
    if (!cfg.statsUrl && !cfg.chartUrl) return;
    const seq = ++requestSeq.current; // ignore results from superseded calls
    setLoading(true);
    if (cfg.statsUrl) {
      try {
        const r = await fetch(cfg.statsUrl);
        const j = await r.json();
        if (seq === requestSeq.current && j && j.channel) setLiveStats(j);
      } catch (e) {}
    }
    if (cfg.chartUrl) {
      try {
        const r = await fetch(cfg.chartUrl);
        const j = await r.json();
        if (seq === requestSeq.current && Array.isArray(j)) setLiveChart(j);
      } catch (e) {}
    }
    if (seq === requestSeq.current) setLoading(false);
  }

  function saveConfig(cfg) {
    setConfig(cfg);
    store.set("maxforge-lab-config", cfg);
    loadLive(cfg);
  }

  useEffect(() => {
    (async () => {
      const saved = await store.get("maxforge-lab-conversations");
      if (saved) setConversations(saved);
      const cfg = await store.get("maxforge-lab-config");
      if (cfg) { setConfig(cfg); loadLive(cfg); }
      else if (ENV_CONFIG.statsUrl || ENV_CONFIG.chartUrl) loadLive(ENV_CONFIG);
    })();
  }, []);

  function persist(list) {
    setConversations(list);
    store.set("maxforge-lab-conversations", list);
  }

  function newChat() {
    const conv = { id: "c" + Date.now(), title: "Neuer Chat", messages: [], updatedAt: Date.now() };
    setActiveConv(conv); setScreen("coach");
  }

  function openConv(id) {
    const c = conversations.find((x) => x.id === id);
    if (c) { setActiveConv(c); setScreen("coach"); }
  }

  function updateConv(conv) {
    setActiveConv(conv);
    const exists = conversations.some((c) => c.id === conv.id);
    const list = exists ? conversations.map((c) => (c.id === conv.id ? conv : c)) : [conv, ...conversations];
    persist(list);
  }

  function go(to) {
    if (to === "home") setScreen("home");
    else if (to === "newchat") newChat();
    else if (to === "coach") newChat();
    else setScreen(to);
  }

  return (
    <div className="w-full min-h-screen flex justify-center" style={{ background: "#000" }}>
      <div className="w-full max-w-[430px] flex flex-col relative overflow-hidden"
        style={{ background: C.bg, color: C.text, height: "100vh", fontFamily: "system-ui, -apple-system, sans-serif" }}>

        <Drawer open={drawer} onClose={() => setDrawer(false)} go={go}
          conversations={conversations} openConv={openConv} />

        {/* Status bar */}
        <div className="flex items-center justify-between px-5 pt-3 pb-1 text-[15px] font-semibold shrink-0">
          <span>0:51</span>
          <div className="flex items-center gap-2" style={{ color: C.sub }}>
            <Moon size={15} /><BellOff size={15} /><Signal size={15} />
            <span className="flex items-center gap-1 text-[13px]"><BatteryCharging size={17} /> 38%</span>
            <span className="w-2 h-2 rounded-full" style={{ background: C.green }} />
          </div>
        </div>

        {/* Screens */}
        <div className="flex-1 min-h-0 flex flex-col">
          {screen === "home" && (
            <Dashboard openMenu={() => setDrawer(true)} go={go} tab={tab} setTab={setTab}
              stats={liveStats} chart={liveChart} loading={loading} onRefresh={() => loadLive(config)} />
          )}
          {screen === "coach" && activeConv && (
            <CoachScreen onBack={() => setScreen("home")} conv={activeConv} onUpdate={updateConv} />
          )}
          {screen === "keywords" && <KeywordsScreen onBack={() => setScreen("home")} />}
          {screen === "optimize" && <OptimizeScreen onBack={() => setScreen("home")} />}
          {screen === "upgrade" && <UpgradeScreen onBack={() => setScreen("home")} />}
          {screen === "settings" && (
            <SettingsScreen onBack={() => setScreen("home")} config={config} onSave={saveConfig} />
          )}
        </div>

        {/* Bottom nav (only on home) */}
        {screen === "home" && (
          <div className="absolute bottom-0 left-0 w-full px-4 pb-4 pt-3"
            style={{ background: `linear-gradient(to top, ${C.bg} 70%, transparent)` }}>
            <div className="flex items-center gap-3">
              <button onClick={() => setScreen("home")} className="w-14 h-14 rounded-full flex items-center justify-center shrink-0" style={{ background: C.card }}>
                <Home size={24} />
              </button>
              <button onClick={newChat} className="flex-1 h-14 rounded-full flex items-center gap-3 px-5" style={{ background: C.card }}>
                <div className="w-6 h-6 rounded-full" style={{ background: C.blue }} />
                <span className="text-[17px]" style={{ color: C.sub }}>AI Coach fragen</span>
              </button>
              <button onClick={() => setScreen("keywords")} className="w-14 h-14 rounded-full flex items-center justify-center shrink-0" style={{ background: C.card }}>
                <Search size={24} />
              </button>
            </div>
          </div>
        )}

        <style>{`.no-scrollbar::-webkit-scrollbar{display:none}.no-scrollbar{-ms-overflow-style:none;scrollbar-width:none}`}</style>
      </div>
    </div>
  );
}
