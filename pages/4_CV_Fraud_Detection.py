import re
import streamlit as st
from pathlib import Path
from agents.cv_fraud_agent import analyse_document, analyse_text
from shared.file_utils import read_sample, mime_for

st.set_page_config(page_title="CV Fraud Detection — Persowerk", page_icon="🔍")
st.title("🔍 CV & Certificate Fraud Detection")
st.caption("Client: Persowerk Deutschland GmbH (Saarbrücken) — Detect AI-generated CVs and fraudulent certificates")

CVS_DIR = Path("samples/cvs")
CERTS_DIR = Path("samples/certificates")
CV_FILES = sorted(CVS_DIR.iterdir()) if CVS_DIR.exists() else []
CERT_FILES = sorted(CERTS_DIR.iterdir()) if CERTS_DIR.exists() else []


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


def _score_color(score_str: str):
    try:
        score = int(re.search(r'\d+', score_str).group())
    except Exception:
        return "#6b7280", "#f3f4f6", score_str
    if score >= 70:
        return "#7f1d1d", "#fff1f2", f"{score}/100 — HIGH RISK"
    elif score >= 40:
        return "#78350f", "#fffbeb", f"{score}/100 — MEDIUM RISK"
    else:
        return "#14532d", "#f0fdf4", f"{score}/100 — LOW RISK"


def show_verdict(result: str):
    fields = _parse_result(result)
    verdict = fields.get("OVERALL VERDICT", "").upper()
    score_raw = fields.get("FRAUD RISK SCORE", "?")

    if "PASS" in verdict:
        color, bg, border = "#14532d", "#f0fdf4", "#16a34a"
        icon, label = "✅", "PASS — No significant fraud signals"
    elif "REJECT" in verdict:
        color, bg, border = "#7f1d1d", "#fff1f2", "#dc2626"
        icon, label = "🚫", "REJECT — High fraud risk"
    else:
        color, bg, border = "#78350f", "#fffbeb", "#d97706"
        icon, label = "⚠️", "REVIEW — Manual verification recommended"

    score_color, score_bg, score_label = _score_color(score_raw)

    st.markdown(f"""
<div style="background:{bg}; border:2px solid {border}; border-radius:10px;
            padding:16px 20px; margin-bottom:18px; display:flex;
            justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
  <div style="font-size:20px; font-weight:800; color:{color};">{icon} {label}</div>
  <div style="background:{score_bg}; border:1.5px solid {score_color}; border-radius:8px;
              padding:8px 16px; font-weight:700; font-size:14px; color:{score_color};">
    Fraud Score: {score_label}
  </div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Document Type:** {fields.get('DOCUMENT TYPE', '—')}")
        st.markdown(f"**Candidate Name:** {fields.get('CANDIDATE NAME', '—')}")
        st.markdown(f"**AI Generation Risk:** {fields.get('AI GENERATION RISK', '—')}")

    with col2:
        st.markdown(f"**Timeline Issues:** {fields.get('TIMELINE ISSUES', '—')}")
        st.markdown(f"**Skill/Experience Mismatch:** {fields.get('SKILL/EXPERIENCE MISMATCH', '—')}")

    suspicious = fields.get("SUSPICIOUS CLAIMS", "None")
    cert_flags = fields.get("CERTIFICATE FLAGS", "None")
    companies = fields.get("COMPANIES TO VERIFY", "None")

    if suspicious and suspicious.lower() not in ("none", "n/a", ""):
        st.error(f"**Suspicious Claims:**\n\n{suspicious}")
    if cert_flags and cert_flags.lower() not in ("none", "n/a", ""):
        st.warning(f"**Certificate Flags:**\n\n{cert_flags}")
    if companies and companies.lower() not in ("none", "n/a", ""):
        st.info(f"**Companies to Verify:** {companies}")

    notes = fields.get("NOTES", "")
    if notes:
        st.markdown(f"**Assessment:** {notes}")

    with st.expander("Raw output"):
        st.code(result, language="markdown")


tab_cv_sample, tab_cert_sample, tab_upload, tab_text = st.tabs([
    "📂 Sample CVs", "📂 Sample Certificates", "⬆️ Upload Document", "✏️ Paste Text"
])

with tab_cv_sample:
    if not CV_FILES:
        st.info("No sample CVs found in samples/cvs/ — use the Upload or Paste Text tab.")
    else:
        cv_names = {f.name: f for f in CV_FILES}
        chosen = st.selectbox("Select a CV to analyse", list(cv_names.keys()))
        if st.button("Run Fraud Analysis on CV", type="primary", key="cv_sample_btn"):
            f = cv_names[chosen]
            with st.spinner(f"Analysing {chosen}..."):
                result = analyse_document(read_sample(f), "application/pdf", "CV")
            st.markdown("### Fraud Analysis Report")
            show_verdict(result)

with tab_cert_sample:
    if not CERT_FILES:
        st.info("No sample certificates found in samples/certificates/ — use the Upload or Paste Text tab.")
    else:
        cert_names = {f.name: f for f in CERT_FILES}
        chosen_cert = st.selectbox("Select a certificate to analyse", list(cert_names.keys()))
        if st.button("Run Fraud Analysis on Certificate", type="primary", key="cert_sample_btn"):
            f = cert_names[chosen_cert]
            mime = mime_for(f.name)
            with st.spinner(f"Analysing {chosen_cert}..."):
                result = analyse_document(read_sample(f), mime, "Certificate")
            st.markdown("### Fraud Analysis Report")
            show_verdict(result)

with tab_upload:
    doc_type = st.selectbox("Document type", ["CV", "Certificate", "Reference Letter", "Diploma"])
    uploaded = st.file_uploader(
        f"Upload {doc_type} (PDF or image)", type=["pdf", "png", "jpg", "jpeg"]
    )
    if uploaded and st.button("Run Fraud Analysis", type="primary", key="upload_fraud_btn"):
        mime = "application/pdf" if uploaded.name.endswith(".pdf") else f"image/{uploaded.name.rsplit('.', 1)[-1]}"
        with st.spinner(f"Analysing {doc_type}..."):
            result = analyse_document(uploaded.read(), mime, doc_type)
        st.markdown("### Fraud Analysis Report")
        show_verdict(result)

with tab_text:
    text = st.text_area("Paste CV or certificate text", height=300,
                        placeholder="Name: John Smith\nExperience: 10 years at Google (2014–2024)\nEducation: PhD MIT 2013\n...")
    if st.button("Analyse for Fraud", key="text_fraud_btn") and text:
        with st.spinner("Running fraud analysis..."):
            result = analyse_text(text)
        st.markdown("### Fraud Analysis Report")
        show_verdict(result)
