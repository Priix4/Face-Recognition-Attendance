import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys
from fpdf import FPDF

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar_helper import show_sidebar

st.set_page_config(page_title="👩‍🏫 Teacher Dashboard", layout="wide")
show_sidebar()

st.title("👩‍🏫 Teacher Dashboard")

if not st.session_state.get("logged_in"):
    st.switch_page("pages/1_login_page.py")

# ---------------- FILE PATHS ----------------
ATTENDANCE_FILE = r"C:\Users\Priya\OneDrive\Desktop\Face_recognition_Attendance\data\Attendance.csv"
STUDENT_FILE    = r"C:\Users\Priya\OneDrive\Desktop\Face_recognition_Attendance\data\student_database.csv"

# ---------------- SUBJECTS ----------------
SUBJECTS = ["DBMS", "DSA", "JAVA", "PYTHON", "C++"]

# ---------------- SESSION STATE INIT ----------------
if "mark_result" not in st.session_state:
    st.session_state.mark_result = None
if "mark_message" not in st.session_state:
    st.session_state.mark_message = ""

# ---------------- LOAD DATA ----------------
@st.cache_data(ttl=10)
def load_attendance():
    df = pd.read_csv(ATTENDANCE_FILE, on_bad_lines='skip', engine='python')
    df.columns    = df.columns.str.lower().str.strip()
    df['date']    = pd.to_datetime(df['date'], errors='coerce')
    df['subject'] = df['subject'].str.strip().str.upper()   # ← UPPERCASE always
    df['status']  = df['status'].str.strip().str.lower()
    df['roll_no'] = pd.to_numeric(df['roll_no'], errors='coerce').fillna(0).astype(int)
    df = df.dropna(subset=['date'])
    return df

@st.cache_data(ttl=10)
def load_students():
    df = pd.read_csv(STUDENT_FILE, on_bad_lines='skip', engine='python')
    df.columns    = df.columns.str.lower().str.strip()
    df['roll_no'] = df['roll_no'].astype(int)
    return df

if not (os.path.exists(ATTENDANCE_FILE) and os.path.exists(STUDENT_FILE)):
    st.error("File not found!")
    st.stop()

att      = load_attendance()
students = load_students()

roll_options = {
    f"Roll {row['roll_no']} — {row['name']}": row['roll_no']
    for _, row in students.sort_values('roll_no').iterrows()
}

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.divider()
st.sidebar.header("🗓️ Date Filter")
from datetime import date, timedelta
today         = date.today()
default_start = today.replace(day=1)   # first of current month

date_range = st.sidebar.date_input(
    "Select Period",
    value=(default_start, today),
    min_value=date(2024, 1, 1),
    max_value=date(2030, 12, 31),      # NO restriction — fully free
    key='sidebar_date_picker'
)

st.sidebar.caption(f"📅 Today: {today.strftime('%d %b %Y')}")

st.sidebar.header("🔍 Course Filter")
dept_list        = students['department'].unique().tolist()
selected_dept    = st.sidebar.selectbox("Department", dept_list)
subject_list     = SUBJECTS
selected_subject = st.sidebar.selectbox("Subject", subject_list)

# ---------------- DATA PROCESSING ----------------
if len(date_range) == 2:
    start_date, end_date = date_range
elif len(date_range) == 1:
    start_date = end_date = date_range[0]
else:
    start_date = end_date = today

att_filtered = att[
    (att['date'].dt.date >= start_date) &
    (att['date'].dt.date <= end_date)
].copy()

filtered_students = students[students['department'] == selected_dept]

# ── both sides UPPERCASE — will now match ──
att_filtered = att_filtered[
    (att_filtered['subject'] == selected_subject.upper()) &
    (att_filtered['roll_no'].isin(filtered_students['roll_no']))
]

# ---------------- CALCULATION ----------------
def calculate_summary(df_att, df_students):
    summary = []
    total_working_days = df_att['date'].nunique()
    for _, student in df_students.iterrows():
        roll = student['roll_no']
        student_records = df_att[df_att['roll_no'] == roll]
        present_days = student_records[student_records['status'] == 'present']['date'].nunique()
        percent = (present_days / total_working_days * 100) if total_working_days > 0 else 0
        summary.append({
            'Roll No':    roll,
            'Name':       student['name'],
            'Present':    present_days,
            'Total Days': total_working_days,
            'Percentage': round(percent, 2)
        })
    return pd.DataFrame(summary)

summary_df = calculate_summary(att_filtered, filtered_students)

