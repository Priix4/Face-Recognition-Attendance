import cv2
import os
import sys
import time
from datetime import datetime

SUBJECT = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
MODEL_PATH = "trainer/face_model.yml"

if not os.path.exists(MODEL_PATH):
    print("[ERROR] Model file not found")
    sys.exit(1)

# Load recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_PATH)

# Load cascade
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Camera not opening")
    sys.exit(1)

TIME_LIMIT = 4  # seconds
start_time = datetime.now().timestamp()
recognized = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in faces:
        roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
        label, confidence = recognizer.predict(roi)

        if confidence < 90:
            recognized = True
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, f"FACE RECOGNIZED ({SUBJECT})", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        else:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 2)
            cv2.putText(frame, "Unknown", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    cv2.imshow("Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    if datetime.now().timestamp() - start_time > TIME_LIMIT:
        print("[INFO] Time limit reached, closing scanner")
        break

cap.release()
cv2.destroyAllWindows()

if recognized:
    print(f"[SUCCESS] Recognized for subject: {SUBJECT}")
else:
    print("[FAILED] Not recognized")