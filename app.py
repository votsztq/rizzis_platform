import streamlit as st
import os
import sys

# Ensure the current directory path framework is active
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database

st.set_page_config(page_title="RIZZIS Platform", page_icon="🌐", layout="wide")

# Inject bold, underlined sidebar selection links with visual hover zoom transitions
st.markdown("""
    <style>
    div[data-testid="stSidebarNav"] ul {
        list-style-type: none;
        padding-left: 0rem;
    }
    .stRadio > label {
        font-weight: bold !important;
        text-decoration: underline !important;
    }
    .stRadio div[role="radiogroup"] label {
        font-weight: bold !important;
        text-decoration: underline !important;
        padding: 6px 0px;
        transition: transform 0.2s ease, padding-left 0.2s ease;
    }
    .stRadio div[role="radiogroup"] label:hover {
        transform: scale(1.06);
        padding-left: 6px;
        color: #ff4b4b;
    }
    </style>
""", unsafe_allow_html=True)

if "auth_passed" not in st.session_state:
    st.session_state.auth_passed = False
if "screen_acknowledged" not in st.session_state:
    st.session_state.screen_acknowledged = False

# =========================================================
# 🔒 FRAMEWORK STAGE 1: ENTRY AUTHORIZATION PORTAL
# =========================================================
if not st.session_state.auth_passed:
    st.markdown("<h1 style='text-align: left; margin-bottom: 0px;'>Welcome to the RIZZIS</h1>", unsafe_allow_html=True)
    st.write("---")

    # FIX: Explicitly provided the integer argument '2' to create two balanced layout columns
    col_left, col_right = st.columns(2)
    with col_left:
        input_email = st.text_input("User Email Access Address", placeholder="Enter authorization identifier...")
        input_password = st.text_input("Security Access Key", type="password", placeholder="••••••••")

        if st.button("Authorize", use_container_width=True):
            # Strict credential authentication targets validation
            if input_email and input_email.strip() == "rzsiddiq" and input_password == "Agent#1487":
                st.session_state.auth_passed = True
                st.rerun()
            else:
                st.error("Access Denied: Invalid credentials.")

# =========================================================
# 📺 FRAMEWORK STAGE 2: MANDATORY FULL-SCREEN FLASH TIMEOUT
# =========================================================
elif st.session_state.auth_passed and not st.session_state.screen_acknowledged:
    st.write("---")
    st.success("🎉 Authorization Successful!")
    st.markdown("### Accessing Core Platform Framework Subsystems...")

    if st.button("Enter Platform Hub", use_container_width=True):
        st.session_state.screen_acknowledged = True
        st.rerun()

# =========================================================
# 🏛️ FRAMEWORK STAGE 3: THE MAIN MODULAR ROUTING APP
# =========================================================
else:
    st.sidebar.markdown("## 🧭 Navigator Hub")
    st.sidebar.write("---")

    selected_portal = st.sidebar.radio(
        "Select Portal System Options:",
        [
            "Access Dashboard",
            "Access Education portal",
            "Access Career Portal",
            "Access Content creation Portal",
            "Access Projects portal"
        ]
    )

    st.sidebar.write("---")
    if st.sidebar.button("Terminate Session (Logout)", use_container_width=True):
        st.session_state.auth_passed = False
        st.session_state.screen_acknowledged = False
        # Completely clear all session variables to drop cached views instantly upon logout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Routing matrix parsing individual sub-modules cleanly
    try:
        if selected_portal == "Access Dashboard":
            import portals.dashboard as dashboard

            st.session_state.view_analytics = st.session_state.get("view_analytics", False)
            st.session_state.selected_task_id = st.session_state.get("selected_task_id", None)
            dashboard.show_portal()
        elif selected_portal == "Access Education portal":
            import portals.education as education

            education.show_portal()
        elif selected_portal == "Access Career Portal":
            import portals.career as career

            career.show_portal()
        elif selected_portal == "Access Content creation Portal":
            import portals.content as content

            content.show_portal()
        elif selected_portal == "Access Projects portal":
            import portals.projects as projects

            projects.show_portal()
    except Exception as err:
        st.warning(f"🔄 Module tracking update initialization event active: {err}")
