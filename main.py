import time
from datetime import datetime, timezone

import mss
import numpy as np
import pydirectinput
from pynput import keyboard
from rich import print

from src.dungeon import NightmareDungeon, StandStillDungeon, StraightWalkDungeon
from src.miscs import CENTER_SCREEN, GAMEMODE_PROMPT_MONITOR, GAMEMODE_PROMPT_OFFSET
from src.vision import Vision

VISIONS = {
    "easy": Vision("screenshots/easy.png", offset=GAMEMODE_PROMPT_OFFSET),
    "medium": Vision("screenshots/medium.png", offset=GAMEMODE_PROMPT_OFFSET),
    "hard": Vision("screenshots/medium.png", offset=GAMEMODE_PROMPT_OFFSET),
    "leaf raid": Vision("screenshots/leaf raid.png", offset=GAMEMODE_PROMPT_OFFSET),
    "insane": Vision("screenshots/insane.png", offset=GAMEMODE_PROMPT_OFFSET),
    "crazy": Vision("screenshots/crazy.png", offset=GAMEMODE_PROMPT_OFFSET),
    "nightmare": Vision("screenshots/nightmare.png", offset=GAMEMODE_PROMPT_OFFSET),
    "yes": Vision("screenshots/yes.png", offset=GAMEMODE_PROMPT_OFFSET),
}


DUNGEONS = {
    "easy": StraightWalkDungeon,
    "medium": StraightWalkDungeon,
    "hard": StraightWalkDungeon,
    "leaf raid": StandStillDungeon,
    "insane": StraightWalkDungeon,
    "crazy": StraightWalkDungeon,
    "nightmare": NightmareDungeon,
}

running = True


def on_press(key):
    global running

    try:
        if key.char == "q":
            print("User requested exit ('q' pressed).")
            running = False
            return False
    except AttributeError:
        pass


class Runner:
    @staticmethod
    def get_difficulty():
        minute = datetime.now(timezone.utc).minute

        if minute < 10:
            return "easy"
        elif 10 <= minute < 20:
            return "medium"
        elif 20 <= minute < 25:
            return "hard"
        elif 25 <= minute < 30:
            return "leaf raid"
        elif 30 <= minute < 40:
            return "insane"
        elif 40 <= minute < 50:
            return "crazy"
        else:
            return "nightmare"

    @staticmethod
    def loop(allowed: list[str]):
        global running

        with mss.mss() as sct:
            while running:
                time.sleep(1)

                difficulty = Runner.get_difficulty()

                if difficulty not in allowed:
                    continue

                vision = VISIONS.get(difficulty)

                if vision is None:
                    continue

                screenshot = np.array(sct.grab(GAMEMODE_PROMPT_MONITOR))

                if len(vision.find(screenshot)) == 0:
                    continue

                print(f"{difficulty} prompt found, searching for 'yes' button.")
                rectangles = VISIONS["yes"].find(screenshot)

                if len(rectangles) == 0:
                    continue

                print("Yes button found, clicking...")
                x, y = vision.get_click_points(rectangles)[0]

                pydirectinput.moveTo(x, y, duration=1)
                pydirectinput.click()

                dungeon = DUNGEONS.get(difficulty)

                if dungeon:
                    time.sleep(1)
                    dungeon.start(sct)
                    pydirectinput.moveTo(CENTER_SCREEN[0], CENTER_SCREEN[1], duration=1)


if __name__ == "__main__":
    allowed = [
        "easy",
        "medium",
        "hard",
        "insane",
        "crazy",
    ]

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        Runner.loop(allowed)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected.")
    finally:
        runner = False
        listener.stop()
        print("Exited gracefully.")
