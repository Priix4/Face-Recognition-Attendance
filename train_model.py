import cv2
import numpy as np
import os
import sys
import pickle

# Path to dataset folder
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset")

if not os.path.exists(DATASET_PATH):
    print("[ERROR] Dataset folder not found!")
    sys.exit()

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces     = []
labels    = []
label_map = {}  # {sequential_int: roll_no_int}  e.g. {0: 101, 1: 102, 2: 103}

print("[INFO] Reading images...")

# ── Assign sequential IDs 0,1,2... to each roll folder ──
# LBPH requires labels to be 0-based integers, NOT 101,102,103
current_label = 0

for folder_name in sorted(os.listdir(DATASET_PATH)):   # sorted for consistency
    person_path = os.path.join(DATASET_PATH, folder_name)

    if not os.path.isdir(person_path):
        continue

    try:
        roll_no = int(folder_name)   # folder name IS the roll number
    except ValueError:
        print(f"[WARNING] Skipping folder: {folder_name} (must be numeric)")
        continue

    # Map sequential label → actual roll number
    label_map[current_label] = roll_no
    print(f"[INFO] Folder {folder_name} (Roll {roll_no}) → Label {current_label}")

    for image_name in os.listdir(person_path):
        if image_name.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(person_path, image_name)
            img        = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

            if img is None:
                continue

            img = cv2.resize(img, (200, 200))
            faces.append(img)
            labels.append(current_label)   # use sequential label, NOT roll_no

    current_label += 1

print(f"[INFO] Total faces found: {len(faces)}")
print(f"[INFO] Label map: {label_map}")

if len(faces) == 0:
    print("[ERROR] No images found. Training aborted.")
    sys.exit()

labels_np = np.array(labels)

print("[INFO] Training model... please wait.")
recognizer.train(faces, labels_np)

os.makedirs(os.path.join(BASE_DIR, "trainer"), exist_ok=True)

# Save model
model_path = os.path.join(BASE_DIR, "trainer", "face_model.yml")
recognizer.save(model_path)
print(f"[SUCCESS] Saved: {model_path}")

# Save label map — {0: 101, 1: 102, 2: 103 ...}
labels_path = os.path.join(BASE_DIR, "trainer", "labels.pickle")
with open(labels_path, "wb") as f:
    pickle.dump(label_map, f)
print(f"[SUCCESS] Saved: {labels_path}")
print(f"[INFO] Final label map saved: {label_map}")

print("\n[FINISH] Training complete. You can now run the Attendance Dashboard.")