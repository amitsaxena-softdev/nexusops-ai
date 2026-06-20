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

# Initialize session state so demo pre-fill works before widgets render
for key, default in [
    ("ward_input", ""),
    ("qual_input", ""),
    ("reason_input", ""),
    ("notes_input", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("**Describe the shift gap:**")

# Demo button fires BEFORE widgets so session state is set on rerun
if st.button("⬇ Load demo gap"):
    st.session_state["ward_input"] = "Intensivstation 3 (ICU)"
    st.session_state["qual_input"] = "Intensivpflegefachkraft, Beatmung"
    st.session_state["reason_input"] = "Krankheitsfall — Thomas Kraus"
    st.session_state["notes_input"] = "Zwei Beatmungspatienten, Erfahrung mit Beatmung zwingend erforderlich"
    st.rerun()

col1, col2 = st.columns(2)
with col1:
    ward = st.text_input(
        "Ward / Department", key="ward_input", placeholder="ICU Station 3"
    )
    shift_date = st.date_input("Shift Date")
with col2:
    shift_time = st.selectbox(
        "Shift", ["Night (22:00–06:00)", "Day (06:00–14:00)", "Late (14:00–22:00)"]
    )
    qualification = st.text_input(
        "Required Qualification", key="qual_input",
        placeholder="Intensivpflegefachkraft / ICU"
    )

reason = st.text_input(
    "Reason for gap", key="reason_input", placeholder="Called in sick — Anna Weber"
)
notes = st.text_area(
    "Additional notes", key="notes_input",
    placeholder="High patient load expected, minimum 2 years ICU experience required",
    height=80,
)

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
