import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar_helper import show_sidebar

st.set_page_config(page_title="📁 Assignments", layout="wide")
show_sidebar()

if not st.session_state.get("logged_in"):
    st.switch_page("pages/1_login_page.py")

BASE_DIR          = r"C:\Users\Priya\OneDrive\Desktop\Face_recognition_Attendance"
ASSIGNMENTS_FILE  = os.path.join(BASE_DIR, "data", "assignments.csv")
SUBMISSIONS_FILE  = os.path.join(BASE_DIR, "data", "submissions.csv")
GRADES_FILE       = os.path.join(BASE_DIR, "data", "grades.csv")
ASSIGNMENTS_DIR   = os.path.join(BASE_DIR, "assignments")    # teacher uploaded PDFs
SUBMISSIONS_DIR   = os.path.join(BASE_DIR, "submissions")    # student uploaded PDFs

# ── Create folders and CSVs if missing ──
os.makedirs(ASSIGNMENTS_DIR, exist_ok=True)
os.makedirs(SUBMISSIONS_DIR, exist_ok=True)

if not os.path.exists(ASSIGNMENTS_FILE):
    pd.DataFrame(columns=["id","title","subject","due_date","posted_by","posted_on","filename","filepath"]).to_csv(ASSIGNMENTS_FILE, index=False)

if not os.path.exists(SUBMISSIONS_FILE):
    pd.DataFrame(columns=["submission_id","assignment_id","roll_no","student_name","filename","filepath","submitted_on"]).to_csv(SUBMISSIONS_FILE, index=False)

if not os.path.exists(GRADES_FILE):
    pd.DataFrame(columns=["submission_id","assignment_id","roll_no","student_name","marks","out_of","feedback","graded_by","graded_on"]).to_csv(GRADES_FILE, index=False)

# ── Loaders ──
@st.cache_data(ttl=5)
def load_assignments():
    df = pd.read_csv(ASSIGNMENTS_FILE, on_bad_lines='skip', engine='python')
    df.columns = df.columns.str.lower().str.strip()
    return df

@st.cache_data(ttl=5)
def load_submissions():
    df = pd.read_csv(SUBMISSIONS_FILE, on_bad_lines='skip', engine='python')
    df.columns = df.columns.str.lower().str.strip()
    return df

@st.cache_data(ttl=5)
def load_grades():
    df = pd.read_csv(GRADES_FILE, on_bad_lines='skip', engine='python')
    df.columns = df.columns.str.lower().str.strip()
    return df

def clear_cache():
    load_assignments.clear()
    load_submissions.clear()
    load_grades.clear()

role     = st.session_state.get("role", "student")
username = st.session_state.get("username", "")
roll_no  = st.session_state.get("roll_no", None)

st.title("📁 Assignment Portal")

