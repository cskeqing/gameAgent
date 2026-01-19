from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QGroupBox
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import time
from src.core.capture import ScreenCapture

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
        
        # Config Group (Placeholder)
        config_group = QGroupBox("Quick Config")
        config_layout = QVBoxLayout()
        config_layout.addWidget(QLabel("Agent Mode: Hybrid (Rule + LLM)"))
        # Add more config widgets here later
        config_group.setLayout(config_layout)
        
        right_layout.addWidget(log_group, stretch=2)
        right_layout.addWidget(config_group, stretch=1)
        
        main_layout.addLayout(right_layout, stretch=1)

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
