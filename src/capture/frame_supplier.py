from typing import Tuple, Union

import cv2
import numpy as np

from pipeline.pipeline import Supplier


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
