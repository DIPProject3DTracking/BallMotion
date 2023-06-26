from abc import ABC
import numpy as np
from pipeline.pipeline import Mapper


class Geom2D(ABC):

    def __init__(self, position: np.ndarray):
        self.position = position


class Circle(Geom2D):

    def __init__(self, position: np.ndarray, radius: float):
        super().__init__(position)
        self.radius = radius


class Geom3D(ABC):

    def __init__(self, position: np.ndarray):
        super().__init__(position)


class Sphere(Geom3D):

    def __init__(self, position: np.ndarray, radius: float):
        super().__init__(position)
        self.radius = radius


class StereoEllipseGeometryExtractor(Mapper):

    def __init__(self):
        super().__init__()

    def map(self, obj):
        left = obj[0]
        right = obj[1]

        ellipse_left = left[-1]
        radius_left = ellipse_left.get_radius()
        center_left = ellipse_left.center

        ellipse_right = right[-1]
        radius_right = ellipse_right.get_radius()
        center_right = ellipse_right.center

        return Circle(center_left, radius_left), Circle(center_right, radius_right)


class SpatialGeometryTransformer(Mapper):

    def __init__(self):
        super().__init__()

    def triangulate(self, cam_matrix: np.ndarray, left: Circle, right: Circle) -> Sphere:
        pass

    def map(self, obj):
        left = obj[0]
        right = obj[1]

        return self.triangulate(left, right)