# ================================================================
# TEACHER / ADMIN — Post PDF assignment + Gradebook
# ================================================================
if role in ["teacher", "admin"]:
    tab1, tab2 = st.tabs(["📤 Post Assignment", "📊 Gradebook"])

    # ── TAB 1: Post Assignment as PDF ──
    with tab1:
        st.subheader("📤 Post New Assignment")
        st.info("Upload a PDF file with the assignment instructions. Students will be able to download it.")

        with st.form("post_assignment_form"):
            c1, c2 = st.columns(2)
            with c1:
                title    = st.text_input("Assignment Title", placeholder="e.g. Unit 3 ER Diagram")
                subject  = st.text_input("Subject", placeholder="e.g. DBMS")
                due_date = st.date_input("Due Date")
            with c2:
                uploaded_pdf = st.file_uploader(
                    "📎 Upload Assignment File (PDF / Word / Image)",
                    type=["pdf", "docx", "doc", "png", "jpg", "jpeg", "txt"]
                )

            if st.form_submit_button("📤 Post Assignment", type="primary", use_container_width=True):
                if not title or not subject:
                    st.error("❌ Title and Subject are required!")
                elif uploaded_pdf is None:
                    st.error("❌ Please upload an assignment file!")
                else:
                    # Save file to assignments folder
                    safe_name = f"asgn_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_pdf.name.replace(' ', '_')}"
                    save_path = os.path.join(ASSIGNMENTS_DIR, safe_name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_pdf.getbuffer())

                    df = load_assignments()
                    new_id = int(df["id"].max() + 1) if not df.empty else 1

                    new_row = pd.DataFrame([{
                        "id":        new_id,
                        "title":     title.replace(",", ""),
                        "subject":   subject.replace(",", ""),
                        "due_date":  str(due_date),
                        "posted_by": username,
                        "posted_on": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "filename":  safe_name,
                        "filepath":  save_path
                    }])
                    df_updated = pd.concat([df, new_row], ignore_index=True)
                    df_updated.to_csv(ASSIGNMENTS_FILE, index=False, lineterminator='\n')
                    clear_cache()
                    st.success(f"✅ Assignment '{title}' posted with file: **{uploaded_pdf.name}**")
                    st.rerun()

        # ── List all posted assignments ──
        st.divider()
        st.markdown("### 📋 All Posted Assignments")
        assignments = load_assignments()

        if assignments.empty:
            st.info("No assignments posted yet.")
        else:
            for _, asgn in assignments.sort_values("posted_on", ascending=False).iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 2, 1])
                    with c1:
                        st.markdown(f"**{asgn['title']}** — `{asgn['subject']}`")
                        st.caption(f"📅 Due: {asgn['due_date']} | Posted by {asgn['posted_by']} on {asgn['posted_on']}")
                    with c2:
                        # Download button for the assignment file
                        fp = str(asgn.get("filepath", ""))
                        fn = str(asgn.get("filename", "file"))
                        if fp and os.path.exists(fp):
                            with open(fp, "rb") as f:
                                st.download_button(
                                    label="⬇️ Download File",
                                    data=f.read(),
                                    file_name=fn,
                                    mime="application/octet-stream",
                                    key=f"dl_asgn_{asgn['id']}"
                                )
                        else:
                            st.warning("File missing")
                    with c3:
                        if st.button("🗑️ Delete", key=f"del_{asgn['id']}"):
                            df = load_assignments()
                            df = df[df["id"] != asgn["id"]]
                            df.to_csv(ASSIGNMENTS_FILE, index=False, lineterminator='\n')
                            clear_cache()
                            st.rerun()

    # ── TAB 2: Gradebook ──
    with tab2:
        st.subheader("📊 Gradebook — Review & Grade Submissions")

        submissions = load_submissions()
        assignments = load_assignments()
        grades      = load_grades()

        if submissions.empty:
            st.info("📭 No submissions received yet.")
        else:
            # Filter by assignment
            asgn_options = {"All": None}
            if not assignments.empty:
                for _, row in assignments.iterrows():
                    asgn_options[f"{row['title']} (ID {row['id']})"] = row["id"]

            selected_label = st.selectbox("Filter by Assignment", list(asgn_options.keys()))
            selected_id    = asgn_options[selected_label]
            subs_view      = submissions if selected_id is None else submissions[submissions["assignment_id"] == selected_id]

            # Metrics
            total   = len(subs_view)
            graded  = len(subs_view[subs_view["submission_id"].isin(grades["submission_id"])]) if not grades.empty else 0
            pending = total - graded

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Submissions", total)
            m2.metric("✅ Graded",          graded)
            m3.metric("⏳ Pending",         pending)
            st.divider()

            for _, sub in subs_view.iterrows():
                already_graded = not grades.empty and (grades["submission_id"] == sub["submission_id"]).any()
                badge = "✅ Graded" if already_graded else "⏳ Pending"

                with st.expander(f"{badge}  |  {sub['student_name']} (Roll {sub['roll_no']})  |  {sub['submitted_on']}"):

                    # Download student submission
                    fp = str(sub.get("filepath", ""))
                    fn = str(sub.get("filename", "submission"))
                    if fp and os.path.exists(fp):
                        with open(fp, "rb") as f:
                            st.download_button(
                                label=f"⬇️ Download Submission: {fn}",
                                data=f.read(),
                                file_name=fn,
                                mime="application/octet-stream",
                                key=f"dl_sub_{sub['submission_id']}"
                            )
                    else:
                        st.warning("⚠️ Submission file not found.")

                    st.divider()

                    # Grade or show existing grade
                    if already_graded:
                        gr = grades[grades["submission_id"] == sub["submission_id"]].iloc[0]
                        st.success(f"**Marks: {gr['marks']} / {gr['out_of']}**")
                        st.info(f"💬 Feedback: {gr['feedback']}")
                        st.caption(f"Graded by {gr['graded_by']} on {gr['graded_on']}")
                    else:
                        with st.form(f"grade_{sub['submission_id']}"):
                            g1, g2 = st.columns(2)
                            with g1:
                                marks  = st.number_input("Marks", min_value=0, max_value=100, step=1)
                                out_of = st.number_input("Out Of", min_value=1, max_value=100, value=10, step=1)
                            with g2:
                                feedback = st.text_area("Feedback to Student", height=100)

                            if st.form_submit_button("✅ Submit Grade", type="primary", use_container_width=True):
                                df_grades = load_grades()
                                new_grade = pd.DataFrame([{
                                    "submission_id": sub["submission_id"],
                                    "assignment_id": sub["assignment_id"],
                                    "roll_no":       sub["roll_no"],
                                    "student_name":  sub["student_name"],
                                    "marks":         marks,
                                    "out_of":        out_of,
                                    "feedback":      feedback.replace(",", ""),
                                    "graded_by":     username,
                                    "graded_on":     datetime.now().strftime("%Y-%m-%d %H:%M")
                                }])
                                df_updated = pd.concat([df_grades, new_grade], ignore_index=True)
                                df_updated.to_csv(GRADES_FILE, index=False, lineterminator='\n')
                                clear_cache()
                                st.success("✅ Grade submitted!")
                                st.rerun()

