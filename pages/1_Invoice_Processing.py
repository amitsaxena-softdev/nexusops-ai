import re
import streamlit as st
from pathlib import Path
from agents.invoice_agent import process_invoice, process_invoice_text
from shared.file_utils import extract_text_from_docx, mime_for, is_native_gemini, read_sample

st.set_page_config(page_title="Invoice Processing — Globus Group", page_icon="🧾")
st.title("🧾 Invoice Processing Agent")
st.caption("Client: Globus Group (St. Wendel) — Automated invoice routing to the right department")

SAMPLES_DIR = Path("samples/invoices")
SAMPLE_FILES = sorted([f for f in SAMPLES_DIR.iterdir() if f.suffix != ".csv"]) if SAMPLES_DIR.exists() else []

MOCK_EMAILS = {
    "01_stadtwerke_gas_de.pdf": {
        "from_name": "Stadtwerke St. Wendel",
        "from_email": "rechnung@stadtwerke-stwenden.de",
        "subject": "Ihre Rechnung – Gaslieferung Q2 2026",
        "body": "Sehr geehrte Damen und Herren, im Anhang finden Sie unsere aktuelle Rechnung für die Gaslieferung im zweiten Quartal 2026. Bitte überweisen Sie den Betrag innerhalb von 14 Tagen auf das angegebene Konto.",
    },
    "02_microsoft_licenses_en.pdf": {
        "from_name": "Microsoft Billing",
        "from_email": "invoicing@microsoft.com",
        "subject": "Microsoft Invoice – Enterprise License Renewal 2026",
        "body": "Dear Globus Group, please find attached your invoice for the annual renewal of your Microsoft 365 enterprise licenses. Payment is due within 30 days of the invoice date.",
    },
    "03_eon_strom_de.png": {
        "from_name": "E.ON Energie Deutschland",
        "from_email": "rechnung@eon.de",
        "subject": "E.ON Stromrechnung – Juni 2026",
        "body": "Sehr geehrte Damen und Herren, anbei erhalten Sie Ihre Stromrechnung für den aktuellen Abrechnungszeitraum. Bei Fragen stehen wir Ihnen gerne zur Verfügung.",
    },
    "04_aws_cloud_en.docx": {
        "from_name": "Amazon Web Services",
        "from_email": "aws-invoices@amazon.com",
        "subject": "AWS Invoice – May 2026 Usage Statement",
        "body": "Hello, your AWS invoice for the billing period May 2026 is attached. This covers your usage of EC2, S3, RDS, and other AWS services.",
    },
    "05_buerobedarf_de.png": {
        "from_name": "Office Partner GmbH",
        "from_email": "rechnung@officepartner.de",
        "subject": "Rechnung Bürobedarf – Bestellung Nr. BP-2026-0541",
        "body": "Sehr geehrte Damen und Herren, vielen Dank für Ihre Bestellung. Im Anhang finden Sie die Rechnung für die gelieferten Büromaterialien.",
    },
    "06_brightpath_consulting_en.docx": {
        "from_name": "Brightpath Consulting Ltd.",
        "from_email": "finance@brightpath-consulting.com",
        "subject": "Consulting Invoice – Project Alpha Q2 2026",
        "body": "Dear Globus Group, please find attached our invoice for consulting services rendered during Q2 2026. We appreciate your continued partnership.",
    },
    "07_hotel_adlon_de.docx": {
        "from_name": "Hotel Adlon Kempinski",
        "from_email": "reservierung@hotel-adlon.de",
        "subject": "Hotelrechnung – Veranstaltung 12. Juni 2026",
        "body": "Sehr geehrte Damen und Herren, anbei erhalten Sie die Sammelrechnung für die Veranstaltungsräume und Übernachtungen vom 12. Juni 2026.",
    },
    "08_adobe_creativecloud_en.png": {
        "from_name": "Adobe Systems",
        "from_email": "invoices@adobe.com",
        "subject": "Adobe Creative Cloud for Teams – Invoice June 2026",
        "body": "Hello, your Adobe Creative Cloud for Teams subscription invoice for June 2026 is attached. Please contact billing@adobe.com with any questions.",
    },
    "09_telekom_internet_de.pdf": {
        "from_name": "Deutsche Telekom AG",
        "from_email": "rechnung@telekom.de",
        "subject": "Ihre Telekom Rechnung – Juni 2026",
        "body": "Sehr geehrte Damen und Herren, Ihre monatliche Rechnung für Internet- und Telefondienstleistungen im Juni 2026 ist beigefügt.",
    },
    "10_dell_hardware_en.png": {
        "from_name": "Dell Technologies GmbH",
        "from_email": "invoices@dell.com",
        "subject": "Dell Invoice – Hardware Order #DT-2026-88432",
        "body": "Dear Globus Group, thank you for your recent hardware purchase. Please find your invoice attached for order #DT-2026-88432.",
    },
}


