import pyautogui
import time
import random
from loguru import logger

class InputEngine:
    def __init__(self):
        # Fail-safe: moving mouse to corner throws exception
        pyautogui.FAILSAFE = True
        self.mouse_speed = 0.5 # Default duration in seconds

    def move_to(self, x, y, duration=None):
        """
        Human-like mouse movement using PyAutoGUI's tweening + jitter.
        """
        dur = duration if duration else self.mouse_speed
        
        # Add random offset to target to simulate human inaccuracy
        target_x = x + random.randint(-3, 3)
        target_y = y + random.randint(-3, 3)
        
        # Add random variation to duration
        real_dur = dur * random.uniform(0.8, 1.2)
        
        try:
            # easeOutQuad starts fast and slows down at the end, natural for mouse
            pyautogui.moveTo(target_x, target_y, duration=real_dur, tween=pyautogui.easeOutQuad)
        except Exception as e:
            logger.error(f"Mouse move failed: {e}")

    def click(self, x=None, y=None):
        if x is not None and y is not None:
            self.move_to(x, y)
        
        time.sleep(random.uniform(0.05, 0.15))
        pyautogui.click()
        logger.debug(f"Clicked at {x}, {y}")

    def press(self, key):
        pyautogui.press(key)
        time.sleep(random.uniform(0.05, 0.15))
        logger.debug(f"Pressed key: {key}")
