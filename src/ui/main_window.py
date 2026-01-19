from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QGroupBox, QLineEdit, QListWidget
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import time
from src.core.capture import ScreenCapture
from src.utils.config import ConfigManager
from src.brain.llm import LLMBrain
from src.brain.planner import Planner
from src.core.executor import AutoPilotThread

class VisionThread(QThread):
    frame_captured = Signal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.capture = None

    def run(self):
        self.capture = ScreenCapture()
        self.running = True
        while self.running:
            frame = self.capture.grab()
            if frame is not None:
                self.frame_captured.emit(frame)
            self.msleep(30) # Limit to ~30 FPS to save CPU

    def stop(self):
        self.running = False
        if self.capture:
            self.capture.release()
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Agent Console - Hybrid Imitation Engine")
        self.resize(1200, 800)
        
        self.vision_thread = VisionThread()
        self.vision_thread.frame_captured.connect(self.update_frame)
        
        # Initialize Config and Brains
        self.config_manager = ConfigManager()
        self.llm_brain = LLMBrain(
            model=self.config_manager.get("llm.model", "gpt-4o-mini"),
            api_base=self.config_manager.get("llm.api_base"),
            api_key=self.config_manager.get("llm.api_key")
        )
        self.planner = Planner(self.llm_brain)
        
        # Auto-Pilot
        self.autopilot_thread = AutoPilotThread(self.planner, self.llm_brain)
        self.autopilot_thread.log_message.connect(self.log)
        self.autopilot_thread.task_updated.connect(self.update_task_list)

        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left Side: Video Feed
        left_layout = QVBoxLayout()
        self.video_label = QLabel("Waiting for video feed...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        self.video_label.setMinimumSize(640, 480)
        left_layout.addWidget(self.video_label)
        
        # Controls under video
        control_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start Vision")
        self.btn_start.clicked.connect(self.start_vision)
        self.btn_stop = QPushButton("Stop Vision")
        self.btn_stop.clicked.connect(self.stop_vision)
        self.btn_stop.setEnabled(False)
        
        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_stop)
        left_layout.addLayout(control_layout)
        
        main_layout.addLayout(left_layout, stretch=2)
        
        # Right Side: Logs and Config
        right_layout = QVBoxLayout()
        
        # Log Group
        log_group = QGroupBox("Decision Logs")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        # Planner Group
        planner_group = QGroupBox("Planner")
        planner_layout = QVBoxLayout()
        
        # Goal Input
        goal_layout = QHBoxLayout()
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("Enter goal (e.g. 'Finish Daily Quests')")
        self.btn_plan = QPushButton("Generate Plan")
        self.btn_plan.clicked.connect(self.generate_plan)
        goal_layout.addWidget(self.goal_input)
        goal_layout.addWidget(self.btn_plan)
        planner_layout.addLayout(goal_layout)
        
        # Auto-Execute Button
        self.btn_auto = QPushButton("Start Auto-Execution 🚀")
        self.btn_auto.clicked.connect(self.toggle_autopilot)
        self.btn_auto.setEnabled(False) # Enable only when plan exists
        planner_layout.addWidget(self.btn_auto)

        # Task List
        self.task_list = QListWidget()
        planner_layout.addWidget(self.task_list)
        
        planner_group.setLayout(planner_layout)

        # Config Group (Placeholder)
        config_group = QGroupBox("Quick Config")
        config_layout = QVBoxLayout()
        config_layout.addWidget(QLabel(f"Model: {self.llm_brain.model}"))
        # Add more config widgets here later
        config_group.setLayout(config_layout)
        
        right_layout.addWidget(log_group, stretch=1)
        right_layout.addWidget(planner_group, stretch=2)
        right_layout.addWidget(config_group, stretch=0)
        
        main_layout.addLayout(right_layout, stretch=1)

    def generate_plan(self):
        goal = self.goal_input.text()
        if not goal:
            self.log("System: Please enter a goal first.")
            return
            
        self.log(f"System: Generating plan for '{goal}'...")
        self.btn_plan.setEnabled(False)
        
        # Run in thread or just blocking for now (MVP)
        # Ideally this should be async
        try:
            self.planner.set_goal(goal)
            self.update_task_list()
            self.log("System: Plan generated.")
            self.btn_auto.setEnabled(True)
        except Exception as e:
            self.log(f"Error: {e}")
        
        self.btn_plan.setEnabled(True)

    def toggle_autopilot(self):
        if self.autopilot_thread.isRunning():
            self.autopilot_thread.stop()
            self.btn_auto.setText("Start Auto-Execution 🚀")
            self.log("System: Auto-Execution paused.")
        else:
            if not self.planner.get_current_task():
                self.log("System: No pending tasks.")
                return
            self.autopilot_thread.start()
            self.btn_auto.setText("Stop Auto-Execution 🛑")
            self.log("System: Auto-Execution started...")

    def update_task_list(self):
        self.task_list.clear()
        for task in self.planner.plan:
            self.task_list.addItem(f"[{task.status.upper()}] {task.description}")

    def start_vision(self):
        if not self.vision_thread.isRunning():
            self.vision_thread.start()
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.log("System: Vision started.")

    def stop_vision(self):
        if self.vision_thread.isRunning():
            self.vision_thread.stop()
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.log("System: Vision stopped.")

    def update_frame(self, frame):
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        
        # Create QImage
        qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale to label size
        scaled_pixmap = QPixmap.fromImage(qt_img).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def log(self, message):
        self.log_text.append(message)
        # Auto scroll
        sb = self.log_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def closeEvent(self, event):
        self.stop_vision()
        event.accept()
