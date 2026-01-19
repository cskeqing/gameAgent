from PySide6.QtCore import QThread, Signal
from loguru import logger
import time
import json
from src.core.capture import ScreenCapture
from src.core.vision import VisionEngine
from src.core.input import InputEngine
from src.brain.llm import LLMBrain
from src.brain.planner import Planner

class AutoPilotThread(QThread):
    log_message = Signal(str)
    task_updated = Signal()

    def __init__(self, planner: Planner, llm: LLMBrain):
        super().__init__()
        self.planner = planner
        self.llm = llm
        self.running = False
        self.capture = ScreenCapture()
        self.vision = VisionEngine() # YOLO loaded by default
        self.input_engine = InputEngine()

    def run(self):
        self.running = True
        self.log_message.emit("Auto-Pilot Started.")

        while self.running:
            # 1. Get Current Task
            current_task = self.planner.get_current_task()
            if not current_task:
                self.log_message.emit("No pending tasks. Auto-Pilot finished.")
                break
            
            if current_task.status == "completed":
                # Should have advanced index, but just in case
                self.planner.complete_current_task()
                continue

            self.log_message.emit(f"Executing Task: {current_task.description}")

            # 2. Perception
            frame = self.capture.grab()
            if frame is None:
                self.log_message.emit("Failed to grab screen.")
                time.sleep(1)
                continue

            # Run OCR & Object Detection
            # We assume YOLO is light, OCR is heavier. Run both for max context.
            objects = self.vision.detect_objects(frame)
            texts = self.vision.detect_text(frame)
            
            vision_data = {
                "objects": [{"name": o["name"], "box": o["box"]} for o in objects],
                "texts": [{"text": t["text"], "box": t["box"]} for t in texts]
            }

            # 3. Decision (LLM)
            action_plan = self.llm.decide_action(current_task.description, vision_data)
            self.log_message.emit(f"Decision: {action_plan.get('reasoning', 'No reasoning')}")

            # 4. Execution
            action_type = action_plan.get("action")
            target = action_plan.get("target")
            value = action_plan.get("value")

            if action_type == "click":
                coords = self._resolve_coords(target, vision_data)
                if coords:
                    x, y = coords
                    self.input_engine.move_to(x, y)
                    self.input_engine.click()
                    self.log_message.emit(f"Clicked at ({x}, {y})")
                    # Assume click completes the step for now (naive)
                    self.planner.complete_current_task()
                    self.task_updated.emit()
                else:
                    self.log_message.emit(f"Target '{target}' not found on screen.")
            
            elif action_type == "type":
                if value:
                    # Click first if target provided, else just type
                    if target:
                        coords = self._resolve_coords(target, vision_data)
                        if coords:
                            self.input_engine.move_to(coords[0], coords[1])
                            self.input_engine.click()
                    
                    self.input_engine.type_text(value) # Need to impl type_text in InputEngine
                    self.log_message.emit(f"Typed '{value}'")
                    self.planner.complete_current_task()
                    self.task_updated.emit()

            elif action_type == "press":
                if value:
                    self.input_engine.press(value)
                    self.log_message.emit(f"Pressed '{value}'")
                    self.planner.complete_current_task()
                    self.task_updated.emit()
            
            elif action_type == "finish":
                self.planner.complete_current_task()
                self.task_updated.emit()

            elif action_type == "wait":
                time.sleep(2)
            
            # Wait a bit before next loop
            time.sleep(1)

        self.running = False
        self.log_message.emit("Auto-Pilot Stopped.")

    def _resolve_coords(self, target, vision_data):
        """
        Convert target string/list to (x, y) center coordinates.
        """
        if isinstance(target, list) and len(target) == 2:
            return target
        
        if isinstance(target, str):
            # Try to match text
            for t in vision_data["texts"]:
                if target.lower() in t["text"].lower():
                    # Box is [[x1,y1], [x2,y1], [x2,y2], [x1,y2]] usually from Paddle
                    # But our vision.py returns simple format? Let's check vision.py
                    # Vision.py detect_text returns box_points = [[x,y],...]
                    # Let's calculate center
                    points = t["box"]
                    center_x = int((points[0][0] + points[2][0]) / 2)
                    center_y = int((points[0][1] + points[2][1]) / 2)
                    return (center_x, center_y)
            
            # Try to match object name
            for o in vision_data["objects"]:
                if target.lower() in o["name"].lower():
                    # Box is [x1, y1, x2, y2]
                    b = o["box"]
                    center_x = int((b[0] + b[2]) / 2)
                    center_y = int((b[1] + b[3]) / 2)
                    return (center_x, center_y)
                    
        return None

    def stop(self):
        self.running = False
        self.wait()
