from abc import ABC
from typing import Optional, Tuple

import cv2
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

    def depixelize(self, pixel_size: float):
        return Circle(self.position * pixel_size, self.radius * pixel_size)


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

        cv2.imshow("left", left[1])
        cv2.waitKey(1)
        cv2.imshow("right", right[1])
        cv2.waitKey(1)

        ellipse_left = left[-1]
        center_left = None
        radius_left = None
        if ellipse_left is not None:
            radius_left = ellipse_left.get_radius()
            center_left = ellipse_left.center

        ellipse_right = right[-1]
        center_right = None
        radius_right = None
        if ellipse_right is not None:
            radius_right = ellipse_right.get_radius()
            center_right = ellipse_right.center

        circle_left = (
            Circle(center_left, radius_left) if ellipse_left is not None else None
        )
        circle_right = (
            Circle(center_right, radius_right) if ellipse_right is not None else None
        )

        return circle_left, circle_right


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
        """Find both alpha values that minimize the distance between the two rays
        There is porbably a closed form solution to this..."""

        def objective(alpha):
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
        # use the same v coordinate for both points
        mean_v = (left.position[1] + right.position[1]) / 2

        left.position[1] = mean_v
        right.position[1] = mean_v

        mean_radius = (
                              left.radius + right.radius
                      ) / 2  # the radius should be scaled based on the distance the distance towards the camera

        print("B")
        left_homogeneous_q = self.homogenize(left.position).T
        right_homogeneous_q = self.homogenize(right.position).T

        print("C")
        # together with variable alphas these describe ray equations
        left_vect = self.__left_inverse @ left_homogeneous_q
        right_vect = self.__right_inverse @ right_homogeneous_q

        print("D")
        # find the point that is closest to the intersection of the two rays
        alpha = self.find_closest_alpha(left_vect, right_vect)
        if alpha is not None:
            self.alpha = alpha

        print("E")
        # calculate the world points, use the mean and de-homogenize
        world_point_h = self.tau_world + np.multiply(
            self.alpha.reshape(-1, 1), np.vstack((left_vect, right_vect))
        )
        world_point = np.mean(world_point_h[:, :3] / world_point_h[:, 3], axis=0)

        print("F")
        return Sphere(
            world_point, mean_radius
        )  # or right.radius depending on how you handle radius in 3D.

    def map(self, obj):
        left = obj[0]
        right = obj[1]

        sphere = (
            self.triangulate(left, right)
            if left is not None and right is not None
            else None
        )
        return (
            {
                "x": float(sphere.position[0]),
                "y": float(sphere.position[1]),
                "z": float(sphere.position[2]),
            }
            if sphere is not None
            else None
        )
