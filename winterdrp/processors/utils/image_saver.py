"""
Module for saving images
"""
from pathlib import Path

from winterdrp.data import ImageBatch
from winterdrp.paths import (
    BASE_NAME_KEY,
    LATEST_SAVE_KEY,
    LATEST_WEIGHT_SAVE_KEY,
    base_output_dir,
    get_output_path,
)
from winterdrp.processors.base_processor import BaseImageProcessor


class ImageSaver(BaseImageProcessor):
    """
    Processor to save images
    """

    base_key = "save"

    def __init__(
        self,
        output_dir_name: str,
        write_mask: bool = True,
        output_dir: str | Path = base_output_dir,
    ):
        super().__init__()
        self.output_dir_name = output_dir_name
        self.write_mask = write_mask
        self.output_dir = Path(output_dir)

    def __str__(self):
        return f"Processor to save images to the '{self.output_dir_name}' subdirectory"

    def _apply_to_images(
        self,
        batch: ImageBatch,
    ) -> ImageBatch:
        for image in batch:
            path = get_output_path(
                image[BASE_NAME_KEY],
                dir_root=self.output_dir_name,
                sub_dir=self.night_sub_dir,
                output_dir=self.output_dir,
            )

            if not path.parent.exists():
                path.parent.mkdir(parents=True)

            image[LATEST_SAVE_KEY] = str(path)
            if self.write_mask:
                mask_path = self.save_weight_image(image, img_path=path)
                image[LATEST_WEIGHT_SAVE_KEY] = str(mask_path)
            self.save_fits(image, path)

        return batch
