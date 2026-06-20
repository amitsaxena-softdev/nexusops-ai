import re
import csv
import time
import streamlit as st
from pathlib import Path
from agents.invoice_agent import parse_invoice, parse_invoice_text, route_invoice
from shared.file_utils import extract_text_from_docx, mime_for, is_native_gemini, read_sample
from shared.theme import apply_theme

st.set_page_config(page_title="Invoice Processing — Globus Group", page_icon="🧾")
apply_theme()
st.title("🧾 Invoice Processing Agent")
st.caption("Client: Globus Group (St. Wendel) — Automated invoice routing from the Finance inbox")

DEMO_EMAIL = "finanzen@globus.de"
_EMAIL_RE  = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

SAMPLES_DIR  = Path("samples/invoices")
SAMPLE_FILES = sorted([f for f in SAMPLES_DIR.iterdir() if f.suffix != ".csv"]) if SAMPLES_DIR.exists() else []

MOCK_EMAILS = {
    "01_stadtwerke_gas_de.pdf":         {"from_name": "Stadtwerke St. Wendel",       "from_email": "rechnung@stadtwerke-stwenden.de",  "subject": "Ihre Rechnung – Gaslieferung Q2 2026",                  "body": "Sehr geehrte Damen und Herren, im Anhang finden Sie unsere aktuelle Rechnung für die Gaslieferung im zweiten Quartal 2026. Bitte überweisen Sie den Betrag innerhalb von 14 Tagen."},
    "02_microsoft_licenses_en.pdf":     {"from_name": "Microsoft Billing",            "from_email": "invoicing@microsoft.com",           "subject": "Microsoft Invoice – Enterprise License Renewal 2026",  "body": "Dear Globus Group, please find attached your invoice for the annual renewal of your Microsoft 365 enterprise licenses. Payment is due within 30 days."},
    "03_eon_strom_de.png":              {"from_name": "E.ON Energie Deutschland",     "from_email": "rechnung@eon.de",                   "subject": "E.ON Stromrechnung – Juni 2026",                       "body": "Sehr geehrte Damen und Herren, anbei erhalten Sie Ihre Stromrechnung für den aktuellen Abrechnungszeitraum."},
    "04_aws_cloud_en.docx":             {"from_name": "Amazon Web Services",          "from_email": "aws-invoices@amazon.com",            "subject": "AWS Invoice – May 2026 Usage Statement",               "body": "Hello, your AWS invoice for the billing period May 2026 is attached."},
    "05_buerobedarf_de.png":            {"from_name": "Office Partner GmbH",          "from_email": "rechnung@officepartner.de",          "subject": "Rechnung Bürobedarf – Bestellung Nr. BP-2026-0541",    "body": "Sehr geehrte Damen und Herren, im Anhang finden Sie die Rechnung für die gelieferten Büromaterialien."},
    "06_brightpath_consulting_en.docx": {"from_name": "Brightpath Consulting Ltd.",   "from_email": "finance@brightpath-consulting.com",  "subject": "Consulting Invoice – Project Alpha Q2 2026",           "body": "Dear Globus Group, please find attached our invoice for consulting services rendered during Q2 2026."},
    "07_hotel_adlon_de.docx":           {"from_name": "Hotel Adlon Kempinski",        "from_email": "reservierung@hotel-adlon.de",       "subject": "Hotelrechnung – Veranstaltung 12. Juni 2026",          "body": "Sehr geehrte Damen und Herren, anbei erhalten Sie die Sammelrechnung für Veranstaltungsräume und Übernachtungen."},
    "08_adobe_creativecloud_en.png":    {"from_name": "Adobe Systems",                "from_email": "invoices@adobe.com",                "subject": "Adobe Creative Cloud for Teams – Invoice June 2026",   "body": "Hello, your Adobe Creative Cloud for Teams subscription invoice for June 2026 is attached."},
    "09_telekom_internet_de.pdf":       {"from_name": "Deutsche Telekom AG",          "from_email": "rechnung@telekom.de",               "subject": "Ihre Telekom Rechnung – Juni 2026",                    "body": "Sehr geehrte Damen und Herren, Ihre monatliche Rechnung für Internet- und Telefondienstleistungen ist beigefügt."},
    "10_dell_hardware_en.png":          {"from_name": "Dell Technologies GmbH",       "from_email": "invoices@dell.com",                 "subject": "Dell Invoice – Hardware Order #DT-2026-88432",         "body": "Dear Globus Group, thank you for your recent hardware purchase. Please find your invoice attached."},
}