# ---------------- PDF LOGIC ----------------
def generate_pdf(df, subject, start, end):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, f"Attendance Report: {subject.upper()}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(190, 10, f"Period: {start} to {end}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, "Roll No",      border=1, fill=True, align='C')
    pdf.cell(80, 10, "Student Name", border=1, fill=True, align='C')
    pdf.cell(40, 10, "Days Present", border=1, fill=True, align='C')
    pdf.cell(40, 10, "Percentage",   border=1, fill=True, align='C')
    pdf.ln()
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        pdf.cell(30, 10, str(row['Roll No']),     border=1, align='C')
        pdf.cell(80, 10, str(row['Name']),        border=1)
        pdf.cell(40, 10, str(row['Present']),     border=1, align='C')
        pdf.cell(40, 10, f"{row['Percentage']}%", border=1, align='C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# ---------------- UI LAYOUT ----------------
st.subheader(f"📊 Attendance for {selected_subject.upper()} ({start_date} to {end_date})")

if not summary_df.empty:
    fig = px.bar(
        summary_df, x='Name', y='Percentage',
        text='Percentage', color='Percentage',
        color_continuous_scale='RdYlGn',
        labels={"Percentage": "Attendance %", "Name": "Student"},
        range_y=[0, 110]
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(yaxis_title="Attendance %")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for the selected filters.")

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚨 Defaulter List (<75%)")
    defaulters = summary_df[summary_df['Percentage'] < 75]
    if not defaulters.empty:
        st.dataframe(defaulters, use_container_width=True)
    else:
        st.success("✅ All students are above 75%!")

with col2:
    st.markdown("### 📥 Export Reports")
    if not summary_df.empty:
        pdf_bytes = generate_pdf(summary_df, selected_subject, start_date, end_date)
        st.download_button(
            "📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"Report_{selected_subject}.pdf",
            mime="application/pdf"
        )
    avg_total = summary_df['Percentage'].mean() if not summary_df.empty else 0
    st.metric("Class Average Attendance", f"{avg_total:.1f}%")

# ================================================================
# MANUAL ATTENDANCE OVERRIDE
# ================================================================
st.divider()
st.subheader("✍️ Manual Attendance Override")

if st.session_state.mark_result == "success":
    st.success(st.session_state.mark_message)
    st.session_state.mark_result = None
elif st.session_state.mark_result == "duplicate":
    st.warning(st.session_state.mark_message)
    st.session_state.mark_result = None
elif st.session_state.mark_result == "error":
    st.error(st.session_state.mark_message)
    st.session_state.mark_result = None

m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    selected_roll_label = st.selectbox(
        "Select Student (Roll No)",
        list(roll_options.keys()),
        key='manual_student_select'
    )
with m_col2:
    manual_subject = st.selectbox(
        "Select Subject",
        subject_list,
        key='manual_subject_select'
    )
with m_col3:
    today_date = datetime.now().strftime("%Y-%m-%d")
    st.text_input("Date", value=today_date, disabled=True, key='manual_date_display')

# ---------------- BUTTON CALLBACK ----------------
def mark_attendance():
    selected_label = st.session_state.manual_student_select
    subject        = st.session_state.manual_subject_select.upper()  # ← UPPERCASE
    date_str       = datetime.now().strftime("%Y-%m-%d")
    time_str       = datetime.now().strftime("%I:%M:%S %p")

    roll = roll_options[selected_label]
    name = students[students['roll_no'] == roll]['name'].values[0]

    try:
        latest = pd.read_csv(ATTENDANCE_FILE, on_bad_lines='skip', engine='python')
        latest.columns    = latest.columns.str.lower().str.strip()
        latest['roll_no'] = pd.to_numeric(latest['roll_no'], errors='coerce').fillna(0).astype(int)
        latest['date']    = pd.to_datetime(latest['date'], errors='coerce')
        latest['subject'] = latest['subject'].str.strip().str.upper()  # ← UPPERCASE
        latest['status']  = latest['status'].str.strip().str.lower()

        already_present = (
            (latest['roll_no'] == roll) &
            (latest['subject'] == subject) &
            (latest['date'].dt.strftime('%Y-%m-%d') == date_str) &
            (latest['status'] == 'present')
        ).any()

        if already_present:
            st.session_state.mark_result  = "duplicate"
            st.session_state.mark_message = f"⚠️ Roll {roll} ({name}) is already marked Present for {subject} today!"
            return

        absent_mask = (
            (latest['roll_no'] == roll) &
            (latest['subject'] == subject) &
            (latest['date'].dt.strftime('%Y-%m-%d') == date_str) &
            (latest['status'] == 'absent')
        )

        if absent_mask.any():
            latest.loc[absent_mask, 'status'] = 'present'
            latest.loc[absent_mask, 'time']   = time_str
            latest['date'] = latest['date'].dt.strftime('%Y-%m-%d')
            latest.to_csv(ATTENDANCE_FILE, index=False, lineterminator='\n')
            load_attendance.clear()
            st.session_state.mark_result  = "success"
            st.session_state.mark_message = f"✅ Roll {roll} ({name}) updated Absent → Present for {subject} on {date_str} at {time_str}!"
        else:
            df_full = pd.concat([latest, pd.DataFrame([{
                'roll_no': roll,
                'subject': subject,
                'status':  'present',
                'date':    date_str,
                'time':    time_str
            }])], ignore_index=True)
            df_full['date'] = df_full['date'].apply(
                lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else x
            )
            df_full.to_csv(ATTENDANCE_FILE, index=False, lineterminator='\n')
            load_attendance.clear()
            st.session_state.mark_result  = "success"
            st.session_state.mark_message = f"✅ Roll {roll} ({name}) marked Present for {subject} on {date_str} at {time_str}!"

    except Exception as e:
        st.session_state.mark_result  = "error"
        st.session_state.mark_message = f"❌ Failed to save!\nError: {e}"

st.button(
    "✅ Mark Present Manually",
    on_click=mark_attendance,
    use_container_width=True,
    type="primary"
)