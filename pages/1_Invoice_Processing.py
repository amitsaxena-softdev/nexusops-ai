import re
import streamlit as st
from pathlib import Path
from agents.invoice_agent import process_invoice, process_invoice_text
from shared.file_utils import extract_text_from_docx, mime_for, is_native_gemini, read_sample

st.set_page_config(page_title="Invoice Processing — Globus Group", page_icon="🧾")
st.title("🧾 Invoice Processing Agent")
st.caption("Client: Globus Group (St. Wendel) — Automated invoice routing from the Finance inbox")

SAMPLES_DIR = Path("samples/invoices")
SAMPLE_FILES = sorted([f for f in SAMPLES_DIR.iterdir() if f.suffix != ".csv"]) if SAMPLES_DIR.exists() else []

MOCK_EMAILS = {
    "01_stadtwerke_gas_de.pdf": {
        "from_name": "Stadtwerke St. Wendel",
        "from_email": "rechnung@stadtwerke-stwenden.de",
        "subject": "Ihre Rechnung – Gaslieferung Q2 2026",
        "body": "Sehr geehrte Damen und Herren, im Anhang finden Sie unsere aktuelle Rechnung für die Gaslieferung im zweiten Quartal 2026. Bitte überweisen Sie den Betrag innerhalb von 14 Tagen.",
    },
    "02_microsoft_licenses_en.pdf": {
        "from_name": "Microsoft Billing",
        "from_email": "invoicing@microsoft.com",
        "subject": "Microsoft Invoice – Enterprise License Renewal 2026",
        "body": "Dear Globus Group, please find attached your invoice for the annual renewal of your Microsoft 365 enterprise licenses. Payment is due within 30 days.",
    },
    "03_eon_strom_de.png": {
        "from_name": "E.ON Energie Deutschland",
        "from_email": "rechnung@eon.de",
        "subject": "E.ON Stromrechnung – Juni 2026",
        "body": "Sehr geehrte Damen und Herren, anbei erhalten Sie Ihre Stromrechnung für den aktuellen Abrechnungszeitraum.",
    },
    "04_aws_cloud_en.docx": {
        "from_name": "Amazon Web Services",
        "from_email": "aws-invoices@amazon.com",
        "subject": "AWS Invoice – May 2026 Usage Statement",
        "body": "Hello, your AWS invoice for the billing period May 2026 is attached. This covers EC2, S3, RDS, and other services.",
    },
    "05_buerobedarf_de.png": {
        "from_name": "Office Partner GmbH",
        "from_email": "rechnung@officepartner.de",
        "subject": "Rechnung Bürobedarf – Bestellung Nr. BP-2026-0541",
        "body": "Sehr geehrte Damen und Herren, im Anhang finden Sie die Rechnung für die gelieferten Büromaterialien.",
    },
    "06_brightpath_consulting_en.docx": {
        "from_name": "Brightpath Consulting Ltd.",
        "from_email": "finance@brightpath-consulting.com",
        "subject": "Consulting Invoice – Project Alpha Q2 2026",
        "body": "Dear Globus Group, please find attached our invoice for consulting services rendered during Q2 2026.",
    },
    "07_hotel_adlon_de.docx": {
        "from_name": "Hotel Adlon Kempinski",
        "from_email": "reservierung@hotel-adlon.de",
        "subject": "Hotelrechnung – Veranstaltung 12. Juni 2026",
        "body": "Sehr geehrte Damen und Herren, anbei erhalten Sie die Sammelrechnung für Veranstaltungsräume und Übernachtungen.",
    },
    "08_adobe_creativecloud_en.png": {
        "from_name": "Adobe Systems",
        "from_email": "invoices@adobe.com",
        "subject": "Adobe Creative Cloud for Teams – Invoice June 2026",
        "body": "Hello, your Adobe Creative Cloud for Teams subscription invoice for June 2026 is attached.",
    },
    "09_telekom_internet_de.pdf": {
        "from_name": "Deutsche Telekom AG",
        "from_email": "rechnung@telekom.de",
        "subject": "Ihre Telekom Rechnung – Juni 2026",
        "body": "Sehr geehrte Damen und Herren, Ihre monatliche Rechnung für Internet- und Telefondienstleistungen ist beigefügt.",
    },
    "10_dell_hardware_en.png": {
        "from_name": "Dell Technologies GmbH",
        "from_email": "invoices@dell.com",
        "subject": "Dell Invoice – Hardware Order #DT-2026-88432",
        "body": "Dear Globus Group, thank you for your recent hardware purchase. Please find your invoice attached.",
    },
}

# ── Session state ──────────────────────────────────────────────────────────────
if "inbox_results" not in st.session_state:
    st.session_state.inbox_results = {}
if "inbox_forwarded" not in st.session_state:
    st.session_state.inbox_forwarded = set()
if "single_forwarded" not in st.session_state:
    st.session_state.single_forwarded = False


