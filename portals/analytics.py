import streamlit as st
import database
import time
import pandas as pd
from datetime import datetime


def show_portal():
    st.markdown("<h2 style='text-align: left;'>📊 Analytics Dashboard & AUX Stopwatch Hub</h2>", unsafe_allow_html=True)
    st.write("---")

    # ==========================================
    # ⏱️ PART 1: THE AUX STOPWATCH CONTROLLER
    # ==========================================
    st.subheader("⏱️ AUX State Control Deck")

    # Initialize operational session indicators
    if "aux_active" not in st.session_state:
        st.session_state.aux_active = False
    if "aux_unit_state" not in st.session_state:
        st.session_state.aux_unit_state = "Offline"
    if "aux_start_timestamp" not in st.session_state:
        st.session_state.aux_start_timestamp = None

    # Sync backgrounds - if active, check elapsed tracking log metrics automatically
    if st.session_state.aux_active and st.session_state.aux_unit_state != "Offline":
        current_now = time.time()
        elapsed_delta = int(current_now - st.session_state.aux_start_timestamp)

        if elapsed_delta >= 1:  # Log delta blocks securely every second
            today_stamp = datetime.now().strftime("%d/%m/%Y")
            database.log_aux_time(today_stamp, st.session_state.aux_unit_state, elapsed_delta)
            st.session_state.aux_start_timestamp = current_now

    # The Start Working Command Box Interface
    with st.form("aux_control_deck"):
        col_ctrl1, col_ctrl2 = st.columns([2, 1])

        target_unit = col_ctrl1.selectbox(
            "Select Current Operational Aux-Unit Environment:",
            ["Available", "Break", "Project", "Education", "Work", "Idle", "Developing", "Offline"]
        )

        action_toggle = col_ctrl2.form_submit_button("⚡ Update Status State", use_container_width=True)

        if action_toggle:
            if target_unit == "Offline":
                st.session_state.aux_active = False
                st.session_state.aux_unit_state = "Offline"
                st.session_state.aux_start_timestamp = None
                st.toast("System logged out. Stopwatch execution paused.")
            else:
                st.session_state.aux_active = True
                st.session_state.aux_unit_state = target_unit
                st.session_state.aux_start_timestamp = time.time()
                st.toast(f"Status tracking engaged: {target_unit}")
            st.rerun()

    # Renders status flags to notify user
    if st.session_state.aux_active:
        st.success(
            f"🟢 Active Session Profile: Tracking system running inside **[{st.session_state.aux_unit_state}]** status framework.")
    else:
        st.info(
            "⚪ Passive Session Profile: Status set to **[Offline]**. Running background stopwatch calculations paused.")

    st.write("---")

    # ==========================================
    # 📈 PART 2: STRUCTURAL LEDGER METRICS & GRAPHS
    # ==========================================
    st.subheader("📈 Performance Ledger Metrics")

    # Selector calendar filters
    col_filter1, col_filter2 = st.columns([1, 2])
    selected_date = col_filter1.date_input("📆 Select a Date to review:", value=datetime.today().date())
    formatted_filter_date = selected_date.strftime("%d/%m/%Y")
    today_stamp_str = datetime.now().strftime("%d/%m/%Y")

    # Calculate current progress arrays from storage
    tasks_completed_count = database.get_completed_tasks_count(formatted_filter_date)
    total_assigned_today = database.get_assigned_tasks_today_count(today_stamp_str)

    # Fetch stopwatch values
    raw_time_map = database.get_aux_time_matrix(formatted_filter_date)

    # Display performance summary parameters inside metric dashboards
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Total Tasks Completed (Selected Date)", tasks_completed_count)
    m_col2.metric("Total Assigned Tasks on Today", total_assigned_today)

    # Calculate Total Active working duration hours cleanly
    total_seconds_logged = sum(raw_time_map.values())
    formatted_hours_sum = round(total_seconds_logged / 3600, 2)
    m_col3.metric("Total Status Review Time (Hours)", f"{formatted_hours_sum} hrs")

    st.write("---")

    # Render Bar Charts detailing Task Category Breakdown
    st.write("### 📦 Completed Tasks Distribution by Category Module")
    cat_distribution_data = database.get_completed_tasks_by_category()

    if cat_distribution_data:
        chart_dataframe = pd.DataFrame(
            list(cat_distribution_data.items()),
            columns=["Pipeline Category", "Total Closed Count"]
        ).set_index("Pipeline Category")
        st.bar_chart(chart_dataframe, use_container_width=True)
    else:
        st.info("No historical analytics available. Complete a task row item to map data charts.")

    # Render data chart for Status Reviews
    st.write("### ⏱️ Total Time on a Status Review (Minutes Spent)")
    if raw_time_map:
        minutes_time_map = {unit: round(sec / 60, 1) for unit, sec in raw_time_map.items()}
        time_dataframe = pd.DataFrame(
            list(minutes_time_map.items()),
            columns=["Aux-Unit", "Minutes Logged"]
        ).set_index("Aux-Unit")
        st.bar_chart(time_dataframe, use_container_width=True)
    else:
        st.info("No stopwatch logs registered for this date timeline.")
