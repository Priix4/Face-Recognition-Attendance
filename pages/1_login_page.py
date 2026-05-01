import streamlit as st
import csv
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar_helper import hide_default_nav

st.set_page_config(page_title="EduTrack — Login", layout="centered")
hide_default_nav()

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* Light grey background */
[data-testid="stAppViewContainer"] {
    background: #f0f2f5;
    min-height: 100vh;
}

[data-testid="stHeader"] { background: transparent; }

/* Card */
.login-card {
    background: white;
    border-radius: 24px;
    padding: 40px 40px 30px 40px;
    margin: 0 auto;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.06);
}

/* Logo circle */
.logo-circle {
    width: 90px;
    height: 90px;
    background: linear-gradient(135deg, #e94560, #a855f7);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20px auto;
    font-size: 40px;
    box-shadow: 0 8px 25px rgba(233, 69, 96, 0.3);
}

/* Title */
.edu-title {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    background: linear-gradient(135deg, #e94560, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    margin-bottom: 4px;
}

/* Subtitle */
.edu-subtitle {
    text-align: center;
    color: #999;
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 30px;
}

/* Divider */
.edu-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #ddd, transparent);
    margin: 20px 0 30px 0;
}

/* Input labels */
.stTextInput label {
    color: #555 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* Input fields */
.stTextInput input {
    background: #f8f9fa !important;
    border: 1.5px solid #e0e0e0 !important;
    border-radius: 12px !important;
    color: #333 !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
}

.stTextInput input:focus {
    border-color: #e94560 !important;
    background: white !important;
    box-shadow: 0 0 0 3px rgba(233,69,96,0.12) !important;
}

/* Login button */
.stButton button {
    background: linear-gradient(135deg, #e94560, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 8px 25px rgba(233,69,96,0.25) !important;
    margin-top: 10px !important;
}

.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 30px rgba(233,69,96,0.4) !important;
}

/* Hide streamlit branding */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------- AUTH FUNCTIONS ----------------
def authenticate(username, password):
    try:
        with open("data/users.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"] == username and row["password"] == password:
                    return row
    except FileNotFoundError:
        st.error("User database not found.")
    return None

def get_student_roll_no(username):
    try:
        df = pd.read_csv("data/student_database.csv")
        student = df[df["username"] == username]
        if not student.empty:
            return int(float(student.iloc[0]["roll_no"]))
    except Exception as e:
        st.error(f"Student database error: {e}")
    return None

# ---------------- LOGIN UI ----------------
st.markdown("<br><br>", unsafe_allow_html=True)

_, center, _ = st.columns([1, 2, 1])

with center:
    st.markdown("""
    <div class="login-card">
        <div class="logo-circle">🎓</div>
        <div class="edu-title">EduTrack</div>
        <div class="edu-subtitle">Face Recognition Attendance System</div>
        <div class="edu-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    login_clicked = st.button("🔐  Login", use_container_width=True)

    st.markdown("""
    <div style='text-align:center; color:#bbb; font-size:11px; margin-top:24px;'>
        © 2026 EduTrack. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

# ---------------- LOGIN LOGIC ----------------
if login_clicked:
    if not username or not password:
        st.error("Please enter both username and password.")
    else:
        user = authenticate(username, password)
        if user:
            role = user["role"]
            st.session_state["username"]  = username
            st.session_state["role"]      = role
            st.session_state["logged_in"] = True
            st.session_state["subject"]   = user.get("subject") if role == "teacher" else None

            if role == "student":
                roll_no = get_student_roll_no(username)
                if roll_no is None:
                    st.error("Student record not found. Contact admin.")
                    st.stop()
                st.session_state["roll_no"] = roll_no
                st.switch_page("pages/2_Student.py")
            elif role == "teacher":
                st.switch_page("pages/4_Teacher.py")
            elif role == "admin":
                st.switch_page("pages/3_Admin.py")
        else:
            st.error("❌ Invalid username or password")

