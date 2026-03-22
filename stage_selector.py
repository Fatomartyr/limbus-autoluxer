import time
from typing import Optional, Tuple, Callable

try:
    from pynput import mouse
    PYINPUT_AVAILABLE = True
except ImportError:
    PYINPUT_AVAILABLE = False
    mouse = None


class StageSelector:
    """Handles mouse click detection for stage selection in game window."""

    DEFAULT_TIMEOUT: int = 1800
    CHECK_INTERVAL: float = 0.1
    NOTIFY_INTERVAL: int = 60

    def __init__(self, game_window):
        self.game_window = game_window
        self._stage_select_position: Optional[Tuple[int, int]] = None
        self._stage_start_position: Optional[Tuple[int, int]] = None

    def wait_for_user_click(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        click_number: int = 1,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[Tuple[int, int]]:
        """
        Wait for user to click inside game window.
        :param timeout:
        :param click_number: 1 for stage select, 2 for stage start
        :param status_callback: Function to call for status updates
        :return: Click coordinates (x, y) or None if timeout/error
        """
        if not PYINPUT_AVAILABLE:
            self._notify_status(status_callback, "❌ Ошибка: пакет 'pynput' не установлен")
            return None

        self._click_position: Optional[Tuple[int, int]] = None
        self._click_received = False

        if click_number == 1:
            self._notify_status(status_callback, "Ожидание ПЕРВОГО клика...\nКликните на кнопку 'Enter' стадии")
        else:
            self._notify_status(status_callback, "Ожидание ВТОРОГО клика...\nКликните на кнопку запуска боя")

        def on_click(x, y, button, pressed):
            """Callback for mouse click events."""
            if button == mouse.Button.left and pressed:
                pos = (int(x), int(y))
                if self._is_in_game_window(pos):
                    self._click_position = pos
                    self._click_received = True
                    return False

        with mouse.Listener(on_click=on_click):
            start_time = time.time()

            while not self._click_received:
                elapsed = int(time.time() - start_time)

                if elapsed > 0 and elapsed % self.NOTIFY_INTERVAL == 0:
                    minutes = elapsed // 60
                    self._notify_status(status_callback, f"Прошло {minutes} мин... ожидание клика")
                if elapsed >= timeout:
                    self._notify_status(status_callback, "Время вышло!")
                    return None
                time.sleep(self.CHECK_INTERVAL)
        if self._click_position:
            if click_number == 1:
                self._stage_select_position = self._click_position
                self._notify_status(status_callback, "Первый клик запомнен!")
            else:
                self._stage_start_position = self._click_position
                self._notify_status(status_callback, "Второй клик запомнен!")
            return self._click_position

        return None

    def _notify_status(self, callback: Optional[Callable[[str], None]], message: str):
        """Helper to safely call status callback."""
        if callback:
            try:
                callback(message)
            except Exception:
                print(f"[Status] {message}")

    def _is_in_game_window(self, pos: Tuple[int, int]) -> bool:
        """Check if coordinates are within game window bounds."""
        if self.game_window is None:
            return False

        left = self.game_window.left
        top = self.game_window.top
        right = left + self.game_window.width
        bottom = top + self.game_window.height

        return left <= pos[0] <= right and top <= pos[1] <= bottom

    def get_stage_select_position(self) -> Optional[Tuple[int, int]]:
        return self._stage_select_position

    def get_stage_start_position(self) -> Optional[Tuple[int, int]]:
        return self._stage_start_position

    def reset(self) -> None:
        """Clear stored positions."""
        self._stage_select_position = None
        self._stage_start_position = None
