from ultralytics import YOLO
from paddleocr import PaddleOCR
from loguru import logger
import numpy as np

class VisionEngine:
    def __init__(self, model_path=None):
        self.yolo = None
        self.ocr = None
        self._load_yolo(model_path)
        # Lazy load OCR because it's heavy and might not be needed immediately
        self.ocr_loaded = False

    def _load_yolo(self, path):
        try:
            model_name = path if path else "yolov8n.pt"
            self.yolo = YOLO(model_name)
            logger.info(f"YOLO model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load YOLO: {e}")

    def _ensure_ocr(self):
        if not self.ocr_loaded:
            try:
                logger.info("Initializing PaddleOCR...")
                # use_angle_cls=False for speed, lang="ch" for Chinese support
                self.ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)
                self.ocr_loaded = True
                logger.info("PaddleOCR loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load OCR: {e}")

    def detect_objects(self, frame):
        """
        Run YOLO detection.
        Returns: List of dicts {cls, conf, box: [x1,y1,x2,y2], name}
        """
        detections = []
        if self.yolo:
            try:
                results = self.yolo(frame, verbose=False)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        b = box.xyxy[0].cpu().numpy().tolist() # x1, y1, x2, y2
                        c = int(box.cls)
                        conf = float(box.conf)
                        name = self.yolo.names[c]
                        detections.append({
                            "class": c,
                            "name": name,
                            "confidence": conf,
                            "box": [int(x) for x in b]
                        })
            except Exception as e:
                logger.error(f"YOLO detection failed: {e}")
        return detections

    def detect_text(self, frame):
        """
        Run OCR.
        Returns: List of dicts {text, conf, box}
        """
        self._ensure_ocr()
        texts = []
        if self.ocr:
            try:
                # PaddleOCR expects numpy array (BGR or RGB)
                result = self.ocr.ocr(frame, cls=False)
                if result and result[0]:
                    for line in result[0]:
                        # line format: [[pt1, pt2, pt3, pt4], (text, conf)]
                        box_points = line[0]
                        txt_info = line[1]
                        texts.append({
                            "text": txt_info[0],
                            "confidence": txt_info[1],
                            "box": box_points
                        })
            except Exception as e:
                logger.error(f"OCR failed: {e}")
        return texts
