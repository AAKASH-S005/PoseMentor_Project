import os
os.environ['QT_OPENGL'] = 'software'
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from  PyQt5.QtWidgets import QLabel
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
        self.setWindowIcon(QIcon("Icons/posementor_icon.png"))
        iconLabel = QLabel()
        iconPixmap = QPixmap("Icons/posementor_icon.png")
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
        # PsoeMentor title and top-left icon
        iconLabel = QLabel()
        iconPixmap = QPixmap("Icons/posementor_icon.png")
        iconPixmap = iconPixmap.scaled(85, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        iconLabel.setPixmap(iconPixmap)

        # Logo and Title
        title = QLabel("PoseMentor")
        title.setFont(QFont("Arial", 30, QFont.Bold))
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        #Create the workout dropdown and add items with bigger icons
        self.workoutBox = QComboBox()
        # Ensures icons show 
        self.workoutBox.setIconSize(QSize(48, 48))
        # PushUps
        self.workoutBox.addItem(QIcon("Icons/pushups_icon.png"), "Pushups")
        # PullUps
        self.workoutBox.addItem(QIcon("Icons/pullups_icon.png"), "Pullups")
        # Parallel Dips
        self.workoutBox.addItem(QIcon("Icons/dips_icon.png"), "Parallel Dips")
        # BodyWeight Squats
        self.workoutBox.addItem(QIcon("Icons/squats_icon.png"), "Bodyweight Squats")
        # Plank
        self.workoutBox.addItem(QIcon("Icons/plank_icon.png"), "Plank")
        # HollowBody Hold
        self.workoutBox.addItem(QIcon("Icons/hollowbody_icon.png"), "Hollow Body Hold")
        # Superman Hold
        self.workoutBox.addItem(QIcon("Icons/superman_icon.png"), "Superman Hold")
        # Hanging Leg Raises
        self.workoutBox.addItem(QIcon("Icons/legraises_icon.png"), "Hanging Leg Raises")

        # Start your Workout
        self.startButton = QPushButton("Start Workout")
        self.startButton.setIcon(QIcon("Icons/start_icon.png"))
        # Set ison size on startbutton
        self.startButton.setIconSize(QSize(30, 30)) 
        self.startButton.clicked.connect(self.start_workout)

        # Camera Display area
        # Camera Scanner Background
        self.cameraLabel = QLabel()
        self.cameraLabel.setStyleSheet("background-color: black; border: 2px solid gray;")
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.cameraLabel.setFixedSize(720, 720)
        
        #Feedback label
        self.feedbackLabel = QLabel("Select a workout and start.")
        self.feedbackLabel.setFont(QFont("Arial", 12))
        self.feedbackLabel.setAlignment(Qt.AlignCenter)
        self.feedbackLabel.setStyleSheet("color: green")

        # Layout for top panel
        topPanel = QHBoxLayout()
        # Add icon
        topPanel.addWidget(iconLabel)    
        # Title text
        topPanel.addWidget(title)          
        topPanel.addStretch()
        topPanel.addWidget(QLabel("Select Workout:"))
        topPanel.addWidget(self.workoutBox)
        topPanel.addWidget(self.startButton)

        # Central layout for camera
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

    # Workout analyser and initialiser
    def start_workout(self):
        self.feedbackLabel.setText(f"Form checking for {self.workoutBox.currentText()} started.")
        self.feedbackLabel.setStyleSheet("color: green")
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.timer.start(30)

    # Angle Monitoring
    def get_angle(self, a, b, c):
        ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
        return abs(ang + 360) if ang < 0 else abs(ang)
    
    # Pose Analyser
    def analyze_pose(self, lm, workout):
        feedback = "Good form! Keep it up."
        feedback_color = "green"
        def coords(i): 
            return [lm[i].x, lm[i].y]
        a = lambda i, j, k: self.get_angle(coords(i), coords(j), coords(k))

        if workout == "Pushups":
            e_angle = a(12, 14, 16)
            h_angle = a(12, 24, 26)
            s_y, h_y = lm[12].y, lm[24].y

            b_straight = abs(s_y - h_y) < 0.05

            if e_angle > 160:
                feedback = "Not going low enough. Lower your chest and adjust your hips."
            elif e_angle < 40:
                feedback = "Too deep. Maintain a straight pushup."
            elif h_angle < 150:
                feedback = "Don't let your Hips sagging or piking. Tighten your core."
            elif not b_straight:
                feedback = "Keep your body straight like a Bridge."

            if feedback != "Good form! Keep it up.": feedback_color = "red"

        elif workout == "Pullups":
            e_angle = a(12, 14, 16)
            c_y = lm[0].y
            s_y = lm[12].y
            swing = abs(lm[24].x - lm[23].x) > 0.1

            if e_angle > 150:
                feedback = "Pull higher. Elbows too extended."
            elif e_angle < 50:
                feedback = "Too low. Control descent."
            elif swing:
                feedback = "Avoid swinging yourself. Control movement."
            elif c_y > s_y:
                feedback = "Your Chin not above bar."

            if feedback != "Good form! Keep it up.": feedback_color = "red"

        elif workout == "Parallel Dips":
            e_angle = a(12, 14, 16)
            tilt = abs(lm[12].x - lm[24].x) > 0.1
            if e_angle > 150:
                feedback = "Not dipping deep enough."
            elif e_angle < 60:
                feedback = "You're Too low. Risk of shoulder strain."
            elif tilt:
                feedback = "Keep your torso upright."
            elif abs(lm[12].y - lm[14].y) > 0.15:
                feedback = "Your Shoulders looks uneven."

            if feedback != "Good form! Keep it up.": feedback_color = "red"

        elif workout == "Bodyweight Squats":
            k_angle = a(24, 26, 28)
            b_angle = a(12, 24, 26)
            knee_in = abs(lm[26].x - lm[28].x) > 0.15
            feet_wide = abs(lm[27].x - lm[28].x) > 0.5

            if k_angle > 150:
                feedback = "You're Not squatting deep enough."
            elif k_angle < 60:
                feedback = "Too deep. Avoid knee strain."
            elif b_angle < 150:
                feedback = "Keep your back straighter."
            elif not feet_wide:
                feedback = "Spread your feet Slight more."

            if feedback != "Good form! Keep it up.": feedback_color = "red"

        elif workout == "Plank":
            angle = a(12, 24, 28)
            if angle < 160:
                feedback = "Engage your core. Body not straight."
            elif abs(lm[12].y - lm[14].y) > 0.1:
                feedback = "Shoulders not aligned."
            elif abs(lm[12].x - lm[14].x) > 0.1:
                feedback = "Keep shoulders over wrists."
            elif abs(lm[24].y - lm[26].y) > 0.1:
                feedback = "Hips too high/low."

            if feedback != "Good form! Keep it up.": feedback_color = "red"

        elif workout == "Hollow Body Hold":
            angle = a(12, 24, 26)
            if angle > 120:
                feedback = "Tighten your core."
            elif lm[24].y > lm[12].y:
                feedback = "Lift shoulders."
            elif lm[28].y > lm[26].y:
                feedback = "Lift legs slight higher."
            elif abs(lm[24].y - lm[26].y) > 0.1:
                feedback = "Bend knees less."

            if feedback != "Good form! Keep it up.": feedback_color = "red"

        elif workout == "Superman Hold":
            angle = a(11, 23, 27)
            if angle < 140:
                feedback = "Lift chest and legs more."
            elif abs(lm[11].y - lm[23].y) > 0.2:
                feedback = "Arms too low."
            elif abs(lm[27].y - lm[23].y) > 0.2:
                feedback = "Legs too low."
            elif abs(lm[0].y - lm[23].y) > 0.3:
                feedback = "Neck not aligned."

            if feedback != "Good form! Keep it up.": feedback_color = "red"

        elif workout == "Hanging Leg Raises":
            angle = a(24, 26, 28)
            if angle < 70:
                feedback = "Raise legs higher."
            elif abs(lm[24].x - lm[23].x) > 0.1:
                feedback = "Stop swinging."
            elif abs(lm[28].x - lm[26].x) > 0.1:
                feedback = "Control knees."
            elif abs(lm[11].x - lm[12].x) > 0.1:
                feedback = "Keep grip balanced."

            if feedback != "Good form! Keep it up.": feedback_color = "red"

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
