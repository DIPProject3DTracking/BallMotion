from pipeline.pipeline import Pipeline
from capture.frame_supplier import FrameSupplier
from visualization.frame_viewer import FrameViewer

CAPTURE_DEVICE = 0


def main():
    pipe = Pipeline.builder() \
        .add(FrameSupplier(CAPTURE_DEVICE)) \
        .add(FrameViewer()) \
        .build()

    try:
        pipe.run()
    except KeyboardInterrupt:
        pipe.stop()


if __name__ == '__main__':
    main()
