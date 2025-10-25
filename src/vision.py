import cv2 as cv
import numpy as np


class Vision:
    def __init__(
        self, needle_img_path: str, offset=(0, 0), method=cv.TM_CCOEFF_NORMED
    ) -> None:
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_GRAYSCALE)

        if self.needle_img is None:
            raise ValueError(f"Failed to load image: {needle_img_path}")

        self.w, self.h = self.needle_img.shape[::-1]

        self.offset = offset
        self.method = method

    def find(
        self, haystack_img: np.ndarray, threshold=0.8
    ) -> list[tuple[int, int, int, int]]:
        result = cv.matchTemplate(
            cv.cvtColor(haystack_img, cv.COLOR_BGR2GRAY), self.needle_img, self.method
        )

        locations = np.where(result >= threshold)

        rectangles = []

        for x, y in zip(*locations[::-1]):
            rect = (x, y, x + self.w, y + self.h)

            rectangles.append(rect)
            rectangles.append(rect)

        rectangles, _ = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

        return rectangles

    def get_click_points(
        self,
        rectangles: list[tuple[int, int, int, int]],
    ) -> list[tuple[int, int]]:
        return [
            ((x1 + x2) // 2 + self.offset[0], (y1 + y2) // 2 + self.offset[1])
            for x1, y1, x2, y2 in rectangles
        ]

    @staticmethod
    def draw_rectangles(
        img: np.ndarray,
        rectangles: list[list[int, int, int, int]],
        color=(0, 255, 0),
        thickness=2,
    ):
        for x1, y1, x2, y2 in rectangles:
            cv.rectangle(img, (x1, y1), (x2, y2), color, thickness)
