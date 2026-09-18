import streamlit as st
import database
import pandas as pd
from datetime import datetime


def show_portal():
    st.markdown("<h2 style='text-align: left;'>💼 Career Portal: Application Outreach Ledger</h2>",
                unsafe_allow_html=True)
    st.write("---")

    st.subheader("📝 Job Applications Follow-up Matrix")

    # Fetch career ledger lines from database
    raw_applications = database.get_career_notes()

    app_data_list = []
    for idx, r in enumerate(raw_applications):
        try:
            parsed_follow_up = datetime.strptime(r[5], "%d/%m/%Y").date()
        except ValueError:
            parsed_follow_up = datetime.today().date()

        app_data_list.append({
            "S.No": idx + 1,
            "Database ID": r[0],
            "Jobs Role Applied": r[1],
            "Company Name": r[2],
            "Field": r[3],
            "Resume Submitted": r[4],
            "Follow-up Date": parsed_follow_up
        })

    if not app_data_list:
        app_dataframe = pd.DataFrame(
            columns=["S.No", "Database ID", "Jobs Role Applied", "Company Name", "Field", "Resume Submitted",
                     "Follow-up Date"])
    else:
        app_dataframe = pd.DataFrame(app_data_list)

    # Required flags set to False allows cells to be cleanly emptied or wiped out
    edited_apps = st.data_editor(
        app_dataframe,
        key="career_application_spreadsheet_editor",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        disabled=["S.No"],
        column_config={
            "Database ID": None,  # Kept hidden securely from view
            "Jobs Role Applied": st.column_config.TextColumn(required=False),
            "Company Name": st.column_config.TextColumn(required=False),
            "Field": st.column_config.TextColumn(required=False),
            "Resume Submitted": st.column_config.SelectboxColumn(options=["Yes", "No"], required=False),
            "Follow-up Date": st.column_config.DateColumn(format="DD/MM/YYYY", required=False)
        }
    )

    if st.button("💾 Save Changes", use_container_width=True, key="btn_save_career_changes"):
        try:
            current_ids = set(
                edited_apps["Database ID"].dropna().tolist()) if "Database ID" in edited_apps.columns else set()

            # 1. First, wipe out any records that were explicitly dropped or deleted
            for r in raw_applications:
                if r[0] not in current_ids:
                    database.delete_career_note_row(r[0])

            # 2. Next, process the text changes and filter out blanks
            for index, row in edited_apps.iterrows():
                row_id = row.get("Database ID") if pd.notna(row.get("Database ID")) else None
                j_role = row.get("Jobs Role Applied")
                c_name = row.get("Company Name")
                f_field = row.get("Field", "")
                r_sub = row.get("Resume Submitted", "Yes")

                f_date_val = row.get("Follow-up Date")
                if isinstance(f_date_val, str):
                    f_date = f_date_val
                elif hasattr(f_date_val, "strftime"):
                    f_date = f_date_val.strftime("%d/%m/%Y")
                else:
                    f_date = datetime.today().strftime("%d/%m/%Y")

                # Dynamic Cleanse: If you wiped out the data or text fields, delete the row from DB completely
                if pd.isna(j_role) or pd.isna(c_name) or str(j_role).strip() == "" or str(c_name).strip() == "":
                    if row_id is not None:
                        database.delete_career_note_row(row_id)
                else:
                    # Otherwise, save the active application updates safely
                    database.sync_career_note_row(row_id, str(j_role).strip(), str(c_name).strip(),
                                                  str(f_field).strip(), r_sub, f_date)

            st.toast("Career tracker applications synchronized perfectly!")
            st.rerun()
        except Exception as e:
            st.error(f"Career Sync Warning: {e}")
