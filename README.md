# 🎭 Face Recognition Attendance System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A smart, automated attendance system that uses real-time face recognition to mark attendance — no manual entry needed!

---

## 💡 Features
- 🔍 Real-time face detection using webcam
- 🧠 Automatic attendance marking using face recognition
- 📝 Register new students/faces into the system
- 📊 Attendance records saved with date and time
- 📁 Export attendance data
- 🖥️ Clean and beginner-friendly UI built with Streamlit

---

## 🛠️ Technologies Used
| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| OpenCV | Real-time face detection |
| Face Recognition | Face encoding and matching |
| Streamlit | Web interface |
| Pandas | Attendance data management |

---

## 📂 Project Structure

```
Face_recognition_Attendance/
│
├── home.py               # Main app entry point
├── scanner.py            # Face scanning logic
├── register_face.py      # Register new faces
├── train_model.py        # Train the recognition model
├── requirements.txt      # Dependencies
│
├── data/                 # Attendance records
├── dataset/              # Stored face images
├── models/               # Trained models
├── modules/              # Helper modules
└── pages/                # Streamlit pages
```

---

## ⚙️ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Priix4/Face-Recognition-Attendance.git
cd Face-Recognition-Attendance
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run home.py
```

---

## 🚀 How It Works
1. **Register** — Add a new person by capturing their face images
2. **Train** — Train the model on registered faces
3. **Scan** — Run the scanner to detect and recognize faces
4. **Attendance** — Attendance is automatically marked and saved

---

## 👩‍💻 Author
**Priya Gupta** 

[![GitHub](https://img.shields.io/badge/GitHub-Priix4-black?logo=github)](https://github.com/Priix4)

---

## 📄 License
This project is licensed under the MIT License.


