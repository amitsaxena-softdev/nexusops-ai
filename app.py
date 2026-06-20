import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NexusOps AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Background + reset */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #08080f !important;
}
[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; }
#MainMenu, footer { visibility: hidden !important; }
.stDeployButton { display: none !important; }
section[data-testid="stSidebar"] > div { background: #0d0d1a !important; }

/* Main container */
.block-container {
    padding-top: 0 !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1360px !important;
    margin: 0 auto !important;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0;
    padding: 4px 0 36px;
}
.stat {
    text-align: center;
    padding: 0 40px;
}
.stat-num {
    font-size: 36px;
    font-weight: 900;
    color: #f1f5f9;
    line-height: 1;
    letter-spacing: -1px;
}
.stat-label {
    font-size: 10px;
    color: rgba(255,255,255,0.28);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 5px;
}
.stat-sep {
    width: 1px;
    height: 40px;
    background: rgba(255,255,255,0.07);
}

/* ── Section heading ── */
.section-label {
    text-align: center;
    margin-bottom: 20px;
}
.section-label span {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.2);
    padding: 0 16px;
    position: relative;
}
.section-label span::before,
.section-label span::after {
    content: "";
    position: absolute;
    top: 50%;
    width: 60px;
    height: 1px;
    background: rgba(255,255,255,0.07);
}
.section-label span::before { right: 100%; }
.section-label span::after  { left:  100%; }

/* ── Agent cards ── */
[data-testid="column"] { padding: 5px !important; }

.nexus-card {
    position: relative;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 20px 18px 16px;
    height: 174px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.26s cubic-bezier(0.34, 1.56, 0.64, 1),
                border-color 0.22s ease,
                box-shadow 0.26s ease;
}
.nexus-card::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 18px;
    background: linear-gradient(135deg, var(--c) 0%, transparent 55%);
    opacity: 0;
    transition: opacity 0.26s ease;
}
.nexus-card:hover {
    transform: translateY(-6px) scale(1.01);
    border-color: var(--c);
    box-shadow: 0 20px 60px color-mix(in srgb, var(--c) 30%, transparent);
}
.nexus-card:hover::after { opacity: 0.07; }

.card-link {
    position: absolute;
    inset: 0;
    z-index: 30;
    border-radius: 18px;
}

.card-num {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    color: var(--c);
    font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
    margin-bottom: 10px;
    opacity: 0.6;
}
.card-icon { font-size: 26px; line-height: 1; margin-bottom: 9px; }
.card-name {
    font-size: 13.5px;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1.25;
    margin-bottom: 4px;
}
.card-client {
    font-size: 10.5px;
    color: var(--c);
    font-weight: 500;
    margin-bottom: 6px;
    opacity: 0.75;
}
.card-desc {
    font-size: 10.5px;
    color: rgba(255,255,255,0.3);
    line-height: 1.5;
}
.card-tag {
    position: absolute;
    top: 14px;
    right: 14px;
    font-size: 8.5px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--c);
    background: color-mix(in srgb, var(--c) 12%, transparent);
    border: 1px solid color-mix(in srgb, var(--c) 35%, transparent);
    padding: 3px 8px;
    border-radius: 100px;
}

