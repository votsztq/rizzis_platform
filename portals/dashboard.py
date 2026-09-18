import streamlit as st
import database
from datetime import datetime


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
    # 📝 MAIN TASK LIST VIEW
    # =========================================================
    st.markdown("<h2 style='text-align: left;'>Heart System: Everyday Task Dashboard</h2>", unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns(2)
    with col_nav2:
        if st.button("📈 Go to Analytics", use_container_width=True):
            st.session_state.view_analytics = True
            st.rerun()

    st.write("---")

    raw_tasks = database.get_active_tasks()

    if not raw_tasks:
        st.info("Your task ledger list is currently empty. Click the creation button below to log new objectives!")
    else:
        tasks_per_page = 10
        total_tasks = len(raw_tasks)
        total_pages = (total_tasks + tasks_per_page - 1) // tasks_per_page

        if "current_page" not in st.session_state:
            st.session_state.current_page = 1

        start_idx = (st.session_state.current_page - 1) * tasks_per_page
        end_idx = start_idx + tasks_per_page
        paginated_tasks = raw_tasks[start_idx:end_idx]

        ch1, ch2, ch3, ch4, ch5 = st.columns(5)
        ch1.markdown("**Task Title**")
        ch2.markdown("**Due Date**")
        ch3.markdown("**Priority**")
        ch4.markdown("**Create Date**")
        ch5.markdown("**Category**")
        st.write("---")

        for task in paginated_tasks:
            t_id, t_title, t_due, t_priority, t_create, t_category, _, _, _, _ = task
            c1, c2, c3, c4, c5 = st.columns(5)

            if c1.button(t_title, key=f"btn_task_{t_id}", use_container_width=True):
                st.session_state.selected_task_id = t_id
                st.rerun()

            c2.write(t_due)
            c3.write(t_priority)
            c4.write(t_create)
            c5.write(t_category)

        if total_pages > 1:
            st.write("---")
            page_options = [f"Page {i}" for i in range(1, total_pages + 1)]
            selected_page_str = st.selectbox(
                "Navigate Task Ledger Sheets:",
                page_options,
                index=st.session_state.current_page - 1
            )
            new_page = int(selected_page_str.split(" "))
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

            col_f1, col_f2, col_f3 = st.columns(3)
            f_date = col_f1.date_input("Target Date Limit:", min_value=datetime.today().date())
            f_priority = col_f2.selectbox("Priority Ranking Scale:", ["Low", "Medium", "High", "Critical"])
            f_category = col_f3.selectbox("Pipeline Assignment Module:", [
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
    selected_task = next((t for t in raw_tasks if t == t_id), None)

    if not selected_task:
        st.session_state.selected_task_id = None
        st.rerun()
        return

    _, t_title, t_due, t_priority, t_create, t_category, t_notes, t_desc, t_important, t_ref = selected_task

    h_col1, h_col2 = st.columns(2)
    h_col1.markdown(f"<h2>📋 {t_title} Dashboard Profile</h2>", unsafe_allow_html=True)
    if h_col2.button("✅ Mark as Complete", type="primary", use_container_width=True):
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

        col_t1, col_t2 = st.columns(2)
        updated_due = col_t1.date_input("Alter Target Due Calendar Parameter:", value=parsed_due,
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
    """Routes the internal interface execution into the primary analytics tracking files."""
    import portals.analytics as analytics

    # 1. First, call your active stopwatch and metric visualizations layer script
    analytics.show_portal()

    # 2. Render a permanent return switch button right below the analytics logs
    st.write("---")
    if st.button("⬅️ Return to Core Task Dashboard", use_container_width=True, key="global_analytics_return_btn"):
        st.session_state.view_analytics = False
        st.rerun()

