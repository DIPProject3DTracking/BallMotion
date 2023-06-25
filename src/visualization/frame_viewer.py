from typing import Any

import cv2

from pipeline.pipeline import Consumer

WINDOW_NAME = "View"


class FrameViewer(Consumer):
    __window_index = 0

    def __init__(self):
        super().__init__()
        self.__window_name = WINDOW_NAME + "_" + str(FrameViewer.__window_index)
        FrameViewer.__window_index += 1

    def consume(self, obj: Any) -> None:
        if type(obj) is tuple:
            cv2.imshow(self.__window_name, obj[1])
            cv2.waitKey(1)
        else:
            cv2.imshow(self.__window_name, obj)
            cv2.waitKey(1)

    def stop(self):
        cv2.destroyWindow(WINDOW_NAME)
