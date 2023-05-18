import time
from abc import ABC

import cv2

from debug.debug_cam_pipeline import DebugCamImageDisplay, DebugCamSupplier
from pipeline.pipeline import Pipeline


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
