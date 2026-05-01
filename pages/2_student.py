import streamlit as st
import pandas as pd
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date as _date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar_helper import show_sidebar

st.set_page_config(page_title="Student Dashboard", layout="wide")
show_sidebar()

if not st.session_state.get("logged_in"):
    st.error("Login required")
    st.switch_page("pages/1_login_page.py")

roll_no = int(st.session_state.get("roll_no", -1))

STUDENT_FILE    = r"C:\Users\Priya\OneDrive\Desktop\Face_recognition_Attendance\data\student_database.csv"
ATTENDANCE_FILE = r"C:\Users\Priya\OneDrive\Desktop\Face_recognition_Attendance\data\Attendance.csv"
ALL_SUBJECTS    = ["DBMS", "DSA", "JAVA", "PYTHON", "C++"]

@st.cache_data(ttl=10)
def load_student_data():
    if not os.path.exists(STUDENT_FILE):
        return pd.DataFrame()
    df = pd.read_csv(STUDENT_FILE)
    df.columns = df.columns.str.lower().str.strip()
    df["roll_no"] = df["roll_no"].astype(int)
    return df

@st.cache_data(ttl=10)
def load_attendance_data():
    if not os.path.exists(ATTENDANCE_FILE):
        return pd.DataFrame()
    df = pd.read_csv(ATTENDANCE_FILE)
    df.columns = df.columns.str.lower().str.strip()
    df["roll_no"] = df["roll_no"].astype(int)
    df["subject"] = df["subject"].str.strip().str.upper()
    df["status"]  = df["status"].str.strip().str.lower()
    df["date"]    = pd.to_datetime(df["date"].str.strip(), errors="coerce")
    return df.dropna(subset=["date"])

# ── Load student ──
students = load_student_data()
if students.empty:
    st.error("Student database not found.")
    st.stop()

student = students[students["roll_no"] == roll_no]
if student.empty:
    st.error("Student record not found.")
    st.stop()

s = student.iloc[0]
def safe(col): return s[col] if col in s.index else "N/A"

# ── Load ALL attendance for this student (no date restriction) ──
att = load_attendance_data()
if att.empty:
    st.info("No attendance records yet.")
    st.stop()

student_att_all = att[att["roll_no"] == roll_no].copy()
if student_att_all.empty:
    st.warning("No attendance records found for your roll number yet.")
    st.stop()

today = _date.today()

# ─────────────────────────────────────────────
# SIDEBAR — only subject filter + view options
# No date restriction on overall data
# ─────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.header("📚 Subject Filter")
subject_options  = ["All Subjects"] + ALL_SUBJECTS
selected_subject = st.sidebar.selectbox("Select Subject", subject_options, key="student_subj_filter")

# Apply subject filter
if selected_subject != "All Subjects":
    student_att = student_att_all[student_att_all["subject"] == selected_subject]
else:
    student_att = student_att_all

# ─────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────
st.title("🎓 Student Dashboard")
st.caption(f"Welcome back, **{safe('name')}** · {datetime.now().strftime('%A, %d %B %Y')}")
st.divider()

# ── Profile box ──
st.subheader("👤 Personal Details")
with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.caption("👤 NAME")
        st.markdown(f"**{safe('name')}**")
    with c2:
        st.caption("🎫 ROLL NO")
        st.markdown(f"**{safe('roll_no')}**")
    with c3:
        st.caption("🏫 DEPARTMENT")
        st.markdown(f"**{safe('department')}**")
    with c4:
        st.caption("📅 YEAR / SEM")
        st.markdown(f"**{safe('year')}**")

st.divider()

# ─────────────────────────────────────────────
# OVERALL SUMMARY — based on ALL data (no date filter)
# ─────────────────────────────────────────────
st.subheader("📊 Overall Attendance Summary")
if selected_subject != "All Subjects":
    st.caption(f"Showing: **{selected_subject}** · All time")

total   = len(student_att)
present = len(student_att[student_att["status"] == "present"])
absent  = total - present
pct     = round(present / total * 100, 1) if total > 0 else 0

