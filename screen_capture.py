import cv2
import numpy as np
from mss import mss


class ScreenCapture:
    """Capture game screen"""
    def __init__(self, game_window):
        self.game_window = game_window

    def capture_region(self, x_percent=(0, 100), y_percent=(0, 100)):

        if self.game_window is None:
            return None

        with mss() as sct:
            monitor = {
                "left": self.game_window.left,
                "top": self.game_window.top,
                "width": self.game_window.width,
                "height": self.game_window.height
            }
            screenshot = np.asarray(sct.grab(monitor))  # type: ignore[arg-type]
            screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        h, w = screenshot_bgr.shape[:2]
        x1 = int(w * x_percent[0] / 100)
        x2 = int(w * x_percent[1] / 100)
        y1 = int(h * y_percent[0] / 100)
        y2 = int(h * y_percent[1] / 100)

        roi = screenshot_bgr[y1:y2, x1:x2]
        return roi if roi.size > 0 else None

    def capture_full(self):
        return self.capture_region((0, 100), (0, 100))

    def get_window_coords(self):
        if self.game_window is None:
            return None
        return {
            "left": self.game_window.left,
            "top": self.game_window.top,
            "width": self.game_window.width,
            "height": self.game_window.height
        }
