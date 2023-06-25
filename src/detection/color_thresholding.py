from typing import List, Optional, Union, Tuple

import cv2
import numpy as np
from numpy import ndarray

from pipeline.pipeline import Mapper


class Ellipse:
    def __init__(self, cnt: np.ndarray, eccentricity_treshold: float = 0.9) -> None:
        self.ellipse = cv2.fitEllipse(cnt)
        self.cnt_area = cv2.contourArea(cnt)
        self.radius: Optional[float] = None
        self.circ_area: Optional[float] = None
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

    def get_radius(self) -> float:
        if self.radius is None:
            self.radius = (self.major_axis + self.minor_axis) / 4
        return self.radius

    def get_circ_area(self) -> float:
        if self.circ_area is None:
            self.circ_area = np.pi * (self.get_radius()) ** 2
        return self.circ_area

    def get_rel_area_error(self) -> float:
        return (self.cnt_area - self.circ_area) / self.cnt_area

    def get_eccentricity(self) -> float:
        if self.eccentricity is None:
            self.eccentricity = np.sqrt(1 - (self.major_axis / self.minor_axis) ** 2)
        return self.eccentricity

    def draw(self, binary_image: np.ndarray) -> np.ndarray:
        print("Pre-Draw")
        if self.get_eccentricity() > self.eccentricity_treshold:
            print("Simple circle")
            return binary_image
        print("Drawing color")
        color_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
        print("Drawing ellipse")
        cv2.ellipse(color_image, self.ellipse, (0, 255, 0), 2)
        print("Drawing corcle")
        cv2.circle(color_image, tuple(int(i) for i in self.center), 6, (0, 0, 255), -1)

        text = (
                f"Radius: {self.get_radius():.2f}, Eccentricity: {self.get_eccentricity():.2f}, "
                + f"Cnt Area: {self.cnt_area:.2f}, Circ Area: {self.get_circ_area():.2f}, Rel Error: {self.get_rel_area_error():.3%}"
        )
        print("Adding text")
        cv2.putText(
            color_image,
            text,
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        return color_image


class ColorSegmenter(Mapper):
    def __init__(
            self,
            base_color: List[int],
            rel_tol: List[float],
            morph_ksize: int = 5,
            blur_ksize: int = 11,
            blur_sigma: int = 3,
    ) -> None:
        super(ColorSegmenter, self).__init__()
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

    def map(self, frame: np.ndarray) -> tuple[ndarray, np.ndarray, Optional[Ellipse]]:
        binary_image = self.apply_color_thresholding(frame)
        ellipse = self.detect_ellipse(binary_image)
        if ellipse is not None:
            circle_img = ellipse.draw(frame)
        else:
            circle_img = frame
        return frame, circle_img, ellipse

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

        # binary_image = cv2.medianBlur(binary_image, 5)
        # Perform opening
        binary_image = cv2.morphologyEx(
            binary_image, cv2.MORPH_OPEN, self.structuring_element, iterations=6
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
