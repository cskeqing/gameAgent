import sqlite3
import time
import os
import cv2
from loguru import logger

class BlackBoxRecorder:
    def __init__(self, db_path="logs/blackbox.db"):
        self.db_path = db_path
        self.img_dir = "logs/snapshots"
        
        # Ensure directories exist
        log_dir = os.path.dirname(db_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)
            
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS decision_log
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          timestamp REAL,
                          screenshot_path TEXT,
                          prompt TEXT,
                          llm_response TEXT,
                          action TEXT)''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to init DB: {e}")

    def log(self, frame, prompt, response, action):
        timestamp = time.time()
        img_name = f"{int(timestamp*1000)}.jpg"
        img_path = os.path.join(self.img_dir, img_name)
        
        # Save image
        if frame is not None:
            try:
                cv2.imwrite(img_path, frame)
            except Exception as e:
                logger.error(f"Failed to save snapshot: {e}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO decision_log (timestamp, screenshot_path, prompt, llm_response, action) VALUES (?, ?, ?, ?, ?)",
                      (timestamp, img_path, str(prompt), str(response), str(action)))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log to DB: {e}")
