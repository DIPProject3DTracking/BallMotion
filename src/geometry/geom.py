from abc import ABC
from typing import Optional, Tuple

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
        super().__init__()
        self.position = position


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
        self.__left_inverse = np.linalg.pinv(left_matrix)
        self.__right_inverse = np.linalg.pinv(right_matrix)
        self.alpha = np.array([0.5, 0.5])
        self.tau_world = np.array([[0, 0, 0, 0], [120.0, 0, 0, 0]])

    def homogenize(self, point):
        return np.append(point, 1)

    def find_closest_alpha(self, left_vec, right_vec) -> Optional[np.ndarray]:
        def objective(alpha):
            # print(alpha, left_vec, right_vec, sep="\n")
            # print(alpha.shape, left_vec.shape, right_vec.shape, sep="\n")
            assert left_vec.shape == (
                4,
            ), f"left_vec.shape = {(alpha[0] * left_vec).shape}"
            assert right_vec.shape == (
                4,
            ), f"right_vec.shape: {(alpha[1] * right_vec).shape}"
            left_p = np.array([0, 0, 0, 0]) + alpha[0] * left_vec
            right_p = np.array([120.0, 0, 0, 0]) + alpha[1] * right_vec
            return np.linalg.norm(left_p - right_p)

        result = minimize(objective, self.alpha, method="L-BFGS-B")
        if result.success:
            return result.x

    def triangulate(self, left: Circle, right: Circle) -> Optional[Sphere]:
        left_homogeneous_q = self.homogenize(left.position).T
        right_homogeneous_q = self.homogenize(right.position).T
        print(left_homogeneous_q.shape, right_homogeneous_q.shape)
        print(self.__left_inverse.shape, self.__right_inverse.shape)

        left_vect = self.__left_inverse @ left_homogeneous_q
        right_vect = self.__right_inverse @ right_homogeneous_q

        alpha = self.find_closest_alpha(left_vect, right_vect)
        if alpha is not None:
            self.alpha = alpha

        world_point = self.tau_world + np.multiply(
            self.alpha.reshape(-1, 1), np.vstack((left_vect, right_vect))
        )

        position = np.mean(world_point, axis=0)[:3]
        return Sphere(position, left.radius)  # or right.radius depending on how you handle radius in 3D.

    def map(self, obj):
        left = obj[0]
        right = obj[1]

        return self.triangulate(left, right)


import unittest

from pipeline.pipeline import Mapper


class TestSpatialGeometryTransformer(unittest.TestCase):
    def setUp(self):
        left_matrix = np.arange(12).reshape((3, 4))
        right_matrix = np.arange(12).reshape((3, 4))
        self.transformer = SpatialGeometryTransformer(left_matrix, right_matrix)

    def test_homogenize(self):
        point = np.array([1, 2, 3])
        result = self.transformer.homogenize(point)
        np.testing.assert_array_equal(result, np.array([1, 2, 3, 1]))

    def test_find_closest_alpha(self):
        left_vec = np.array([1, 0, 0])
        right_vec = np.array([0, 1, 0])
        result = self.transformer.find_closest_alpha(left_vec, right_vec)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (2,))

    def test_triangulate(self):
        left_circle = Circle(np.array([1, 0]), 1)
        right_circle = Circle(np.array([0, 1]), 1)
        result = self.transformer.triangulate(left_circle, right_circle)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Sphere)
        np.testing.assert_array_almost_equal(result.position, np.array([0.5, 0.5]))
        self.assertEqual(result.radius, left_circle.radius)


if __name__ == "__main__":
    unittest.main()
