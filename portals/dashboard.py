import streamlit as st
import database
from datetime import datetime
import pandas as pd


def show_portal():
    if "view_analytics" not in st.session_state:
        st.session_state.view_analytics = False
    if "selected_task_id" not in st.session_state:
        st.session_state.selected_task_id = None
    if "show_creation_form" not in st.session_state:
        st.session_state.show_creation_form = False

    if st.session_state.view_analytics:
        render_analytics_dashboard()
        return

    if st.session_state.selected_task_id is not None:
        render_task_details_page()
        return

    # =========================================================
    # 📝 MAIN TASK LIST VIEW (Mobile-Responsive Layout Optimization)
    # =========================================================
    st.markdown("<h2 style='text-align: left;'>Heart System: Everyday Task Dashboard</h2>", unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav2:
        if st.button("📈 Go to Analytics", use_container_width=True):
            st.session_state.view_analytics = True
            st.rerun()

    st.write("---")

    raw_tasks = database.get_active_tasks()

    if not raw_tasks:
        st.info("Your task ledger list is currently empty. Click the creation button below to log new objectives!")
    else:
        # Core Pagination calculations
        tasks_per_page = 10
        total_tasks = len(raw_tasks)
        total_pages = (total_tasks + tasks_per_page - 1) // tasks_per_page

        if "current_page" not in st.session_state:
            st.session_state.current_page = 1

        start_idx = (st.session_state.current_page - 1) * tasks_per_page
        end_idx = start_idx + tasks_per_page
        paginated_tasks = raw_tasks[start_idx:end_idx]

        # 📱 OPTIMIZATION: Convert the data into a clean structure for unified rendering
        tasks_list = []
        for task in paginated_tasks:
            t_id, t_title, t_due, t_priority, t_create, t_category, _, _, _, _ = task
            tasks_list.append({
                "Task ID": t_id,
                "Task Title": t_title,
                "Due Date": t_due,
                "Priority": t_priority,
                "Create Date": t_create,
                "Category": t_category
            })

        df = pd.DataFrame(tasks_list)

        st.write("### 📝 Active Project Tasks")
        st.info(
            "📱 Mobile Users: You can scroll the table horizontally. Click on a task title cell row selection dropdown below to view or configure full rich detail parameters.")

        # We render a clean, standard data sheet layout instead of structural horizontal text column blocks
        # This keeps headers locked perfectly in place on mobile devices!
        st.dataframe(
            df[["Task Title", "Due Date", "Priority", "Create Date", "Category"]],
            use_container_width=True,
            hide_index=True
        )

        # Clean mobile selector drawer block to view rich details without columns misalignment
        st.write("---")
        task_options = {t["Task Title"]: t["Task ID"] for t in tasks_list}
        selected_task_title = st.selectbox("🔍 Select a specific task row line item to inspect/edit:",
                                           ["-- Choose a Task --"] + list(task_options.keys()))

        if selected_task_title != "-- Choose a Task --":
            st.session_state.selected_task_id = task_options[selected_task_title]
            st.rerun()

        if total_pages > 1:
            st.write("---")
            page_options = [f"Page {i}" for i in range(1, total_pages + 1)]
            selected_page_str = st.selectbox(
                "Navigate Task Ledger Sheets:",
                page_options,
                index=st.session_state.current_page - 1
            )
            new_page = int(selected_page_str.split(" ")[1])
            if new_page != st.session_state.current_page:
                st.session_state.current_page = new_page
                st.rerun()

    # =========================================================
    # ➕ REPOSITIONED TASK CREATION DECK (Toggle View Button)
    # =========================================================
    st.write("---")

    if not st.session_state.show_creation_form:
        if st.button("➕ Create Task", use_container_width=True, type="primary"):
            st.session_state.show_creation_form = True
            st.rerun()
    else:
        st.markdown("### ➕ Register New Task Specifications")
        if st.button("❌ Collapse Creation Panel", use_container_width=True):
            st.session_state.show_creation_form = False
            st.rerun()

        with st.form("dashboard_task_form", clear_on_submit=True):
            f_title = st.text_input("Task Title / Wording Object:", placeholder="e.g. Complete MSc Assignment")
            f_desc = st.text_area("Task Details Description:",
                                  placeholder="Enter full details about what needs to be complete...")
            f_important = st.text_area("Important Alert Instructions:",
                                       value="Please note in the case the following action was not complete setup appropriate follow-up")
            f_ref = st.text_input("Reference Target Link URL Address Path:", value="https://sample.com")

            # Form fields stack cleanly on mobile natively
            f_date = st.date_input("Target Date Limit:", min_value=datetime.today().date())
            f_priority = st.selectbox("Priority Ranking Scale:", ["Low", "Medium", "High", "Critical"])
            f_category = st.selectbox("Pipeline Assignment Module:", [
                "Job Applications", "MBA Studies", "MSc Studies", "Content Creation", "Misc Works"
            ])

            if st.form_submit_button("Submit & Initialize Task", use_container_width=True):
                if f_title and f_title.strip() != "":
                    database.add_task(
                        f_title.strip(),
                        f_date.strftime("%d/%m/%Y"),
                        f_priority,
                        f_category,
                        f_desc.strip(),
                        f_important.strip(),
                        f_ref.strip()
                    )
                    st.session_state.show_creation_form = False
                    st.toast("Task registered safely inside data schemas!")
                    st.rerun()
                else:
                    st.error("Task description value cannot be empty.")


def render_task_details_page():
    t_id = st.session_state.selected_task_id
    raw_tasks = database.get_active_tasks()
    selected_task = next((t for t in raw_tasks if t[0] == t_id), None)

    if not selected_task:
        st.session_state.selected_task_id = None
        st.rerun()
        return

    _, t_title, t_due, t_priority, t_create, t_category, t_notes, t_desc, t_important, t_ref = selected_task

    st.markdown(f"<h2>📋 {t_title} Dashboard Profile</h2>", unsafe_allow_html=True)
    if st.button("✅ Mark as Complete", type="primary", use_container_width=True):
        database.complete_task(t_id)
        st.success("Task shifted out of active pipelines.")
        st.session_state.selected_task_id = None
        st.rerun()

    if st.button("⬅️ Return to Main Board Panel", use_container_width=True):
        st.session_state.selected_task_id = None
        st.rerun()

    st.write("---")

    tab1, tab2, tab3 = st.tabs(["📄 Task Details", "⚠️ Important Rules", "🔗 Reference Mappings"])

    with tab1:
        st.markdown(f"### 📋 Task Details Spec (Due on {t_due})")
        updated_desc = st.text_area("Edit Task Details Text Content:", value=t_desc if t_desc else "", height=150)

        parsed_due = datetime.today().date()
        if t_due:
            try:
                parsed_due = datetime.strptime(t_due.strip(), "%d/%m/%Y").date()
            except ValueError:
                pass

        updated_due = st.date_input("Alter Target Due Calendar Parameter:", value=parsed_due,
                                    min_value=datetime.today().date())

    with tab2:
        st.markdown("### ⚠️ Important Notice Container Layer")
        updated_important = st.text_area("Alert Context Line (Editable):", value=t_important if t_important else "",
                                         height=100)
        st.warning(updated_important)

    with tab3:
        st.markdown("### 🔗 Structural Connection Hyperlinks")
        updated_ref = st.text_input("Reference Target Link URL Address Path:", value=t_ref if t_ref else "https://")
        if updated_ref.startswith("http"):
            st.markdown(f"👉 **Live Target Hyperlink:** [{updated_ref}]({updated_ref})")

    st.write("---")
    st.markdown("### 💾 Add Completion Notes")
    updated_notes = st.text_area("Annotation Logging Lines:", value=t_notes if t_notes else "",
                                 placeholder="Log updates before saving...")

    if st.button("💾 Save Matrix Parameters & Notes", use_container_width=True):
        database.update_task_details(
            t_id,
            updated_due.strftime("%d/%m/%Y"),
            updated_notes.strip(),
            updated_desc.strip(),
            updated_important.strip(),
            updated_ref.strip()
        )
        st.toast("Database parameters saved!")
        st.rerun()


def render_analytics_dashboard():
    import portals.analytics as analytics
    analytics.show_portal()
    st.write("---")
    if st.button("⬅️ Return to Core Task Dashboard", use_container_width=True):
        st.session_state.view_analytics = False
        st.rerun()