/* ── Footer ── */
.nx-footer {
    text-align: center;
    padding: 40px 0 20px;
    font-size: 11px;
    color: rgba(255,255,255,0.12);
    letter-spacing: 1px;
}
.nx-footer b { color: rgba(255,255,255,0.25); }
</style>
""", unsafe_allow_html=True)

# ── Hero (iframe for typing animation + grid) ──────────────────────────────────
components.html("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
    background: #08080f;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 300px;
    overflow: hidden;
}

/* Animated grid */
.grid {
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(99,102,241,0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,0.045) 1px, transparent 1px);
    background-size: 52px 52px;
    animation: drift 25s linear infinite;
    pointer-events: none;
}
@keyframes drift {
    from { transform: translate(0,0); }
    to   { transform: translate(52px, 52px); }
}

/* Radial glow center */
.glow {
    position: fixed; top:50%; left:50%;
    transform: translate(-50%,-50%);
    width: 700px; height: 320px;
    background: radial-gradient(ellipse at center,
        rgba(99,102,241,0.13) 0%,
        rgba(139,92,246,0.06) 40%,
        transparent 70%);
    pointer-events: none;
}

.hero {
    position: relative; z-index: 10;
    text-align: center;
}

.badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.28);
    color: #a5b4fc;
    font-size: 9.5px; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    padding: 7px 20px; border-radius: 100px;
    margin-bottom: 22px;
    opacity: 0;
    animation: riseIn 0.8s ease forwards 0.1s;
}
.dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #6366f1;
    animation: pulse 2s ease infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50% { opacity:0.4; transform:scale(0.75); }
}

/* Title */
.title-row {
    display: flex; align-items: baseline;
    justify-content: center;
    height: 90px; gap: 0;
    margin-bottom: 14px;
}
.t { font-size: 82px; font-weight: 900; letter-spacing: -3px; line-height: 1; }
.t-nexus { color: #f1f5f9; }
.t-ops   { color: #818cf8; }
.t-gap   { display: inline-block; width: 22px; }
.t-ai {
    background: linear-gradient(130deg, #6366f1, #a855f7 45%, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}

.cursor {
    display: inline-block;
    width: 5px; height: 70px;
    background: linear-gradient(180deg, #6366f1, #06b6d4);
    border-radius: 3px;
    vertical-align: bottom; margin-bottom: 8px; margin-left: 4px;
    animation: blink 0.85s step-end infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

.subtitle {
    font-size: 14.5px;
    color: rgba(255,255,255,0.32);
    letter-spacing: 0.3px;
    opacity: 0;
}

@keyframes riseIn {
    from { opacity:0; transform:translateY(18px); }
    to   { opacity:1; transform:translateY(0); }
}
</style>
</head>
<body>
<div class="grid"></div>
<div class="glow"></div>

<div class="hero">
    <div class="badge">
        <div class="dot"></div>
        Saarland Hackathon 2026 &nbsp;&middot;&nbsp; Enterprise AI Demo
    </div>

    <div class="title-row">
        <span class="t t-nexus" id="tn"></span>
        <span class="t t-ops"   id="to"></span>
        <span class="t-gap"     id="tg" style="display:none"></span>
        <span class="t t-ai"    id="ta"></span>
        <span class="cursor"    id="cur"></span>
    </div>

    <div class="subtitle" id="sub">
        10 AI agents &nbsp;&bull;&nbsp; One platform &nbsp;&bull;&nbsp; Built for Saarland enterprises
    </div>
</div>

<script>
const STEPS = [
    { id:"tn", text:"Nexus", ms:95 },
    { id:"to", text:"Ops",   ms:95 },
    { id:"tg", text:"",      ms:0, gap:true },
    { id:"ta", text:"AI",    ms:130 },
];

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function run() {
    await sleep(500);
    for (const step of STEPS) {
        const el = document.getElementById(step.id);
        if (step.gap) { el.style.display = "inline-block"; await sleep(40); continue; }
        for (let i = 1; i <= step.text.length; i++) {
            el.textContent = step.text.slice(0, i);
            await sleep(step.ms + (Math.random() * 20 - 10));
        }
        await sleep(20);
    }

    // Hide cursor after a pause
    await sleep(1600);
    const cur = document.getElementById("cur");
    cur.style.transition = "opacity 0.5s";
    cur.style.opacity = "0";
    cur.style.animation = "none";

    // Subtitle rises in
    await sleep(300);
    const sub = document.getElementById("sub");
    sub.style.transition = "opacity 0.9s ease, transform 0.9s ease";
    sub.style.transform   = "translateY(14px)";
    sub.style.opacity     = "0";
    await sleep(20);
    sub.style.opacity   = "1";
    sub.style.transform = "translateY(0)";
}

run();
</script>
</body>
</html>
""", height=320, scrolling=False)

# ── Stats bar ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="stats-bar">
    <div class="stat">
        <div class="stat-num">10</div>
        <div class="stat-label">AI Agents</div>
    </div>
    <div class="stat-sep"></div>
    <div class="stat">
        <div class="stat-num">6</div>
        <div class="stat-label">Industries</div>
    </div>
    <div class="stat-sep"></div>
    <div class="stat">
        <div class="stat-num">5</div>
        <div class="stat-label">Clients</div>
    </div>
    <div class="stat-sep"></div>
    <div class="stat">
        <div class="stat-num" style="font-size:22px; padding-top:6px;">Gemini</div>
        <div class="stat-label">2.5 Flash · Live</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Section label ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-label">
    <span>Choose Your Agent</span>