with st.container(border=True):
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.caption("📋 TOTAL CLASSES")
        st.markdown(f"**{total}**")
    with m2:
        st.caption("✅ PRESENT")
        st.markdown(f"**{present}**")
    with m3:
        st.caption("❌ ABSENT")
        st.markdown(f"**{absent}**")
    with m4:
        color = "green" if pct >= 75 else "red"
        st.caption("📊 ATTENDANCE %")
        st.markdown(f"**:{color}[{pct}%]**")

st.divider()

# ── Goal tracker ──
st.subheader("🛡️ Attendance Goal Tracker (Target: 75%)")
if total == 0:
    st.info("No data to calculate.")
elif pct >= 75:
    can_miss = int((present / 0.75) - total)
    st.success(f"✅ You are SAFE! You can miss **{max(0, can_miss)}** more class(es) and stay above 75%.")
else:
    needed = int((0.75 * total - present) / 0.25)
    st.error(f"🚨 Below 75%! Attend **{max(0, needed)}** consecutive classes without absence to reach 75%.")

st.divider()

# ─────────────────────────────────────────────
# SUBJECT-WISE PERFORMANCE — always all 5 subjects, all time
# ─────────────────────────────────────────────
st.subheader("📚 Subject-wise Performance (All Time)")

sub_rows = []
for subj in ALL_SUBJECTS:
    subj_data = student_att_all[student_att_all["subject"] == subj]
    total_s   = len(subj_data)
    present_s = len(subj_data[subj_data["status"] == "present"])
    pct_s     = round(present_s / total_s * 100, 1) if total_s > 0 else 0.0
    sub_rows.append({"subject": subj, "present": present_s, "total": total_s, "percent": pct_s})

sub_summary = pd.DataFrame(sub_rows)

sc1, sc2 = st.columns([2, 1])
with sc1:
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=sub_summary["percent"],
        theta=sub_summary["subject"],
        fill="toself", name="Attendance",
        line_color="#4caf82",
        fillcolor="rgba(76,175,130,0.15)"
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        margin=dict(t=30, b=30, l=30, r=30)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with sc2:
    st.write("**Subject Breakdown:**")
    for _, row in sub_summary.iterrows():
        if row["total"] == 0:
            st.markdown(f"**{row['subject']}**: — *(no classes yet)*")
        else:
            color = "green" if row["percent"] >= 75 else "red"
            st.markdown(f"**{row['subject']}**: :{color}[{row['percent']}%] ({int(row['present'])}/{int(row['total'])} classes)")

st.divider()

# ─────────────────────────────────────────────
# DAILY / MONTHLY — radio switch, NO date restriction
# ─────────────────────────────────────────────
st.subheader("📆 Attendance Detail")
view_mode = st.radio("View by:", ["📅 Daily", "🗓️ Monthly"], horizontal=True, key="att_view_mode")
st.divider()

# Use subject-filtered data but ALL dates
view_data = student_att.copy()

