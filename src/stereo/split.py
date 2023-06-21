from pipeline.pipeline import Mapper


class StereoSplitter(Mapper):

    def __init__(self):
        super().__init__()

    def map(self, obj):
        dimensions = obj.shape
        height = dimensions[0]
        width = dimensions[1]
        left_start_x, left_start_y = int(0), int(0)
        left_end_x, left_end_y = int(width / 2), height

        cropped_left = obj[left_start_y:left_end_y, left_start_x:left_end_x]

        right_start_x, right_start_y = int(width / 2), int(0)
        right_end_x, right_end_y = int(width), height

        cropped_right = obj[right_start_y:right_end_y, right_start_x:right_end_x]

        return cropped_left, cropped_right
