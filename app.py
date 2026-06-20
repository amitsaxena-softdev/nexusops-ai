from urllib.parse import quote

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
BG        = "#0d0f17"  if D else "#f8fafc"
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

# ── Global theme (no sidebar on the homepage) ──────────────────────────────────
apply_theme(sidebar=False)

# ── Landing-page-specific CSS (stats bar, section label, cards, footer) ────────
st.markdown(f"""
<style>
.block-container {{
    padding-top: 0 !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1260px !important;
    margin: 0 auto !important;
}}
[data-testid="column"] {{ padding: 5px !important; }}

/* Hero iframe blends into the page (no opaque black rectangle). */
[data-testid="stIFrame"], .stApp iframe {{ background: transparent !important; }}

/* Make the app container a stacking context so the aurora's negative
   z-index layers above the solid background but below page content. */
[data-testid="stAppViewContainer"] {{ position: relative; z-index: 0; }}

/* ── Aurora background (drifting blurred colour blobs) ── */
.aurora {{ position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none; }}
.aurora b {{
    position: absolute; display: block; border-radius: 50%;
    filter: blur(100px); opacity: {0.38 if D else 0.14};
}}
.aurora .b1 {{ width: 460px; height: 460px; background: #6366f1; top: -120px; left: -60px;
              animation: floaty1 24s ease-in-out infinite; }}
.aurora .b2 {{ width: 420px; height: 420px; background: #a855f7; top: 28%; right: -120px;
              animation: floaty2 28s ease-in-out infinite; }}
.aurora .b3 {{ width: 400px; height: 400px; background: #06b6d4; bottom: -140px; left: 32%;
              animation: floaty3 32s ease-in-out infinite; }}
@keyframes floaty1 {{ 0%,100% {{ transform: translate(0,0) scale(1); }}
                      50% {{ transform: translate(70px,50px) scale(1.18); }} }}
@keyframes floaty2 {{ 0%,100% {{ transform: translate(0,0) scale(1); }}
                      50% {{ transform: translate(-60px,40px) scale(1.12); }} }}
@keyframes floaty3 {{ 0%,100% {{ transform: translate(0,0) scale(1); }}
                      50% {{ transform: translate(40px,-50px) scale(1.2); }} }}

/* ── Entrance motion ── */
@keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(16px); }}
                     to   {{ opacity: 1; transform: none; }} }}
@keyframes cardIn {{ from {{ opacity: 0; transform: translateY(20px) scale(0.97); }}
                     to   {{ opacity: 1; transform: none; }} }}
@keyframes sheen  {{ from {{ left: -60%; }} to {{ left: 130%; }} }}

.stats-bar {{
    display: flex; justify-content: center; align-items: center;
    padding: 0 0 36px;
    animation: fadeUp 0.6s ease 0.15s backwards;
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

.section-label {{ text-align: center; margin-bottom: 20px; animation: fadeUp 0.6s ease 0.28s backwards; }}
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

.card-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    margin-bottom: 8px;
}}
@media (max-width: 1100px) {{ .card-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
@media (max-width: 720px)  {{ .card-grid {{ grid-template-columns: repeat(2, 1fr); }} }}

.nexus-card {{
    position: relative; background: {CARD_BG};
    border: 1px solid {CARD_BD}; border-radius: 18px;
    padding: 22px 16px; height: 152px; overflow: hidden; cursor: pointer;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; gap: 12px;
    transition: transform 0.26s cubic-bezier(0.34,1.56,0.64,1),
                border-color 0.22s ease, box-shadow 0.26s ease;
    animation: cardIn 0.5s cubic-bezier(0.22,1,0.36,1) backwards;
}}
.nexus-card::after {{
    content: ""; position: absolute; inset: 0; border-radius: 18px;
    background: linear-gradient(160deg, var(--c) 0%, transparent 60%);
    opacity: 0; transition: opacity 0.26s ease;
}}
/* hover sheen sweep */
.nexus-card::before {{
    content: ""; position: absolute; top: 0; left: -60%;
    width: 45%; height: 100%; z-index: 5; pointer-events: none;
    background: linear-gradient(100deg, transparent,
                rgba(255,255,255,{0.14 if D else 0.0}), transparent);
    transform: skewX(-18deg); opacity: 0;
}}
.nexus-card:hover::before {{ opacity: 1; animation: sheen 0.9s ease; }}
.nexus-card:hover {{
    transform: translateY(-6px) scale(1.01);
    border-color: var(--c);
    box-shadow: 0 20px 56px color-mix(in srgb, var(--c) 28%, transparent);
}}
.nexus-card:hover::after {{ opacity: {0.06 if D else 0.04}; }}
.card-link {{ position: absolute; inset: 0; z-index: 30; border-radius: 18px; }}

.card-icon-wrap {{
    width: 50px; height: 50px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    background: color-mix(in srgb, var(--c) 14%, transparent);
    border: 1px solid color-mix(in srgb, var(--c) 22%, transparent);
    transition: transform 0.26s cubic-bezier(0.34,1.56,0.64,1);
}}
.nexus-card:hover .card-icon-wrap {{ transform: scale(1.1) translateY(-1px); }}
.card-icon {{
    width: 25px; height: 25px; display: block;
    background-color: var(--c);
    -webkit-mask: var(--icon) center / contain no-repeat;
            mask: var(--icon) center / contain no-repeat;
}}
.card-name {{ font-size: 14.5px; font-weight: 700; color: {TEXT}; line-height: 1.3; }}
.card-cat {{
    font-size: 9px; font-weight: 700; letter-spacing: 1.8px;
    text-transform: uppercase; color: var(--c); opacity: 0.9;
}}

.nx-footer {{
    text-align: center; padding: 40px 0 20px;
    font-size: 11px; color: {FOOTER_C}; letter-spacing: 1px;
}}
.nx-footer b {{ color: {SECTION_C}; }}

@media (prefers-reduced-motion: reduce) {{
    .aurora b, .nexus-card, .stats-bar, .section-label {{ animation: none !important; }}
    .nexus-card:hover::before {{ animation: none !important; }}
}}
</style>
<div class="aurora"><b class="b1"></b><b class="b2"></b><b class="b3"></b></div>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
components.html(f"""
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
    background:transparent;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    height:280px;overflow:hidden;
}}
.grid{{
    position:fixed;inset:0;
    background-image:linear-gradient({GRID_CLR} 1px,transparent 1px),
                     linear-gradient(90deg,{GRID_CLR} 1px,transparent 1px);
    background-size:52px 52px;animation:drift 28s linear infinite;pointer-events:none;
    -webkit-mask-image:linear-gradient(to bottom,#000 30%,transparent 92%);
    mask-image:linear-gradient(to bottom,#000 30%,transparent 92%);
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
# Line icons (Lucide-style) rendered as accent-coloured CSS masks — no emojis.
_ICON_PATHS = {
    "file":      "<path d='M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><path d='M14 2v6h6'/><path d='M16 13H8'/><path d='M16 17H8'/><path d='M10 9H8'/>",
    "pulse":     "<path d='M22 12h-4l-3 9L9 3l-3 9H2'/>",
    "clipboard": "<rect width='8' height='4' x='8' y='2' rx='1' ry='1'/><path d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/><path d='m9 14 2 2 4-4'/>",
    "search":    "<circle cx='11' cy='11' r='8'/><path d='m21 21-4.3-4.3'/>",
    "briefcase": "<rect width='20' height='14' x='2' y='7' rx='2'/><path d='M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16'/>",
    "clapper":   "<path d='M20.2 6 3 11l-.9-2.4c-.3-1.1.3-2.2 1.3-2.5l13.5-4c1.1-.3 2.2.3 2.5 1.3Z'/><path d='m6.2 5.3 3.1 3.9'/><path d='m12.4 3.4 3.1 4'/><path d='M3 11h18v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z'/>",
    "chart":     "<path d='M3 3v18h18'/><path d='M18 17V9'/><path d='M13 17V5'/><path d='M8 17v-3'/>",
    "tag":       "<path d='M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z'/><circle cx='7.5' cy='7.5' r='1.5'/>",
    "target":    "<circle cx='12' cy='12' r='10'/><circle cx='12' cy='12' r='6'/><circle cx='12' cy='12' r='2'/>",
    "shield":    "<path d='M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z'/><path d='m9 12 2 2 4-4'/>",
}

def _icon_uri(key):
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
        + _ICON_PATHS[key] + "</svg>"
    )
    return "data:image/svg+xml," + quote(svg)

# (icon, name, page, accent colour, category)
AGENTS = [
    ("file",      "Invoice Processing",       "Invoice_Processing",       "#f59e0b", "Finance"),
    ("pulse",     "Shift Replacement",        "Shift_Replacement",        "#ef4444", "Healthcare"),
    ("clipboard", "Work Permit Validation",   "Work_Permit_Validation",   "#8b5cf6", "HR & Legal"),
    ("search",    "CV Fraud Detection",       "CV_Fraud_Detection",       "#6366f1", "HR Security"),
    ("briefcase", "Interview Support",        "Interview_Support",        "#06b6d4", "Recruiting"),
    ("clapper",   "Marketing Content",        "Marketing_Content",        "#ec4899", "Marketing"),
    ("chart",     "Customer Analytics",       "Customer_Analytics",       "#10b981", "Analytics"),
    ("tag",       "Dynamic Pricing",          "Dynamic_Pricing",          "#f59e0b", "Pricing"),
    ("target",    "Competitive Gap Analysis", "Competitive_Gap_Analysis", "#a855f7", "Strategy"),
    ("shield",    "Secure Email Agent",       "Secure_Email_Agent",       "#64748b", "Security"),
]

def _card(icon, name, page, color, cat, delay=0.0):
    return f"""
<div class="nexus-card" style="--c:{color}; --icon:url('{_icon_uri(icon)}'); animation-delay:{delay:.2f}s;">
  <a href="/{page}" target="_self" class="card-link" aria-label="{name}"></a>
  <div class="card-icon-wrap"><span class="card-icon"></span></div>
  <div class="card-name">{name}</div>
  <div class="card-cat">{cat}</div>
</div>"""

cards_html = "".join(_card(*a, delay=0.35 + i * 0.05) for i, a in enumerate(AGENTS))
st.markdown(f'<div class="card-grid">{cards_html}</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="nx-footer"><b>NexusOps AI</b> &nbsp;&middot;&nbsp; Enterprise Operations Suite</div>', unsafe_allow_html=True)
