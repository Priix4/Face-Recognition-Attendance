import streamlit as st
import pandas as pd
import subprocess
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar_helper import show_sidebar

st.set_page_config(page_title="🔐 Admin Panel", layout="wide")
show_sidebar()
st.title("🔐 Admin Panel")

if not st.session_state.get("logged_in") or st.session_state.get("role") != "admin":
    st.error("Admin access required.")
    st.switch_page("pages/1_login_page.py")

# ---------------- FILE PATHS ----------------
BASE_DIR        = r"C:\Users\Priya\OneDrive\Desktop\Face_recognition_Attendance"
STUDENT_FILE    = os.path.join(BASE_DIR, "data", "student_database.csv")
USERS_FILE      = os.path.join(BASE_DIR, "data", "users.csv")
REGISTER_SCRIPT = os.path.join(BASE_DIR, "register_face.py")
TRAIN_SCRIPT    = os.path.join(BASE_DIR, "train_model.py")

# ---------------- LOAD DATA ----------------
@st.cache_data(ttl=10)
def load_students():
    if not os.path.exists(STUDENT_FILE):
        return pd.DataFrame(columns=['username','roll_no','name','department','year','division','email'])
    df = pd.read_csv(STUDENT_FILE, on_bad_lines='skip', engine='python')
    df.columns = df.columns.str.lower().str.strip()
    df['roll_no'] = pd.to_numeric(df['roll_no'], errors='coerce').fillna(0).astype(int)
    return df

@st.cache_data(ttl=10)
def load_users():
    if not os.path.exists(USERS_FILE):
        return pd.DataFrame(columns=['username','password','role'])
    df = pd.read_csv(USERS_FILE, on_bad_lines='skip', engine='python')
    df.columns = df.columns.str.lower().str.strip()
    return df

# ================================================================
# TAB LAYOUT
# ================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "👤 Add New Student",
    "📸 Register Face",
    "🧠 Train Model",
    "📋 View Students"
])

# ================================================================
# TAB 1 — ADD NEW STUDENT
# ================================================================
with tab1:
    st.subheader("👤 Add New Student to Database")
    st.info("Fill in the details below. Username is auto-generated from the name.")

    with st.form("add_student_form"):
        f1, f2 = st.columns(2)
        with f1:
            new_name     = st.text_input("Full Name")
            new_dept     = st.text_input("Department (e.g. TYIT)")
            new_year     = st.selectbox("Year", [1, 2, 3, 4])
            new_roll     = st.number_input("Roll No", min_value=1, step=1)
        with f2:
            new_division = st.selectbox("Division", ["A", "B", "C", "D"])
            new_email    = st.text_input("Email")
            new_password = st.text_input("Password for Login", type="password")

        submitted = st.form_submit_button("➕ Add Student", use_container_width=True, type="primary")

        if submitted:
            # Sanitise — remove commas to prevent CSV corruption
            new_name     = new_name.strip().replace(",", "")
            new_dept     = new_dept.strip().replace(",", "")
            new_email    = new_email.strip().replace(",", "")
            new_password = new_password.strip()

            # Auto-generate username from name
            new_username = "stu_" + new_name.lower().replace(" ", "")

            if not all([new_name, new_dept, new_email, new_password]):
                st.error("❌ Please fill in all fields!")
            else:
                # Always reload fresh before checking
                load_students.clear()
                load_users.clear()
                students_fresh = load_students()
                users_fresh    = load_users()

                roll_exists     = not students_fresh.empty and int(new_roll) in students_fresh['roll_no'].values
                username_exists = not students_fresh.empty and new_username in students_fresh['username'].values

                if roll_exists:
                    st.error(f"❌ Roll No {int(new_roll)} already exists!")
                elif username_exists:
                    st.error(f"❌ Username '{new_username}' already exists!")
                else:
                    # ── Add to student_database.csv ──
                    new_student_row = pd.DataFrame([{
                        'username':   new_username,
                        'roll_no':    int(new_roll),
                        'name':       new_name,
                        'department': new_dept,
                        'year':       new_year,
                        'division':   new_division,
                        'email':      new_email
                    }])
                    df_students_updated = pd.concat([students_fresh, new_student_row], ignore_index=True)
                    df_students_updated.to_csv(STUDENT_FILE, index=False, lineterminator='\n')

                    # ── Add to users.csv ──
                    new_user_row = pd.DataFrame([{
                        'username': new_username,
                        'password': new_password,
                        'role':     'student'
                    }])
                    df_users_updated = pd.concat([users_fresh, new_user_row], ignore_index=True)
                    df_users_updated.to_csv(USERS_FILE, index=False, lineterminator='\n')

                    load_students.clear()
                    load_users.clear()
                    st.success(f"✅ Student **{new_name}** (Roll {int(new_roll)}) added!")
                    st.info(f"👤 Username: `{new_username}` | 🔑 Password: `{new_password}`")
                    st.info("👉 Go to **Register Face** tab next.")

