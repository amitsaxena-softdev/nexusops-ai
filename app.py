from urllib.parse import quote

import streamlit as st
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
BG          = "#0d0f17"  if D else "#e9edf6"
CARD_BG     = "rgba(255,255,255,0.025)" if D else "#ffffff"
CARD_BD     = "rgba(255,255,255,0.06)"  if D else "rgba(15,23,42,0.07)"
CARD_SHADOW = ("0 4px 16px rgba(0,0,0,0.25)" if D
               else "0 1px 2px rgba(15,23,42,0.05), 0 10px 26px rgba(15,23,42,0.07)")
TEXT      = "#f1f5f9"  if D else "#0f172a"
MUTED     = "rgba(255,255,255,0.28)"  if D else "rgba(15,23,42,0.42)"
DESC      = "rgba(255,255,255,0.3)"   if D else "rgba(15,23,42,0.45)"
SEP       = "rgba(255,255,255,0.07)"  if D else "rgba(15,23,42,0.1)"
SECTION_C = "rgba(255,255,255,0.18)"  if D else "rgba(15,23,42,0.3)"
FOOTER_C  = "rgba(255,255,255,0.12)"  if D else "rgba(15,23,42,0.25)"
GRID_CLR  = "rgba(99,102,241,0.045)"  if D else "rgba(99,102,241,0.06)"
GLOW_CLR  = "rgba(99,102,241,0.13)"   if D else "rgba(99,102,241,0.1)"

# ── Global theme (no sidebar on the homepage) ──────────────────────────────────
apply_theme(sidebar=False)

