import streamlit as st

st.set_page_config(
    page_title="NexusOps AI — Agent Suite",
    page_icon="🤖",
    layout="wide",
)

st.title("NexusOps AI — Enterprise Agent Suite")
st.markdown(
    """
    Welcome. Select an agent from the sidebar to get started.

    | # | Agent | Client |
    |---|-------|--------|
    | 1 | Invoice Processing | Globus Group |
    | 2 | Shift Replacement | Universitätsklinikum des Saarlandes |
    | 3 | Work Permit Validation | Leistenschneider Personaldienstleistungen |
    | 4 | CV & Certificate Fraud Detection | Persowerk Deutschland GmbH |
    | 5 | Interview Support | Kohlpharma GmbH |
    | 6 | Marketing Content / Filmmaker | Dr. Theiss Naturwaren GmbH |
    | 7 | Customer Analytics | Dr. Theiss Naturwaren GmbH |
    | 8 | Dynamic Pricing | Dr. Theiss Naturwaren GmbH |
    | 9 | Competitive Gap Analysis | Dr. Theiss Naturwaren GmbH |
    | 10 | Secure Email Agent | Rheinmetall |
    """
)
