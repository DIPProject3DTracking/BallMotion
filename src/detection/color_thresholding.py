from dataclasses import dataclass
from typing import List, Optional

import cv2
import numpy as np


@dataclass
class Ellipse:
    def __init__(self, cnt: np.ndarray, eccentricity_treshold: float = 0.9) -> None:
        self.ellipse = cv2.fitEllipse(cnt)
        self.eccentricity: Optional[float] = None
        self.eccentricity_treshold = eccentricity_treshold

    @property
    def center(self) -> tuple:
        return self.ellipse[0]

    @property
    def major_axis(self) -> float:
        return self.ellipse[1][0]

    @property
    def minor_axis(self) -> float:
        return self.ellipse[1][1]

    @property
    def angle(self) -> float:
        return self.ellipse[2]

    def get_eccentricity(self) -> float:
        if self.eccentricity is None:
            self.eccentricity = np.sqrt(1 - (self.major_axis / self.minor_axis) ** 2)
        return self.eccentricity

    def draw(self, binary_image: np.ndarray) -> np.ndarray:
        if self.get_eccentricity() > self.eccentricity_treshold:
            return binary_image
        color_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
        cv2.ellipse(color_image, self.ellipse, (0, 255, 0), 2)
        cv2.circle(color_image, tuple(int(i) for i in self.center), 6, (0, 0, 255), -1)
        return color_image


class ColorSegmenter:
    def __init__(
        self,
        base_color: List[int],
        rel_tol: List[float],
        morph_ksize: int = 5,
        blur_ksize: int = 11,
        blur_sigma: int = 3,
    ) -> None:
        self.blur_ksize = blur_ksize
        self.blur_sigma = blur_sigma

        self.ellipses: List[Ellipse] = []

        rel_tol = np.array(rel_tol, dtype=np.float32)
        lab_color_range = np.array([255, 255, 255], dtype=np.uint8)
        self.lower_bound = np.clip(
            base_color - rel_tol * lab_color_range, a_min=0, a_max=lab_color_range
        ).astype(np.uint8)
        self.upper_bound = np.clip(
            base_color + rel_tol * lab_color_range, a_min=0, a_max=lab_color_range
        ).astype(np.uint8)

        # Structuring element for morphological operations
        self.structuring_element = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (morph_ksize, morph_ksize)
        )

    def apply_color_thresholding(self, frame: np.ndarray) -> np.ndarray:
        lab_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

        # Perform histogram equalization on the V channel to improve contrast
        lab_frame[:, :, 0] = cv2.equalizeHist(lab_frame[:, :, 0])

        lab_frame = cv2.GaussianBlur(
            lab_frame,
            ksize=(self.blur_ksize, self.blur_ksize),
            sigmaX=self.blur_sigma,
            sigmaY=self.blur_sigma,
        )

        binary_image = cv2.inRange(lab_frame, self.lower_bound, self.upper_bound)

        # Perform opening
        binary_image = cv2.morphologyEx(
            binary_image, cv2.MORPH_ERODE, self.structuring_element, iterations=4
        )

        return binary_image

    def detect_ellipse(self, binary_image: np.ndarray) -> Optional[Ellipse]:
        contours, _ = cv2.findContours(
            binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return None
        contour = max(contours, key=cv2.contourArea)
        if contour.shape[0] < 5:
            return None
        detected_ellipse = Ellipse(contour)
        if detected_ellipse.minor_axis == 0:
            return None
        return detected_ellipse

    def generate_bin_img(self) -> None:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            raise IOError("Cannot open webcam")

        while cv2.waitKey(1) & 0xFF != ord("q"):
            ret_succ, frame = cap.read()

            if not ret_succ:
                print("Could not read frame! Exiting ...")
                break

            binary_image = self.apply_color_thresholding(frame)
            ellipse = self.detect_ellipse(binary_image)
            if ellipse is not None:
                # print("Roundness:", ellipse.get_eccentricity())
                self.ellipses.append(ellipse)
                cv2.imshow("Processed Frame", ellipse.draw(binary_image))
            else:
                cv2.imshow("Processed Frame", binary_image)

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    color_tracker = ColorSegmenter(base_color=[87, 192, 167], rel_tol=[0.7, 0.11, 0.1])
    color_tracker.generate_bin_img()
