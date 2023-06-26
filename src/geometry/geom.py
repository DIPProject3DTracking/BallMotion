from abc import ABC

import numpy as np
from scipy.optimize import minimize

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
        self.alpha = np.array([0.5, 0.5])
        self.tau_world = np.array([[0, 0, 0], [120.0, 0, 0]])

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

    def find_closest_alpha(self, left_vec, right_vec) -> tuple[float, float]:
        def objective(alpha):
            left_p = np.array([0, 0, 0]) + alpha[0] * left_vec
            right_p = np.array([120.0, 0, 0]) + alpha[1] * right_vec
            return np.linalg.norm(left_p - right_p)

        result = minimize(objective, self.alpha, method="nelder-mead")
        return result.x

    def triangulate(self, left: Circle, right: Circle) -> Sphere:
        left_homogeneous_q = self.homogenize(left.position)
        right_homogeneous_q = self.homogenize(right.position)

        left_vect = np.dot(self.__left_inverse, left_homogeneous_q)
        right_vect = np.dot(self.__right_inverse, right_homogeneous_q)

        self.alpha = self.find_closest_alpha(left_vect, right_vect)

        world_point = self.tau_world + self.alpha * np.vstack((left_vect, right_vect))

        position = sum(world_point[:2]) / world_point[2] / 2
        return Sphere(
            position, left.radius
        )  # or right.radius depending on how you handle radius in 3D.

    def map(self, obj):
        left = obj[0]
        right = obj[1]

        return self.triangulate(left, right)
