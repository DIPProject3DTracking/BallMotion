import cv2
import numpy as np

from detection.color_thresholding import ColorSegmenter


def apply_hough_transform(binary_image):
    # Apply the Hough Circle transform
    circles = cv2.HoughCircles(
        binary_image,
        cv2.HOUGH_GRADIENT,
        dp=5,  # image resolution / accumulator resolution
        minDist=500,  # min distance between the centers of detected circles
        param1=180,  # Upper threshold for the internal Canny edge detector; lower threshold = param1 / 2
        param2=200,  # Min number of votes in the accumulator array
        minRadius=30,
        maxRadius=600,
    )

    color_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for x, y, r in circles[0, :]:
            xy = (x, y)
            # outer circle
            cv2.circle(color_image, xy, r, (0, 255, 0), 2)
            # center of the circle
            cv2.circle(color_image, xy, 2, (0, 0, 255), 3)

    return color_image


if __name__ == "__main__":
    color_tracker = ColorSegmenter(base_color=[87, 106, 221], rel_tol=[0.03, 0.1, 0.5])

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while cv2.waitKey(1) & 0xFF != ord("q"):
        ret_succ, frame = cap.read()

        if not ret_succ:
            print("Could not read frame! Exiting ...")
            break

        binary_image = color_tracker.adaptive_thresholding(frame)
        circle_img = apply_hough_transform(binary_image)
        cv2.imshow("Processed Frame", circle_img)

    cap.release()
    cv2.destroyWindow("Processed Frame")
