"""
shared/theme.py  —  Call apply_theme() once per page, right after st.set_page_config().
Injects global CSS and renders the consistent sidebar (logo, toggle, navigation).
"""
import streamlit as st

# ── Navigation manifest ────────────────────────────────────────────────────────
_NAV = [
    ("pages/1_Invoice_Processing.py",      "🧾", "Invoice Processing"),
    ("pages/2_Shift_Replacement.py",        "🏥", "Shift Replacement"),
    ("pages/3_Work_Permit_Validation.py",   "📋", "Work Permit Validation"),
    ("pages/4_CV_Fraud_Detection.py",       "🔍", "CV Fraud Detection"),
    ("pages/5_Interview_Support.py",        "💼", "Interview Support"),
    ("pages/6_Marketing_Content.py",        "🎬", "Marketing Content"),
    ("pages/7_Customer_Analytics.py",       "📊", "Customer Analytics"),
    ("pages/8_Dynamic_Pricing.py",          "💰", "Dynamic Pricing"),
    ("pages/9_Competitive_Gap_Analysis.py", "🔭", "Competitive Gap Analysis"),
    ("pages/10_Secure_Email_Agent.py",      "🛡️", "Secure Email Agent"),
]

_GROUPS = [
    ("HR & Operations", _NAV[:5]),
    ("Dr. Theiss",      _NAV[5:9]),
    ("Security",        _NAV[9:]),
]


def apply_theme(sidebar: bool = True):
    """Inject theme CSS, floating toggle, and (optionally) the sidebar.

    Call after st.set_page_config(). Pass sidebar=False on pages that should
    have no drawer (e.g. the homepage) — this hides it via CSS injected up
    front AND skips rendering its contents, so it never flashes on reload.
    """
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    D = st.session_state.theme == "dark"
    _inject_css(D, sidebar)
    _render_toggle(D)
    if sidebar:
        _render_sidebar(D)


def _render_toggle(D: bool):
    """Floating dark/light toggle, pinned top-right on every page."""
    tog = st.container(key="nx_theme_toggle")
    with tog:
        if st.button(
            "☀️" if D else "🌙",
            key="nx_theme_btn",
            help="Switch to light mode" if D else "Switch to dark mode",
        ):
            st.session_state.theme = "light" if D else "dark"
            st.rerun()


def _inject_css(D: bool, sidebar: bool = True):
    BG      = "#0d0f17"  if D else "#f8fafc"
    BG_SIDE = "#11131d"  if D else "#f1f5f9"
    SEP     = "rgba(255,255,255,0.07)" if D else "rgba(0,0,0,0.08)"
    NAV_LNK = "#cbd5e1"  if D else "#334155"
    NAV_HOV = "rgba(99,102,241,0.1)"   if D else "rgba(99,102,241,0.08)"
    TOG_BG  = "rgba(22,22,34,0.85)"    if D else "rgba(255,255,255,0.92)"
    TOG_BD  = "rgba(255,255,255,0.12)" if D else "rgba(0,0,0,0.12)"

    # Hide the drawer entirely when this page wants no sidebar.
    HIDE_SIDEBAR = (
        'section[data-testid="stSidebar"], [data-testid="collapsedControl"] '
        '{ display: none !important; }'
    ) if not sidebar else ""

    st.markdown(f"""
<style>
{HIDE_SIDEBAR}
/* ── Background ── */
html, body, [data-testid="stAppViewContainer"], .stApp {{
    background: {BG} !important;
}}
[data-testid="stHeader"] {{
    background: transparent !important;
    box-shadow: none !important;
    /* Let clicks fall through the empty header to the floating theme toggle
       beneath it; the header's own buttons are re-enabled just below. */
    pointer-events: none !important;
}}
[data-testid="stHeader"] button,
[data-testid="stHeader"] a,
[data-testid="stHeader"] [role="button"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {{ pointer-events: auto !important; }}
#MainMenu, footer {{ visibility: hidden !important; }}
[data-testid="stAppDeployButton"], .stDeployButton {{ display: none !important; }}

/* ── Sidebar shell ── */
section[data-testid="stSidebar"] > div:first-child {{
    background: {BG_SIDE} !important;
    border-right: 1px solid {SEP} !important;
    padding: 0 !important;
}}
[data-testid="stSidebarNav"] {{ display: none !important; }}

/* ── Sidebar page links ── */
[data-testid="stPageLink"] {{ margin: 1px 0 !important; }}
[data-testid="stPageLink"] a {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 8px 16px !important;
    border-radius: 9px !important;
    text-decoration: none !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: {NAV_LNK} !important;
    background: transparent !important;
    border: none !important;
    transition: background 0.15s ease, color 0.15s ease !important;
}}
[data-testid="stPageLink"] a:hover {{
    background: {NAV_HOV} !important;
    color: #818cf8 !important;
}}

/* ── Floating dark/light toggle (top-right, every page) ── */
.st-key-nx_theme_toggle {{
    position: fixed !important;
    top: 11px !important;
    right: 16px !important;
    z-index: 1000 !important;
    width: auto !important;
    min-width: 0 !important;
}}
.st-key-nx_theme_toggle div[data-testid="stButton"] button {{
    font-size: 16px !important;
    line-height: 1 !important;
    padding: 0 !important;
    width: 40px !important;
    height: 40px !important;
    min-height: 40px !important;
    border-radius: 50% !important;
    background: {TOG_BG} !important;
    border: 1px solid {TOG_BD} !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.28) !important;
    backdrop-filter: blur(8px) !important;
    transition: transform 0.15s ease, border-color 0.15s ease !important;
}}
.st-key-nx_theme_toggle div[data-testid="stButton"] button:hover {{
    transform: scale(1.08) !important;
    border-color: #6366f1 !important;
}}
</style>
""", unsafe_allow_html=True)


def _render_sidebar(D: bool):
    TEXT   = "#f1f5f9" if D else "#0f172a"
    MUTED  = "rgba(255,255,255,0.28)" if D else "rgba(0,0,0,0.38)"
    SEP    = "rgba(255,255,255,0.07)" if D else "rgba(0,0,0,0.08)"
    CAT    = "rgba(255,255,255,0.22)" if D else "rgba(0,0,0,0.28)"

    with st.sidebar:
        # Logo / home link
        st.markdown(f"""
<div style="padding:24px 20px 20px;">
  <a href="/" target="_self" style="text-decoration:none;">
    <div style="font-size:22px;font-weight:900;letter-spacing:-0.5px;
                color:{TEXT};line-height:1;">
      <span style="color:#6366f1;">⚡</span>
      NexusOps <span style="color:#818cf8;">AI</span>
    </div>
    <div style="font-size:9.5px;color:{MUTED};letter-spacing:2.5px;
                text-transform:uppercase;margin-top:5px;">
      Enterprise Operations Suite
    </div>
  </a>
</div>""", unsafe_allow_html=True)

        st.markdown(
            f'<hr style="border:none;border-top:1px solid {SEP};margin:4px 0 10px;">',
            unsafe_allow_html=True,
        )

        # Grouped navigation
        for group_label, pages in _GROUPS:
            st.markdown(
                f'<div style="padding:6px 16px 3px;font-size:9.5px;font-weight:700;'
                f'letter-spacing:2px;text-transform:uppercase;color:{CAT};">'
                f'{group_label}</div>',
                unsafe_allow_html=True,
            )
            for path, icon, label in pages:
                st.page_link(path, label=label, icon=icon)
            st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
