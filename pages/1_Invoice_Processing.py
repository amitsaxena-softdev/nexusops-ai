import re
import csv
import streamlit as st
from pathlib import Path
from agents.invoice_agent import process_invoice, process_invoice_text
from shared.file_utils import extract_text_from_docx, mime_for, is_native_gemini, read_sample

st.set_page_config(page_title="Invoice Processing — Globus Group", page_icon="🧾")
st.title("🧾 Invoice Processing Agent")
st.caption("Client: Globus Group (St. Wendel) — Automated invoice routing from the Finance inbox")

SAMPLES_DIR = Path("samples/invoices")
SAMPLE_FILES = sorted([f for f in SAMPLES_DIR.iterdir() if f.suffix != ".csv"]) if SAMPLES_DIR.exists() else []

# Load ground-truth manifest
MANIFEST = {}
_manifest_path = SAMPLES_DIR / "00_manifest.csv"
if _manifest_path.exists():
    with open(_manifest_path, newline="", encoding="utf-8") as _f:
        for row in csv.DictReader(_f):
            MANIFEST[row["file"]] = row

def _quality_badge(filename: str) -> str:
    q = MANIFEST.get(filename, {}).get("quality", "").lower()
    if "bad" in q:
        detail = q.replace("bad", "").strip().strip("()")
        return f'<span style="background:#fef3c7; color:#92400e; border:1px solid #f59e0b; border-radius:10px; padding:2px 8px; font-size:10px; font-weight:600;">📸 Poor scan{(" · " + detail) if detail else ""}</span>'
    return '<span style="background:#f0fdf4; color:#166534; border:1px solid #16a34a; border-radius:10px; padding:2px 8px; font-size:10px; font-weight:600;">✅ Good quality</span>'

def _accuracy_badge(extracted: str, expected: str) -> str:
    """Compare extracted amount to manifest ground truth — strip non-numeric chars."""
    def _normalise(s):
        return re.sub(r"[^0-9]", "", s or "")
    if not expected:
        return ""
    match = _normalise(extracted) == _normalise(expected)
    if match:
        return f'<span style="background:#f0fdf4; color:#166534; border:1px solid #16a34a; border-radius:10px; padding:2px 8px; font-size:10px; font-weight:600;">✅ Amount correct</span>'
    return f'<span style="background:#fff1f2; color:#991b1b; border:1px solid #dc2626; border-radius:10px; padding:2px 8px; font-size:10px; font-weight:600;">⚠️ Expected {expected}</span>'

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

def _update_metrics(slot, processed, forwarded, held, total):
    with slot.container():
        c = st.columns(4)
        c[0].metric("Total Emails", total)
        c[1].metric("Processed", f"{processed}/{total}")
        c[2].metric("✅ Forwarded", forwarded)
        c[3].metric("⚠️ On Hold", held)


