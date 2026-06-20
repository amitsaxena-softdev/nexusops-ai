import re
import io
import streamlit as st
import pdfplumber
from pathlib import Path
from agents.work_permit_agent import validate_permit, validate_permit_text
from shared.file_utils import read_sample

st.set_page_config(page_title="Work Permit Validation — Leistenschneider", page_icon="📋")
st.title("📋 Work Permit Validation Agent")
st.caption("Client: Leistenschneider Personaldienstleistungen GmbH (Saarbrücken) — Instant permit validation with confidence score")

PERMITS_DIR = Path("samples/work_permits")
SAMPLE_PERMITS = sorted(PERMITS_DIR.iterdir()) if PERMITS_DIR.exists() else []


def _parse_result(text: str) -> dict:
    inner = re.search(r'---\s*(.*?)\s*---', text, re.DOTALL)
    content = inner.group(1) if inner else text
    fields = {}
    current_key = None
    current_lines = []
    for line in content.strip().split('\n'):
        m = re.match(r'^([A-Za-z][A-Za-z0-9 &\/]+):\s*(.*)', line, re.IGNORECASE)
        if m:
            if current_key:
                fields[current_key] = '\n'.join(current_lines).strip()
            current_key = m.group(1).strip().upper()
            val = m.group(2).strip()
            current_lines = [val] if val else []
        elif current_key and line.strip():
            current_lines.append(line.strip())
    if current_key:
        fields[current_key] = '\n'.join(current_lines).strip()
    return fields


def _show_doc_preview(file_bytes: bytes, filename: str = "permit.pdf"):
    st.download_button(
        "⬇ Download PDF",
        data=file_bytes,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
    )
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join(p.extract_text() or "" for p in pdf.pages).strip()
    except Exception:
        text = "(Could not extract document text)"

    # Strip the specimen footer so the preview looks clean
    text = re.sub(
        r'SYNTHETISCHE TESTDATEN.*?Sample ID:.*', '', text, flags=re.DOTALL
    ).strip()

    st.markdown(f"""
<div style="background:#ffffff; border:1px solid #d0d7de; border-radius:8px;
            padding:20px 22px; height:500px; overflow-y:auto;
            font-family:'Courier New', monospace; font-size:11.5px;
            line-height:1.8; color:#24292f; white-space:pre-wrap;">{text}</div>
""", unsafe_allow_html=True)


def _show_result(result: str, file_bytes: bytes = None):
    fields = _parse_result(result)
    valid = fields.get("VALID WORK PERMIT", "").upper()

    if "YES" in valid:
        color, icon, label = "#14532d", "✅", "VALID — Employment Permitted"
        bg, border = "#f0fdf4", "#16a34a"
    elif "NO" in valid:
        color, icon, label = "#7f1d1d", "❌", "INVALID"
        bg, border = "#fff1f2", "#dc2626"
    else:
        color, icon, label = "#78350f", "⚠️", "UNCERTAIN — Manual Review Required"
        bg, border = "#fffbeb", "#d97706"

    # Two-column layout when a PDF is available
    if file_bytes:
        col_left, col_right = st.columns([1, 1])
    else:
        col_left = st.container()
        col_right = None

    with col_left:
        # Verdict banner
        st.markdown(f"""
<div style="background:{bg}; border:2px solid {border}; border-radius:10px;
            padding:16px 20px; margin-bottom:18px;">
  <div style="font-size:20px; font-weight:800; color:{color}; margin-bottom:4px;">
    {icon} {label}
  </div>
  <div style="font-size:13px; color:{color}; opacity:0.8;">
    Confidence: {fields.get('CONFIDENCE', 'N/A')}
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown(f"**Holder:** {fields.get('HOLDER NAME', '—')}")
        st.markdown(f"**Date of Birth:** {fields.get('DATE OF BIRTH', '—')}")
        st.markdown(f"**Nationality:** {fields.get('NATIONALITY', '—')}")
        st.markdown(f"**Permit Type:** {fields.get('PERMIT TYPE', '—')}")
        st.markdown(f"**Issued By:** {fields.get('ISSUED BY', '—')}")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Valid Until:** {fields.get('VALID UNTIL', '—')}")
        with col_b:
            st.markdown(f"**Expires In:** {fields.get('EXPIRES IN', '—')}")

        st.markdown(f"**Recommendation:** `{fields.get('RECOMMENDATION', '—')}`")

        flags = fields.get("RED FLAGS", "None")
        if flags and flags.lower() not in ("none", "n/a", ""):
            st.error(f"**Red Flags:**\n\n{flags}")
        else:
            st.success("No red flags detected")

        with st.expander("Raw output"):
            st.code(result, language="markdown")

    if col_right is not None and file_bytes:
        with col_right:
            st.markdown("**Document Preview**")
            _show_doc_preview(file_bytes)


# ── TABS ──────────────────────────────────────────────────────────────────────
tab_sample, tab_upload, tab_text = st.tabs(["📂 Load Sample", "⬆️ Upload Document", "✏️ Manual Entry"])

with tab_sample:
    if not SAMPLE_PERMITS:
        st.info("No sample permits found in samples/work_permits/")
    else:
        permit_names = {f.name: f for f in SAMPLE_PERMITS}
        chosen = st.selectbox(
            "Pick a sample permit", list(permit_names.keys()),
            help="valid_01/02 → should pass  |  invalid_01 → expired  |  invalid_02 → student permit, employment not allowed"
        )
        selected = permit_names[chosen]
        if st.button("Validate This Permit", type="primary", key="sample_permit_btn"):
            file_bytes = read_sample(selected)
            with st.spinner("Validating..."):
                result = validate_permit(file_bytes, "application/pdf")
            _show_result(result, file_bytes)

with tab_upload:
    uploaded = st.file_uploader(
        "Upload work permit / Aufenthaltstitel (PDF or image)",
        type=["pdf", "png", "jpg", "jpeg"],
    )
    if uploaded:
        is_pdf = uploaded.name.lower().endswith(".pdf")
        ext = uploaded.name.rsplit(".", 1)[-1].lower()
        mime = "application/pdf" if is_pdf else f"image/{ext}"

        if not is_pdf:
            st.image(uploaded, caption="Uploaded document", use_container_width=True)

        if st.button("Validate Document", type="primary", key="upload_permit_btn"):
            file_bytes = uploaded.read()
            with st.spinner("Validating work permit..."):
                result = validate_permit(file_bytes, mime)
            _show_result(result, file_bytes if is_pdf else None)

with tab_text:
    text = st.text_area(
        "Describe the document or paste extracted text",
        placeholder="Name: John Smith\nPermit type: Aufenthaltserlaubnis §18a\nValid until: 31.12.2025\n...",
        height=200,
    )
    if st.button("Validate", key="text_permit_btn") and text:
        with st.spinner("Validating..."):
            result = validate_permit_text(text)
        _show_result(result)
