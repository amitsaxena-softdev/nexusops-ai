import streamlit as st
import streamlit.components.v1 as components
from shared.theme import apply_theme

st.set_page_config(
    page_title="NexusOps AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme state ────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

D = st.session_state.theme == "dark"

# ── Colour tokens (hero + cards need these) ────────────────────────────────────
BG        = "#08080f"  if D else "#f8fafc"
CARD_BG   = "rgba(255,255,255,0.025)" if D else "rgba(0,0,0,0.028)"
CARD_BD   = "rgba(255,255,255,0.06)"  if D else "rgba(0,0,0,0.08)"
TEXT      = "#f1f5f9"  if D else "#0f172a"
MUTED     = "rgba(255,255,255,0.28)"  if D else "rgba(0,0,0,0.38)"
DESC      = "rgba(255,255,255,0.3)"   if D else "rgba(0,0,0,0.42)"
SEP       = "rgba(255,255,255,0.07)"  if D else "rgba(0,0,0,0.08)"
SECTION_C = "rgba(255,255,255,0.18)"  if D else "rgba(0,0,0,0.22)"
FOOTER_C  = "rgba(255,255,255,0.12)"  if D else "rgba(0,0,0,0.2)"
GRID_CLR  = "rgba(99,102,241,0.045)"  if D else "rgba(99,102,241,0.055)"
GLOW_CLR  = "rgba(99,102,241,0.13)"   if D else "rgba(99,102,241,0.07)"

# ── Global theme: CSS + sidebar ────────────────────────────────────────────────
apply_theme()

# ── Landing-page-specific CSS (stats bar, section label, cards, footer) ────────
st.markdown(f"""
<style>
/* ── Hide sidebar entirely on the homepage ── */
section[data-testid="stSidebar"],
[data-testid="collapsedControl"] {{
    display: none !important;
}}

.block-container {{
    padding-top: 0 !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1260px !important;
    margin: 0 auto !important;
}}
[data-testid="column"] {{ padding: 5px !important; }}

.stats-bar {{
    display: flex; justify-content: center; align-items: center;
    padding: 0 0 36px;
}}
.stat {{ text-align: center; padding: 0 44px; }}
.stat-num {{
    font-size: 36px; font-weight: 900;
    color: {TEXT}; line-height: 1; letter-spacing: -1px;
}}
.stat-label {{
    font-size: 10px; color: {MUTED};
    letter-spacing: 2px; text-transform: uppercase; margin-top: 5px;
}}
.stat-sep {{ width: 1px; height: 40px; background: {SEP}; }}

.section-label {{ text-align: center; margin-bottom: 20px; }}
.section-label span {{
    font-size: 10px; font-weight: 700; letter-spacing: 4px;
    text-transform: uppercase; color: {SECTION_C};
    padding: 0 16px; position: relative;
}}
.section-label span::before, .section-label span::after {{
    content: ""; position: absolute; top: 50%;
    width: 60px; height: 1px; background: {SEP};
}}
.section-label span::before {{ right: 100%; }}
.section-label span::after  {{ left:  100%; }}

.nexus-card {{
    position: relative; background: {CARD_BG};
    border: 1px solid {CARD_BD}; border-radius: 18px;
    padding: 20px 18px 16px; height: 174px; overflow: hidden; cursor: pointer;
    transition: transform 0.26s cubic-bezier(0.34,1.56,0.64,1),
                border-color 0.22s ease, box-shadow 0.26s ease;
}}
.nexus-card::after {{
    content: ""; position: absolute; inset: 0; border-radius: 18px;
    background: linear-gradient(135deg, var(--c) 0%, transparent 55%);
    opacity: 0; transition: opacity 0.26s ease;
}}
.nexus-card:hover {{
    transform: translateY(-6px) scale(1.01);
    border-color: var(--c);
    box-shadow: 0 20px 56px color-mix(in srgb, var(--c) 28%, transparent);
}}
.nexus-card:hover::after {{ opacity: {0.07 if D else 0.05}; }}
.card-link {{ position: absolute; inset: 0; z-index: 30; border-radius: 18px; }}
.card-num {{
    font-size: 10px; font-weight: 700; letter-spacing: 2.5px;
    color: var(--c); font-family: 'SF Mono','Fira Code',monospace;
    margin-bottom: 10px; opacity: 0.6;
}}
.card-icon  {{ font-size: 26px; line-height: 1; margin-bottom: 9px; }}
.card-name  {{ font-size: 13.5px; font-weight: 700; color: {TEXT}; line-height: 1.25; margin-bottom: 4px; }}
.card-client {{ font-size: 10.5px; color: var(--c); font-weight: 500; margin-bottom: 6px; opacity: 0.8; }}
.card-desc  {{ font-size: 10.5px; color: {DESC}; line-height: 1.5; }}
.card-tag {{
    position: absolute; top: 14px; right: 14px;
    font-size: 8.5px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;
    color: var(--c);
    background: color-mix(in srgb, var(--c) 12%, transparent);
    border: 1px solid color-mix(in srgb, var(--c) 35%, transparent);
    padding: 3px 8px; border-radius: 100px;
}}

.nx-footer {{
    text-align: center; padding: 40px 0 20px;
    font-size: 11px; color: {FOOTER_C}; letter-spacing: 1px;
}}
.nx-footer b {{ color: {SECTION_C}; }}
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
components.html(f"""
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
    background:{BG};
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    height:280px;overflow:hidden;
}}
.grid{{
    position:fixed;inset:0;
    background-image:linear-gradient({GRID_CLR} 1px,transparent 1px),
                     linear-gradient(90deg,{GRID_CLR} 1px,transparent 1px);
    background-size:52px 52px;animation:drift 28s linear infinite;pointer-events:none;
}}
@keyframes drift{{from{{transform:translate(0,0)}}to{{transform:translate(52px,52px)}}}}
.glow{{
    position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
    width:700px;height:300px;
    background:radial-gradient(ellipse at center,{GLOW_CLR} 0%,transparent 70%);
    pointer-events:none;
}}
.hero{{position:relative;z-index:10;text-align:center;}}
.title-row{{display:flex;align-items:baseline;justify-content:center;height:90px;margin-bottom:14px;}}
.t{{font-size:82px;font-weight:900;letter-spacing:-3px;line-height:1;}}
.t-nexus{{color:{"#f1f5f9" if D else "#0f172a"};}}
.t-ops{{color:#818cf8;}}
.t-gap{{display:inline-block;width:22px;}}
.t-ai{{background:linear-gradient(130deg,#6366f1,#a855f7 45%,#06b6d4);
       -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
.cursor{{display:inline-block;width:5px;height:70px;
         background:linear-gradient(180deg,#6366f1,#06b6d4);border-radius:3px;
         vertical-align:bottom;margin-bottom:8px;margin-left:4px;
         animation:blink 0.85s step-end infinite;}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
.subtitle{{font-size:14.5px;color:{"rgba(255,255,255,0.32)" if D else "rgba(0,0,0,0.38)"};letter-spacing:0.3px;opacity:0;}}
</style></head><body>
<div class="grid"></div><div class="glow"></div>
<div class="hero">
  <div class="title-row">
    <span class="t t-nexus" id="tn"></span>
    <span class="t t-ops"   id="to"></span>
    <span class="t-gap"     id="tg" style="display:none"></span>
    <span class="t t-ai"    id="ta"></span>
    <span class="cursor"    id="cur"></span>
  </div>
  <div class="subtitle" id="sub">
    10 AI agents &nbsp;&bull;&nbsp; One platform &nbsp;&bull;&nbsp; Built for modern enterprises
  </div>
</div>
<script>
const STEPS=[{{id:"tn",text:"Nexus",ms:95}},{{id:"to",text:"Ops",ms:95}},
             {{id:"tg",text:"",ms:0,gap:true}},{{id:"ta",text:"AI",ms:130}}];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function run(){{
  await sleep(400);
  for(const s of STEPS){{
    const el=document.getElementById(s.id);
    if(s.gap){{el.style.display="inline-block";await sleep(40);continue;}}
    for(let i=1;i<=s.text.length;i++){{
      el.textContent=s.text.slice(0,i);
      await sleep(s.ms+Math.random()*18-9);
    }}
    await sleep(20);
  }}
  await sleep(1600);
  const cur=document.getElementById("cur");
  cur.style.transition="opacity 0.5s";cur.style.animation="none";cur.style.opacity="0";
  await sleep(300);
  const sub=document.getElementById("sub");
  sub.style.transition="opacity 0.9s ease,transform 0.9s ease";
  sub.style.transform="translateY(14px)";sub.style.opacity="0";
  await sleep(20);sub.style.opacity="1";sub.style.transform="translateY(0)";
}}
run();
</script>
</body></html>
""", height=300, scrolling=False)

# ── Stats bar ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stats-bar">
  <div class="stat"><div class="stat-num">10</div><div class="stat-label">AI Agents</div></div>
  <div class="stat-sep"></div>
  <div class="stat"><div class="stat-num">6</div><div class="stat-label">Industries</div></div>
  <div class="stat-sep"></div>
  <div class="stat"><div class="stat-num">5</div><div class="stat-label">Clients</div></div>
</div>
""", unsafe_allow_html=True)

# ── Section label ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label"><span>Choose Your Agent</span></div>', unsafe_allow_html=True)

# ── Agent cards ────────────────────────────────────────────────────────────────
AGENTS = [
    ("01","🧾","Invoice Processing",      "Globus Group · St. Wendel",          "Auto-sort & route supplier invoices to the right department",          "Invoice_Processing",      "#f59e0b","Finance"),
    ("02","🏥","Shift Replacement",        "UKS · Homburg",                       "Fill last-minute night-shift gaps and draft outreach messages",         "Shift_Replacement",       "#ef4444","Healthcare"),
    ("03","📋","Work Permit Validation",   "Leistenschneider GmbH · Saarbrücken", "Validate permits and confirm expiry dates in seconds",                 "Work_Permit_Validation",  "#8b5cf6","HR & Legal"),
    ("04","🔍","CV Fraud Detection",       "Persowerk Deutschland · Saarbrücken", "Spot AI-generated CVs, fake certs and misrepresented history",         "CV_Fraud_Detection",      "#6366f1","HR Security"),
    ("05","💼","Interview Support",        "Kohlpharma GmbH · Merzig",            "Smart questions, red flags & feedback letters for hirers",             "Interview_Support",       "#06b6d4","Recruiting"),
    ("06","🎬","Marketing Content",        "Dr. Theiss Naturwaren · Homburg",     "Production briefs for TikTok & Instagram reels with safe zones",      "Marketing_Content",       "#ec4899","Marketing"),
    ("07","📊","Customer Analytics",       "Dr. Theiss Naturwaren · Homburg",     "Behavioural patterns, targeting signals, and campaign lift",           "Customer_Analytics",      "#10b981","Analytics"),
    ("08","💰","Dynamic Pricing",          "Dr. Theiss Naturwaren · Homburg",     "Signal-driven pricing engine — weather, events, supply chain",        "Dynamic_Pricing",         "#f59e0b","Pricing"),
    ("09","🔭","Competitive Gap Analysis", "Dr. Theiss Naturwaren · Homburg",     "White-space gaps competitors aren't filling — live research",          "Competitive_Gap_Analysis","#a855f7","Strategy"),
    ("10","🛡️","Secure Email Agent",       "Rheinmetall",                         "Prompt-injection-resistant job application processing",               "Secure_Email_Agent",      "#64748b","Security"),
]

def _card(num, icon, name, client, desc, page, color, tag):
    return f"""
<div class="nexus-card" style="--c:{color};">
  <a href="/{page}" target="_self" class="card-link" aria-label="{name}"></a>
  <div class="card-num">{num}</div>
  <div class="card-icon">{icon}</div>
  <div class="card-name">{name}</div>
  <div class="card-client">{client}</div>
  <div class="card-desc">{desc}</div>
  <div class="card-tag">{tag}</div>
</div>"""

row1 = st.columns(5, gap="small")
for i, a in enumerate(AGENTS[:5]):
    with row1[i]: st.markdown(_card(*a), unsafe_allow_html=True)

row2 = st.columns(5, gap="small")
for i, a in enumerate(AGENTS[5:]):
    with row2[i]: st.markdown(_card(*a), unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="nx-footer"><b>NexusOps AI</b> &nbsp;&middot;&nbsp; Enterprise Operations Suite</div>', unsafe_allow_html=True)