def _render_row(slot, f, result=None, forwarded=False):
    meta = MOCK_EMAILS.get(f.name, {})
    manifest_row = MANIFEST.get(f.name, {})
    expected_total = manifest_row.get("total", "")
    invoice_type = manifest_row.get("invoice_type", "")
    quality = manifest_row.get("quality", "")
    quality_icon = "📸" if "bad" in quality.lower() else "✅"
    quality_desc = quality.replace("bad", "").strip().strip("()") if "bad" in quality.lower() else "Good quality"

    with slot.container(border=True):
        col_info, col_badge = st.columns([5, 1])
        with col_info:
            st.markdown(f"📧 **{meta.get('from_name', f.name)}** &nbsp; {quality_icon} *{quality_desc}*")
            st.caption(f"{meta.get('subject', '')} · 📎 `{f.name}`")
            if invoice_type or expected_total:
                st.caption(f"{invoice_type}{(' · Expected: ' + expected_total) if expected_total else ''}")
        with col_badge:
            if result is None:
                st.caption("📬 Unread")
            else:
                status_raw = result["fields"].get("STATUS", result["fields"].get("VALIDITY", ""))
                _, _, s_label = _status_style(status_raw)
                if forwarded:
                    st.success("Forwarded")
                elif "INCOMPLETE" in s_label.upper() or "REVIEW" in s_label.upper():
                    st.warning("On Hold")
                elif "NOT AN INVOICE" in s_label.upper() or "REJECTED" in s_label.upper():
                    st.error("Not invoice")
                else:
                    st.success("Forwarded")

        if result:
            fields = result["fields"]
            status_raw = fields.get("STATUS", fields.get("VALIDITY", ""))
            dept = fields.get("ROUTED TO", "—")
            amount = fields.get("TOTAL AMOUNT", "")
            _, _, s_label = _status_style(status_raw)
            can_forward = "NOT AN INVOICE" not in s_label.upper() and "REJECTED" not in s_label.upper()

            def _norm(s): return re.sub(r"[^0-9]", "", s or "")
            accuracy_ok = _norm(amount) == _norm(expected_total) if expected_total else None
            acc_str = (" · ✅ amount correct" if accuracy_ok is True
                       else (f" · ⚠️ expected {expected_total}" if accuracy_ok is False else ""))

            if forwarded:
                st.success(f"✅ Forwarded to **{dept}** · {amount}{acc_str}")
            elif not can_forward:
                st.error("❌ Not an invoice — returned to sender")
            else:
                st.warning(f"⚠️ On hold — Finance following up · {dept}")

            with st.expander("Details"):
                st.code(result["raw"], language="markdown")


with tab_inbox:
    if not SAMPLE_FILES:
        st.info("No sample invoices found in samples/invoices/")
    else:
        results = st.session_state.inbox_results
        forwarded_set = st.session_state.inbox_forwarded
        total = len(SAMPLE_FILES)

        col_hdr, col_btn = st.columns([3, 1])
        with col_hdr:
            st.markdown("**📬 finanzen@globus.de** — Finance inbox")
        with col_btn:
            process_clicked = st.button(
                "▶ Process & Route All", type="primary", use_container_width=True
            )

        # Dynamic slots — updated in real time during processing
        metrics_slot = st.empty()
        bar_slot = st.empty()

        # Show current metrics from session state (before any click)
        if results and not process_clicked:
            _update_metrics(metrics_slot, len(results), len(forwarded_set),
                            len(results) - len(forwarded_set), total)

        st.divider()

        # Row slots created upfront — filled below
        row_slots = [st.empty() for _ in SAMPLE_FILES]

        if process_clicked:
            # Reset
            st.session_state.inbox_results = {}
            st.session_state.inbox_forwarded = set()
            new_results = {}
            auto_forwarded = set()

            # Show all emails as unread immediately
            for i, f in enumerate(SAMPLE_FILES):
                _render_row(row_slots[i], f, None, False)

            _update_metrics(metrics_slot, 0, 0, 0, total)
            bar = bar_slot.progress(0, text="Starting…")

            for i, f in enumerate(SAMPLE_FILES):
                sender = MOCK_EMAILS.get(f.name, {}).get("from_name", f.name)
                bar.progress((i + 1) / total, text=f"Processing invoice from {sender}…")

                result = _process_file(f)
                new_results[f.name] = result

                s = result["fields"].get("STATUS", result["fields"].get("VALIDITY", "")).upper()
                if "NOT AN INVOICE" not in s and "REJECTED" not in s:
                    auto_forwarded.add(f.name)

                # Update this row immediately
                _render_row(row_slots[i], f, result, f.name in auto_forwarded)

                # Update metrics immediately
                fwd = len(auto_forwarded)
                _update_metrics(metrics_slot, i + 1, fwd, (i + 1) - fwd, total)

            bar_slot.empty()
            st.session_state.inbox_results = new_results
            st.session_state.inbox_forwarded = auto_forwarded

        else:
            # Restore from session state on any non-button render
            for i, f in enumerate(SAMPLE_FILES):
                _render_row(row_slots[i], f, results.get(f.name), f.name in forwarded_set)

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
        if can_forward:
            st.success(f"✅ Invoice automatically forwarded to **{dept}** — awaiting department confirmation.")
        else:
            st.error("🚫 Not an invoice — returned to sender.")

        with st.expander("Raw output"):
            st.code(r["raw"], language="markdown")
