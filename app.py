import sys
import time
import click
import random
import threading
import pygetwindow as gw
import cv2

from config_dialog import FarmConfigDialog
from stage_selector import StageSelector
from screen_capture import ScreenCapture
from template_finder import TemplateFinder
from gear_finder import GearFinder


class GameFarmAutomation:
    """Automated luxcavation farming bot for Limbus Company"""

    def __init__(self, confidence: float = 0.7):
        windows = gw.getWindowsWithTitle('LimbusCompany')
        self.game_window = windows[0] if windows else None

        if self.game_window is None:
            return

        self.screen_capture = ScreenCapture(self.game_window)
        self.template_finder = TemplateFinder(self.screen_capture, confidence)

        self.win_rate_template = cv2.imread('battle-images/win_rate.jpg', cv2.IMREAD_COLOR)
        self.gear_template = cv2.imread('battle-images/Gear.png', cv2.IMREAD_COLOR)
        self.confirm_template = cv2.imread('battle-images/confirm.jpg', cv2.IMREAD_COLOR)
        self.level_up_template = cv2.imread('battle-images/lvl.jpg', cv2.IMREAD_COLOR)

        self.gear_finder = GearFinder(
            self.screen_capture,
            self.template_finder,
            self.gear_template
        )

        self.stage_selector = StageSelector(self.game_window)
        self._stop_flag = False

    def request_stop(self):
        self._stop_flag = True

    def is_stopped(self):
        return self._stop_flag

    def find_win_rate(self):
        return self.template_finder.find_in_region(
            self.win_rate_template,
            confidence=0.43,
            x_percent=(50, 100),
            y_percent=(50, 100)
        )

    def check_win_rate_and_click_gear(self):
        win_rate_pos = self.find_win_rate()

        if win_rate_pos:
            click.click_mouse(win_rate_pos[0], win_rate_pos[1])
            time.sleep(2.0)

            gear_pos = self.gear_finder.find_near_win_rate(win_rate_pos)
            if gear_pos:
                click.click_mouse(gear_pos[0], gear_pos[1])
                return True
        return False

    def click_on_stage_positions(self, random_offset: int = 5):
        positions = self.stage_selector.get_stage_positions()

        if self.game_window:
            self.game_window.activate()
            self.game_window.restore()
            time.sleep(0.3)

        for i, (x, y) in enumerate(positions):
            click_x = x + random.randint(-random_offset, random_offset)
            click_y = y + random.randint(-random_offset, random_offset)
            click.click_mouse(click_x, click_y)
            if i < len(positions) - 1:
                time.sleep(1)

        time.sleep(2)
        return True

    def handle_post_battle_screen(self):
        level_up_pos = self.template_finder.find_on_screen(self.level_up_template)
        if level_up_pos:
            click.click_mouse(level_up_pos[0], level_up_pos[1])
            time.sleep(1.5)

        confirm_pos = self.template_finder.find_on_screen(self.confirm_template, confidence=0.8)
        if confirm_pos:
            click.click_mouse(confirm_pos[0], confirm_pos[1])
            time.sleep(1.5)
            return True

        return False

    def _farm_loop_thread(self, runs, status_window):
        try:
            for run in range(1, runs + 1):
                if self.is_stopped():
                    break

                if status_window:
                    status_window.update_progress(run, runs)

                if run > 1:
                    if not self.click_on_stage_positions():
                        break
                    time.sleep(3)

                battle_active = True
                while battle_active and not self.is_stopped():
                    completed = self.handle_post_battle_screen()
                    if completed:
                        battle_active = False
                        break

                    found = self.check_win_rate_and_click_gear()
                    if not found:
                        time.sleep(1)

                if run < runs:
                    time.sleep(2)

            if status_window:
                status_window.set_finished()

        except Exception:
            pass
        finally:
            pass

    def start_farm(self, runs, status_window):
        self._stop_flag = False
        thread = threading.Thread(
            target=self._farm_loop_thread,
            args=(runs, status_window),
            daemon=True
        )
        thread.start()
        return thread


def main():
    windows = gw.getWindowsWithTitle('LimbusCompany')
    game_window = windows[0] if windows else None

    config_dialog = FarmConfigDialog(game_window=game_window)
    config = config_dialog.get_farm_config()

    if config is None:
        return

    bot = GameFarmAutomation(confidence=0.8)
    if bot.game_window is None:
        return

    if "stage_positions" in config and config["stage_positions"]:
        bot.stage_selector.set_stage_positions(config["stage_positions"])
    else:
        return

    def on_finish():
        config_dialog.root.quit()
        config_dialog.root.destroy()
        config_dialog.root.after(100, lambda: sys.exit(0))

    status_window = config_dialog.show_status_window(
        config["runs"],
        on_stop_callback=bot.request_stop,
        on_finish_callback=on_finish
    )

    bot.start_farm(runs=config["runs"], status_window=status_window)
    config_dialog.root.mainloop()
    sys.exit(0)


if __name__ == "__main__":
    main()
