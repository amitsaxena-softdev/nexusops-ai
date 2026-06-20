import streamlit as st
from pathlib import Path
from agents.shift_agent import find_staff
from shared.file_utils import extract_text_from_xlsx, read_sample

st.set_page_config(page_title="Shift Replacement — UKS", page_icon="🏥")
st.title("🏥 Shift Replacement Agent")
st.caption("Client: Universitätsklinikum des Saarlandes (Homburg) — Fill last-minute shift gaps instantly")

SCHEDULE_PATH = Path("samples/hospital_schedule.xlsx")
schedule_text = ""

with st.expander("📅 Roster & schedule (100 staff)"):
    if SCHEDULE_PATH.exists():
        schedule_text = extract_text_from_xlsx(read_sample(SCHEDULE_PATH))
        st.text(schedule_text[:4000])
        if len(schedule_text) > 4000:
            st.caption(f"… {len(schedule_text) - 4000} more characters — full data is passed to the agent")
    else:
        st.info("Schedule file not found in samples/")

st.divider()

DEMO_MESSAGE = (
    "Felix Haddad (HOSP-1059) just called in sick. He was scheduled for tonight's ICU night shift "
    "(19:00–07:00, Saturday 20 June). We need a Registered Nurse with BLS and ACLS. Who can cover?"
)

if "shift_msg" not in st.session_state:
    st.session_state.shift_msg = ""

if st.button("⬇ Load tonight's scenario"):
    st.session_state.shift_msg = DEMO_MESSAGE
    st.rerun()

message = st.text_area(
    "Message the agent — describe the gap in plain language",
    key="shift_msg",
    placeholder=(
        "e.g. Anna Weber called in sick for tonight's ICU night shift (19:00–07:00). "
        "Need a Registered Nurse with BLS and ACLS. Who's available?"
    ),
    height=110,
)

if st.button("Find Staff & Draft Messages", type="primary") and message:
    with st.spinner("Checking roster and schedule..."):
        result = find_staff(message, schedule_text)
    st.markdown("### Available Staff")
    st.markdown(result)