def _make_email_context(meta, filename):
    return (
        f"From: {meta['from_name']} <{meta['from_email']}>\n"
        f"Subject: {meta['subject']}\n"
        f"Body: {meta['body']}\n"
        f"Attachment: {filename}"
    )


def _show_email_card(meta, attachment_name):
    st.markdown(f"""
<div style="border:1px solid #d0d7de; border-radius:8px; padding:16px 20px;
            background:#f6f8fa; margin-bottom:16px;">
  <div style="font-size:11px; color:#8b949e; text-transform:uppercase;
              letter-spacing:0.5px; margin-bottom:8px;">📧 Incoming Email — Finance Inbox</div>
  <div style="font-weight:600; font-size:15px; margin-bottom:6px; color:#24292f;">
    {meta['subject']}
  </div>
  <div style="font-size:12px; color:#57606a; margin-bottom:12px;">
    <b>From:</b> {meta['from_name']} &lt;{meta['from_email']}&gt;
  </div>
  <div style="font-size:13px; color:#444; border-left:3px solid #d0d7de;
              padding-left:12px; margin-bottom:14px; line-height:1.6;">
    {meta['body']}
  </div>
  <div style="font-size:12px; display:inline-flex; align-items:center; gap:6px;
              background:#ffffff; border:1px solid #d0d7de; border-radius:6px;
              padding:5px 10px; color:#24292f;">
    📎 <span style="font-weight:500;">{attachment_name}</span>
  </div>
</div>
""", unsafe_allow_html=True)


def _parse_result(text):
    inner = re.search(r'---\s*(.*?)\s*---', text, re.DOTALL)
    content = inner.group(1) if inner else text
    fields = {}
    current_key = None
    current_lines = []
    for line in content.strip().split('\n'):
        m = re.match(r'^([A-Z][A-Z &\/]+):\s*(.*)', line)
        if m:
            if current_key:
                fields[current_key] = '\n'.join(current_lines).strip()
            current_key = m.group(1).strip()
            val = m.group(2).strip()
            current_lines = [val] if val else []
        elif current_key and line.strip():
            current_lines.append(line.strip())
    if current_key:
        fields[current_key] = '\n'.join(current_lines).strip()
    return fields


