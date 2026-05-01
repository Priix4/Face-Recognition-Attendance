
import streamlit as st
import subprocess
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar_helper import show_sidebar

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Face Recognition Attendance", layout="wide") # 'wide' helps centering
show_sidebar()

# ---------------- CENTERED UI ----------------
# We create 3 columns. The middle one (2) holds our content.
# The side columns (1.5) act as empty spacers to push content to the middle.
left_spacer, center_col, right_spacer = st.columns([1.5, 2, 1.5])

with center_col:
    st.title("ATTENDANCE DASHBOARD")
    
    subject = st.selectbox(
        "Subject:", 
        ["DBMS", "DSA", "JAVA", "PYTHON", "C++"],
        key="attendance_subject_select"
    )
    
    # The button is now compact and centered with the selectbox
    start_btn = st.button("Start Attendance", type="primary", use_container_width=True)

    if start_btn:
        st.info("📸 Camera window opening... Please wait.")

        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "scanner_runtime.py"
        )

        try:
            result = subprocess.run(
                [sys.executable, "-u", script_path, subject],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=False
            )

            output = result.stdout
            stderr = result.stderr

            if "MARKED_SUCCESSFULLY" in output:
                st.success(f"✅ Attendance marked for **{subject.upper()}**!")
                st.balloons()
            elif "ALREADY_MARKED" in output:
                st.warning(f"⚠️ Already recorded for {subject.upper()} today.")
            elif "SESSION_COMPLETE" in output:
                st.info("Scanner session ended.")
            else:
                st.info("Scanner session ended.")

            # Process output lines
            for line in output.splitlines():
                if line.startswith("ABSENT_MARKED:"):
                    count = line.split(":")[1]
                    st.info(f"📋 {count} student(s) marked Absent.")

            if stderr:
                with st.expander("⚠️ Error details"):
                    st.code(stderr)

        except Exception as e:
            st.error(f"Unexpected error: {e}")

    st.divider()
    st.caption("Tip: If the camera does not open, check if another app is using your webcam.")

