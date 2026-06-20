import re
import time
import threading
import streamlit as st
from agents.cv_fraud_agent import analyse_document, verify_employers
from shared.file_utils import mime_for

st.set_page_config(page_title="CV Fraud Detection — Persowerk", page_icon="🔍")
st.title("🔍 CV & Certificate Fraud Detection")
st.caption("Client: Persowerk Deutschland GmbH (Saarbrücken) — Detect AI-generated CVs and fraudulent certificates")


# ── Helpers ────────────────────────────────────────────────────────────────────
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


def _score_color(score_str: str):
    try:
        score = int(re.search(r'\d+', score_str).group())
    except Exception:
        return "#6b7280", "#f3f4f6", score_str
    if score >= 60:
        return "#7f1d1d", "#fff1f2", f"{score}/100 — HIGH RISK"
    elif score >= 30:
        return "#78350f", "#fffbeb", f"{score}/100 — MEDIUM RISK"
    else:
        return "#14532d", "#f0fdf4", f"{score}/100 — LOW RISK"


def _parse_companies(raw: str) -> list:
    if not raw or raw.lower() in ("none", "n/a", ""):
        return []
    return [
        c.strip().lstrip("-•·").strip()
        for c in re.split(r'[,\n]', raw)
        if c.strip().lstrip("-•·").strip()
        and c.strip().lower() not in ("none", "n/a")
    ]


def _parse_verify_results(text: str) -> dict:
    inner = re.search(r'---\s*(.*?)\s*---', text, re.DOTALL)
    content = inner.group(1) if inner else text
    results = {}
    for line in content.strip().split('\n'):
        if re.match(r'(VERIFICATION RESULTS|OVERALL)\s*[:\-]?', line.strip(), re.IGNORECASE):
            continue
        m = re.match(r'^(.+?):\s*(Found|Not Found|Uncertain)\s*[—–-]\s*(.+)$', line.strip(), re.IGNORECASE)
        if m:
            results[m.group(1).strip()] = (m.group(2).strip(), m.group(3).strip())
    return results


def _has_content(val: str) -> bool:
    if not val:
        return False
    v = val.strip().lower()
    return not (v.startswith("none") or v.startswith("n/a") or v in ("—", ""))


