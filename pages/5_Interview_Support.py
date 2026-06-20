import streamlit as st
from pathlib import Path
from agents.interview_agent import get_chat_session, generate_questions
from shared.llm import ask_with_file

st.set_page_config(page_title="Interview Support — Kohlpharma", page_icon="💼")
st.title("💼 Interview Support Agent")
st.caption("Client: Kohlpharma GmbH (Merzig) — AI interview coach for non-technical hiring managers")

JOB_OFFERS_PATH = Path("samples/job_offers.pdf")

if "interview_session" not in st.session_state:
    st.session_state.interview_session = None
if "interview_messages" not in st.session_state:
    st.session_state.interview_messages = []
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if not st.session_state.interview_started:
    st.markdown("### Tell me about the role you're hiring for")

    tab_sample, tab_manual = st.tabs(["📂 Load from Sample Job Offers", "✏️ Enter Manually"])

    with tab_sample:
        if JOB_OFFERS_PATH.exists():
            st.info("We have sample job offers from the hackathon pack. Click below to extract and use them.")
            if st.button("Load Job Offers PDF & Start", type="primary"):
                file_bytes = JOB_OFFERS_PATH.read_bytes()
                with st.spinner("Extracting job descriptions from PDF..."):
                    extracted = ask_with_file(
                        "Extract all job descriptions from this PDF. List each role clearly.",
                        file_bytes, "application/pdf"
                    )
                st.session_state.interview_session = get_chat_session()
                response = generate_questions(extracted, st.session_state.interview_session)
                st.session_state.interview_messages = [
                    {"role": "user", "content": f"[Loaded from job_offers.pdf]\n\n{extracted}"},
                    {"role": "assistant", "content": response},
                ]
                st.session_state.interview_started = True
                st.rerun()
        else:
            st.info("Sample job offers not found. Use the manual tab.")

    with tab_manual:
        role_input = st.text_area(
            "Paste the job description or describe the role",
            placeholder="We're hiring a Senior Data Engineer. Requirements: Python, SQL, cloud experience (AWS/GCP), 5+ years...",
            height=180,
        )
        if st.button("Generate Interview Pack", type="primary") and role_input:
            with st.spinner("Preparing your interview questions and coaching tips..."):
                session = get_chat_session()
                response = generate_questions(role_input, session)
            st.session_state.interview_session = session
            st.session_state.interview_messages = [
                {"role": "user", "content": role_input},
                {"role": "assistant", "content": response},
            ]
            st.session_state.interview_started = True
            st.rerun()

else:
    if st.button("↩ Start over with a new role"):
        st.session_state.interview_session = None
        st.session_state.interview_messages = []
        st.session_state.interview_started = False
        st.rerun()

    for msg in st.session_state.interview_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask a follow-up (e.g. 'The candidate said X, is that a red flag?')")
    if prompt:
        st.session_state.interview_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.interview_session.send_message(prompt).text
            st.markdown(response)
        st.session_state.interview_messages.append({"role": "assistant", "content": response})
