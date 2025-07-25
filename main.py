import os
os.environ['QT_OPENGL'] = 'software'
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
import cv2
import sys
import mediapipe as mp
import math

class PoseMentor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PoseMentor -> AI-Powered Calisthenics Workout Form Corrector")
        self.setGeometry(100, 100, 900, 700)

        self.initUI()
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def initUI(self):
        title = QLabel("PoseMentor")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)

        self.workoutBox = QComboBox()
        self.workoutBox.addItems([
            "Pushups", "Pullups", "Dips", "Bodyweight Squats",
            "Plank", "Hollow Body Hold", "Superman Hold", "Hanging Leg Raises"
        ])
        self.startButton = QPushButton("Start Workout")
        self.startButton.clicked.connect(self.start_workout)

        self.cameraLabel = QLabel()
        self.cameraLabel.setStyleSheet("background-color: black; border: 2px solid gray;")
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setFixedSize(640, 480)

        self.feedbackLabel = QLabel("Select a workout and start.")
        self.feedbackLabel.setFont(QFont("Arial", 12))
        self.feedbackLabel.setAlignment(Qt.AlignCenter)
        self.feedbackLabel.setStyleSheet("color: green")

        topPanel = QHBoxLayout()
        topPanel.addWidget(title)
        topPanel.addStretch()
        topPanel.addWidget(QLabel("Select Workout:"))
        topPanel.addWidget(self.workoutBox)
        topPanel.addWidget(self.startButton)

        centerLayout = QHBoxLayout()
        centerLayout.addStretch()
        centerLayout.addWidget(self.cameraLabel)
        centerLayout.addStretch()

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topPanel)
        mainLayout.addSpacing(20)
        mainLayout.addLayout(centerLayout)
        mainLayout.addSpacing(10)
        mainLayout.addWidget(self.feedbackLabel)

        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def start_workout(self):
        self.feedbackLabel.setText(f"Form checking for {self.workoutBox.currentText()} started.")
        self.feedbackLabel.setStyleSheet("color: green")
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.timer.start(30)

    def get_angle(self, a, b, c):
        ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
        return abs(ang + 360) if ang < 0 else abs(ang)

    def analyze_pose(self, landmarks, workout):
        feedback = "Good form!"
        feedback_color = "green"

        def coords(idx): return [landmarks[idx].x, landmarks[idx].y]

        if workout == "Pushups":
            shoulder = coords(12)
            elbow = coords(14)
            wrist = coords(16)
            angle = self.get_angle(shoulder, elbow, wrist)
            if angle > 160:
                feedback = "You're not lowering enough. Go deeper."
                feedback_color = "red"
            elif angle < 40:
                feedback = "You're too low. Maintain a straight pushup."
                feedback_color = "red"

        elif workout == "Plank":
            shoulder = coords(12)
            hip = coords(24)
            ankle = coords(28)
            angle = self.get_angle(shoulder, hip, ankle)
            if angle < 160:
                feedback = "Body is not straight. Engage your core."
                feedback_color = "red"

        elif workout == "Bodyweight Squats":
            hip = coords(24)
            knee = coords(26)
            ankle = coords(28)
            angle = self.get_angle(hip, knee, ankle)
            if angle > 150:
                feedback = "You're not squatting deep enough."
                feedback_color = "red"
            elif angle < 60:
                feedback = "Too deep. Avoid straining your knees."
                feedback_color = "red"

        elif workout == "Hollow Body Hold":
            shoulder = coords(12)
            hip = coords(24)
            knee = coords(26)
            angle = self.get_angle(shoulder, hip, knee)
            if angle > 120:
                feedback = "Tighten your core. Maintain the hollow shape."
                feedback_color = "red"

        elif workout == "Superman Hold":
            shoulder = coords(11)
            hip = coords(23)
            ankle = coords(27)
            angle = self.get_angle(shoulder, hip, ankle)
            if angle < 140:
                feedback = "Lift chest and legs higher."
                feedback_color = "red"

        elif workout == "Pullups":
            shoulder = coords(12)
            elbow = coords(14)
            wrist = coords(16)
            angle = self.get_angle(shoulder, elbow, wrist)
            if angle > 160:
                feedback = "Pull up higher. Elbows not bent enough."
                feedback_color = "red"

        elif workout == "Dips":
            shoulder = coords(12)
            elbow = coords(14)
            wrist = coords(16)
            angle = self.get_angle(shoulder, elbow, wrist)
            if angle > 150:
                feedback = "You're not dipping low enough."
                feedback_color = "red"
            elif angle < 60:
                feedback = "Going too low. Avoid shoulder strain."
                feedback_color = "red"

        elif workout == "Hanging Leg Raises":
            hip = coords(24)
            knee = coords(26)
            ankle = coords(28)
            angle = self.get_angle(hip, knee, ankle)
            if angle < 70:
                feedback = "Raise your legs higher."
                feedback_color = "red"

        return feedback, feedback_color

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_image)

                if results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        rgb_image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                    )
                    workout = self.workoutBox.currentText()
                    feedback, color = self.analyze_pose(results.pose_landmarks.landmark, workout)
                    self.feedbackLabel.setText(feedback)
                    self.feedbackLabel.setStyleSheet(f"color: {color}")

                h, w, ch = rgb_image.shape
                qimg = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
                self.cameraLabel.setPixmap(QPixmap.fromImage(qimg))


    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PoseMentor()
    window.show()
    sys.exit(app.exec_()) 


