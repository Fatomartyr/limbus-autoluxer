import cv2
from screen_capture import ScreenCapture


class TemplateFinder:
    """Find game templates on screen"""
    def __init__(self, screen_capture: ScreenCapture, confidence: float = 0.7):
        self.screen_capture = screen_capture
        self.confidence = confidence
        self._clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

    def _prepare_images(self, roi, template):
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        return self._clahe.apply(roi_gray), self._clahe.apply(template_gray)

    def _match_template_core(self, roi, template, confidence=None):
        if confidence is None:
            confidence = self.confidence
        roi_gray, template_gray = self._prepare_images(roi, template)
        result = cv2.matchTemplate(roi_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            return max_loc[0], max_loc[1], max_val, template.shape[:2]
        return None

    def find_in_region(self, template, confidence=None, x_percent=(0, 100), y_percent=(0, 100)):
        roi = self.screen_capture.capture_region(x_percent, y_percent)
        match = self._match_template_core(roi, template, confidence)
        if match:
            x, y, _, (h_t, w_t) = match
            coords = self.screen_capture.get_window_coords()
            offset_x = coords["left"] + int(coords["width"] * x_percent[0] / 100)
            offset_y = coords["top"] + int(coords["height"] * y_percent[0] / 100)
            center_x = offset_x + x + w_t // 2
            center_y = offset_y + y + h_t // 2
            return int(center_x), int(center_y)
        return None

    def find_on_screen(self, template, confidence=None):
        return self.find_in_region(template, confidence, (0, 100), (0, 100))

    def find_in_roi(self, template, roi, offset_x=0, offset_y=0, confidence=None):
        if template is None or roi is None:
            return None

        match = self._match_template_core(roi, template, confidence)
        if match:
            x, y, _, (h_t, w_t) = match
            center_x = offset_x + x + w_t // 2
            center_y = offset_y + y + h_t // 2
            return int(center_x), int(center_y)
        return None