# ================================================================
# TAB 2 — REGISTER FACE
# ================================================================
with tab2:
    st.subheader("📸 Register Face for a Student")
    st.info("Select a student and open the camera to capture their face.")

    students_fresh = load_students()

    if students_fresh.empty:
        st.warning("No students found. Add students first.")
    else:
        dataset_path = os.path.join(BASE_DIR, "dataset")
        registered   = []
        unregistered = []

        for _, row in students_fresh.iterrows():
            folder = os.path.join(dataset_path, str(row['roll_no']))
            if os.path.exists(folder) and len(os.listdir(folder)) >= 10:
                registered.append(f"✅ {row['name']} (Roll {row['roll_no']})")
            else:
                unregistered.append(f"❌ {row['name']} (Roll {row['roll_no']})")

        r1, r2 = st.columns(2)
        with r1:
            st.markdown("**Already Registered:**")
            for r in registered or ["_None yet_"]:
                st.markdown(f"- {r}")
        with r2:
            st.markdown("**Not Yet Registered:**")
            for u in unregistered or ["_All registered!_"]:
                st.markdown(f"- {u}")

        st.markdown("---")

        student_options = {
            f"Roll {row['roll_no']} — {row['name']}": row['roll_no']
            for _, row in students_fresh.sort_values('roll_no').iterrows()
        }
        selected_student = st.selectbox("Select Student to Register", list(student_options.keys()))
        selected_roll    = student_options[selected_student]

        st.warning("Make sure the student is sitting in front of the camera before clicking.")

        if st.button("📸 Start Face Registration", type="primary", use_container_width=True):
            st.info(f"Camera opening for **{selected_student}**... Please wait.")
            try:
                result = subprocess.run(
                    [sys.executable, "-u", REGISTER_SCRIPT, str(selected_roll)],
                    capture_output=True, text=True,
                    encoding='utf-8', errors='replace', check=False
                )
                output = result.stdout
                if "Face registration completed" in output or "Image 25 saved" in output:
                    st.success(f"✅ Face registered for **{selected_student}**! Now go to **Train Model** tab.")
                elif "Failed to access camera" in output:
                    st.error("❌ Camera not accessible.")
                else:
                    st.info("Registration session ended.")
                if result.stderr:
                    with st.expander("⚠️ Error details"):
                        st.code(result.stderr)
            except Exception as e:
                st.error(f"Error: {e}")

# ================================================================
# TAB 3 — TRAIN MODEL
# ================================================================
with tab3:
    st.subheader("🧠 Train Face Recognition Model")
    st.info("Run this after registering faces for new students.")

    dataset_path  = os.path.join(BASE_DIR, "dataset")
    trained_count = 0
    if os.path.exists(dataset_path):
        for folder in os.listdir(dataset_path):
            fp = os.path.join(dataset_path, folder)
            if os.path.isdir(fp) and len(os.listdir(fp)) >= 10:
                trained_count += 1

    st.metric("Students with face data ready", trained_count)

    if trained_count == 0:
        st.warning("No face data found. Register faces first.")
    else:
        if st.button("🧠 Train Model Now", type="primary", use_container_width=True):
            with st.spinner("Training model... please wait."):
                try:
                    result = subprocess.run(
                        [sys.executable, "-u", TRAIN_SCRIPT],
                        capture_output=True, text=True,
                        encoding='utf-8', errors='replace', check=False
                    )
                    if result.returncode == 0:
                        st.success("✅ Model trained successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Training failed.")
                    if result.stdout:
                        with st.expander("📄 Training output"):
                            st.code(result.stdout)
                    if result.stderr:
                        with st.expander("⚠️ Error details"):
                            st.code(result.stderr)
                except Exception as e:
                    st.error(f"Error: {e}")

# ================================================================
# TAB 4 — VIEW / REMOVE STUDENTS
# ================================================================
with tab4:
    st.subheader("📋 All Registered Students")

    students_view = load_students()

    if students_view.empty:
        st.warning("No students found.")
    else:
        search = st.text_input("🔍 Search by name or roll number")
        df_show = students_view.copy()

        if search:
            mask = (
                df_show['name'].str.contains(search, case=False, na=False) |
                df_show['roll_no'].astype(str).str.contains(search)
            )
            df_show = df_show[mask]

        st.dataframe(df_show, use_container_width=True)
        st.caption(f"Total: {len(df_show)} student(s)")

        st.markdown("---")
        st.markdown("### ❌ Remove Student")

        remove_options = {
            f"Roll {row['roll_no']} — {row['name']}": row['roll_no']
            for _, row in load_students().sort_values('roll_no').iterrows()
        }
        student_to_remove = st.selectbox("Select student to remove", list(remove_options.keys()), key="remove_select")
        roll_to_remove    = remove_options[student_to_remove]

        if st.button("🗑️ Remove Student", type="primary", use_container_width=True):
            # Get username before removing
            df_all   = load_students()
            match    = df_all[df_all['roll_no'] == roll_to_remove]
            username_to_remove = match.iloc[0]['username'] if not match.empty else ""

            # Remove from student_database.csv
            df_all = df_all[df_all['roll_no'] != roll_to_remove]
            df_all.to_csv(STUDENT_FILE, index=False, lineterminator='\n')

            # Remove from users.csv
            if os.path.exists(USERS_FILE) and username_to_remove:
                users = load_users()
                users = users[users['username'] != username_to_remove]
                users.to_csv(USERS_FILE, index=False, lineterminator='\n')

            load_students.clear()
            load_users.clear()
            st.success(f"✅ {student_to_remove} removed successfully.")
            st.rerun()