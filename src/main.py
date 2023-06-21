import time

from pipeline.pipeline import Pipeline
from stereo.stereo_pipeline import *
from capture.frame_supplier import FrameSupplier
from visualization.frame_viewer import FrameViewer
from stereo.split import StereoSplitter


def main():
    stereo_cam_sup = FrameSupplier(1)

    frame_splitter = StereoSplitter()

    left_image_view = FrameViewer()
    right_image_view = FrameViewer()
    stereo_frame_view = StereoConsumer(left_image_view, right_image_view)

    pipe1 = Pipeline.builder() \
        .add(stereo_cam_sup) \
        .add(frame_splitter) \
        .add(stereo_frame_view) \
        .build()

    try:
        pipe1.run()
        while True:
            print(pipe1.get_endpoint_sizes())
            time.sleep(2.0)
    except KeyboardInterrupt:
        pipe1.stop()


if __name__ == '__main__':
    main()