</div>
""", unsafe_allow_html=True)

# ── Agent data ─────────────────────────────────────────────────────────────────
AGENTS = [
    {
        "num": "01", "icon": "🧾",
        "name": "Invoice Processing",
        "client": "Globus Group · St. Wendel",
        "desc": "Auto-sort & route supplier invoices to the right department",
        "page": "Invoice_Processing",
        "color": "#f59e0b",
        "tag": "Finance",
    },
    {
        "num": "02", "icon": "🏥",
        "name": "Shift Replacement",
        "client": "UKS Homburg",
        "desc": "Fill last-minute night-shift gaps and draft WhatsApp messages",
        "page": "Shift_Replacement",
        "color": "#ef4444",
        "tag": "Healthcare",
    },
    {
        "num": "03", "icon": "📋",
        "name": "Work Permit Validation",
        "client": "Leistenschneider GmbH",
        "desc": "Validate permits and confirm expiry dates in seconds",
        "page": "Work_Permit_Validation",
        "color": "#8b5cf6",
        "tag": "HR & Legal",
    },
    {
        "num": "04", "icon": "🔍",
        "name": "CV Fraud Detection",
        "client": "Persowerk Deutschland",
        "desc": "Spot AI-generated CVs, fake certs and misrepresented history",
        "page": "CV_Fraud_Detection",
        "color": "#6366f1",
        "tag": "HR Security",
    },
    {
        "num": "05", "icon": "💼",
        "name": "Interview Support",
        "client": "Kohlpharma GmbH · Merzig",
        "desc": "Smart questions, red flags & feedback letters for hirers",
        "page": "Interview_Support",
        "color": "#06b6d4",
        "tag": "Recruiting",
    },
    {
        "num": "06", "icon": "🎬",
        "name": "Marketing Content",
        "client": "Dr. Theiss Naturwaren",
        "desc": "Production briefs for TikTok & Instagram reels with safe zones",
        "page": "Marketing_Content",
        "color": "#ec4899",
        "tag": "Marketing",
    },
    {
        "num": "07", "icon": "📊",
        "name": "Customer Analytics",
        "client": "Dr. Theiss Naturwaren",
        "desc": "Behavioural patterns, targeting signals, and campaign lift",
        "page": "Customer_Analytics",
        "color": "#10b981",
        "tag": "Analytics",
    },
    {
        "num": "08", "icon": "💰",
        "name": "Dynamic Pricing",
        "client": "Dr. Theiss Naturwaren",
        "desc": "Signal-driven pricing — weather, fixtures, supply chain",
        "page": "Dynamic_Pricing",
        "color": "#f59e0b",
        "tag": "Pricing",
    },
    {
        "num": "09", "icon": "🔭",
        "name": "Competitive Gap Analysis",
        "client": "Dr. Theiss Naturwaren",
        "desc": "White-space gaps competitors aren't filling — live search",
        "page": "Competitive_Gap_Analysis",
        "color": "#a855f7",
        "tag": "Strategy",
    },
    {
        "num": "10", "icon": "🛡️",
        "name": "Secure Email Agent",
        "client": "Rheinmetall",
        "desc": "Prompt-injection-resistant job application processing",
        "page": "Secure_Email_Agent",
        "color": "#64748b",
        "tag": "Security",
    },
]


def _card(a: dict) -> str:
    return f"""
<div class="nexus-card" style="--c:{a['color']};">
  <a href="/{a['page']}" target="_self" class="card-link" aria-label="{a['name']}"></a>
  <div class="card-num">{a['num']}</div>
  <div class="card-icon">{a['icon']}</div>
  <div class="card-name">{a['name']}</div>
  <div class="card-client">{a['client']}</div>
  <div class="card-desc">{a['desc']}</div>
  <div class="card-tag">{a['tag']}</div>
</div>"""


# Row 1 — agents 1–5
row1 = st.columns(5, gap="small")
for i, agent in enumerate(AGENTS[:5]):
    with row1[i]:
        st.markdown(_card(agent), unsafe_allow_html=True)

# Row 2 — agents 6–10
row2 = st.columns(5, gap="small")
for i, agent in enumerate(AGENTS[5:]):
    with row2[i]:
        st.markdown(_card(agent), unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nx-footer">
    <b>NexusOps AI</b> &nbsp;&middot;&nbsp;
    Built for Saarland Hackathon 2026 &nbsp;&middot;&nbsp;
    Powered by Gemini 2.5 Flash
</div>
""", unsafe_allow_html=True)
