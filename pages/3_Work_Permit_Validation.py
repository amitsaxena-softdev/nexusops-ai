import re
import io
import streamlit as st
import pdfplumber
from agents.work_permit_agent import validate_permit
from shared.file_utils import mime_for

st.set_page_config(page_title="Work Permit Validation — Leistenschneider", page_icon="📋")
st.title("📋 Work Permit Validation Agent")
st.caption("Client: Leistenschneider Personaldienstleistungen GmbH (Saarbrücken) — Instant permit validation with confidence score")


def _parse_result(text: str) -> dict:
    inner = re.search(r'---\s*(.*?)\s*---', text, re.DOTALL)
    content = inner.group(1) if inner else text
    fields, current_key, current_lines = {}, None, []
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


def _show_doc_preview(file_bytes: bytes, filename: str):
    st.download_button("⬇ Download PDF", data=file_bytes, file_name=filename,
                       mime="application/pdf", use_container_width=True)
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join(p.extract_text() or "" for p in pdf.pages).strip()
        text = re.sub(r'SYNTHETISCHE TESTDATEN.*?Sample ID:.*', '', text, flags=re.DOTALL).strip()
    except Exception:
        text = "(Could not extract document text)"
    st.markdown(f"""
<div style="background:#ffffff; border:1px solid #d0d7de; border-radius:8px;
            padding:20px 22px; height:460px; overflow-y:auto;
            font-family:'Courier New', monospace; font-size:11.5px;
            line-height:1.8; color:#24292f; white-space:pre-wrap;">{text}</div>
""", unsafe_allow_html=True)


def _show_result(result: str, file_bytes: bytes = None, filename: str = "permit.pdf"):
    fields = _parse_result(result)
    valid  = fields.get("VALID WORK PERMIT", "").upper()

    if "YES" in valid:
        color, icon, label = "#14532d", "✅", "VALID — Employment Permitted"
        bg, border = "#f0fdf4", "#16a34a"
    elif "NO" in valid:
        color, icon, label = "#7f1d1d", "❌", "INVALID"
        bg, border = "#fff1f2", "#dc2626"
    else:
        color, icon, label = "#78350f", "⚠️", "UNCERTAIN — Manual Review Required"
        bg, border = "#fffbeb", "#d97706"

    if file_bytes and filename.lower().endswith(".pdf"):
        col_left, col_right = st.columns([1, 1])
    else:
        col_left = st.container()
        col_right = None

    with col_left:
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

    if col_right is not None:
        with col_right:
            st.markdown("**Document Preview**")
            _show_doc_preview(file_bytes, filename)


# ── Upload ────────────────────────────────────────────────────────────────────
uploaded_files = st.file_uploader(
    "Upload work permits / Aufenthaltstitel",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
)
st.caption("💡 To upload an entire folder, open it in the file picker and press **Ctrl+A** (or **⌘+A** on Mac).")

if uploaded_files:
    n = len(uploaded_files)
    st.caption(f"{n} file{'s' if n > 1 else ''} selected")

    if st.button("▶ Validate All Permits", type="primary"):
        for f in uploaded_files:
            file_bytes = f.read()
            with st.spinner(f"Validating **{f.name}**…"):
                result = validate_permit(file_bytes, mime_for(f.name))
            with st.container(border=True):
                st.markdown(f"**📄 {f.name}**")
                _show_result(result, file_bytes, f.name)
