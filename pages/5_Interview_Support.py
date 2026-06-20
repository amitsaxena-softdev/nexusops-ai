import streamlit as st
from agents.interview_agent import (
    generate_questions, send_followup,
    extract_cv_summary, fetch_job_from_indeed, generate_feedback_letter,
)
from shared.file_utils import mime_for

st.set_page_config(page_title="Interview Support — Kohlpharma", page_icon="💼")
st.title("💼 Interview Support Agent")
st.caption("Client: Kohlpharma GmbH (Merzig) — AI interview coach for non-technical hiring managers")

# ── Session state ──────────────────────────────────────────────────────────────
_DEFAULTS = {
    "interview_started":        False,
    "interview_pack":           None,
    "interview_role":           "",
    "interview_cv_summary":     "",
    "interview_followups":      [],
    "indeed_prefill":           "",
    "interview_feedback":       "",
    "interview_candidate_name": "",
    "sel_key":                  None,
    "sel_item":                 None,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Setup
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.interview_started:

    st.markdown("### Set up the interview")

    indeed_url = st.text_input(
        "Indeed job URL",
        placeholder="https://www.indeed.com/viewjob?jk=…",
    )
    st.caption("Works only when the posting is publicly indexed on Google. If it fails, paste the description below.")

    if st.button("Fetch from Indeed", disabled=not indeed_url.strip()):
        with st.spinner("Fetching job description…"):
            try:
                st.session_state.indeed_prefill = fetch_job_from_indeed(indeed_url.strip())
            except Exception as e:
                st.warning(f"Could not fetch: {e}. Paste manually below.")

    role_input = st.text_area(
        "Job description",
        value=st.session_state.indeed_prefill,
        placeholder="Role title, requirements, responsibilities…",
        height=160,
    )

    cv_file = st.file_uploader(
        "Candidate CV (optional — enables candidate-specific probe questions)",
        type=["pdf", "png", "jpg", "jpeg"],
    )

    st.divider()
    if st.button("▶ Generate Interview Pack", type="primary", disabled=not role_input.strip()):
        cv_summary = ""
        if cv_file:
            with st.spinner("Reading candidate CV…"):
                try:
                    cv_summary = extract_cv_summary(cv_file.read(), mime_for(cv_file.name))
                except Exception as e:
                    st.warning(f"Could not parse CV: {e}")

        with st.spinner("Preparing interview pack…"):
            try:
                pack = generate_questions(role_input, cv_summary)
            except Exception as e:
                st.error(f"Failed to generate questions: {e}")
                st.stop()

        st.session_state.interview_pack       = pack
        st.session_state.interview_role       = role_input
        st.session_state.interview_cv_summary = cv_summary
        st.session_state.interview_started    = True
        st.session_state.interview_followups  = []
        st.session_state.interview_feedback   = ""
        st.session_state.sel_key              = None
        st.session_state.sel_item             = None
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — Interview in progress
# ══════════════════════════════════════════════════════════════════════════════
else:
    pack = st.session_state.interview_pack or {}

    if st.button("↩ Start over with a new role"):
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()

    st.divider()

    # ── Two-column card layout ─────────────────────────────────────────────────
    left, right = st.columns([2, 2.5], gap="large")

    SECTIONS = [
        ("🎯 Technical",   "technical",   False),
        ("🔍 Probe",       "probe",        True),
        ("💬 Behavioural", "behavioural",  False),
        ("⚡ Mini-Tasks",  "mini_tasks",   None),
    ]

    with left:
        with st.container(height=520, border=False):
            for section_label, section_key, has_trigger in SECTIONS:
                items = pack.get(section_key, [])
                if not items:
                    continue
                st.markdown(f"**{section_label}**")
                for i, item in enumerate(items):
                    card_key = f"{section_key}_{i}"
                    is_sel   = st.session_state.sel_key == card_key
                    text     = item.get("q") or item.get("task", "")
                    btn_lbl  = ("✓ " if is_sel else "") + text
                    if st.button(btn_lbl, key=f"btn_{card_key}",
                                 use_container_width=True,
                                 type="primary" if is_sel else "secondary"):
                        st.session_state.sel_key  = card_key
                        st.session_state.sel_item = {"item": item, "section": section_key, "has_trigger": has_trigger}
                        st.rerun()
                st.markdown("")  # spacing between sections

    with right:
        sel = st.session_state.sel_item
        if sel:
            item = sel["item"]
            sec  = sel["section"]
            if sec == "mini_tasks":
                st.markdown("**Task**")
                st.markdown(item.get("task", ""))
                st.divider()
                st.markdown("**What good performance looks like**")
                st.markdown(item.get("tip", ""))
            else:
                st.markdown("**Question**")
                st.markdown(f"> {item.get('q', '')}")
                if sel["has_trigger"] and item.get("trigger"):
                    st.info(f"**Why this question:** {item['trigger']}")
                st.divider()
                st.markdown("**A good answer sounds like**")
                st.markdown(item.get("a", ""))
        else:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.info("← Click any question card to see the expected answer")

    # ── Red flags ──────────────────────────────────────────────────────────────
    red_flags = pack.get("red_flags", [])
    if red_flags:
        st.divider()
        st.markdown("**⚠️ Red Flags to Watch**")
        cols = st.columns(2)
        for i, flag in enumerate(red_flags):
            cols[i % 2].markdown(f"🚩 {flag}")

    # ── Follow-up chat ─────────────────────────────────────────────────────────
    st.divider()
    with st.expander("💬 Ask a follow-up question"):
        for msg in st.session_state.interview_followups:
            icon = "👤" if msg["role"] == "user" else "🤖"
            role_label = "You" if msg["role"] == "user" else "Coach"
            st.markdown(f"{icon} **{role_label}:** {msg['content']}")

        with st.form("followup_form"):
            followup_q = st.text_area(
                "Your question",
                height=80,
                placeholder="e.g. 'The candidate said X — is that a red flag?'",
            )
            send_clicked = st.form_submit_button("Send", type="primary")

        if send_clicked and followup_q.strip():
            with st.spinner("Thinking…"):
                try:
                    reply = send_followup(
                        st.session_state.interview_followups,
                        followup_q.strip(),
                        st.session_state.interview_role,
                    )
                    st.session_state.interview_followups.append({"role": "user",  "content": followup_q.strip()})
                    st.session_state.interview_followups.append({"role": "coach", "content": reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── Post-interview evaluation ──────────────────────────────────────────────
    st.divider()
    st.markdown("### 📋 Post-Interview Evaluation")
    st.caption("Fill this in after the interview to generate a transparent feedback letter for the candidate.")

    with st.form("eval_form"):
        candidate_name = st.text_input("Candidate name", placeholder="e.g. Anna Müller")
        recommendation = st.selectbox(
            "Recommendation",
            ["Proceed to next round", "Hold — needs further evaluation", "Reject"],
        )
        col_s, col_c = st.columns(2)
        with col_s:
            strengths = st.text_area("Strengths observed", height=110,
                                     placeholder="Strong Python, explained Kubernetes clearly…")
        with col_c:
            concerns = st.text_area("Concerns / red flags", height=110,
                                    placeholder="Couldn't explain pipeline failures…")
        submitted = st.form_submit_button("✉️ Generate Candidate Feedback Letter", type="primary")

    if submitted:
        if not candidate_name.strip():
            st.warning("Please enter the candidate's name.")
        else:
            with st.spinner("Writing feedback letter…"):
                try:
                    letter = generate_feedback_letter(
                        role           = st.session_state.interview_role,
                        candidate_name = candidate_name.strip(),
                        strengths      = strengths,
                        concerns       = concerns,
                        recommendation = recommendation,
                    )
                    st.session_state.interview_feedback          = letter
                    st.session_state.interview_candidate_name    = candidate_name.strip()
                except Exception as e:
                    st.error(f"Could not generate letter: {e}")

    if st.session_state.interview_feedback:
        st.divider()
        st.markdown("### ✉️ Candidate Feedback Letter")
        st.info(st.session_state.interview_feedback)
        st.download_button(
            "Download as .txt",
            data     = st.session_state.interview_feedback,
            file_name = f"feedback_{st.session_state.interview_candidate_name.replace(' ', '_')}.txt",
            mime     = "text/plain",
        )
