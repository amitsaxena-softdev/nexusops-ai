import streamlit as st
from pathlib import Path
from agents.work_permit_agent import validate_permit, validate_permit_text
from shared.file_utils import read_sample

st.set_page_config(page_title="Work Permit Validation — Leistenschneider", page_icon="📋")
st.title("📋 Work Permit Validation Agent")
st.caption("Client: Leistenschneider Personaldienstleistungen GmbH (Saarbrücken) — Instant permit validation with confidence score")

PERMITS_DIR = Path("samples/work_permits")
SAMPLE_PERMITS = sorted(PERMITS_DIR.iterdir()) if PERMITS_DIR.exists() else []


def show_result(result: str):
    st.markdown("### Validation Result")
    if "VALID WORK PERMIT: YES" in result:
        st.success("✅ Valid work permit detected")
    elif "VALID WORK PERMIT: NO" in result:
        st.error("❌ Invalid or expired document")
    else:
        st.warning("⚠️ Manual review required")
    st.code(result, language="markdown")


tab_sample, tab_upload, tab_text = st.tabs(["📂 Load Sample", "⬆️ Upload Document", "✏️ Manual Entry"])

with tab_sample:
    if not SAMPLE_PERMITS:
        st.info("No sample permits found in samples/work_permits/")
    else:
        permit_names = {f.name: f for f in SAMPLE_PERMITS}
        chosen = st.selectbox(
            "Pick a sample permit", list(permit_names.keys()),
            help="valid_01/02 should pass; invalid_01/02 should fail"
        )
        selected = permit_names[chosen]
        if st.button("Validate This Permit", type="primary", key="sample_permit_btn"):
            file_bytes = read_sample(selected)
            with st.spinner("Validating..."):
                result = validate_permit(file_bytes, "application/pdf")
            show_result(result)

with tab_upload:
    uploaded = st.file_uploader(
        "Upload work permit / Aufenthaltstitel (PDF or image)",
        type=["pdf", "png", "jpg", "jpeg"],
    )
    if uploaded:
        if uploaded.name.lower().endswith((".png", ".jpg", ".jpeg")):
            st.image(uploaded, caption="Uploaded document", use_container_width=True)
        mime = "application/pdf" if uploaded.name.endswith(".pdf") else f"image/{uploaded.name.rsplit('.', 1)[-1]}"
        if st.button("Validate Document", type="primary", key="upload_permit_btn"):
            with st.spinner("Validating work permit..."):
                result = validate_permit(uploaded.read(), mime)
            show_result(result)

with tab_text:
    text = st.text_area(
        "Describe the document or paste extracted text",
        placeholder="Name: John Smith\nPermit type: Aufenthaltserlaubnis §18a\nValid until: 31.12.2025\n...",
        height=200,
    )
    if st.button("Validate", key="text_permit_btn") and text:
        with st.spinner("Validating..."):
            result = validate_permit_text(text)
        show_result(result)