# ── Landing-page-specific CSS (stats bar, section label, cards, footer) ────────
st.markdown(f"""
<style>
.block-container {{
    padding-top: 0 !important;
    padding-bottom: 1.25rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1260px !important;
    margin: 0 auto !important;
}}
[data-testid="column"] {{ padding: 5px !important; }}

/* The whole homepage body is one flex column that fills the viewport and
   distributes its sections evenly; on short/mobile screens it just scrolls. */
.block-container [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
.nx-page {{
    display: flex; flex-direction: column;
    min-height: calc(100vh - 1.5rem);
    justify-content: space-between;
}}

/* Hero iframe blends into the page (no opaque black rectangle) and never
   intercepts clicks meant for the floating toggle above it. */
[data-testid="stIFrame"], .stApp iframe {{
    background: transparent !important;
    pointer-events: none !important;
}}

/* ── Aurora background (drifting blurred colour blobs) ── */
.aurora {{ position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none; }}
.aurora b {{
    position: absolute; display: block; border-radius: 50%;
    filter: blur(100px); opacity: {0.38 if D else 0.30};
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
    padding: 0;
    animation: fadeUp 0.6s ease 0.15s backwards;
}}
.stat {{ text-align: center; padding: 0 56px; }}
.stat-num {{
    font-size: 56px; font-weight: 900; line-height: 1; letter-spacing: -2px;
    background: linear-gradient(135deg, #6366f1, #a855f7 50%, #06b6d4);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.stat-label {{
    font-size: 11px; color: {MUTED}; font-weight: 600;
    letter-spacing: 2.5px; text-transform: uppercase; margin-top: 10px;
}}
.stat-sep {{ width: 1px; height: 54px;
    background: linear-gradient(to bottom, transparent, {SEP}, transparent); }}

.section-label {{ text-align: center; margin: 0; animation: fadeUp 0.6s ease 0.28s backwards; }}
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
}}
@media (max-width: 1100px) {{ .card-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
@media (max-width: 720px)  {{ .card-grid {{ grid-template-columns: repeat(2, 1fr); }} }}

.nexus-card {{
    position: relative; background: {CARD_BG};
    border: 1px solid {CARD_BD}; border-radius: 18px;
    box-shadow: {CARD_SHADOW};
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
    text-align: center; padding: 0;
    font-size: 11px; color: {FOOTER_C}; letter-spacing: 1px;
}}
.nx-footer b {{ color: {SECTION_C}; }}

/* ── Hero (pure CSS, part of the page — blends with no iframe rectangle) ── */
.nx-hero {{ position: relative; text-align: center; padding: 16px 0 0; }}
.nx-hero::before {{
    content: ""; position: absolute; top: 46%; left: 50%;
    width: 640px; max-width: 90%; height: 230px; transform: translate(-50%,-50%);
    background: radial-gradient(ellipse at center, {GLOW_CLR} 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}}
.nx-title {{
    position: relative; z-index: 1;
    font-size: 74px; font-weight: 900; letter-spacing: -3px; line-height: 1;
}}
.nx-ltr {{
    display: inline-block; max-width: 0; opacity: 0; overflow: hidden;
    vertical-align: bottom; padding-bottom: 0.16em; margin-bottom: -0.16em;
    animation: typeIn 0.05s linear var(--d) forwards;
}}
@keyframes typeIn {{ to {{ max-width: 1.3em; opacity: 1; }} }}
.nx-ai {{
    background: linear-gradient(130deg,#6366f1,#a855f7 45%,#06b6d4);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}}
.nx-caret {{
    display: inline-block; width: 5px; height: 0.82em;
    background: linear-gradient(180deg,#6366f1,#06b6d4); border-radius: 3px;
    vertical-align: baseline; margin-left: 7px; opacity: 0;
    animation: nxBlink 0.85s step-end var(--d) infinite;
}}
@keyframes nxBlink {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
.nx-sub {{
    position: relative; z-index: 1;
    font-size: 16px; font-weight: 500; letter-spacing: 0.4px;
    color: {"rgba(255,255,255,0.46)" if D else "rgba(15,23,42,0.52)"};
    margin-top: 15px;
    animation: fadeUp 0.7s ease var(--subd) backwards;
}}

@media (prefers-reduced-motion: reduce) {{
    .aurora b, .nexus-card, .stats-bar, .section-label,
    .nx-sub {{ animation: none !important; }}
    .nx-ltr {{ animation: none !important; max-width: none !important; opacity: 1 !important; }}
    .nx-caret {{ animation: nxBlink 0.85s step-end infinite !important; opacity: 1; }}
    .nexus-card:hover::before {{ animation: none !important; }}
}}
</style>
<div class="aurora"><b class="b1"></b><b class="b2"></b><b class="b3"></b></div>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
def _hero_html():
    nexus_c = "#f1f5f9" if D else "#0f172a"
    segs = [("Nexus", f"color:{nexus_c}"), ("Ops", "color:#818cf8"),
            (" ", ""), ("AI", "GRAD")]
    spans, d = [], 0.30
    for text, style in segs:
        for ch in text:
            cls   = "nx-ltr nx-ai" if style == "GRAD" else "nx-ltr"
            extra = "" if style in ("GRAD", "") else f";{style}"
            disp  = "&nbsp;" if ch == " " else ch
            spans.append(f'<span class="{cls}" style="--d:{d:.2f}s{extra}">{disp}</span>')
            d += 0.08
    caret_d = d + 0.02
    sub_d   = caret_d + 0.35
    spans.append(f'<span class="nx-caret" style="--d:{caret_d:.2f}s"></span>')
    return (f'<div class="nx-hero"><div class="nx-title">{"".join(spans)}</div>'
            f'<div class="nx-sub" style="--subd:{sub_d:.2f}s">'
            f'Specialized AI agents for every enterprise operation</div></div>')

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

# ── Full page (one flex column that fills the viewport) ─────────────────────────
st.markdown(f"""
<div class="nx-page">
  {_hero_html()}
  <div class="stats-bar">
    <div class="stat"><div class="stat-num">10</div><div class="stat-label">AI Agents</div></div>
    <div class="stat-sep"></div>
    <div class="stat"><div class="stat-num">6</div><div class="stat-label">Industries</div></div>
    <div class="stat-sep"></div>
    <div class="stat"><div class="stat-num">5</div><div class="stat-label">Clients</div></div>
  </div>
  <div class="section-label"><span>Choose Your Agent</span></div>
  <div class="card-grid">{cards_html}</div>
  <div class="nx-footer"><b>NexusOps AI</b> &nbsp;&middot;&nbsp; Enterprise Operations Suite</div>
</div>
""", unsafe_allow_html=True)
