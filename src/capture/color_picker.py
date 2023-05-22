import statistics

import cv2
import numpy as np

from pipeline.pipeline import Consumer


class ColorPicker:
    def __init__(self, radius=100):
        self.radius = radius

        self.half_width: int
        self.half_height: int
        self.mask = None

        self.color_median = []
        self.color_std = []

        # self.color_hsv = None
        self.color_bgr = (0, 255, 0)

    def update_mask(self):
        self.mask = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.mask = cv2.circle(
            img=self.mask,
            center=(self.half_width, self.half_height),
            radius=self.radius,
            color=(255, 255, 255),
            thickness=-1,
        )

    def run(self):
        median = None
        cap = cv2.VideoCapture(0)
        self.width, self.height = (
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        self.half_width, self.half_height = self.width // 2, self.height // 2
        self.update_mask()

        while True:
            ret_succ, frame = cap.read()
            if not ret_succ:
                break

            self.extract_color(frame)

            frame = self.draw_crosshair(frame)

            match chr(cv2.waitKey(1) & 0xFF):
                case "q":
                    break
                case "+":
                    self.radius += 10
                    self.update_mask()
                case "-":
                    self.radius = max(10, self.radius - 10)
                    self.update_mask()
                case "r":
                    median, std = self.print_color()

            if median is not None:
                cv2.putText(
                    frame,
                    median,
                    (50, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )
                cv2.putText(
                    frame,
                    std,
                    (50, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )
            cv2.imshow("frame", frame)

        self.print_color()
        cap.release()
        cv2.destroyAllWindows()

    def draw_crosshair(self, frame):
        frame = cv2.line(
            frame,
            (self.half_width, self.half_height - self.radius),
            (self.half_width, self.half_height + self.radius),
            self.color_bgr,
            5,
        )
        frame = cv2.line(
            frame,
            (self.half_width - self.radius, self.half_height),
            (self.half_width + self.radius, self.half_height),
            self.color_bgr,
            5,
        )
        frame = cv2.circle(
            frame,
            (self.half_width, self.half_height),
            self.radius,
            self.color_bgr,
            5,
        )
        return frame

    def extract_color(self, frame):
        # Convert to HSV and perform histogram equalization on the V channel
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame[:, :, 2] = cv2.equalizeHist(frame[:, :, 2])

        frame = cv2.bitwise_and(self.mask, frame)  # Apply mask

        non_black_pixels_mask = np.any(frame > [0, 0, 0], axis=-1)

        h_channel, s_channel, v_channel = frame[non_black_pixels_mask].T

        # compute median and standard deviation for each channel
        color_median = np.median([h_channel, s_channel, v_channel], axis=1)
        color_std = np.std([h_channel, s_channel, v_channel], axis=1)

        self.color_median.append(color_median)
        self.color_std.append(color_std)

    def print_color(self):
        color = np.mean(self.color_median, axis=0)
        color_bgr = cv2.cvtColor(
            color.astype(np.uint8).reshape(1, 1, 3), cv2.COLOR_HSV2BGR
        ).squeeze()
        median_str = f"Median (HSV): {color}; (BGR): {color_bgr})"
        std_str = f"Std: {np.mean(self.color_std, axis=0)}"
        self.color_bgr = tuple(int(c) for c in color_bgr.squeeze())
        print(median_str, std_str, sep="\n")

        self.color_median = []
        self.color_std = []

        return median_str, std_str


if __name__ == "__main__":
    color_picker = ColorPicker()
    color_picker.run()