def _make_email_context(meta, filename):
    return (
        f"From: {meta['from_name']} <{meta['from_email']}>\n"
        f"Subject: {meta['subject']}\n"
        f"Body: {meta['body']}\n"
        f"Attachment: {filename}"
    )


def _parse_result(text):
    inner = re.search(r'---\s*(.*?)\s*---', text, re.DOTALL)
    content = inner.group(1) if inner else text
    fields = {}
    current_key = None
    current_lines = []
    for line in content.strip().split('\n'):
        m = re.match(r'^([A-Z][A-Z0-9 &\/]+):\s*(.*)', line)
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


def _status_style(status: str):
    s = status.upper()
    if "READY" in s or "CONFIRMED" in s:
        return "#16a34a", "#f0fdf4", "✅ Ready to forward"
    elif "INCOMPLETE" in s or "REVIEW" in s:
        return "#d97706", "#fffbeb", "⚠️ Incomplete"
    elif "NOT AN INVOICE" in s or "REJECTED" in s:
        return "#dc2626", "#fff1f2", "❌ Not an invoice"
    return "#6b7280", "#f3f4f6", status or "Unknown"


def _process_file(f: Path) -> dict:
    meta = MOCK_EMAILS.get(f.name, {})
    email_context = _make_email_context(meta, f.name) if meta else ""
    file_bytes = read_sample(f)
    ext = f.suffix.lstrip(".")
    if is_native_gemini(f.name):
        raw = process_invoice(file_bytes, mime_for(f.name), email_context)
    elif ext == "docx":
        text = extract_text_from_docx(file_bytes)
        raw = process_invoice_text(f"[From DOCX: {f.name}]\n\n{text}", email_context)
    else:
        raw = ""
    return {"fields": _parse_result(raw), "raw": raw, "meta": meta}


# ── TABS ───────────────────────────────────────────────────────────────────────
tab_inbox, tab_single = st.tabs(["📬 Finance Inbox", "✉️ Simulate Single Email"])

