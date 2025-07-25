# 🤸‍♂️ PoseMentor - AI-Powered Calisthenics Form Checker

**PoseMentor** is a real-time AI application that helps users correct their form in bodyweight workouts like pushups, planks, squats, dips, and more. Built using **PyQt5**, **OpenCV**, and **MediaPipe**, this tool is perfect for calisthenics enthusiasts and fitness learners.

---

## 🎯 Features

- 📷 Real-time pose detection using webcam
- 🧠 AI-powered form analysis and feedback
- 🧘 Supports 8 workouts:
  - Pushups
  - Pullups
  - Dips
  - Bodyweight Squats
  - Plank
  - Hollow Body Hold
  - Superman Hold
  - Hanging Leg Raises
- 🗣 Live feedback with color-coded messages
- 🖥 PyQt5-based intuitive desktop UI

---

## 🛠 Tech Stack

- **Frontend/UI**: PyQt5
- **Computer Vision**: OpenCV
- **Pose Detection**: MediaPipe
- **Language**: Python 3

---

## 🖼 UI Overview

- **Top Left**: App title
- **Top Right**: Workout selector and Start button
- **Center**: Live webcam feed
- **Bottom**: Real-time feedback on form (color-coded)

---

## 🧰 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/posementor.git
cd posementor

## Requirements.txt
PyQt5==5.15.9
opencv-python==4.8.0.76
mediapipe==0.10.3
