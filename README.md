# Face-Recognition-Attendance
# 🎭 Face Recognition Attendance System

A smart attendance system using face recognition to automate attendance marking with role-based dashboards.

## ⚙️ How to Run
# Clone repository
git clone <your-repo-link>

# Go inside folder
cd Face-Recognition-Attendance

# Install dependencies
pip install -r requirements.txt

# Run project
streamlit run home.py


## 💡 Features
🔐 Login system (Admin / Teacher / Student)
🎓 Student dashboard (attendance, marks, notifications)
👩‍🏫 Teacher dashboard (manage attendance)
🛠️ Admin dashboard (manage users & data)
📷 Face registration (capture student faces)
🤖 Train model using captured images
✅ Automatic attendance using webcam
📊 Attendance stored in CSV files

---

## 🛠️ Tech Stack
Python
 Streamlit
 OpenCV
 Pandas

---
## 🔄 Project Flow (Step-by-Step)

### 🔐 Login & Navigation
1. User opens the application (`Home.py`)
2. Landing page is displayed
3. User clicks on **Login**
4. User enters username and password
5. System verifies credentials from `users.csv`
6. User is redirected based on role:
   - Student → Student Dashboard
   - Teacher → Teacher Dashboard
   - Admin → Admin Dashboard

---

### 📷 Student Registration (Admin/Teacher)
7. Admin/Teacher selects **Register Student**
8. Enters student details (ID, Name)
9. Webcam opens using OpenCV
10. System captures 20–50 face images
11. Images are stored in dataset folder
12. Student details are saved in `student_database.csv`

---

### 🤖 Model Training
13. Admin/Teacher clicks **Train Model**
14. System reads all captured images
15. Faces are converted into numerical data
16. Model is trained using face recognition algorithm
17. Trained model is saved for recognition

---

### ✅ Attendance Marking
18. Teacher starts **Take Attendance**
19. Webcam activates in real-time
20. System detects and recognizes faces
21. Matched faces are marked **Present**
22. Date and time are recorded
23. Attendance is saved in `Attendance.csv`
24. Duplicate attendance entries are prevented

---

### 🎓 Student Dashboard
25. Student logs in to view:
   - Profile details
   - Attendance records
   - 📊 Attendance bar graph
   - Marks and notifications
26. Additional features:
   - 📝 Notes section
   - 📚 Assignment tracker
   - 📅 Timetable
   - 🎯 Goal tracker

---

### 👩‍🏫 Teacher Dashboard
27. Teacher can:
   - View student attendance
   - Manage records
   - Monitor class performance

---

### 🛠️ Admin Dashboard
28. Admin can:
   - Add or remove users
   - Manage student database
   - Monitor overall system data

---

### 📊 Data Storage
29. All data is stored in CSV files:
   - `users.csv` → login credentials  
   - `student_database.csv` → student details  
   - `Attendance.csv` → attendance records  
   - `marks.csv` → academic data  
   - `notifications.csv` → alerts & updates