if view_mode == "📅 Daily":
    # ── DAILY ──
    view_data["day_str"]  = view_data["date"].dt.strftime("%d %b %Y")
    view_data["sort_key"] = view_data["date"].map(lambda x: x.toordinal())

    all_days = (
        view_data[["day_str", "sort_key"]].drop_duplicates()
        .sort_values("sort_key", ascending=False)["day_str"].tolist()
    )

    if not all_days:
        st.info("No daily records found.")
    else:
        today_str   = today.strftime("%d %b %Y")
        default_idx = all_days.index(today_str) if today_str in all_days else 0
        selected_day = st.selectbox("Select Date:", all_days, index=default_idx, key="student_day_select")

        day_data = view_data[view_data["day_str"] == selected_day]

        if day_data.empty:
            st.info(f"No records on {selected_day}.")
        else:
            # Build complete row for all subjects
            day_rows = []
            for subj in ALL_SUBJECTS:
                sd = day_data[day_data["subject"] == subj]
                if len(sd) == 0:
                    day_rows.append({"Subject": subj, "Status": "—", "Marked": "No data"})
                else:
                    is_present = (sd.iloc[0]["status"] == "present")
                    day_rows.append({
                        "Subject": subj,
                        "Status": "✅ Present" if is_present else "❌ Absent",
                        "Marked": sd.iloc[0]["status"].capitalize()
                    })

            day_df = pd.DataFrame(day_rows).set_index("Subject")
            st.dataframe(day_df, use_container_width=True)

            # Bar chart — only subjects that have data on this day
            chart_data = day_data.groupby("subject").agg(
                present=("status", lambda x: (x == "present").sum()),
                total=("status", "count")
            ).reset_index()
            chart_data["percent"] = (chart_data["present"] / chart_data["total"] * 100).round(1)
            chart_data["Color"]   = chart_data["percent"].apply(lambda p: "Present ✅" if p >= 100 else "Absent ❌")

            if not chart_data.empty:
                fig = px.bar(chart_data, x="subject", y="percent", color="Color", text="percent",
                             color_discrete_map={"Present ✅": "#4caf82", "Absent ❌": "#ff6b6b"},
                             labels={"percent": "Attendance %", "subject": "Subject"},
                             range_y=[0, 115])
                fig.update_traces(texttemplate="%{text}%", textposition="outside")
                fig.update_layout(margin=dict(t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

else:
    # ── MONTHLY ──
    view_data["month"]    = view_data["date"].dt.strftime("%b %Y")
    view_data["sort_key"] = view_data["date"].dt.to_period("M").apply(lambda x: x.ordinal)

    # All months in data — no restriction
    all_months = (
        view_data[["month", "sort_key"]].drop_duplicates()
        .sort_values("sort_key", ascending=False)["month"].tolist()
    )

    if not all_months:
        st.info("No monthly data found.")
    else:
        today_month = today.strftime("%b %Y")
        default_idx = all_months.index(today_month) if today_month in all_months else 0
        selected_month = st.selectbox("Select Month:", all_months, index=default_idx, key="student_month_select")

        month_data = view_data[view_data["month"] == selected_month]

        # Build complete summary for ALL 5 subjects
        month_rows = []
        for subj in ALL_SUBJECTS:
            sd        = month_data[month_data["subject"] == subj]
            total_s   = len(sd)
            present_s = len(sd[sd["status"] == "present"])
            pct_s     = round(present_s / total_s * 100, 1) if total_s > 0 else 0.0
            month_rows.append({
                "subject": subj,
                "present": present_s,
                "total":   total_s,
                "percent": pct_s,
                "Status":  "Above 75% ✅" if pct_s >= 75 else ("Below 75% ❌" if total_s > 0 else "No Data")
            })

        month_summary = pd.DataFrame(month_rows)

        # Summary box
        m_total   = month_summary["total"].sum()
        m_present = month_summary["present"].sum()
        m_pct     = round(m_present / m_total * 100, 1) if m_total > 0 else 0

        with st.container(border=True):
            a, b, c = st.columns(3)
            a.metric("Total Classes This Month", int(m_total))
            b.metric("Total Present",            int(m_present))
            c.metric("Overall % This Month",     f"{m_pct}%")

        # Bar chart — all 5 subjects
        fig_m = px.bar(
            month_summary[month_summary["total"] > 0],
            x="subject", y="percent", color="Status", text="percent",
            color_discrete_map={"Above 75% ✅": "#4caf82", "Below 75% ❌": "#ff6b6b"},
            labels={"percent": "Attendance %", "subject": "Subject"},
            range_y=[0, 115]
        )
        fig_m.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_m.update_layout(margin=dict(t=40, b=20), showlegend=True)
        st.plotly_chart(fig_m, use_container_width=True)

        # Table
        display_df = month_summary[["subject","present","total","percent","Status"]].copy()
        display_df.columns = ["Subject","Present","Total Classes","Attendance %","Status"]
        display_df = display_df.set_index("Subject")
        st.dataframe(display_df, use_container_width=True)

st.caption("✅ Green = 75% and above  |  ❌ Red = below 75%")