""" from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
import cv2
import sys
import mediapipe as mp
import math

class PoseMentor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PoseMentor - Calisthenics Workout Form Checker")
        self.setGeometry(100, 100, 900, 700)

        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose()

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.initUI()

    def initUI(self):
        # Title Label
        title = QLabel("PoseMentor")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)

        # Workout Selector
        self.workoutBox = QComboBox()
        self.workoutBox.addItems([
            "Pushups", "Plank", "Squats"
        ])
        self.startButton = QPushButton("Start Workout")
        self.startButton.clicked.connect(self.start_workout)

        # Camera display
        self.cameraLabel = QLabel()
        self.cameraLabel.setStyleSheet("background-color: black; border: 2px solid gray;")
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setFixedSize(640, 480)

        # Feedback label
        self.feedbackLabel = QLabel("Select a workout and start.")
        self.feedbackLabel.setStyleSheet("color: green")
        self.feedbackLabel.setAlignment(Qt.AlignCenter)

        # Top panel (title + workout selection)
        topPanel = QHBoxLayout()
        topPanel.addWidget(title)
        topPanel.addStretch()
        topPanel.addWidget(QLabel("Select Workout:"))
        topPanel.addWidget(self.workoutBox)
        topPanel.addWidget(self.startButton)

        # Center camera layout
        centerLayout = QHBoxLayout()
        centerLayout.addStretch()
        centerLayout.addWidget(self.cameraLabel)
        centerLayout.addStretch()

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topPanel)
        mainLayout.addSpacing(20)
        mainLayout.addLayout(centerLayout)
        mainLayout.addSpacing(10)
        mainLayout.addWidget(self.feedbackLabel)

        # Set central widget
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def start_workout(self):
        self.feedbackLabel.setText(f"Checking form for {self.workoutBox.currentText()}")
        self.feedbackLabel.setStyleSheet("color: green")
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.timer.start(30)

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_image)

                if results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        rgb_image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                    )
                    workout = self.workoutBox.currentText()
                    feedback, color = self.analyze_pose(results.pose_landmarks.landmark, workout)
                    self.feedbackLabel.setText(feedback)
                    self.feedbackLabel.setStyleSheet(f"color: {color}")

                h, w, ch = rgb_image.shape
                qimg = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
                self.cameraLabel.setPixmap(QPixmap.fromImage(qimg))

    def get_angle(self, a, b, c):
        angle = math.degrees(math.atan2(c.y - b.y, c.x - b.x) -
                             math.atan2(a.y - b.y, a.x - b.x))
        return abs(angle) if angle > 0 else abs(angle + 360)

    def analyze_pose(self, landmarks, workout):
        if workout == "Pushups":
            left_elbow = self.get_angle(landmarks[11], landmarks[13], landmarks[15])
            right_elbow = self.get_angle(landmarks[12], landmarks[14], landmarks[16])
            if left_elbow < 70 and right_elbow < 70:
                return "Good pushup form.", "green"
            else:
                return "Elbows not bent enough. Lower your body.", "red"

        elif workout == "Plank":
            left_shoulder = landmarks[11]
            left_hip = landmarks[23]
            left_knee = landmarks[25]
            angle = self.get_angle(left_shoulder, left_hip, left_knee)
            if 160 < angle < 180:
                return "Great plank posture.", "green"
            else:
                return "Hips not aligned. Keep your body straight.", "red"

        elif workout == "Squats":
            left_knee = self.get_angle(landmarks[23], landmarks[25], landmarks[27])
            right_knee = self.get_angle(landmarks[24], landmarks[26], landmarks[28])
            if left_knee < 100 and right_knee < 100:
                return "Nice squat depth!", "green"
            else:
                return "Go deeper in your squat.", "red"

        return "Pose detection running...", "gray"

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PoseMentor()
    window.show()
    sys.exit(app.exec_()) """