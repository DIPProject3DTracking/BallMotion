from typing import Any

from stereo.stereo_pipeline import StereoMapper
from pipeline.pipeline import Mapper


class ImageMergeMapper(Mapper):
    def __init__():
        super().__init__()

    def map(self, obj: Any) -> Any:
        left_image = obj[0]
        right_image = obj[1]

