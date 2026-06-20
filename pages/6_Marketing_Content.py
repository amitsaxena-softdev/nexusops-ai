import streamlit as st
from pathlib import Path
from agents.marketing_agent import create_content, create_content_with_image
from shared.llm import ask_with_file

st.set_page_config(page_title="Marketing Content — Dr. Theiss", page_icon="🎬")
st.title("🎬 Marketing Content / Filmmaker Agent")
st.caption("Client: Dr. Theiss Naturwaren GmbH (Homburg) — Studio-quality reel concepts with TikTok/Instagram safe zones")

DR_THEISS_DATA = Path("samples/dr_theiss_data.pdf")


def _show_safe_zones():
    st.divider()
    st.info(
        "**TikTok safe zone:** Text between 14% from top and 20% from bottom. Left/right margin 8%.\n\n"
        "**Instagram Reels safe zone:** Text between 14% from top and 25% from bottom. Left/right margin 8%."
    )


platform = st.selectbox("Target Platform", ["TikTok", "Instagram Reels", "Both"])
style = st.text_input("Style / Tone", placeholder="e.g. authentic, documentary, fast-paced, cinematic")

tab_sample, tab_text, tab_image = st.tabs(["📂 Dr. Theiss Data Pack", "✏️ Describe Product", "🖼️ Upload Image"])

with tab_sample:
    if DR_THEISS_DATA.exists():
        st.info("Uses the official Dr. Theiss Allgäuer product data pack to generate accurate reel concepts.")
        campaign = st.text_input("Campaign focus or product name", placeholder="e.g. Vitamin C Brausetabletten, winter immunity")
        if st.button("Generate from Data Pack", type="primary", key="theiss_sample_btn"):
            file_bytes = DR_THEISS_DATA.read_bytes()
            notes = f"Platform: {platform}. Style: {style or 'authentic, modern'}. Focus: {campaign or 'flagship products'}."
            with st.spinner("Reading Dr. Theiss data pack and creating reel concept..."):
                result = create_content_with_image(file_bytes, "application/pdf", platform, notes)
            st.markdown("### Your Reel Concept")
            st.markdown(result)
            _show_safe_zones()
    else:
        st.info("Dr. Theiss data pack not found in samples/. Use another tab.")

with tab_text:
    product_desc = st.text_area(
        "Product / campaign description",
        placeholder="Dr. Theiss Vitamin C 1000mg effervescent tablets. Target: 25–45 professionals, winter immunity boost.",
        height=150,
    )
    if st.button("Generate Reel Concept", type="primary", key="text_marketing_btn") and product_desc:
        with st.spinner("Writing your reel concept..."):
            result = create_content(product_desc, platform, style)
        st.markdown("### Your Reel Concept")
        st.markdown(result)
        _show_safe_zones()

with tab_image:
    uploaded = st.file_uploader("Upload product image", type=["png", "jpg", "jpeg"])
    notes = st.text_input("Extra notes for the concept", placeholder="Focus on morning routine context")
    if uploaded and st.button("Generate from Image", type="primary", key="image_marketing_btn"):
        st.image(uploaded, use_container_width=True)
        mime = f"image/{uploaded.name.rsplit('.', 1)[-1]}"
        with st.spinner("Creating reel concept from image..."):
            result = create_content_with_image(uploaded.read(), mime, platform, notes)
        st.markdown("### Your Reel Concept")
        st.markdown(result)
        _show_safe_zones()
