import cv2
import os
import sys
import time

# -----------------------------
# Get roll number from command line
# -----------------------------
if len(sys.argv) < 2:
    print("Usage: python register_face.py <roll_no>")
    sys.exit()

roll_no = sys.argv[1]

# -----------------------------
# Create dataset folder
# -----------------------------
dataset_path = os.path.join("dataset", roll_no)
os.makedirs(dataset_path, exist_ok=True)

# -----------------------------
# Load Haar Cascade
# -----------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# -----------------------------
# Open Camera
# -----------------------------
cam = cv2.VideoCapture(0)

count = 0
MAX_IMAGES = 25
last_capture_time = 0

print("[INFO] Look at the camera. Green circle must appear.")
print("[INFO] Capturing 25 images...")

while True:
    ret, frame = cam.read()
    if not ret:
        print("Failed to access camera")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        # Draw green rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        current_time = time.time()

        # Capture image every 0.4 seconds
        if current_time - last_capture_time > 0.4 and count < MAX_IMAGES:
            count += 1

            face_img = gray[y:y + h, x:x + w]
            file_path = f"{dataset_path}/User.{roll_no}.{count}.jpg"
            cv2.imwrite(file_path, face_img)

            print(f"[INFO] Image {count} saved")
            last_capture_time = current_time

    cv2.imshow("Register Face", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

    if count >= MAX_IMAGES:
        break

# -----------------------------
# Cleanup
# -----------------------------
print("[INFO] Face registration completed.")
cam.release()
cv2.destroyAllWindows()

