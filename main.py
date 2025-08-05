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
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QSize
import cv2
import sys
import mediapipe as mp
import math

class PoseMentor(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set the app icon to posementor_icon.png
        self.setWindowIcon(QIcon("icons/posementor_icon.png"))
        iconLabel = QLabel()
        iconPixmap = QPixmap("icons/posementor_icon.png")
        # Bigger size here
        iconPixmap = iconPixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)  
        iconLabel.setPixmap(iconPixmap)
        self.setWindowFlags(self.windowFlags() | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
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
        # PoseMentor title and top-left icon
        iconLabel = QLabel()
        iconPixmap = QPixmap("icons/posementor_icon.png")
        iconPixmap = iconPixmap.scaled(85, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Bigger icon
        iconLabel.setPixmap(iconPixmap)

        title = QLabel("PoseMentor")
        title.setFont(QFont("Arial", 30, QFont.Bold))
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # Create the workout dropdown and add items with bigger icons
        self.workoutBox = QComboBox()
        self.workoutBox.setIconSize(QSize(48, 48))  # Ensures icons show at least as big as taskbar icon
        self.workoutBox.addItem(QIcon("icons/pushups_icon.png"), "Pushups")
        self.workoutBox.addItem(QIcon("icons/pullups_icon.png"), "Pullups")
        self.workoutBox.addItem(QIcon("icons/dips_icon.png"), "Dips")
        self.workoutBox.addItem(QIcon("icons/squats_icon.png"), "Bodyweight Squats")
        self.workoutBox.addItem(QIcon("icons/plank_icon.png"), "Plank")
        self.workoutBox.addItem(QIcon("icons/hollowbody_icon.png"), "Hollow Body Hold")
        self.workoutBox.addItem(QIcon("icons/superman_icon.png"), "Superman Hold")
        self.workoutBox.addItem(QIcon("icons/legraises_icon.png"), "Hanging Leg Raises")

        # Start button
        self.startButton = QPushButton("Start Workout")
        self.startButton.clicked.connect(self.start_workout)

        # Camera display area
        self.cameraLabel = QLabel()
        self.cameraLabel.setStyleSheet("background-color: black; border: 2px solid gray;")
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setFixedSize(720, 720)

        # Feedback label
        self.feedbackLabel = QLabel("Select a workout and start.")
        self.feedbackLabel.setFont(QFont("Arial", 12))
        self.feedbackLabel.setAlignment(Qt.AlignCenter)
        self.feedbackLabel.setStyleSheet("color: green")

        # Layout for top panel
        topPanel = QHBoxLayout()
        topPanel.addWidget(iconLabel)       # App icon
        topPanel.addWidget(title)           # Title text
        topPanel.addStretch()
        topPanel.addWidget(QLabel("Select Workout:"))
        topPanel.addWidget(self.workoutBox)
        topPanel.addWidget(self.startButton)

        # Center layout for camera
        centerLayout = QHBoxLayout()
        centerLayout.addStretch()
        centerLayout.addWidget(self.cameraLabel)
        centerLayout.addStretch()

        # Main vertical layout
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topPanel)
        mainLayout.addSpacing(20)
        mainLayout.addLayout(centerLayout)
        mainLayout.addSpacing(10)
        mainLayout.addWidget(self.feedbackLabel)

        # Set layout to central widget
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

        def coords(idx): 
            return [landmarks[idx].x, landmarks[idx].y]

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