import os

DATASET_DIR = "dataset"

for person in os.listdir(DATASET_DIR):
    person_path = os.path.join(DATASET_DIR, person)

    if not os.path.isdir(person_path):
        continue

    # Extract roll number from folder name (example: priya_101)
    try:
        roll_no = int(person.split("_")[-1])
    except:
        print(f"Skipping folder: {person}")
        continue

    images = os.listdir(person_path)
    count = 1

    for img in images:
        old_path = os.path.join(person_path, img)
        if not img.lower().endswith(".jpg"):
            continue

        new_name = f"User.{roll_no}.{count}.jpg"
        new_path = os.path.join(person_path, new_name)

        os.rename(old_path, new_path)
        count += 1

    print(f"Renamed images for Roll No {roll_no}")