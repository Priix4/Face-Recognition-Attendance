import cv2
import numpy as np
import pandas as pd
import os
import sys
import time
from datetime import datetime
import pickle

# Force UTF-8 output to avoid UnicodeEncodeError on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

# -----------------------------
# SUBJECT FROM TERMINAL
# -----------------------------
if len(sys.argv) < 2:
    print("USAGE_ERROR")
    sys.exit(1)

subject = sys.argv[1].upper()   # ← always store as UPPERCASE

# -----------------------------
# Path Fixes & Loading
# -----------------------------
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH      = os.path.join(BASE_DIR, "trainer", "face_model.yml")
LABELS_PATH     = os.path.join(BASE_DIR, "trainer", "labels.pickle")
ATTENDANCE_FILE = os.path.join(BASE_DIR, "data", "Attendance.csv")
STUDENT_FILE    = os.path.join(BASE_DIR, "data", "student_database.csv")

os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# Load recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_PATH)
faceCascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ── label loading ──
# train_model.py now saves {0: 101, 1: 102, 2: 103 ...}
# sequential label (0,1,2..) → actual roll number (101,102,103...)
with open(LABELS_PATH, "rb") as f:
    labels_raw = pickle.load(f)

labels = {int(k): int(v) for k, v in labels_raw.items()}
# e.g. {0: 101, 1: 102, 2: 103}
print(f"[SCANNER] Label map loaded: {labels}")

# CSV Setup
if not os.path.exists(ATTENDANCE_FILE):
    pd.DataFrame(columns=["roll_no", "subject", "status", "date", "time"]).to_csv(
        ATTENDANCE_FILE, index=False
    )

# -----------------------------
# Camera Setup
# -----------------------------
cap                = cv2.VideoCapture(0, cv2.CAP_DSHOW)
prev_face_pos      = None
movement_threshold = 5
live_frames        = 0
live_frames_needed = 2
marked             = False
close_timer        = 0
CONFIDENCE_THRESHOLD = 90

print("SCANNER_STARTED")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in faces:
        center = (x + w // 2, y + h // 2)

        if prev_face_pos is not None:
            if abs(center[0] - prev_face_pos[0]) > movement_threshold:
                live_frames += 1
        prev_face_pos = center

        faceROI = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
        label_id, confidence = recognizer.predict(faceROI)

        if confidence < CONFIDENCE_THRESHOLD and live_frames >= live_frames_needed and not marked:

            # ── FIXED: label_id is int, labels dict is {int: int} ──
            roll_no = labels.get(label_id, None)

            if roll_no is None:
                print(f"LABEL_NOT_FOUND:{label_id}")
                continue

            df = pd.read_csv(ATTENDANCE_FILE)
            df.columns = df.columns.str.lower().str.strip()
            now      = datetime.now()
            date_str = now.strftime("%Y-%m-%d")

            already_marked = (
                (df["roll_no"].astype(int) == int(roll_no)) &
                (df["subject"].str.upper() == subject) &
                (df["date"] == date_str)
            ).any()

            if not already_marked:
                new_entry = pd.DataFrame([{
                    "roll_no": int(roll_no),
                    "subject": subject,          # ← UPPERCASE
                    "status":  "Present",
                    "date":    date_str,
                    "time":    now.strftime("%I:%M:%S %p")
                }])
                new_entry.to_csv(ATTENDANCE_FILE, mode='a', header=False, index=False)
                print("MARKED_SUCCESSFULLY")
            else:
                print("ALREADY_MARKED")

            marked      = True
            close_timer = time.time()

        display_name = str(labels.get(label_id, "?")) if confidence < CONFIDENCE_THRESHOLD else "Unknown"
        color        = (0, 255, 0) if confidence < CONFIDENCE_THRESHOLD else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, f"Roll {display_name} ({int(confidence)})", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow("EduTrack Scanner - Press Q to quit", frame)

    # ── Check if X button was clicked to close window ──
    window_closed = cv2.getWindowProperty("EduTrack Scanner - Press Q to quit", cv2.WND_PROP_VISIBLE) < 1

    if (
        (marked and time.time() - close_timer > 2) or   # auto close 2s after marking
        window_closed or                                  # X button clicked
        (cv2.waitKey(1) & 0xFF == ord('q'))              # Q key pressed
    ):
        break

cap.release()
cv2.destroyAllWindows()

# ================================================================
# Mark ABSENT for all students not recorded today for this subject
# ================================================================
today_str = datetime.now().strftime("%Y-%m-%d")

try:
    all_students = pd.read_csv(STUDENT_FILE)
    all_students.columns = all_students.columns.str.lower().str.strip()

    att_today = pd.read_csv(ATTENDANCE_FILE)
    att_today.columns = att_today.columns.str.lower().str.strip()
    att_today['date'] = pd.to_datetime(att_today['date'], errors='coerce')

    already_recorded = att_today[
        (att_today['subject'].str.upper() == subject) &
        (att_today['date'].dt.strftime('%Y-%m-%d') == today_str)
    ]['roll_no'].astype(int).tolist()

    absent_rows = []
    for _, student in all_students.iterrows():
        if int(student['roll_no']) not in already_recorded:
            absent_rows.append({
                'roll_no': int(student['roll_no']),
                'subject': subject,              # ← UPPERCASE
                'status':  'Absent',
                'date':    today_str,
                'time':    datetime.now().strftime("%I:%M:%S %p")
            })

    if absent_rows:
        pd.DataFrame(absent_rows).to_csv(ATTENDANCE_FILE, mode='a', header=False, index=False)
        print(f"ABSENT_MARKED:{len(absent_rows)}")
    else:
        print("ALL_RECORDED")

except Exception as e:
    print(f"ABSENT_ERROR:{e}")

print("SESSION_COMPLETE")