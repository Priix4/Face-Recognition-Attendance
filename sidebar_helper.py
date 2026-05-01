import streamlit as st

def hide_default_nav():
    """Hides Streamlit's auto-generated sidebar page list."""
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

def show_sidebar():
    """Shows a clean custom sidebar based on logged-in role."""
    hide_default_nav()

    role     = st.session_state.get("role", None)
    username = st.session_state.get("username", None)

    if not role:
        return

    with st.sidebar:
        st.markdown(f"👋 **{username}**")
        st.markdown(f"🔖 Role: `{role}`")
        st.divider()

        if role == "student":
            st.markdown("**📚 My Pages**")
            st.page_link("pages/2_Student.py",     label="🎓 My Dashboard")
            st.page_link("pages/5_Notes.py",        label="📝 Notes & Announcements")
            st.page_link("pages/6_Timetable.py",    label="📅 Timetable")
            st.page_link("pages/7_Assignments.py",  label="📁 Assignments")

        elif role == "teacher":
            st.markdown("**📚 My Pages**")
            st.page_link("pages/4_Teacher.py",      label="👩‍🏫 Teacher Dashboard")
            st.page_link("pages/1_Face_Scan.py",    label="📸 Face Scan")
            st.page_link("pages/5_Notes.py",        label="📝 Notes & Announcements")
            st.page_link("pages/6_Timetable.py",    label="📅 Timetable")
            st.page_link("pages/7_Assignments.py",  label="📁 Assignments & Gradebook")

        elif role == "admin":
            st.markdown("**📚 My Pages**")
            st.page_link("pages/3_Admin.py",        label="🔐 Admin Panel")
            st.page_link("pages/1_Face_Scan.py",    label="📸 Face Scan")
            st.page_link("pages/4_Teacher.py",      label="👩‍🏫 Teacher Dashboard")
            st.page_link("pages/5_Notes.py",        label="📝 Notes & Announcements")
            st.page_link("pages/6_Timetable.py",    label="📅 Timetable")
            st.page_link("pages/7_Assignments.py",  label="📁 Assignments & Gradebook")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("pages/1_login_page.py")
