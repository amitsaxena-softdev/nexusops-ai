import streamlit as st
from agents.marketing_agent import create_content, DR_THEISS_CATALOG

st.set_page_config(page_title="Marketing Content — Dr. Theiss", page_icon="🎬")
st.title("🎬 Marketing Content / Filmmaker Agent")
st.caption("Client: Dr. Theiss Naturwaren GmbH (Homburg) — Studio-quality reel storyboards with TikTok/Instagram safe zones")


# ── Safe zone phone mockup ─────────────────────────────────────────────────────
def _phone_html(title, border_color, top_pct, bottom_pct):
    h, w = 284, 160
    top_px    = int(h * top_pct    / 100)
    bottom_px = int(h * bottom_pct / 100)
    side_px   = int(w * 8          / 100)
    return f"""
<div style="text-align:center; display:inline-block;">
  <div style="font-weight:700; font-size:13px; margin-bottom:10px; color:#e5e7eb;">{title}</div>
  <div style="width:{w}px; height:{h}px; border:3px solid {border_color}; border-radius:22px;
              overflow:hidden; position:relative; background:#111827; box-shadow:0 8px 20px rgba(0,0,0,0.6);">
    <div style="position:absolute; top:8px; left:50%; transform:translateX(-50%);
                width:38px; height:5px; background:#374151; border-radius:3px; z-index:10;"></div>
    <div style="position:absolute; top:0; left:0; right:0; height:{top_px}px;
                background:rgba(220,38,38,0.88); display:flex; align-items:center; justify-content:center;">
      <span style="font-size:8px; color:#fff; font-weight:800; text-transform:uppercase;">⚠ UI Overlay · {top_pct}%</span>
    </div>
    <div style="position:absolute; bottom:0; left:0; right:0; height:{bottom_px}px;
                background:rgba(220,38,38,0.88); display:flex; align-items:center; justify-content:center;">
      <span style="font-size:8px; color:#fff; font-weight:800; text-transform:uppercase;">⚠ UI Overlay · {bottom_pct}%</span>
    </div>
    <div style="position:absolute; top:{top_px}px; bottom:{bottom_px}px; left:0; width:{side_px}px;
                background:rgba(234,179,8,0.40);"></div>
    <div style="position:absolute; top:{top_px}px; bottom:{bottom_px}px; right:0; width:{side_px}px;
                background:rgba(234,179,8,0.40);"></div>
    <div style="position:absolute; top:{top_px}px; bottom:{bottom_px}px;
                left:{side_px}px; right:{side_px}px;
                background:rgba(22,163,74,0.18); border:2px dashed rgba(34,197,94,0.75);
                display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px;">
      <span style="font-size:22px;">✅</span>
      <span style="font-size:9.5px; color:#86efac; font-weight:700; text-align:center; line-height:1.5;">
        SAFE ZONE<br>Place text &amp; logos here
      </span>
    </div>
  </div>
  <div style="font-size:10px; color:#9ca3af; margin-top:10px; line-height:1.7;">
    🔴 Top {top_pct}% | Bottom {bottom_pct}%<br>🟡 Sides 8% each
  </div>
</div>"""


def _show_safe_zones(plat):
    parts = []
    if plat in ("TikTok", "Both"):
        parts.append(_phone_html("TikTok", "#fe2c55", 14, 20))
    if plat in ("Instagram Reels", "Both"):
        parts.append(_phone_html("Instagram Reels", "#833ab4", 14, 25))
    gap = "64px" if len(parts) > 1 else "0"
    st.markdown(f"""
<div style="display:flex; gap:{gap}; justify-content:center; align-items:flex-start;
            padding:28px 24px; background:#1f2937; border-radius:14px;">
  {''.join(parts)}
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FORM
# ══════════════════════════════════════════════════════════════════════════════
product_key = st.selectbox(
    "Product",
    list(DR_THEISS_CATALOG.keys()),
    help="Select a Dr. Theiss product — campaign brief is pre-loaded from the data pack",
)

info = DR_THEISS_CATALOG[product_key]
if product_key != "Custom product / campaign":
    with st.expander("Product brief", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**Line:** {info['line']}\n\n**Price:** {info['price']}")
        c2.markdown(f"**Target:** {info['target']}\n\n**Peak:** {info['peak_season']}")
        c3.markdown(f"**Ingredient:** {info['hero_ingredient']}\n\n**USP:** {info['usp']}")

custom_desc = ""
if product_key == "Custom product / campaign":
    custom_desc = st.text_area(
        "Product / campaign description",
        placeholder="Describe the product, target audience, and campaign goal…",
        height=120,
    )

col_l, col_r = st.columns(2)
with col_l:
    platform = st.selectbox("Target platform", ["TikTok", "Instagram Reels", "Both"])
with col_r:
    style = st.text_input("Style / tone", placeholder="e.g. ASMR, cinematic, fast-paced, documentary")

image_file = st.file_uploader(
    "Product image (optional — enriches visual direction)",
    type=["png", "jpg", "jpeg"],
)

with st.expander("📐 Safe zone reference"):
    _show_safe_zones(platform)

st.divider()

disabled = product_key == "Custom product / campaign" and not custom_desc.strip()
if st.button("🎬 Generate Production Brief", type="primary", disabled=disabled):
    image_bytes, image_mime = None, None
    if image_file:
        image_bytes = image_file.read()
        image_mime  = f"image/{image_file.name.rsplit('.', 1)[-1].lower()}"

    with st.spinner("Writing production brief…"):
        try:
            brief = create_content(
                product_key = product_key,
                platform    = platform,
                style       = style,
                custom_desc = custom_desc,
                image_bytes = image_bytes,
                image_mime  = image_mime,
            )
        except Exception as e:
            st.error(f"Failed to generate brief: {e}")
            st.stop()

    st.markdown("### 🎬 Production Brief")
    st.caption("Paste this directly into Sora, Runway, Kling, Pika, or any AI video tool.")
    st.code(brief, language="markdown")

    st.divider()
    st.markdown("#### 📐 Safe Zone Reference")
    _show_safe_zones(platform)
