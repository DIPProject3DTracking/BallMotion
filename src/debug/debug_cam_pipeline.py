import time

import cv2

from pipeline.pipeline import Consumer, Pipeline, Supplier


class DebugCamSupplier(Supplier):
    def __init__(self, capture_device):
        super().__init__()
        self.capture_device = capture_device

    def supply(self):
        rev, frame = self.capture_device.read()
        return frame


class DebugCamImageDisplay(Consumer):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def consume(self, image):
        cv2.imshow(self.name, image)
        cv2.waitKey(1)


def main():
    cam = cv2.VideoCapture(0)

    if not cam or not cam.isOpened():
        print("Cannot open camera")
        exit()
    pipe = (
        Pipeline.builder()
        .add(DebugCamSupplier(cam))
        .add(DebugCamImageDisplay("cam1"))
        .build()
    )
    pipe.run()
    while True:
        time.sleep(1)
        print(str(pipe))


if __name__ == "__main__":
    main()
