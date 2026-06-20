import streamlit as st
from pathlib import Path
from agents.competitive_agent import analyse_product, get_chat_session
from shared.llm import ask_with_file

st.set_page_config(page_title="Competitive Gap Analysis — Dr. Theiss", page_icon="🔭")
st.title("🔭 Competitive Gap Analysis Agent")
st.caption("Client: Dr. Theiss Naturwaren GmbH (Homburg) — Find white-space opportunities competitors miss")

DR_THEISS_DATA = Path("samples/dr_theiss_data.pdf")

if "comp_session" not in st.session_state:
    st.session_state.comp_session = None
if "comp_messages" not in st.session_state:
    st.session_state.comp_messages = []

tab_sample, tab_quick, tab_chat = st.tabs(["📂 Dr. Theiss Data Pack", "✏️ Quick Analysis", "💬 Research Chat"])

with tab_sample:
    if DR_THEISS_DATA.exists():
        st.info("Benchmarks the full Dr. Theiss Allgäuer product range against competitors to find white-space gaps.")
        if st.button("Run Full Competitive Analysis", type="primary", key="theiss_comp_btn"):
            file_bytes = DR_THEISS_DATA.read_bytes()
            with st.spinner("Benchmarking Dr. Theiss portfolio against competitors..."):
                result = ask_with_file(
                    "You are a competitive intelligence analyst. Extract the product portfolio from this document, "
                    "then for each product category: identify key competitors, map their features and price points, "
                    "and surface white-space gaps Dr. Theiss could exploit. "
                    "Recommend 2–3 new product opportunities per category. "
                    "Focus on the European natural health and pharmacy market.",
                    file_bytes, "application/pdf"
                )
            st.markdown("### Competitive Gap Report")
            st.markdown(result)
    else:
        st.info("Dr. Theiss data pack not found. Use Quick Analysis tab.")

with tab_quick:
    product_input = st.text_area(
        "Describe your product(s) to benchmark",
        placeholder="Dr. Theiss Halsthee — herbal throat tea with sage, thyme, and honey. €3.49 for 20 bags. German pharmacies and DM.",
        height=150,
    )
    if st.button("Run Gap Analysis", type="primary", key="quick_comp_btn") and product_input:
        with st.spinner("Benchmarking against competitors..."):
            result = analyse_product(product_input)
        st.markdown("### Competitive Gap Report")
        st.markdown(result)

with tab_chat:
    st.markdown("Deep-dive research conversation about your competitive landscape.")
    if not st.session_state.comp_session:
        if st.button("Start Research Session", key="start_comp_chat"):
            st.session_state.comp_session = get_chat_session()
            st.session_state.comp_messages = []
            st.rerun()
    else:
        if st.button("↩ New session", key="reset_comp_chat"):
            st.session_state.comp_session = None
            st.session_state.comp_messages = []
            st.rerun()

        for msg in st.session_state.comp_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input("Ask about competitors, gaps, or opportunities...")
        if prompt:
            st.session_state.comp_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Researching..."):
                    response = st.session_state.comp_session.send_message(prompt).text
                st.markdown(response)
            st.session_state.comp_messages.append({"role": "assistant", "content": response})
