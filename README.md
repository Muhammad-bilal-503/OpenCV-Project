# Real-Time AI-Powered Attendance System

  <!-- IMPORTANT: Create a screen recording (GIF) of your project and replace this link! -->

This project is a complete, real-time attendance system built with Python and modern computer vision libraries. It uses a live webcam feed to automatically detect faces, recognize registered students, and log their attendance, all within a custom-built, user-friendly graphical interface.

## 🌟 Key Features

-   **Live Face Recognition**: Identifies multiple known faces in a real-time video stream.
-   **Dynamic UI & Profile Display**: A custom GUI built with OpenCV displays the camera feed and a dynamic profile card for recognized individuals.
-   **"Unknown" Person Detection**: The system is tuned to ignore faces that do not meet a strict confidence threshold, preventing false positives.
-   **Smart Attendance Logging**:
    -   Automatically records attendance to a `attendance_log.csv` file with student ID, name, date, and time.
    -   Prevents duplicate entries by marking a student only **once per day**.
-   **User-Friendly Feedback**: Provides immediate visual feedback with a "Success" animation when attendance is marked, followed by a cooldown period.
-   **High-Accuracy Matching**:
    -   Learns from multiple training images per person for a more robust facial "fingerprint."
    -   Employs a strict matching tolerance to minimize incorrect identifications.
-   **Optimized for Performance**: Intelligently processes frames to ensure smooth, real-time operation even on standard CPU hardware.

## 🛠️ Tech Stack

-   **Language**: Python
-   **Core Libraries**:
    -   [**OpenCV**](https://opencv.org/): For real-time video capture, image processing, and building the custom GUI.
    -   [**face_recognition**](https://github.com/ageitgey/face_recognition): For high-accuracy face detection and creation of 128-d face encodings.
    -   [**NumPy**](https://numpy.org/): For numerical operations and data manipulation.
-   **Data Handling**: Python's built-in `csv` module.

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### 1. Prerequisites

-   Python 3.8 or newer.
-   A webcam connected to your computer.

### 2. Clone the Repository

Open your terminal and clone this repository:

### 3. Install Dependencies

It is highly recommended to use a virtual environment to manage dependencies.

```bash
# Create and activate a virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install the required packages
pip install opencv-python face-recognition numpy
```
> **Note**: If `pip install face-recognition` fails, you likely need to install `dlib` dependencies first. Install `cmake` and a C++ compiler.
> - **Windows**: Install "C++ development tools" via the Visual Studio Installer.
> - **macOS**: Run `xcode-select --install`.
> - **Linux**: Run `sudo apt-get install build-essential cmake`.
> Then, try the `pip install` command again.

---

## 📁 Project Setup & Configuration

This is the most important step. You must create the following file structure manually before running the script.

### Final Folder Structure

Your project folder must look exactly like this:

```
FACERECOGNIZER/
├── Student_Images/
│   ├── Muhammad_Bilal.jpg
│   ├── Muhammad_Bilal_1.jpg
│   └── ... (and images for other students)
│
├── attendance_app.py      (The main Python script)
├── student_data.csv       (Your student database)
└── checkmark.png          (The success icon)
```

### Step-by-Step File Creation

#### **Step A: Create the `Student_Images/` Folder**
1.  Inside the main project folder, create a new folder named `Student_Images`.
2.  Place high-quality, well-lit photos of the students you want to recognize in this folder.
3.  **For Best Accuracy:** Add 2 to 5 different photos for each person. The system will learn from all of them. The filenames should start with the person's name as it appears in the CSV file (e.g., `Muhammad_Bilal.jpg`, `Muhammad_Bilal_smiling.png`, `Muhammad_Bilal_side.jpg`).

#### **Step B: Create the `student_data.csv` File**
1.  In the main project folder, create a new file named `student_data.csv`.
2.  This file is your database. Open it with any text editor or spreadsheet program.
3.  Add the headers: `Name,ID,Major,ImageFile`.
4.  Add a new row for each student. The `ImageFile` column must contain the filename of the student's *primary* photo.

**Example `student_data.csv` content:**
```csv
Name,ID,Major,ImageFile
Muhammad Bilal,1137,Developer & Photographer,Muhammad_Bilal.jpg
Daniyal Tariq,1138,Computer Science,Daniyal_Tariq.jpg
```

#### **Step C: Add the `checkmark.png` Image**
1.  You must add this image file manually. The program uses it for the success animation.
2.  Download a transparent checkmark icon from the internet.
3.  Save it in the main project folder with the exact name `checkmark.png`.

---

### Automatically Generated Files

#### `attendance_log.csv`
-   **DO NOT create this file yourself.**
-   The Python script (`attendance_app.py`) will **automatically create and update** this file the first time a student's attendance is successfully marked. It serves as the permanent record of attendance.

---

## ▶️ How to Run the Application

Once you have set up the folders and files as described above:

1.  Open your terminal.
2.  Make sure you are in the project's root directory (`FACERECOGNIZER/`).
3.  If you created a virtual environment, make sure it's activated.
4.  Run the script with the following command:

```bash
python attendance_app.py
```
A window will appear with the application UI. Point the camera at a registered student to see it in action. To stop the program, press the **'q'** key.

## ⚙️ How It Works

The application operates through a pipeline of computer vision and logic steps:

1.  **Data Loading**: On startup, the system reads `student_data.csv` and finds all corresponding images for each student in the `Student_Images` folder. It then creates a unique 128-point facial encoding (a mathematical "fingerprint") for each image and stores them in memory.
2.  **Video Capture**: OpenCV captures frames from the webcam in real-time.
3.  **Face Detection & Recognition**: For each frame, it finds all faces and creates encodings for them. It then compares these new encodings against all the "known" encodings using Euclidean distance. A match is confirmed only if the distance is below a strict **tolerance level**.
4.  **State Management & UI**: If a match is found, the system switches to a "SUCCESS" state, logs the attendance (checking for daily duplicates), displays the student's profile and the success animation, and then resets after a 5-second cooldown.


