import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar_helper import show_sidebar

st.set_page_config(page_title="📚 Subject Notes", layout="wide")
show_sidebar()

if not st.session_state.get("logged_in"):
    st.switch_page("pages/1_login_page.py")

BASE_DIR   = r"C:\Users\Priya\OneDrive\Desktop\Face_recognition_Attendance"
NOTES_FILE = os.path.join(BASE_DIR, "data", "notes.csv")
NOTES_DIR  = os.path.join(BASE_DIR, "notes_files")  # where PDFs are saved

os.makedirs(NOTES_DIR, exist_ok=True)

if not os.path.exists(NOTES_FILE):
    pd.DataFrame(columns=["roll_no","title","subject","unit","uploaded_by","uploaded_on","filename","filepath"]).to_csv(NOTES_FILE, index=False)

@st.cache_data(ttl=5)
def load_notes():
    df = pd.read_csv(NOTES_FILE, on_bad_lines='skip', engine='python')
    df.columns = df.columns.str.lower().str.strip()
    # Ensure all required columns exist
    for col in ["roll_no","title","subject","unit","uploaded_by","uploaded_on","filename","filepath"]:
        if col not in df.columns:
            df[col] = ""
    return df

def save_notes(df):
    df.to_csv(NOTES_FILE, index=False, lineterminator='\n')
    load_notes.clear()

role     = st.session_state.get("role", "student")
username = st.session_state.get("username", "")

st.title("📚 Subject Notes")

# ================================================================
# TEACHER / ADMIN — Upload notes
# ================================================================
if role in ["teacher", "admin"]:
    with st.expander("➕ Upload New Notes", expanded=False):
        with st.form("upload_notes_form"):
            c1, c2 = st.columns(2)
            with c1:
                title   = st.text_input("Notes Title", placeholder="e.g. Unit 3 — Normalisation")
                subject = st.text_input("Subject", placeholder="e.g. DBMS")
                unit    = st.text_input("Unit / Chapter", placeholder="e.g. Unit 3")
            with c2:
                notes_file = st.file_uploader(
                    "📎 Upload Notes File (PDF or Word)",
                    type=["pdf", "docx", "doc"]
                )

            if st.form_submit_button("📤 Upload Notes", type="primary", use_container_width=True):
                if not title or not subject:
                    st.error("❌ Title and Subject are required!")
                elif notes_file is None:
                    st.error("❌ Please upload a file!")
                else:
                    # Save file
                    safe_name = f"{subject.replace(' ','_')}_{unit.replace(' ','_')}_{notes_file.name.replace(' ','_')}"
                    save_path = os.path.join(NOTES_DIR, safe_name)
                    with open(save_path, "wb") as f:
                        f.write(notes_file.getbuffer())

                    df = load_notes()
                    new_roll_no = int(df["roll_no"].max() + 1) if not df.empty and df["roll_no"].notna().any() else 1
                    new_row = pd.DataFrame([{
                        "roll_no":     new_roll_no,
                        "title":       title.replace(",", ""),
                        "subject":     subject.replace(",", ""),
                        "unit":        unit.replace(",", ""),
                        "uploaded_by": username,
                        "uploaded_on": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "filename":    safe_name,
                        "filepath":    save_path
                    }])
                    df_updated = pd.concat([df, new_row], ignore_index=True)
                    save_notes(df_updated)
                    st.success(f"✅ Notes '{title}' uploaded successfully!")
                    st.rerun()

    st.divider()

# ================================================================
# ALL ROLES — View & Download notes
# ================================================================
st.subheader("📖 All Available Notes")

notes = load_notes()

if notes.empty:
    st.info("📭 No notes uploaded yet.")
else:
    # Search + filter
    c1, c2 = st.columns([3, 2])
    with c1:
        search = st.text_input("🔍 Search by title or subject")
    with c2:
        subjects = ["All"] + sorted(notes["subject"].dropna().unique().tolist())
        filter_subject = st.selectbox("Filter by Subject", subjects)

    df_show = notes.copy()

    if search:
        df_show = df_show[
            df_show["title"].str.contains(search, case=False, na=False) |
            df_show["subject"].str.contains(search, case=False, na=False)
        ]

    if filter_subject != "All":
        df_show = df_show[df_show["subject"] == filter_subject]

    df_show = df_show.sort_values("uploaded_on", ascending=False)

    st.markdown(f"**{len(df_show)} note(s) found**")
    st.markdown("")

    # Group by subject
    for subject in df_show["subject"].unique():
        st.markdown(f"### 📘 {subject}")
        subject_notes = df_show[df_show["subject"] == subject]

        for _, row in subject_notes.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 2, 1])

                with c1:
                    st.markdown(f"**{row['title']}**")
                    unit_text = f"📂 {row['unit']}" if str(row.get('unit','')).strip() else ""
                    st.caption(f"{unit_text}  |  Uploaded by **{row['uploaded_by']}** on {row['uploaded_on']}")

                with c2:
                    fp = str(row.get("filepath", ""))
                    fn = str(row.get("filename", "notes"))
                    if fp and os.path.exists(fp):
                        with open(fp, "rb") as f:
                            st.download_button(
                                label="⬇️ Download",
                                data=f.read(),
                                file_name=fn,
                                mime="application/octet-stream",
                                key=f"dl_note_{row['roll_no']}"
                            )
                    else:
                        st.warning("File missing")

                with c3:
                    if role in ["teacher", "admin"]:
                        if st.button("🗑️", key=f"del_note_{row['roll_no']}"):
                            df_updated = notes[notes["roll_no"] != row["roll_no"]]
                            save_notes(df_updated)
                            st.rerun()

        st.markdown("")