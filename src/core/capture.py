import sys
import platform
import numpy as np
import cv2
from loguru import logger

class ScreenCapture:
    def __init__(self):
        self.os_type = platform.system()
        self.camera = None
        self.method = "unknown"
        self._init_camera()

    def _init_camera(self):
        if self.os_type == 'Windows':
            try:
                import dxcam
                # output_color="BGR" ensures we get OpenCV compatible format directly
                self.camera = dxcam.create(output_color="BGR")
                self.method = "dxcam"
                logger.info("Initialized DXCam backend for Windows.")
            except ImportError:
                logger.warning("DXCam not found, falling back to MSS.")
                self._init_mss()
            except Exception as e:
                logger.error(f"DXCam failed initialization: {e}, falling back to MSS.")
                self._init_mss()
        else:
            self._init_mss()

    def _init_mss(self):
        import mss
        self.camera = mss.mss()
        self.method = "mss"
        logger.info(f"Initialized MSS backend for {self.os_type}.")

    def grab(self, region=None):
        """
        Capture screen.
        region: (left, top, width, height) or None for full screen.
        Returns: np.array (BGR) ready for OpenCV/YOLO.
        """
        try:
            if self.method == "dxcam":
                # DXCam grab. region is (left, top, right, bottom) for dxcam?
                # Check dxcam docs: region is (left, top, right, bottom)
                frame = None
                if region:
                    left, top, w, h = region
                    right, bottom = left + w, top + h
                    frame = self.camera.grab(region=(left, top, right, bottom))
                else:
                    frame = self.camera.grab()
                
                if frame is None:
                    return None
                return frame

            elif self.method == "mss":
                monitor = self.camera.monitors[1] # Primary monitor
                if region:
                    left, top, w, h = region
                    monitor = {"top": top, "left": left, "width": w, "height": h}
                
                img = self.camera.grab(monitor)
                # MSS returns BGRA, convert to BGR
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                return frame
                
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None

    def release(self):
        if self.method == "dxcam":
            del self.camera
        elif self.method == "mss":
            self.camera.close()