MANIFEST = {}
_mp = SAMPLES_DIR / "00_manifest.csv"
if _mp.exists():
    with open(_mp, newline="", encoding="utf-8") as _f:
        for row in csv.DictReader(_f):
            MANIFEST[row["file"]] = row

INBOX_READING_STEPS = [
    (0.15, "Connecting to inbox…"),
    (0.35, "Authenticating…"),
    (0.55, "Scanning for unread emails…"),
    (0.78, f"Found {len(SAMPLE_FILES)} unread supplier invoices…"),
    (0.92, "Preparing to process…"),
    (1.00, "Inbox loaded ✓"),
]

# ── Session state ──────────────────────────────────────────────────────────────
if "inbox_results"   not in st.session_state: st.session_state.inbox_results   = {}
if "inbox_forwarded" not in st.session_state: st.session_state.inbox_forwarded = set()


# ── Helpers ────────────────────────────────────────────────────────────────────
def _make_email_context(meta, filename):
    return (f"From: {meta['from_name']} <{meta['from_email']}>\n"
            f"Subject: {meta['subject']}\nBody: {meta['body']}\nAttachment: {filename}")


def _parse_result(text):
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


def _build_context(meta, manifest_row, filename):
    parts = []
    if meta:
        parts.append(_make_email_context(meta, filename))
    if manifest_row:
        hints = ", ".join(
            f"{k}='{manifest_row[k]}'"
            for k in ("vendor", "invoice_type", "total", "vat_rate", "currency", "language")
            if manifest_row.get(k)
        )
        parts.append(f"Reference hints from our records: {hints}")
    return "\n".join(parts)


def _has_minimum_fields(fields):
    return bool(fields.get("VENDOR") and fields.get("TOTAL AMOUNT"))


def _process_file(f: Path) -> dict:
    meta         = MOCK_EMAILS.get(f.name, {})
    manifest_row = MANIFEST.get(f.name, {})
    context      = _build_context(meta, manifest_row, f.name)
    file_bytes   = read_sample(f)
    ext          = f.suffix.lstrip(".")
    raw_parse, fields = "", {}
    for _ in range(3):
        if is_native_gemini(f.name):
            raw_parse = parse_invoice(file_bytes, mime_for(f.name), context)
        elif ext == "docx":
            raw_parse = parse_invoice_text(extract_text_from_docx(file_bytes), context)
        else:
            break
        fields = _parse_result(raw_parse)
        if _has_minimum_fields(fields):
            break
    raw_route = route_invoice(raw_parse) if raw_parse else ""
    if raw_route:
        fields.update(_parse_result(raw_route))
    return {"fields": fields, "raw": (raw_parse + "\n\n--- ROUTING ---\n\n" + raw_route).strip(), "meta": meta}


def _update_metrics(slot, processed, forwarded, total):
    with slot.container():
        c = st.columns(3)
        c[0].metric("📬 Total Emails", total)
        c[1].metric("⚙️ Processed",    f"{processed}/{total}")
        c[2].metric("✅ Forwarded",     forwarded)


def _strip_status_lines(raw: str) -> str:
    return '\n'.join(
        l for l in raw.split('\n')
        if not re.match(r'^\s*STATUS\s*:', l, re.IGNORECASE)
        and not re.match(r'^\s*STATUS REASON\s*:', l, re.IGNORECASE)
    )


