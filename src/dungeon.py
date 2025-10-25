import time
from abc import ABC, abstractmethod

import numpy as np
import pydirectinput
import pytesseract
from mss.base import MSSBase
from PIL import Image
from rich import print

from .miscs import (
    CENTER_SCREEN,
    DUNGEON_NOT_CHANGED_SECONDS,
    DUNGEON_RESET_AT,
    DUNGEON_ROOM_MONITOR,
    MAX_ERRORS,
    RE_ENTER_MONITOR,
    RE_ENTER_OFFSET,
)
from .vision import Vision

RE_ENTER_VISION = Vision("screenshots/re-enter.png", offset=RE_ENTER_OFFSET)


class Dungeon(ABC):
    @staticmethod
    @abstractmethod
    def start(sct: MSSBase):
        pass

    @staticmethod
    def get_room(sct: MSSBase) -> int:
        pass

    @staticmethod
    def go_back():
        pydirectinput.keyDown("s")
        time.sleep(3)
        pydirectinput.keyUp("s")

    @staticmethod
    def re_enter(sct: MSSBase, room: int):
        print("Searching for re-enter button")

        screenshot = np.array(sct.grab(RE_ENTER_MONITOR))
        rectangles = RE_ENTER_VISION.find(screenshot)

        if len(rectangles) > 0:
            print("Re-enter button found, clicking...")
            x, y = RE_ENTER_VISION.get_click_points(rectangles)[0]

            pydirectinput.moveTo(x, y, duration=1)
            pydirectinput.click()
            pydirectinput.moveTo(CENTER_SCREEN[0], CENTER_SCREEN[1], duration=1)

            pydirectinput.keyDown("w")
            time.sleep(room * 2)
            pydirectinput.keyUp("w")


class StraightWalkDungeon(Dungeon):
    def start(sct: MSSBase):
        print("Dungeon has started")

        error_count = 0
        go_back_count = 0
        last_room = None
        last_change_time = time.time()

        pydirectinput.keyDown("w")

        while True:
            try:
                room = StraightWalkDungeon.get_room(sct)

                if room != last_room:
                    last_room = room
                    last_change_time = time.time()
                elif time.time() - last_change_time > DUNGEON_NOT_CHANGED_SECONDS:
                    go_back_count += 1
                    last_change_time = time.time()

                    pydirectinput.keyUp("w")

                    if go_back_count > DUNGEON_RESET_AT:
                        print(
                            f"Go back called {DUNGEON_RESET_AT} times, re-entering dungeon"
                        )
                        StraightWalkDungeon.re_enter(sct, room)
                        go_back_count = 0
                    else:
                        print(
                            f"Room has not changed for {DUNGEON_NOT_CHANGED_SECONDS} seconds, going back"
                        )
                        StraightWalkDungeon.go_back()

                    pydirectinput.keyDown("w")

                if room == 50:
                    print("Dungeon cleared")
                    break
            except ValueError:
                print(f"Could not find room number, attempt {error_count}")

                error_count += 1

                if error_count > MAX_ERRORS:
                    print("Maximum errors reached, exiting loop")
                    break

                time.sleep(5)

            time.sleep(1)

        pydirectinput.keyUp("w")

    @staticmethod
    def get_room(sct: MSSBase) -> int:
        screenshot = sct.grab(DUNGEON_ROOM_MONITOR)

        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img = img.convert("L")

        return int(
            pytesseract.image_to_string(img).removeprefix("Room Cleared: ").strip()
        )


class StandStillDungeon(Dungeon):
    def start(sct: MSSBase):
        pass


class NightmareDungeon(Dungeon):
    def start(sct: MSSBase):
        pass
