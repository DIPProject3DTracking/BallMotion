from typing import Any

import cv2

from pipeline.pipeline import Consumer

WINDOW_NAME = "View"


class FrameViewer(Consumer):
    def consume(self, obj: Any) -> None:
        cv2.imshow(WINDOW_NAME, obj)
        cv2.waitKey(1)

    def stop(self):
        cv2.destroyWindow(WINDOW_NAME)
