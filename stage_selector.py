import time
from typing import Optional, Tuple, Callable, List
from pynput import mouse


class StageSelector:
    """Handles mouse click detection for stage selection in game window."""

    DEFAULT_TIMEOUT: int = 1800
    CHECK_INTERVAL: float = 0.1
    NOTIFY_INTERVAL: int = 60

    def __init__(self, game_window):
        self.game_window = game_window
        self._stage_positions: List[Tuple[int, int]] = []
        self._click_received = None
        self._click_position = None

    def wait_for_user_click(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        click_number: int = 1,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[Tuple[int, int]]:
        """
        Wait for user to click inside game window.
        :param timeout: Timeout in seconds
        :param click_number: Number of current click (1, 2, or 3)
        :param status_callback: Function to call for status updates
        :return: Click coordinates (x, y) or None if timeout/error
        """
        self._click_position: Optional[Tuple[int, int]] = None
        self._click_received = False

        if status_callback:
            status_callback(f"Ожидание клика #{click_number}...\nКликните на кнопку")

        def on_click(x, y, button, pressed):
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
                    if status_callback:
                        status_callback(f"Прошло {minutes} мин... ожидание клика")
                if elapsed >= timeout:
                    if status_callback:
                        status_callback("Время вышло!")
                    return None
                time.sleep(self.CHECK_INTERVAL)

        if self._click_position:
            self._stage_positions.append(self._click_position)
            if status_callback:
                status_callback(f"Клик #{click_number} запомнен!")
            return self._click_position

        return None

    def _notify_status(self, callback: Optional[Callable[[str], None]], message: str):
        if callback:
            try:
                callback(message)
            except Exception:
                print(f"[Status] {message}")

    def _is_in_game_window(self, pos: Tuple[int, int]) -> bool:
        if self.game_window is None:
            return False

        left = self.game_window.left
        top = self.game_window.top
        right = left + self.game_window.width
        bottom = top + self.game_window.height

        return left <= pos[0] <= right and top <= pos[1] <= bottom

    def set_stage_positions(self, positions: List[Tuple[int, int]]):
        self._stage_positions = positions

    def get_stage_positions(self) -> List[Tuple[int, int]]:
        return self._stage_positions.copy() if self._stage_positions else []

    def get_stage_select_position(self) -> Optional[Tuple[int, int]]:
        return self._stage_positions[0] if len(self._stage_positions) > 0 else None

    def get_stage_start_position(self) -> Optional[Tuple[int, int]]:
        return self._stage_positions[1] if len(self._stage_positions) > 1 else None

    def reset(self) -> None:
        self._stage_positions = []
