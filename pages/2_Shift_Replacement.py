import streamlit as st
from pathlib import Path
from agents.shift_agent import find_staff, STAFF_DB
from shared.file_utils import extract_text_from_xlsx, read_sample

st.set_page_config(page_title="Shift Replacement — UKS", page_icon="🏥")
st.title("🏥 Shift Replacement Agent")
st.caption("Client: Universitätsklinikum des Saarlandes (Homburg) — Fill last-minute shift gaps instantly")

SCHEDULE_PATH = Path("samples/hospital_schedule.xlsx")

with st.expander("📅 View current hospital schedule"):
    if SCHEDULE_PATH.exists():
        schedule_text = extract_text_from_xlsx(read_sample(SCHEDULE_PATH))
        st.text(schedule_text[:3000])
    else:
        st.info("Schedule file not found in samples/")

with st.expander("👥 View available staff database"):
    for s in STAFF_DB:
        st.markdown(
            f"**{s['name']}** ({s['role']}) | "
            f"Quals: {', '.join(s['qualifications'])} | "
            f"Shifts this week: {s['shifts_this_week']} | "
            f"Night available: {'✅' if s['available_nights'] else '❌'}"
        )

st.divider()
st.markdown("**Describe the shift gap:**")

col1, col2 = st.columns(2)
with col1:
    ward = st.text_input("Ward / Department", placeholder="ICU Station 3")
    shift_date = st.date_input("Shift Date")
with col2:
    shift_time = st.selectbox("Shift", ["Night (22:00–06:00)", "Day (06:00–14:00)", "Late (14:00–22:00)"])
    qualification = st.text_input("Required Qualification", placeholder="Intensivpflegefachkraft / ICU")

reason = st.text_input("Reason for gap", placeholder="Called in sick — Anna Weber")
notes = st.text_area(
    "Additional notes",
    placeholder="High patient load expected, minimum 2 years ICU experience required",
    height=80,
)

col_demo, col_run = st.columns([1, 2])
with col_demo:
    if st.button("Load demo gap"):
        st.session_state["demo_gap"] = True
        st.rerun()

if st.session_state.get("demo_gap"):
    ward = "Intensivstation 3 (ICU)"
    qualification = "Intensivpflegefachkraft, Beatmung"
    reason = "Krankheitsfall — Thomas Kraus"
    notes = "Zwei Beatmungspatienten, Erfahrung mit Beatmung zwingend erforderlich"

with col_run:
    if st.button("Find Available Staff & Draft Messages", type="primary"):
        if ward and qualification:
            gap = (
                f"Ward: {ward}\n"
                f"Date: {shift_date}\n"
                f"Shift: {shift_time}\n"
                f"Required qualification: {qualification}\n"
                f"Reason: {reason}\n"
                f"Notes: {notes}"
            )
            with st.spinner("Searching staff database and drafting messages..."):
                result = find_staff(gap)
            st.markdown("### Recommended Staff & Draft Messages")
            st.markdown(result)
        else:
            st.warning("Please fill in ward and required qualification at minimum.")