def _render_row(slot, f, result=None, forwarded=False):
    meta         = MOCK_EMAILS.get(f.name, {})
    manifest_row = MANIFEST.get(f.name, {})
    expected     = manifest_row.get("total", "")
    inv_type     = manifest_row.get("invoice_type", "")
    quality      = manifest_row.get("quality", "")
    q_icon       = "📸" if "bad" in quality.lower() else "✅"
    q_desc       = quality.replace("bad", "").strip().strip("()") if "bad" in quality.lower() else "Good quality"

    with slot.container(border=True):
        col_info, col_badge = st.columns([5, 1])
        with col_info:
            st.markdown(f"📧 **{meta.get('from_name', f.name)}** &nbsp; {q_icon} *{q_desc}*")
            st.caption(f"{meta.get('subject', '')} · 📎 `{f.name}`")
            if inv_type or expected:
                st.caption(f"{inv_type}{(' · Expected: ' + expected) if expected else ''}")
        with col_badge:
            if result is None:
                st.caption("📬 Unread")
            elif forwarded:
                st.success("Forwarded")
            else:
                st.caption("⏳ Processing…")

        if result and forwarded:
            dept   = result["fields"].get("ROUTED TO", "—")
            amount = result["fields"].get("TOTAL AMOUNT", "")
            def _n(s): return re.sub(r"[^0-9]", "", s or "")
            acc    = (" · ✅ amount correct"         if expected and _n(amount) == _n(expected)
                      else f" · ⚠️ expected {expected}" if expected
                      else "")
            st.success(f"✅ Forwarded to **{dept}** · {amount}{acc}")
            with st.expander("Details"):
                st.code(_strip_status_lines(result["raw"]), language="markdown")


# ── UI ─────────────────────────────────────────────────────────────────────────
with st.form("inbox_form"):
    email_input = st.text_input("Finance inbox email address", placeholder="finanzen@globus.de")
    submitted   = st.form_submit_button("▶ Process All Invoices", type="primary")

st.caption("ℹ️ This is a prototype — enter **finanzen@globus.de** to load the Globus Finance inbox")

email       = email_input.strip()
valid_email = bool(_EMAIL_RE.match(email)) if email else False
run_demo    = submitted and valid_email and email.lower() == DEMO_EMAIL
no_results  = submitted and valid_email and email.lower() != DEMO_EMAIL
bad_email   = submitted and bool(email) and not valid_email

if run_demo or no_results:
    st.session_state.inbox_results   = {}
    st.session_state.inbox_forwarded = set()

results       = st.session_state.inbox_results
forwarded_set = st.session_state.inbox_forwarded
total         = len(SAMPLE_FILES)
has_run       = bool(results) or run_demo

if bad_email:
    st.error("Please enter a valid email address.")
elif no_results:
    st.info(f"📭 No invoices found in inbox for **{email}**.")
elif has_run:
    st.divider()
    metrics_slot = st.empty()
    bar_slot     = st.empty()
    st.divider()
    row_slots = [st.empty() for _ in SAMPLE_FILES]

    if run_demo:
        # Phase 1 — fake inbox reading (≈ 2 s)
        reading_bar = bar_slot.progress(0)
        for prog, msg in INBOX_READING_STEPS:
            time.sleep(0.33)
            reading_bar.progress(prog, text=msg)
        time.sleep(0.25)
        bar_slot.empty()

        # Show all as unread
        for i, f in enumerate(SAMPLE_FILES):
            _render_row(row_slots[i], f, None, False)
        _update_metrics(metrics_slot, 0, 0, total)

        # Phase 2 — real processing, one by one
        new_results    = {}
        auto_forwarded = set()
        bar = bar_slot.progress(0)

        for i, f in enumerate(SAMPLE_FILES):
            sender = MOCK_EMAILS.get(f.name, {}).get("from_name", f.name)
            bar.progress((i + 1) / total, text=f"Processing invoice from {sender}…")
            result = _process_file(f)
            new_results[f.name] = result
            auto_forwarded.add(f.name)
            _render_row(row_slots[i], f, result, True)
            _update_metrics(metrics_slot, i + 1, i + 1, total)

        bar_slot.empty()
        st.session_state.inbox_results   = new_results
        st.session_state.inbox_forwarded = auto_forwarded

    else:
        _update_metrics(metrics_slot, len(results), len(forwarded_set), total)
        for i, f in enumerate(SAMPLE_FILES):
            _render_row(row_slots[i], f, results.get(f.name), f.name in forwarded_set)