# ══════════════════════════════════════════════════════════════════════════════
with tab_inbox:
    if not SAMPLE_FILES:
        st.info("No sample invoices found in samples/invoices/")
    else:
        results = st.session_state.inbox_results
        processed = len(results)
        total = len(SAMPLE_FILES)
        forwarded_count = len(st.session_state.inbox_forwarded)

        # ── Inbox header ──────────────────────────────────────────────────────
        col_hdr, col_btn = st.columns([3, 1])
        with col_hdr:
            st.markdown(
                f"**📬 finanzen@globus.de** &nbsp;·&nbsp; "
                f"`{total}` emails &nbsp;·&nbsp; "
                f"`{processed}` processed &nbsp;·&nbsp; "
                f"`{forwarded_count}` forwarded"
            )
        with col_btn:
            if st.button("▶ Process All", type="primary", use_container_width=True):
                st.session_state.inbox_forwarded = set()
                st.session_state.inbox_results = {}
                new_results = {}
                bar = st.progress(0, text="Starting…")
                for i, f in enumerate(SAMPLE_FILES):
                    meta = MOCK_EMAILS.get(f.name, {})
                    sender = meta.get("from_name", f.name)
                    bar.progress((i + 1) / total, text=f"Reading invoice from {sender}…")
                    new_results[f.name] = _process_file(f)
                bar.empty()
                st.session_state.inbox_results = new_results
                st.rerun()

        # ── Forward All button (only when results exist) ───────────────────
        if results:
            ready_names = [
                name for name, r in results.items()
                if "READY" in r["fields"].get("STATUS", r["fields"].get("VALIDITY", "")).upper()
                or "CONFIRMED" in r["fields"].get("STATUS", r["fields"].get("VALIDITY", "")).upper()
            ]
            unforwarded_ready = [n for n in ready_names if n not in st.session_state.inbox_forwarded]
            if unforwarded_ready:
                if st.button(f"📤 Forward All Ready ({len(unforwarded_ready)})", use_container_width=True):
                    for n in unforwarded_ready:
                        st.session_state.inbox_forwarded.add(n)
                    st.rerun()
            elif ready_names:
                st.success(f"✅ All {len(ready_names)} ready invoices have been forwarded.")

        st.divider()

        # ── Inbox rows ────────────────────────────────────────────────────────
        for f in SAMPLE_FILES:
            meta = MOCK_EMAILS.get(f.name, {})
            result = results.get(f.name)
            forwarded = f.name in st.session_state.inbox_forwarded

            if result:
                fields = result["fields"]
                status_raw = fields.get("STATUS", fields.get("VALIDITY", ""))
                dept = fields.get("ROUTED TO", "—")
                amount = fields.get("TOTAL AMOUNT", "")
                s_color, s_bg, s_label = _status_style(status_raw)
                can_forward = "NOT AN INVOICE" not in s_label and "REJECTED" not in s_label
            else:
                s_color, s_bg, s_label = "#6b7280", "#f3f4f6", "● Unprocessed"
                dept = "—"
                amount = ""
                can_forward = False

            row_bg = "#f0fdf4" if forwarded else "#ffffff"
            with st.container():
                st.markdown(f"""
<div style="border:1px solid #e5e7eb; border-radius:8px; padding:12px 16px;
            margin-bottom:8px; background:{row_bg};">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
    <div>
      <div style="font-weight:600; font-size:14px; color:#111827;">
        📧 {meta.get('from_name', f.name)}
      </div>
      <div style="font-size:12px; color:#6b7280; margin-top:2px;">
        {meta.get('subject', '')}
        &nbsp;·&nbsp;
        <span style="font-family:monospace;">📎 {f.name}</span>
      </div>
      {f'<div style="font-size:12px; color:#374151; margin-top:4px;">→ <b>{dept}</b>&nbsp;&nbsp;{amount}</div>' if result else ''}
    </div>
    <div style="display:flex; align-items:center; gap:8px; flex-shrink:0;">
      <span style="background:{s_bg}; color:{s_color}; border:1px solid {s_color};
                   border-radius:12px; padding:3px 10px; font-size:11px; font-weight:600;
                   white-space:nowrap;">
        {s_label}
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

                if result:
                    col_fwd, col_det = st.columns([2, 1])
                    with col_fwd:
                        if forwarded:
                            st.success(f"✅ Forwarded to {dept}")
                        elif can_forward:
                            if st.button(f"📤 Forward to {dept}", key=f"fwd_{f.name}",
                                         use_container_width=True):
                                st.session_state.inbox_forwarded.add(f.name)
                                st.rerun()
                        else:
                            st.error("Not an invoice — return to sender")
                    with col_det:
                        with st.expander("Details"):
                            st.code(result["raw"], language="markdown")

# ══════════════════════════════════════════════════════════════════════════════
with tab_single:
    st.markdown("**Simulate an incoming supplier email with an invoice attachment.**")
    col_a, col_b = st.columns(2)
    with col_a:
        email_from = st.text_input("From (sender)", placeholder="billing@vendor.com")
    with col_b:
        email_subject = st.text_input("Subject", placeholder="Invoice #1234 – June 2026")
    email_body = st.text_area("Email body", placeholder="Please find attached our invoice for...", height=80)
    uploaded = st.file_uploader("📎 Attach invoice (PDF, PNG, JPG, DOCX)",
                                type=["pdf", "png", "jpg", "jpeg", "docx"])

    if uploaded and st.button("📨 Process Email", type="primary", key="single_btn"):
        st.session_state.single_forwarded = False
        email_context = (
            f"From: {email_from}\nSubject: {email_subject}\n"
            f"Body: {email_body}\nAttachment: {uploaded.name}"
        ) if (email_from or email_subject) else ""
        file_bytes = uploaded.read()
        ext = uploaded.name.rsplit(".", 1)[-1].lower()
        with st.spinner("Reading and routing invoice…"):
            if is_native_gemini(uploaded.name):
                raw = process_invoice(file_bytes, mime_for(uploaded.name), email_context)
            elif ext == "docx":
                text = extract_text_from_docx(file_bytes)
                raw = process_invoice_text(f"[From DOCX: {uploaded.name}]\n\n{text}", email_context)
            else:
                st.error("Unsupported format")
                st.stop()
        st.session_state.single_result = {"fields": _parse_result(raw), "raw": raw}
        st.rerun()

    if "single_result" in st.session_state:
        r = st.session_state.single_result
        fields = r["fields"]
        status_raw = fields.get("STATUS", fields.get("VALIDITY", ""))
        dept = fields.get("ROUTED TO", "—")
        s_color, s_bg, s_label = _status_style(status_raw)
        can_forward = "NOT AN INVOICE" not in s_label and "REJECTED" not in s_label

        st.markdown("### Result")
        st.markdown(f"""
<div style="display:flex; gap:10px; margin-bottom:16px; flex-wrap:wrap;">
  <span style="background:{s_color}; color:white; padding:5px 14px;
               border-radius:20px; font-size:13px; font-weight:600;">{s_label}</span>
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

        st.markdown(f"**Routing reason:** {fields.get('REASON', '—')}")
        flags = fields.get("FLAGS", "None")
        if flags and flags.lower() not in ("none", "n/a", ""):
            st.warning(f"⚠️ {flags}")

        st.divider()
        if st.session_state.single_forwarded:
            st.success(f"✅ Invoice forwarded to **{dept}** — awaiting department confirmation.")
        elif can_forward:
            if st.button(f"📤 Forward to {dept}", type="primary", key="single_fwd"):
                st.session_state.single_forwarded = True
                st.rerun()
        else:
            st.error("🚫 Not an invoice — cannot forward.")

        with st.expander("Raw output"):
            st.code(r["raw"], language="markdown")
