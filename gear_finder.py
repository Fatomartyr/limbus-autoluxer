import cv2
import numpy as np
from typing import Optional, Tuple, Dict, Any
from screen_capture import ScreenCapture
from template_finder import TemplateFinder


class GearFinder:
    """Gear Finder Class with double-check search(near win rate and with color definition)"""
    def __init__(self, screen_capture: ScreenCapture, template_finder: TemplateFinder, gear_template=None):
        self.screen_capture = screen_capture
        self.template_finder = template_finder
        self.gear_template = gear_template
        self.search_width_percent = 15
        self.search_height_percent = 15

    def find_near_win_rate(self, win_rate_pos) -> Optional[Tuple[int, int]]:
        coords = self.screen_capture.get_window_coords()
        if coords is None or self.gear_template is None:
            return None

        win_w = coords["width"]
        win_h = coords["height"]

        search_width_px = int(win_w * self.search_width_percent / 100)
        search_height_px = int(win_h * self.search_height_percent / 100)

        win_rate_x = win_rate_pos[0] - coords["left"]
        win_rate_y = win_rate_pos[1] - coords["top"]

        x1 = max(0, win_rate_x - search_width_px)
        y1 = max(0, win_rate_y - search_height_px // 2)
        x2 = min(win_w, win_rate_x)
        y2 = min(win_h, win_rate_y + search_height_px // 2)

        roi = self.screen_capture.capture_region(
            (x1 / win_w * 100, x2 / win_w * 100),
            (y1 / win_h * 100, y2 / win_h * 100)
        )
        if roi is None or roi.size == 0:
            return None

        template_result = self.template_finder.find_in_roi(
            self.gear_template, roi,
            offset_x=coords["left"] + x1,
            offset_y=coords["top"] + y1,
            confidence=0.4
        )
        if template_result:
            return template_result

        return self._find_by_bright_center(roi, x1, y1, coords)

    @staticmethod
    def _find_by_bright_center(roi: np.ndarray, offset_x: int, offset_y: int, coords: Dict[str, int]) -> Optional[Tuple[int, int]]:
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        lower_bright = np.array([15, 100, 200])
        upper_bright = np.array([30, 255, 255])
        bright_mask = cv2.inRange(hsv, lower_bright, upper_bright)

        kernel = np.ones((5, 5), np.uint8)
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            for contour in contours[:3]:
                area = cv2.contourArea(contour)
                x, y, w, h = cv2.boundingRect(contour)

                if area < 500 or w < 30 or h < 30:
                    continue

                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])

                    global_x = coords["left"] + offset_x + cX
                    global_y = coords["top"] + offset_y + cY
                    return int(global_x), int(global_y)

        return None