def _mime(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    return "application/pdf" if ext == "pdf" else f"image/{ext}"


def _animate(bar, from_pct, to_pct, stop_event, total_seconds=5.0):
    steps = to_pct - from_pct
    if steps <= 0:
        return
    delay = total_seconds / steps
    for p in range(from_pct, to_pct):
        if stop_event.is_set():
            break
        bar.progress(p / 100)
        time.sleep(delay)


# ── Rendering ──────────────────────────────────────────────────────────────────
def show_verdict(result: str, verify_map: dict = None):
    fields    = _parse_result(result)
    score_raw = fields.get("FRAUD RISK SCORE", "?")
    doc_type  = fields.get("DOCUMENT TYPE", "").upper()

    # Fraud score
    score_color, score_bg, score_label = _score_color(score_raw)
    st.markdown(f"""
<div style="background:{score_bg}; border:2px solid {score_color}; border-radius:10px;
            padding:12px 18px; margin-bottom:10px; font-weight:700;
            font-size:17px; color:{score_color};">
  Fraud Score: {score_label}
</div>
""", unsafe_allow_html=True)

    # Employer ticks
    if verify_map:
        cols = st.columns(min(len(verify_map), 5))
        for i, (company, payload) in enumerate(verify_map.items()):
            s = (payload[0] if isinstance(payload, tuple) else "Uncertain").upper()
            icon = "✅" if ("FOUND" in s and "NOT FOUND" not in s) else "❌" if "NOT FOUND" in s else "⚠️"
            cols[i % len(cols)].markdown(f"{icon} {company}")

    # Certificate validity
    cert_expiry = fields.get("CERTIFICATE EXPIRY", "").strip()
    cert_valid  = fields.get("CERTIFICATE CURRENTLY VALID", "").strip().upper()
    if "CERTIFICATE" in doc_type and "CV" not in doc_type and _has_content(cert_expiry):
        if "YES" in cert_valid:
            st.success(f"🗓️ Valid until **{cert_expiry}** ✅")
        elif "NO" in cert_valid:
            st.error(f"🗓️ Expired: **{cert_expiry}** ❌")
        else:
            st.warning(f"🗓️ Expiry: **{cert_expiry}** — could not confirm ⚠️")

    # Key facts
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**Candidate**\n\n{fields.get('CANDIDATE NAME', '—')}")
    c2.markdown(f"**Document**\n\n{fields.get('DOCUMENT TYPE', '—')}")
    c3.markdown(f"**AI Risk**\n\n{fields.get('AI GENERATION RISK', '—')}")

    # Suspicious claims
    suspicious = fields.get("SUSPICIOUS CLAIMS", "")
    if _has_content(suspicious):
        st.error(f"**Suspicious Claims:** {suspicious}")

    # Dynamic details
    real_items = [
        (label, val) for label, val in [
            ("Timeline Issues",           fields.get("TIMELINE ISSUES", "")),
            ("Skill/Experience Mismatch", fields.get("SKILL/EXPERIENCE MISMATCH", "")),
            ("Certificate Flags",         fields.get("CERTIFICATE FLAGS", "")),
        ] if _has_content(val)
    ]
    if real_items:
        with st.expander("Full details"):
            for label, val in real_items:
                st.markdown(f"**{label}:** {val}")


def _analyse_one(file_bytes: bytes, filename: str, bar, status_slot, phase_start: int, phase_end: int):
    """Analyse a single file, animating bar from phase_start to phase_end. Returns (result, verify_map)."""
    mime = _mime(filename)

    # Scan phase
    status_slot.caption(f"🔍 Scanning **{filename}**…")
    scan_end = phase_start + (phase_end - phase_start) // 2
    stop1 = threading.Event()
    t1 = threading.Thread(target=_animate, args=(bar, phase_start, scan_end, stop1, 4.0), daemon=True)
    t1.start()
    result = analyse_document(file_bytes, mime)
    stop1.set(); t1.join()
    bar.progress(scan_end / 100)

    # Verify phase
    fields    = _parse_result(result)
    companies = _parse_companies(fields.get("COMPANIES TO VERIFY", ""))
    verify_map = {}
    if companies:
        status_slot.caption(f"🌐 Verifying employers for **{filename}**…")
        stop2 = threading.Event()
        t2 = threading.Thread(target=_animate, args=(bar, scan_end, phase_end, stop2, 4.0), daemon=True)
        t2.start()
        try:
            verify_map = _parse_verify_results(verify_employers(companies))
        except Exception:
            pass
        stop2.set(); t2.join()

    bar.progress(phase_end / 100)
    return result, verify_map


# ── UI ─────────────────────────────────────────────────────────────────────────
uploaded_files = st.file_uploader(
    "Upload CVs and / or certificates",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
)
st.caption("💡 To upload an entire folder, open it in the file picker and press **Ctrl+A** (or **⌘+A** on Mac) to select all files at once.")

if uploaded_files:
    n = len(uploaded_files)
    st.caption(f"{n} file{'s' if n > 1 else ''} selected")

    if st.button("▶ Analyse All Documents", type="primary"):
        bar      = st.progress(0)
        status   = st.empty()
        st.divider()
        slots    = [st.empty() for _ in uploaded_files]

        per_file = 100 // n  # progress budget per file

        for i, f in enumerate(uploaded_files):
            phase_start = i * per_file
            phase_end   = phase_start + per_file if i < n - 1 else 99
            file_bytes  = f.read()

            result, verify_map = _analyse_one(file_bytes, f.name, bar, status, phase_start, phase_end)

            with slots[i].container(border=True):
                st.markdown(f"**📄 {f.name}**")
                show_verdict(result, verify_map)

        bar.progress(1.0)
        time.sleep(0.3)
        bar.empty()
        status.empty()
