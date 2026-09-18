import streamlit as st
import database
import pandas as pd
from datetime import datetime


def show_portal():
    st.markdown("<h2 style='text-align: left;'>🎓 Structured Interactive Educational Portal</h2>",
                unsafe_allow_html=True)
    st.write("---")

    if "view_syllabus_overlay" not in st.session_state:
        st.session_state.view_syllabus_overlay = False

    if st.session_state.view_syllabus_overlay:
        render_syllabus_view_window()
        return

    col_h1, col_h2 = st.columns(2)
    with col_h2:
        if st.button("📚 View Syllabus Matrix", use_container_width=True, type="primary"):
            st.session_state.view_syllabus_overlay = True
            st.rerun()

    # ==========================================
    # 💳 PART 1: INTERACTIVE FINANCIAL LEDGER MATRIX
    # ==========================================
    st.subheader("💳 Academic Financial Ledger Grid")
    st.info(
        "Spreadsheet matrix interface. Click the bottom row to add entries. Click the button below to save changes.")

    raw_fees = database.get_education_fees()

    fee_data_list = []
    for idx, r in enumerate(raw_fees):
        try:
            parsed_date = datetime.strptime(r[4], "%d/%m/%Y").date()
        except ValueError:
            parsed_date = datetime.today().date()

        fee_data_list.append({
            "S.No": idx + 1,  # Creates an incremental Serial Number display instead of raw DB key
            "Database ID": r[0],
            "Fee Pending": r[1],
            "Amount (INR)": float(r[2]),
            "University": r[3],
            "Due Date": parsed_date,
            "Semester": r[5]
        })

    if not fee_data_list:
        fee_dataframe = pd.DataFrame(
            columns=["S.No", "Database ID", "Fee Pending", "Amount (INR)", "University", "Due Date", "Semester"])
    else:
        fee_dataframe = pd.DataFrame(fee_data_list)

    edited_data = st.data_editor(
        fee_dataframe,
        key="education_fee_spreadsheet_editor",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        disabled=["S.No", "Database ID"],
        column_config={
            "Database ID": st.column_config.TextColumn(required=False, disabled=True),
            "Fee Pending": st.column_config.SelectboxColumn(
                options=["Examination Fees", "Lab Fees", "Semester Fees"],
                required=True
            ),
            "Amount (INR)": st.column_config.NumberColumn(
                min_value=0,
                format="INR.%d"
            ),
            "University": st.column_config.SelectboxColumn(
                options=["AU", "IGNOU"],
                required=True
            ),
            "Due Date": st.column_config.DateColumn(
                format="DD/MM/YYYY",
                required=True
            ),
            "Semester": st.column_config.SelectboxColumn(
                options=["I", "II", "III", "IV", "V", "VI"],
                required=True
            )
        }
    )

    # Simplified Save Button text requirement
    if st.button("💾 Save Changes", use_container_width=True):
        try:
            current_ids = set(
                edited_data["Database ID"].dropna().tolist()) if "Database ID" in edited_data.columns else set()
            for r in raw_fees:
                if r[0] not in current_ids:
                    database.delete_education_fee_row(r[0])

            for index, row in edited_data.iterrows():
                row_id = row.get("Database ID") if pd.notna(row.get("Database ID")) else None
                f_type = row.get("Fee Pending", "Semester Fees")
                f_amt = row.get("Amount (INR)", 0.0)
                f_uni = row.get("University", "AU")

                f_date_val = row.get("Due Date")
                if isinstance(f_date_val, str):
                    f_date = f_date_val
                elif hasattr(f_date_val, "strftime"):
                    f_date = f_date_val.strftime("%d/%m/%Y")
                else:
                    f_date = datetime.today().strftime("%d/%m/%Y")

                f_sem = row.get("Semester", "I")

                database.sync_education_fee_row(row_id, f_type, f_amt, f_uni, f_date, f_sem)

            st.toast("Academic financial schema layers synchronized perfectly!")
            st.rerun()
        except Exception as e:
            st.error(f"Synchronization Warning: {e}")


def render_syllabus_view_window():
    st.markdown("<h2 style='text-align: left;'>📚 Academic Syllabus & Course Curriculum Matrix</h2>",
                unsafe_allow_html=True)
    if st.button("⬅️ Close Syllabus Matrix Window", use_container_width=True):
        st.session_state.view_syllabus_overlay = False
        st.rerun()
    st.write("---")

    semesters_list = ["Semester I", "Semester II", "Semester III", "Semester IV", "Semester V", "Semester VI"]

    prog1, prog2 = st.columns(2)
    with prog1:
        st.markdown("### 📊 MBA Program Matrix")
        render_program_syllabus_accordion(semesters_list, "MBA")
    with prog2:
        st.markdown("### 🤖 MSc Program Matrix")
        render_program_syllabus_accordion(semesters_list, "MSC")


def render_program_syllabus_accordion(semesters_list, prefix_key):
    for sem_name in semesters_list:
        with st.expander(f"📦 {sem_name} Modules", expanded=False):
            for slot_num in range(1, 7):
                subject_key = f"{prefix_key}_{sem_name}_Slot_{slot_num}"
                current_notes, saved_title = database.get_syllabus_notes(sem_name, subject_key)
                display_title = saved_title if saved_title != subject_key else f"Subject Slot Model {slot_num}"

                st.write("---")
                col_t1, col_t2 = st.columns(2)
                new_title = col_t1.text_input(
                    f"Subject {slot_num} Title:",
                    value=display_title,
                    key=f"title_input_{subject_key}"
                )

                updated_notes = col_t2.text_area(
                    "Study Material / Description Notes:",
                    value=current_notes,
                    key=f"note_input_{subject_key}"
                )

                if updated_notes != current_notes or new_title != display_title:
                    database.update_syllabus_notes(sem_name, subject_key, updated_notes, new_title)
                    st.toast(f"Saved configuration updates for {new_title}!")
