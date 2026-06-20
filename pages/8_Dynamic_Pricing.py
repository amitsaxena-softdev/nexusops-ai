import streamlit as st
from pathlib import Path
from agents.pricing_agent import get_pricing_recommendation, MOCK_SIGNALS
from shared.llm import ask_with_file

st.set_page_config(page_title="Dynamic Pricing — Dr. Theiss", page_icon="💰")
st.title("💰 Dynamic Pricing Agent")
st.caption("Client: Dr. Theiss Naturwaren GmbH (Homburg) — Signal-driven pricing recommendations")

DR_THEISS_DATA = Path("samples/dr_theiss_data.pdf")

with st.expander("📡 Live signals used today"):
    for k, v in MOCK_SIGNALS.items():
        st.markdown(f"**{k.title()}:** {v}")

st.divider()

tab_sample, tab_manual = st.tabs(["📂 From Dr. Theiss Data Pack", "✏️ Enter Product Manually"])

with tab_sample:
    if DR_THEISS_DATA.exists():
        st.info("Extracts product portfolio from the Dr. Theiss data pack and prices them against today's signals.")
        if st.button("Price Dr. Theiss Product Range", type="primary", key="theiss_pricing_btn"):
            file_bytes = DR_THEISS_DATA.read_bytes()
            import datetime
            signals = "\n".join(f"- {k.title()}: {v}" for k, v in MOCK_SIGNALS.items())
            today = datetime.date.today().strftime("%A, %d %B %Y")
            with st.spinner("Analysing product portfolio and generating pricing recommendations..."):
                result = ask_with_file(
                    f"Today is {today}.\n\nExtract the product list from this document, then for each product "
                    f"provide a dynamic pricing recommendation based on these external signals:\n{signals}\n\n"
                    "Format: for each product show CURRENT PRICE (if visible), RECOMMENDED PRICE, CHANGE %, REASONING.",
                    file_bytes, "application/pdf"
                )
            st.markdown("### Pricing Recommendations")
            st.markdown(result)
    else:
        st.info("Dr. Theiss data pack not found. Use manual tab.")

with tab_manual:
    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("Product name", placeholder="Dr. Theiss Vitamin C 1000mg (20 tabs)")
        category = st.selectbox(
            "Category",
            ["Vitamins & Supplements", "Cold & Flu", "Digestion", "Pain Relief", "Skin Care", "Natural Remedies"],
        )
    with col2:
        current_price = st.number_input("Current price (€)", min_value=0.50, max_value=500.0, value=5.99, step=0.10)

    if st.button("Get Pricing Recommendation", type="primary", key="manual_pricing_btn") and product:
        with st.spinner("Analysing signals and computing recommendation..."):
            result = get_pricing_recommendation(product, current_price, category)
        st.markdown("### Pricing Recommendation")
        if "CHANGE: No change" in result:
            st.info("📊 No price change recommended")
        elif "CHANGE: +" in result:
            st.success("📈 Price increase recommended")
        elif "CHANGE: -" in result:
            st.warning("📉 Price decrease recommended")
        st.code(result, language="markdown")