def _show_result(fields, raw_text):
    validity = fields.get("VALIDITY", "").upper()
    dept = fields.get("ROUTED TO", "—")

    if "CONFIRMED" in validity:
        v_color, v_icon = "#1a7f1a", "✅"
    elif "REVIEW" in validity:
        v_color, v_icon = "#b36b00", "⚠️"
    else:
        v_color, v_icon = "#c0392b", "❌"

    st.markdown(f"""
<div style="display:flex; gap:10px; margin-bottom:16px; flex-wrap:wrap;">
  <span style="background:{v_color}; color:white; padding:5px 14px;
               border-radius:20px; font-size:13px; font-weight:600;">{v_icon} {validity or "UNKNOWN"}</span>
  <span style="background:#1565c0; color:white; padding:5px 14px;
               border-radius:20px; font-size:13px; font-weight:600;">🏢 {dept}</span>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Vendor:** {fields.get('VENDOR', '—')}")
        st.markdown(f"**Invoice No:** {fields.get('INVOICE NO', '—')}")
        st.markdown(f"**Date:** {fields.get('DATE', '—')}")
    with col2:
        st.markdown(f"**Total Amount:** {fields.get('TOTAL AMOUNT', '—')}")
        st.markdown(f"**VAT:** {fields.get('VAT', '—')}")
        st.markdown(f"**Category:** {fields.get('CATEGORY', '—')}")

    line_items = fields.get("LINE ITEMS", "").strip()
    if line_items:
        st.markdown("**Line Items:**")
        for item in line_items.split('\n'):
            item = item.strip().lstrip('-').strip()
            if item:
                st.markdown(f"- {item}")

    st.markdown(f"**Routing reason:** {fields.get('REASON', '—')}")

    v_reason = fields.get("VALIDITY REASON", "")
    if v_reason:
        st.markdown(f"**Validity note:** {v_reason}")

    flags = fields.get("FLAGS", "None")
    if flags and flags.lower() not in ("none", "n/a", ""):
        st.warning(f"⚠️ **Anomaly flags:** {flags}")
    else:
        st.success("No anomalies detected")

    with st.expander("Raw output"):
        st.code(raw_text, language="markdown")


# ── TABS ──────────────────────────────────────────────────────────────────────
tab_sample, tab_upload, tab_text = st.tabs(["📂 Sample Email Inbox", "✉️ Simulate Email", "✏️ Paste Text"])

with tab_sample:
    if not SAMPLE_FILES:
        st.info("No sample invoices found in samples/invoices/")
    else:
        sample_names = {f.name: f for f in SAMPLE_FILES}
        chosen = st.selectbox("Pick a sample invoice", list(sample_names.keys()))
        selected_file = sample_names[chosen]
        meta = MOCK_EMAILS.get(chosen, {})

        if meta:
            _show_email_card(meta, chosen)

        if st.button("Analyse This Invoice", type="primary", key="sample_btn"):
            file_bytes = read_sample(selected_file)
            ext = selected_file.suffix.lstrip(".")
            email_context = _make_email_context(meta, chosen) if meta else ""

            with st.spinner(f"Processing {chosen}..."):
                if is_native_gemini(selected_file.name):
                    result = process_invoice(file_bytes, mime_for(selected_file.name), email_context)
                elif ext == "docx":
                    text = extract_text_from_docx(file_bytes)
                    result = process_invoice_text(
                        f"[Extracted from DOCX: {chosen}]\n\n{text}", email_context
                    )
                else:
                    st.error(f"Unsupported format: .{ext}")
                    st.stop()

            st.markdown("### Result")
            _show_result(_parse_result(result), result)

with tab_upload:
    st.markdown("**Simulate an incoming supplier email with an invoice attachment.**")
    col_a, col_b = st.columns(2)
    with col_a:
        email_from = st.text_input("From (sender)", placeholder="billing@vendor.com")
    with col_b:
        email_subject = st.text_input("Subject", placeholder="Invoice #1234 – June 2026")
    email_body = st.text_area("Email body", placeholder="Please find attached our invoice for...", height=80)
    uploaded = st.file_uploader(
        "📎 Attach invoice (PDF, PNG, JPG, DOCX)", type=["pdf", "png", "jpg", "jpeg", "docx"]
    )

    if uploaded and st.button("📨 Process Email", type="primary", key="upload_btn"):
        file_bytes = uploaded.read()
        ext = uploaded.name.rsplit(".", 1)[-1].lower()
        email_context = ""
        if email_from or email_subject:
            email_context = (
                f"From: {email_from}\nSubject: {email_subject}\n"
                f"Body: {email_body}\nAttachment: {uploaded.name}"
            )
        with st.spinner("Reading and routing invoice..."):
            if is_native_gemini(uploaded.name):
                result = process_invoice(file_bytes, mime_for(uploaded.name), email_context)
            elif ext == "docx":
                text = extract_text_from_docx(file_bytes)
                result = process_invoice_text(
                    f"[Extracted from DOCX: {uploaded.name}]\n\n{text}", email_context
                )
            else:
                st.error("Unsupported format")
                st.stop()
        st.markdown("### Result")
        _show_result(_parse_result(result), result)

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
        _show_result(_parse_result(result), result)
