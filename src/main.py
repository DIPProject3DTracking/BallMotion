import time

import numpy as np
import redis

from broadcast.redis_broadcast import RedisBroadcast
from capture.frame_supplier import FrameSupplier
from debug.debug_cam_pipeline import ResultPrinter
from detection.color_thresholding import ColorSegmenter
from geometry.geom import SpatialGeometryTransformer, StereoEllipseGeometryExtractor
from pipeline.pipeline import Pipeline
from stereo.split import StereoSplitter
from stereo.stereo_pipeline import *
from visualization.frame_viewer import FrameViewer


def main():
    stereo_cam_sup = FrameSupplier(0)

    frame_splitter = StereoSplitter()

    left_image_view = FrameViewer()
    right_image_view = FrameViewer()
    stereo_frame_view = StereoConsumer(left_image_view, right_image_view)

    # color_point = [87, 192, 167]
    # color_point = [202, 134, 192]
    color_point = [252, 157, 199]
    # tolerance = [0.7, 0.11, 0.1]
    tolerance = [0.925, 0.075, 0.075]

    left_segmenter = ColorSegmenter(base_color=color_point, rel_tol=tolerance)
    right_segmenter = ColorSegmenter(base_color=color_point, rel_tol=tolerance)
    stereo_segmenter = StereoMapper(left_segmenter, right_segmenter)

    geometry_extractor = StereoEllipseGeometryExtractor()

    # Projection matrices for the cameras
    # [fx, 0, cx, Tx]
    # [0, fy, cy, Ty]
    # [0,  0,  1,  0]
    # where Tx = -fx * B, B = baseline
    #       Ty = 0
    #       fx = focal length w.r.t. x
    #       fy = focal length w.r.t. y
    #       cx, cy = principal points; [cx] = [cy] = ??
    # TODO: Add cx and cy!!
    # fmt: off
    p_right_matrix = np.array([[2.8,   0, 0, -120.0],
                               [  0, 2.8, 0,      0],
                               [  0,   0, 1,      0]])
    p_left_matrix = np.array([[2.8,   0, 0, 0],
                              [  0, 2.8, 0, 0],
                              [  0,   0, 1, 0]])
    # fmt: on

    geometry_transformer = SpatialGeometryTransformer(p_left_matrix, p_right_matrix)

    client = redis.Redis(host="localhost", port=6379)

    pipe1 = (
        Pipeline.builder()
        .add(stereo_cam_sup)
        .add(frame_splitter)
        .add(stereo_segmenter)
        .add(geometry_extractor)
        .add(geometry_transformer)
        .add(RedisBroadcast(client, "Ball"))
        .build()
    )

    try:
        pipe1.run()
        while True:
            print(pipe1.get_endpoint_sizes())
            time.sleep(2.0)
    except KeyboardInterrupt:
        pipe1.stop()


if __name__ == "__main__":
    main()
