import streamlit as st
from pathlib import Path
from agents.marketing_agent import create_content, create_content_with_image
from shared.llm import ask_with_file

st.set_page_config(page_title="Marketing Content — Dr. Theiss", page_icon="🎬")
st.title("🎬 Marketing Content / Filmmaker Agent")
st.caption("Client: Dr. Theiss Naturwaren GmbH (Homburg) — Studio-quality reel concepts with TikTok/Instagram safe zones")

DR_THEISS_DATA = Path("samples/dr_theiss_data.pdf")

platform = st.selectbox("Target Platform", ["TikTok", "Instagram Reels", "Both"])
style = st.text_input("Style / Tone", placeholder="e.g. authentic, documentary, fast-paced, cinematic")


def _phone_html(title, border_color, top_pct, bottom_pct):
    h, w = 284, 160
    top_px = int(h * top_pct / 100)
    bottom_px = int(h * bottom_pct / 100)
    side_px = int(w * 8 / 100)      # 8% each side

    return f"""
<div style="text-align:center; display:inline-block;">
  <div style="font-weight:700; font-size:13px; margin-bottom:10px; color:#e5e7eb;">{title}</div>
  <div style="width:{w}px; height:{h}px; border:3px solid {border_color}; border-radius:22px;
              overflow:hidden; position:relative; background:#111827;
              box-shadow:0 8px 20px rgba(0,0,0,0.6);">

    <!-- notch -->
    <div style="position:absolute; top:8px; left:50%; transform:translateX(-50%);
                width:38px; height:5px; background:#374151; border-radius:3px; z-index:10;"></div>

    <!-- top danger zone -->
    <div style="position:absolute; top:0; left:0; right:0; height:{top_px}px;
                background:rgba(220,38,38,0.88);
                display:flex; align-items:center; justify-content:center;">
      <span style="font-size:8px; color:#fff; font-weight:800; letter-spacing:0.6px; text-transform:uppercase;">
        ⚠ UI Overlay &nbsp;·&nbsp; {top_pct}%
      </span>
    </div>

    <!-- bottom danger zone -->
    <div style="position:absolute; bottom:0; left:0; right:0; height:{bottom_px}px;
                background:rgba(220,38,38,0.88);
                display:flex; align-items:center; justify-content:center;">
      <span style="font-size:8px; color:#fff; font-weight:800; letter-spacing:0.6px; text-transform:uppercase;">
        ⚠ UI Overlay &nbsp;·&nbsp; {bottom_pct}%
      </span>
    </div>

    <!-- left margin (8%) -->
    <div style="position:absolute; top:{top_px}px; bottom:{bottom_px}px; left:0; width:{side_px}px;
                background:rgba(234,179,8,0.40);"></div>
    <!-- right margin (8%) -->
    <div style="position:absolute; top:{top_px}px; bottom:{bottom_px}px; right:0; width:{side_px}px;
                background:rgba(234,179,8,0.40);"></div>

    <!-- safe zone -->
    <div style="position:absolute; top:{top_px}px; bottom:{bottom_px}px;
                left:{side_px}px; right:{side_px}px;
                background:rgba(22,163,74,0.18);
                border:2px dashed rgba(34,197,94,0.75);
                display:flex; flex-direction:column;
                align-items:center; justify-content:center; gap:6px;">
      <span style="font-size:22px;">✅</span>
      <span style="font-size:9.5px; color:#86efac; font-weight:700;
                   text-align:center; line-height:1.5;">
        SAFE ZONE<br>Place text &amp; logos here
      </span>
    </div>
  </div>

  <!-- legend -->
  <div style="font-size:10px; color:#9ca3af; margin-top:10px; line-height:1.7;">
    🔴 Top {top_pct}% &nbsp;|&nbsp; Bottom {bottom_pct}%<br>
    🟡 Sides 8% each
  </div>
</div>"""


def _show_safe_zones(plat="Both"):
    st.divider()
    st.markdown("#### 📐 Safe Zone Reference")

    parts = []
    if plat in ("TikTok", "Both"):
        parts.append(_phone_html("TikTok", "#fe2c55", 14, 20))
    if plat in ("Instagram Reels", "Both"):
        parts.append(_phone_html("Instagram Reels", "#833ab4", 14, 25))

    gap = "64px" if len(parts) > 1 else "0"
    html = f"""
<div style="display:flex; gap:{gap}; justify-content:center; align-items:flex-start;
            padding:28px 24px; margin:8px 0;
            background:#1f2937; border-radius:14px;">
  {''.join(parts)}
</div>"""
    st.markdown(html, unsafe_allow_html=True)


# ── Always-visible reference above the tabs ───────────────────────────────────
with st.expander("📐 View Safe Zone Reference", expanded=True):
    _show_safe_zones(platform)

st.divider()

tab_sample, tab_text, tab_image = st.tabs([
    "📂 Dr. Theiss Data Pack", "✏️ Describe Product", "🖼️ Upload Image"
])

with tab_sample:
    if DR_THEISS_DATA.exists():
        st.info("Uses the official Dr. Theiss Allgäuer product data pack to generate accurate reel concepts.")
        campaign = st.text_input(
            "Campaign focus or product name",
            placeholder="e.g. Vitamin C Brausetabletten, winter immunity"
        )
        if st.button("Generate from Data Pack", type="primary", key="theiss_sample_btn"):
            file_bytes = DR_THEISS_DATA.read_bytes()
            notes = (
                f"Platform: {platform}. "
                f"Style: {style or 'authentic, modern'}. "
                f"Focus: {campaign or 'flagship products'}."
            )
            with st.spinner("Reading Dr. Theiss data pack and creating reel concept..."):
                result = create_content_with_image(file_bytes, "application/pdf", platform, notes)
            st.markdown("### Your Reel Concept")
            st.markdown(result)
            _show_safe_zones(platform)
    else:
        st.info("Dr. Theiss data pack not found in samples/. Use another tab.")

with tab_text:
    product_desc = st.text_area(
        "Product / campaign description",
        placeholder=(
            "Dr. Theiss Vitamin C 1000mg effervescent tablets. "
            "Target: 25–45 professionals, winter immunity boost."
        ),
        height=150,
    )
    if st.button("Generate Reel Concept", type="primary", key="text_marketing_btn") and product_desc:
        with st.spinner("Writing your reel concept..."):
            result = create_content(product_desc, platform, style)
        st.markdown("### Your Reel Concept")
        st.markdown(result)
        _show_safe_zones(platform)

with tab_image:
    uploaded = st.file_uploader("Upload product image", type=["png", "jpg", "jpeg"])
    img_notes = st.text_input(
        "Extra notes for the concept",
        placeholder="Focus on morning routine context"
    )
    if uploaded and st.button("Generate from Image", type="primary", key="image_marketing_btn"):
        st.image(uploaded, use_container_width=True)
        mime = f"image/{uploaded.name.rsplit('.', 1)[-1]}"
        with st.spinner("Creating reel concept from image..."):
            result = create_content_with_image(uploaded.read(), mime, platform, img_notes)
        st.markdown("### Your Reel Concept")
        st.markdown(result)
        _show_safe_zones(platform)