# ================================================================
# STUDENT — Download assignment PDF + Upload submission
# ================================================================
elif role == "student":
    tab1, tab2 = st.tabs(["📋 My Assignments", "📊 My Grades"])

    with tab1:
        st.subheader("📋 Your Assignments")
        assignments = load_assignments()
        submissions = load_submissions()

        if assignments.empty:
            st.info("📭 No assignments posted yet. Check back later.")
        else:
            for _, asgn in assignments.sort_values("due_date").iterrows():

                already_submitted = (
                    not submissions.empty and
                    ((submissions["assignment_id"] == asgn["id"]) &
                     (submissions["roll_no"] == roll_no)).any()
                )

                try:
                    overdue = pd.Timestamp.today() > pd.to_datetime(asgn["due_date"]) and not already_submitted
                except:
                    overdue = False

                status = "✅ Submitted" if already_submitted else ("🔴 Overdue" if overdue else "⏳ Pending")

                with st.container(border=True):
                    c1, c2 = st.columns([5, 2])
                    with c1:
                        st.markdown(f"### {asgn['title']}  `{asgn['subject']}`")
                        col1, col2, col3 = st.columns(3)
                        col1.markdown(f"📅 **Due:** {asgn['due_date']}")
                        col2.markdown(f"👩‍🏫 **By:** {asgn['posted_by']}")
                        col3.markdown(f"**Status:** {status}")
                    with c2:
                        # Download assignment PDF posted by teacher
                        fp = str(asgn.get("filepath", ""))
                        fn = str(asgn.get("filename", "assignment"))
                        if fp and os.path.exists(fp):
                            with open(fp, "rb") as f:
                                st.download_button(
                                    label="⬇️ Download Assignment",
                                    data=f.read(),
                                    file_name=fn,
                                    mime="application/octet-stream",
                                    key=f"dl_asgn_stu_{asgn['id']}"
                                )

                    st.divider()

                    if already_submitted:
                        my_sub = submissions[
                            (submissions["assignment_id"] == asgn["id"]) &
                            (submissions["roll_no"] == roll_no)
                        ].iloc[0]
                        st.success(f"✅ Submitted: **{my_sub['filename']}** on {my_sub['submitted_on']}")

                        # Resubmit option
                        with st.expander("🔄 Resubmit (replaces previous)"):
                            new_file = st.file_uploader(
                                "Upload new file",
                                type=["pdf", "docx", "doc", "png", "jpg", "jpeg", "txt"],
                                key=f"resub_{asgn['id']}"
                            )
                            if st.button("🔄 Resubmit", key=f"resub_btn_{asgn['id']}"):
                                if new_file is None:
                                    st.error("❌ Please select a file!")
                                else:
                                    safe_name = f"roll{roll_no}_asgn{asgn['id']}_{new_file.name.replace(' ', '_')}"
                                    save_path = os.path.join(SUBMISSIONS_DIR, safe_name)
                                    with open(save_path, "wb") as f:
                                        f.write(new_file.getbuffer())

                                    df_subs = load_submissions()
                                    df_subs.loc[
                                        (df_subs["assignment_id"] == asgn["id"]) &
                                        (df_subs["roll_no"] == roll_no),
                                        ["filename", "filepath", "submitted_on"]
                                    ] = [safe_name, save_path, datetime.now().strftime("%Y-%m-%d %H:%M")]
                                    df_subs.to_csv(SUBMISSIONS_FILE, index=False, lineterminator='\n')
                                    clear_cache()
                                    st.success("✅ Resubmitted successfully!")
                                    st.rerun()

                    elif not overdue:
                        uploaded_file = st.file_uploader(
                            "📎 Upload your completed assignment (PDF / Word / Image)",
                            type=["pdf", "docx", "doc", "png", "jpg", "jpeg", "txt"],
                            key=f"upload_{asgn['id']}"
                        )
                        if st.button("📤 Submit Assignment", type="primary",
                                     use_container_width=True, key=f"submit_{asgn['id']}"):
                            if uploaded_file is None:
                                st.error("❌ Please select a file to upload!")
                            else:
                                safe_name = f"roll{roll_no}_asgn{asgn['id']}_{uploaded_file.name.replace(' ', '_')}"
                                save_path = os.path.join(SUBMISSIONS_DIR, safe_name)
                                with open(save_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())

                                df_subs = load_submissions()
                                new_id  = int(df_subs["submission_id"].max() + 1) if not df_subs.empty else 1
                                new_sub = pd.DataFrame([{
                                    "submission_id": new_id,
                                    "assignment_id": asgn["id"],
                                    "roll_no":       roll_no,
                                    "student_name":  username,
                                    "filename":      safe_name,
                                    "filepath":      save_path,
                                    "submitted_on":  datetime.now().strftime("%Y-%m-%d %H:%M")
                                }])
                                df_updated = pd.concat([df_subs, new_sub], ignore_index=True)
                                df_updated.to_csv(SUBMISSIONS_FILE, index=False, lineterminator='\n')
                                clear_cache()
                                st.success(f"✅ **{uploaded_file.name}** submitted successfully!")
                                st.balloons()
                                st.rerun()
                    else:
                        st.error("🔴 Submission deadline has passed. Contact your teacher.")

    # ── TAB 2: My Grades ──
    with tab2:
        st.subheader("📊 My Grades")
        grades      = load_grades()
        assignments = load_assignments()
        my_grades   = grades[grades["roll_no"] == roll_no] if not grades.empty else pd.DataFrame()

        if my_grades.empty:
            st.info("📭 No grades yet. Your teacher will grade your submissions soon.")
        else:
            total_marks  = my_grades["marks"].sum()
            total_out_of = my_grades["out_of"].sum()
            avg_pct      = round((total_marks / total_out_of) * 100, 1) if total_out_of > 0 else 0

            m1, m2, m3 = st.columns(3)
            m1.metric("Graded",       len(my_grades))
            m2.metric("Total Marks",  f"{total_marks} / {total_out_of}")
            m3.metric("Overall %",    f"{avg_pct}%")
            st.divider()

            for _, grade in my_grades.iterrows():
                asgn_title = f"Assignment {grade['assignment_id']}"
                if not assignments.empty:
                    match = assignments[assignments["id"] == grade["assignment_id"]]
                    if not match.empty:
                        asgn_title = match.iloc[0]["title"]

                pct   = round((grade["marks"] / grade["out_of"]) * 100, 1) if grade["out_of"] > 0 else 0
                color = "🟢" if pct >= 75 else "🟡" if pct >= 50 else "🔴"

                with st.container(border=True):
                    st.markdown(f"{color} **{asgn_title}** — {grade['marks']} / {grade['out_of']} ({pct}%)")
                    st.caption(f"Graded by **{grade['graded_by']}** on {grade['graded_on']}")
                    if str(grade.get("feedback", "")).strip():
                        st.info(f"💬 **Teacher Feedback:** {grade['feedback']}")

