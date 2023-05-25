import time

import cv2
import numpy as np

from detection.color_thresholding import ColorSegmenter


def apply_hough_transform(binary_image):
    contours, _ = cv2.findContours(
        binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    print(contours)
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

    color_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    cv2.rectangle(color_image, (x_roi, y_roi), (x_roi + w, y_roi + h), (255, 0, 0), 1)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for x, y, r in circles[0, :]:
            xy = (
                x + x_roi,
                y + y_roi,
            )
            # outer circle
            cv2.circle(color_image, xy, r, (0, 255, 0), 2)
            # center of the circle
            cv2.circle(color_image, xy, 2, (0, 0, 255), 3)

    return color_image


if __name__ == "__main__":
    color_tracker = ColorSegmenter(base_color=[125, 187, 161], rel_tol=[0.6, 0.11, 0.8])

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while cv2.waitKey(1) & 0xFF != ord("q"):
        prev_time = time.time()
        ret_succ, frame = cap.read()

        if not ret_succ:
            print("Could not read frame! Exiting ...")
            break

        binary_image = color_tracker.adaptive_thresholding(frame)
        circle_img = apply_hough_transform(binary_image)

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

    cap.release()
    cv2.destroyWindow("Processed Frame")
