import streamlit as st
from pathlib import Path
from agents.analytics_agent import analyse_csv_text, analyse_data
from shared.llm import ask_with_file

st.set_page_config(page_title="Customer Analytics — Dr. Theiss", page_icon="📊")
st.title("📊 Customer Analytics Agent")
st.caption("Client: Dr. Theiss Naturwaren GmbH (Homburg) — Behavioural patterns and ad targeting signals")

DR_THEISS_DATA = Path("samples/dr_theiss_data.pdf")

tab_sample, tab_csv, tab_desc = st.tabs(["📂 Dr. Theiss Data Pack", "⬆️ Upload CSV", "✏️ Describe Data"])

with tab_sample:
    if DR_THEISS_DATA.exists():
        st.info("Analyses the Dr. Theiss Allgäuer data pack for customer behavioural patterns and targeting signals.")
        if st.button("Analyse Dr. Theiss Data Pack", type="primary", key="theiss_analytics_btn"):
            file_bytes = DR_THEISS_DATA.read_bytes()
            with st.spinner("Extracting customer insights from data pack..."):
                result = ask_with_file(
                    "Analyse this document for customer behavioural patterns, purchase trends, and generate "
                    "advertising targeting signals. Identify segments, optimal ad timing, and product recommendations. "
                    "Structure your response with: SEGMENTATION, BEHAVIOURAL PATTERNS, TARGETING SIGNALS, "
                    "PRODUCT RECOMMENDATIONS, MEASUREMENT PLAN.",
                    file_bytes, "application/pdf"
                )
            st.markdown("### Analytics Report")
            st.markdown(result)
    else:
        st.info("Dr. Theiss data pack not found in samples/. Use another tab.")

with tab_csv:
    uploaded = st.file_uploader("Upload customer transaction CSV", type=["csv"])
    if uploaded:
        import pandas as pd
        try:
            df = pd.read_csv(uploaded)
            st.dataframe(df.head(20), use_container_width=True)
            st.caption(f"{len(df)} rows × {len(df.columns)} columns")
            if st.button("Analyse for Targeting Signals", type="primary", key="csv_analytics_btn"):
                csv_preview = df.head(200).to_csv(index=False)
                stats = df.describe(include="all").to_string()
                content = f"CSV Preview (first 200 rows):\n{csv_preview}\n\nStatistics:\n{stats}"
                with st.spinner("Detecting patterns and generating targeting signals..."):
                    result = analyse_csv_text(content)
                st.markdown("### Analytics Report")
                st.markdown(result)
        except Exception as e:
            st.error(f"Could not read CSV: {e}")

with tab_desc:
    description = st.text_area(
        "Describe your customer data or paste a summary",
        placeholder="50,000 customers. Peak purchases Sundays. Top products: Vitamin C, Magnesium. Season: Oct–Feb.",
        height=200,
    )
    if st.button("Generate Targeting Analysis", key="desc_analytics_btn") and description:
        with st.spinner("Analysing..."):
            result = analyse_data(description)
        st.markdown("### Analytics Report")
        st.markdown(result)
