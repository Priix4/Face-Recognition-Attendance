import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar_helper import show_sidebar

st.set_page_config(page_title="Timetable", layout="wide")
show_sidebar()

if not st.session_state.get("logged_in"):
    st.switch_page("pages/1_login_page.py")

BASE_DIR       = r"C:\Users\Priya\OneDrive\Desktop\Face_recognition_Attendance"
TIMETABLE_FILE = os.path.join(BASE_DIR, "data", "timetable.csv")

DAYS    = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
PERIODS = ["9:00-10:00","10:00-11:00","11:00-12:00","12:00-1:00","1:00-2:00","2:00-3:00","3:00-4:00"]
LUNCH   = "1:00-2:00"

role  = st.session_state.get("role","student")
today = datetime.now().strftime("%A")
now   = datetime.now()

if not os.path.exists(TIMETABLE_FILE):
    pd.DataFrame(columns=["day","period","subject","teacher","room"]).to_csv(TIMETABLE_FILE, index=False)

@st.cache_data(ttl=5)
def load_timetable():
    df = pd.read_csv(TIMETABLE_FILE, on_bad_lines='skip', engine='python')
    df.columns = df.columns.str.lower().str.strip()
    return df

def save_timetable(df):
    df.to_csv(TIMETABLE_FILE, index=False, lineterminator='\n')
    load_timetable.clear()

def period_status(period_str):
    if period_str == LUNCH: return "lunch"
    try:
        sh = int(period_str.split("-")[0].split(":")[0])
        eh = int(period_str.split("-")[1].split(":")[0])
        if sh <= now.hour < eh: return "current"
        if now.hour < sh: return "future"
        return "past"
    except:
        return "normal"

tt       = load_timetable()
schedule = {}
if not tt.empty:
    for _, row in tt.iterrows():
        schedule[(str(row["day"]).strip(), str(row["period"]).strip())] = row

p_status   = {p: period_status(p) for p in PERIODS}
found_next = False
for p in PERIODS:
    if p_status[p] == "future" and not found_next:
        p_status[p] = "next"; found_next = True

# ── Page header ──
st.title("📅 Timetable")
st.caption(f"Today is **{today}** · {now.strftime('%d %B %Y  %H:%M')}")
st.divider()

# ── Admin editor ──
if role == "admin":
    with st.expander("✏️ Edit Timetable", expanded=False):
        with st.form("tt_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                e_day    = st.selectbox("Day", DAYS)
                e_period = st.selectbox("Period", [p for p in PERIODS if p != LUNCH])
            with c2:
                e_subj    = st.text_input("Subject", placeholder="e.g. DBMS")
                e_teacher = st.text_input("Teacher", placeholder="e.g. Prof. Sharma")
            with c3:
                e_room    = st.text_input("Room", placeholder="e.g. Lab 3")
                submitted = st.form_submit_button("💾 Save", use_container_width=True, type="primary")
            if submitted:
                if not e_subj:
                    st.error("Subject is required.")
                else:
                    df   = load_timetable()
                    mask = (df["day"] == e_day) & (df["period"] == e_period)
                    if mask.any():
                        df.loc[mask, ["subject","teacher","room"]] = [e_subj.upper(), e_teacher, e_room]
                    else:
                        new_row = pd.DataFrame([{"day":e_day,"period":e_period,"subject":e_subj.upper(),"teacher":e_teacher,"room":e_room}])
                        df = pd.concat([df, new_row], ignore_index=True)
                    save_timetable(df)
                    st.success(f"✅ Saved {e_subj.upper()} for {e_day} {e_period}")
                    st.rerun()

        st.write("**Delete a slot:**")
        del_day    = st.selectbox("Day to delete", DAYS, key="del_day")
        del_period = st.selectbox("Period to delete", [p for p in PERIODS if p != LUNCH], key="del_period")
        if st.button("🗑️ Delete slot"):
            df = load_timetable()
            df = df[~((df["day"]==del_day) & (df["period"]==del_period))]
            save_timetable(df)
            st.success("Deleted!")
            st.rerun()

# ── Tabs ──
tab1, tab2 = st.tabs(["📱 Today", "📆 Full Week"])

with tab1:
    st.subheader(f"📅 {today}'s Schedule")
    if today not in DAYS:
        st.info("🎉 It's the weekend — no classes today!")
    elif tt.empty:
        st.info("No timetable set up yet. Ask admin.")
    else:
        # Compact table header
        h0, h1, h2, h3, h4 = st.columns([2, 2, 2, 3, 1])
        h0.markdown("**🕐 Time**")
        h1.markdown("**📘 Subject**")
        h2.markdown("**👩‍🏫 Teacher**")
        h3.markdown("**🏫 Room**")
        h4.markdown("**Status**")
        st.divider()

        has_any = False
        for period in PERIODS:
            if period == LUNCH:
                c0, _ = st.columns([2, 8])
                c0.caption("🍽️ Lunch")
                st.divider()
                continue

            entry  = schedule.get((today, period))
            status = p_status.get(period, "normal")

            if entry is not None:
                has_any = True
                subj    = str(entry.get("subject","")).strip()
                teacher = str(entry.get("teacher","")).strip()
                room    = str(entry.get("room","")).strip()
                if status == "current": badge = "🟢 Live"
                elif status == "next":  badge = "🔵 Next"
                elif status == "past":  badge = "⚪ Done"
                else:                   badge = "🔘"

                c0, c1, c2, c3, c4 = st.columns([2, 2, 2, 3, 1])
                c0.markdown(f"**{period}**")
                c1.markdown(f"**{subj}**")
                c2.caption(teacher if teacher and teacher != "nan" else "—")
                c3.caption(room    if room    and room    != "nan" else "—")
                c4.markdown(badge)
            else:
                if status not in ("past",):
                    c0, c1 = st.columns([2, 8])
                    c0.markdown(f"**{period}**")
                    c1.caption("Free period")

        if not has_any:
            st.info("No classes scheduled for today.")

with tab2:
    st.subheader("📆 Full Week View")
    if tt.empty:
        st.info("No timetable data found.")
    else:
        hcols = st.columns([1]+[2]*6)
        hcols[0].markdown("**Time**")
        for i, day in enumerate(DAYS):
            marker = "📍 " if day == today else ""
            hcols[i+1].markdown(f"**{marker}{day[:3].upper()}**")
        st.divider()
        for period in PERIODS:
            row = st.columns([1]+[2]*6)
            if period == LUNCH:
                row[0].caption("Lunch")
                for i in range(6): row[i+1].caption("—")
                continue
            row[0].caption(period.replace(":00","").replace("-","–"))
            for i, day in enumerate(DAYS):
                entry  = schedule.get((day, period))
                is_now = (day == today and p_status.get(period) == "current")
                if entry is not None:
                    subj = str(entry.get("subject","")).strip()
                    if is_now:   row[i+1].markdown(f"**🟢 {subj}**")
                    elif day == today: row[i+1].markdown(f"**{subj}**")
                    else:        row[i+1].write(subj)
                else:
                    row[i+1].caption("—")