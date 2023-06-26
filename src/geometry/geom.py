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

    def __init__(self, left_matrix, right_matrix):
        super().__init__()
        self.__left_matrix = left_matrix
        self.__right_matrix = right_matrix
        self.__left_inverse = np.linalg.pinv(left_matrix)
        self.__right_inverse = np.linalg.pinv(right_matrix)

    def homogenize(self, point):
        return np.append(point, 1)

    def find_closest_alpa(self, left_vec, right_vec, alpha_start) -> tuple[float, float]:

    def triangulate(self, left: Circle, right: Circle) -> Sphere:
        left_homogeneous_q = self.homogenize(left.position)
        right_homogeneous_q = self.homogenize(right.position)

        left_vect = left_homogeneous_q * self.__left_inverse
        right_vect = right_homogeneous_q * self.__right_inverse

        alpha_start = 0.5

        left_a, right_a = self.find_closest_alpa(left_vect, right_vect, alpha_start)

        left_p = np.array([0, 0, 0]) + left_a * left_vect
        right_p = np.array([120.0, 0, 0]) + right_a * right_vect

        pass

    def map(self, obj):
        left = obj[0]
        right = obj[1]

        return self.triangulate(left, right)
