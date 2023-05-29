import time
from dataclasses import dataclass
from typing import Any, Union

import cv2
import numpy as np

from detection.color_thresholding import ColorSegmenter


@dataclass
class Match:
    x_roi: int
    y_roi: int
    w: int
    h: int
    roi: np.ndarray
    x_center: int
    y_center: int
    radius: int
    color_image: Union[None, np.ndarray] = None

    def set_roi(self, frame, blur_ksize=5, blur_sigma=2, canny_low=100, canny_high=200):
        """
        Extracts the region of interest from the frame and applies a blur and Canny edge detection.
        """
        roi = cv2.cvtColor(
            frame[self.y_roi : self.y_roi + self.h, self.x_roi : self.x_roi + self.w],
            cv2.COLOR_BGR2GRAY,
        )
        roi = cv2.equalizeHist(roi)
        roi = cv2.GaussianBlur(roi, (blur_ksize, blur_ksize), blur_sigma)
        self.roi = cv2.Canny(roi, canny_low, canny_high)


class HoughCircleDetector:
    def __init__(self, display=False):
        self.display = display

    def apply_hough_transform(self, binary_image):
        contours, _ = cv2.findContours(
            binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)

        # Compute the bounding rectangle around the largest contour
        x_roi, y_roi, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))

        cropped_image = binary_image[y_roi : y_roi + h, x_roi : x_roi + w]

        circles = cv2.HoughCircles(
            cropped_image,
            cv2.HOUGH_GRADIENT,
            dp=6,
            minDist=500,
            param1=180,
            param2=100,
            minRadius=int(min(w, h) // 2 * (1 - 0.1)),
            maxRadius=int(max(w, h) // 2 + (1 + 0.1)),
        )

        if circles is None:
            return None

        # Extract the coordintes of the circle with the highest number of votes
        x, y, r = np.uint16(np.around(circles[0, 0]))

        match = Match(
            x_roi=x_roi,
            y_roi=y_roi,
            w=w,
            h=h,
            roi=None,
            x_center=x,
            y_center=y,
            radius=r,
            color_image=None,
        )

        if self.display:
            color_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
            # Bounding box
            cv2.rectangle(
                color_image, (x_roi, y_roi), (x_roi + w, y_roi + h), (255, 0, 0), 1
            )
            xy = (
                x + x_roi,
                y + y_roi,
            )
            # Outer circle
            cv2.circle(color_image, xy, r, (0, 255, 0), -1)
            # Center of the circle
            cv2.circle(color_image, xy, 2, (0, 0, 255), 3)
            match.color_image = color_image

        return match


if __name__ == "__main__":
    color_tracker = ColorSegmenter(base_color=[125, 187, 161], rel_tol=[0.6, 0.11, 0.8])
    hough = HoughCircleDetector(display=True)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while cv2.waitKey(1) & 0xFF != ord("q"):
        prev_time = time.time()
        ret_succ, frame = cap.read()

        if not ret_succ:
            print("Could not read frame! Exiting ...")
            break

        binary_image = color_tracker.apply_color_thresholding(frame)
        match = hough.apply_hough_transform(binary_image)
        if match is None or not isinstance(match, Match):
            continue
        match.set_roi(frame)
        circle_img = match.color_image

        fps = 1 / (time.time() - prev_time)
        cv2.putText(
            circle_img,
            f"FPS: {fps:.2f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        cv2.imshow("Processed Frame", circle_img)
        cv2.imshow("ROI", match.roi)

    cap.release()
    cv2.destroyAllWindows()
