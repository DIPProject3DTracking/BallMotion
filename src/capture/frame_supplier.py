import threading
from typing import Tuple, Union, Any

import cv2
import numpy as np

from pipeline.pipeline import Supplier


class StereoFrameSupplier(Supplier):
    def __init__(self, left_device, right_device, resolution: Union[None, Tuple[int, int]] = None):
        super().__init__()

        self.__is_setup = False

        self.__lock = threading.Lock()

        self.__v_ids = (left_device, right_device)
        self.__resolution = resolution
        self.captures = [None, None]

    def setup(self):
        self.captures[0] = (
            cv2.VideoCapture(self.__v_ids[0])
            if isinstance(self.__v_ids[0], int)
            else self.__v_ids[0]
        )

        self.captures[1] = (
            cv2.VideoCapture(self.__v_ids[1])
            if isinstance(self.__v_ids[1], int)
            else self.__v_ids[1]
        )

        print("e")
        if self.__resolution is not None:
            width, height = self.__resolution
            self.captures[0].set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.captures[0].set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.captures[1].set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.captures[1].set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        print("e2")
        # if not self.captures[0] or not self.captures[0].isOpened():
        #    raise IOError(f"Cannot open capture device {self.captures[0]}!")
        print("e3")
        # if not self.captures[1] or not self.captures[1].isOpened():
        #    raise IOError(f"Cannot open capture device {self.captures[1]}!")

        print("> Stereo cam setup done")

    def supply(self) -> Any:
        global ret_0, frame_0, ret_1, frame_1
        if self.__is_setup is False:
            self.setup()
            self.__is_setup = True

        with self.__lock:
            ret_0, frame_0 = self.captures[0].read()
        with self.__lock:
            ret_1, frame_1 = self.captures[1].read()

        with self.__lock:
            f1 = frame_0
            f2 = frame_1
        return f1, f2

    def stop(self):
        self.captures[0].release()
        self.captures[1].release()


class FrameSupplier(Supplier):
    def __init__(self, capture_device, resolution: Union[None, Tuple[int, int]] = None):
        super().__init__()

        self.capture_device = (
            cv2.VideoCapture(capture_device)
            if isinstance(capture_device, int)
            else capture_device
        )

        if resolution is not None:
            width, height = resolution
            self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if not self.capture_device or not self.capture_device.isOpened():
            raise IOError(f"Cannot open capture device {self.capture_device}!")

    def supply(self) -> np.ndarray:
        ret, frame = self.capture_device.read()
        return frame if ret else None

    def stop(self):
        self.capture_device.release()
