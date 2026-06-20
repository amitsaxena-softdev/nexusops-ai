import streamlit as st
from pathlib import Path
from agents.invoice_agent import process_invoice, process_invoice_text
from shared.file_utils import extract_text_from_docx, mime_for, is_native_gemini, read_sample

st.set_page_config(page_title="Invoice Processing — Globus Group", page_icon="🧾")
st.title("🧾 Invoice Processing Agent")
st.caption("Client: Globus Group (St. Wendel) — Automated invoice routing to the right department")

SAMPLES_DIR = Path("samples/invoices")
SAMPLE_FILES = sorted([f for f in SAMPLES_DIR.iterdir() if f.suffix != ".csv"]) if SAMPLES_DIR.exists() else []

tab_sample, tab_upload, tab_text = st.tabs(["📂 Load Sample", "⬆️ Upload Invoice", "✏️ Paste Text"])

with tab_sample:
    if not SAMPLE_FILES:
        st.info("No sample invoices found in samples/invoices/")
    else:
        sample_names = {f.name: f for f in SAMPLE_FILES}
        chosen = st.selectbox("Pick a sample invoice", list(sample_names.keys()))
        selected_file = sample_names[chosen]

        if st.button("Analyse This Invoice", type="primary", key="sample_btn"):
            file_bytes = read_sample(selected_file)
            ext = selected_file.suffix.lstrip(".")

            with st.spinner(f"Processing {chosen}..."):
                if is_native_gemini(selected_file.name):
                    result = process_invoice(file_bytes, mime_for(selected_file.name))
                elif ext == "docx":
                    text = extract_text_from_docx(file_bytes)
                    result = process_invoice_text(f"[Extracted from DOCX: {chosen}]\n\n{text}")
                else:
                    st.error(f"Unsupported format: .{ext}")
                    st.stop()

            st.markdown("### Result")
            st.code(result, language="markdown")

with tab_upload:
    uploaded = st.file_uploader(
        "Upload invoice (PDF, PNG, JPG, DOCX)", type=["pdf", "png", "jpg", "jpeg", "docx"]
    )
    if uploaded and st.button("Analyse Invoice", key="upload_btn"):
        file_bytes = uploaded.read()
        ext = uploaded.name.rsplit(".", 1)[-1].lower()
        with st.spinner("Reading and routing invoice..."):
            if is_native_gemini(uploaded.name):
                result = process_invoice(file_bytes, mime_for(uploaded.name))
            elif ext == "docx":
                text = extract_text_from_docx(file_bytes)
                result = process_invoice_text(f"[Extracted from DOCX: {uploaded.name}]\n\n{text}")
            else:
                st.error("Unsupported format")
                st.stop()
        st.markdown("### Result")
        st.code(result, language="markdown")

with tab_text:
    text_input = st.text_area(
        "Paste invoice text or describe it",
        placeholder="Vendor: Acme GmbH\nInvoice No: 2024-1234\nDate: 15.06.2024\n...",
        height=200,
    )
    if st.button("Analyse", key="text_btn") and text_input:
        with st.spinner("Analysing..."):
            result = process_invoice_text(text_input)
        st.markdown("### Result")
        st.code(result, language="markdown")
