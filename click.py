import pydirectinput
import pygetwindow as gw
import time
import random

pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0.1


def click_mouse(x: int,
                y: int,
                delay_before: tuple = (0.3, 0.6),
                delay_move: tuple = (0.2, 0.4),
                delay_press: tuple = (0.08, 0.15),
                delay_after: tuple = (0.05, 0.15),
                random_offset: int = 10):
    """
    Mouse click with human-like randomization
    """
    x += random.randint(-random_offset, random_offset)
    y += random.randint(-random_offset, random_offset)

    windows = gw.getWindowsWithTitle('LimbusCompany')
    win = windows[0]
    win.activate()
    win.restore()
    time.sleep(0.3)

    time.sleep(random.uniform(delay_before[0], delay_before[1]))
    move_duration = random.uniform(delay_move[0], delay_move[1])
    pydirectinput.moveTo(x, y, duration=move_duration)
    pydirectinput.mouseDown(button='left')
    time.sleep(random.uniform(delay_press[0], delay_press[1]))
    pydirectinput.mouseUp(button='left')
    time.sleep(random.uniform(delay_after[0], delay_after[1]))
