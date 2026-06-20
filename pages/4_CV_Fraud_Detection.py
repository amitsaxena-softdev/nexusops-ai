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


def show_verdict(result: str):
    if "OVERALL VERDICT: PASS" in result:
        st.success("✅ PASS — No significant fraud signals detected")
    elif "OVERALL VERDICT: REJECT" in result:
        st.error("🚫 REJECT — High fraud risk")
    else:
        st.warning("⚠️ REVIEW — Manual verification recommended")
    st.code(result, language="markdown")


tab_cv_sample, tab_cert_sample, tab_upload, tab_text = st.tabs([
    "📂 Sample CVs", "📂 Sample Certificates", "⬆️ Upload Document", "✏️ Paste Text"
])

with tab_cv_sample:
    if not CV_FILES:
        st.info("No sample CVs found.")
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
        st.info("No sample certificates found.")
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
    text = st.text_area("Paste CV or certificate text", height=300)
    if st.button("Analyse for Fraud", key="text_fraud_btn") and text:
        with st.spinner("Running fraud analysis..."):
            result = analyse_text(text)
        st.markdown("### Fraud Analysis Report")
        show_verdict(result)
