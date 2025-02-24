"""
Module to run
:func:`~winterdrp.processors.astromatic.sextractor.sourceextractor.run_sextractor_single
 as a processor.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional

from winterdrp.data import ImageBatch
from winterdrp.paths import (
    BASE_NAME_KEY,
    LATEST_WEIGHT_SAVE_KEY,
    get_output_dir,
    get_temp_path,
)
from winterdrp.processors.astromatic.sextractor.sourceextractor import (
    default_saturation,
    parse_checkimage,
    run_sextractor_single,
)
from winterdrp.processors.base_processor import BaseImageProcessor
from winterdrp.processors.candidates.utils.regions_writer import write_regions_file
from winterdrp.utils.ldac_tools import get_table_from_ldac

logger = logging.getLogger(__name__)

SEXTRACTOR_HEADER_KEY = "SRCCAT"

sextractor_checkimg_map = {
    "BACKGROUND": "BKGPT",
    "BACKGROUND_RMS": "BKGRMS",
    "MINIBACKGROUND": "MINIBKG",
    "MINIBACK_RMS": "MINIBGRM",
}


class Sextractor(BaseImageProcessor):
    """
    Processor to run sextractor on images
    """

    base_key = "sextractor"
    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        output_sub_dir: str,
        config_path: str,
        parameter_path: str,
        filter_path: str,
        starnnw_path: str,
        saturation: float = default_saturation,
        verbose_type: str = "QUIET",
        checkimage_name: Optional[str | list] = None,
        checkimage_type: Optional[str | list] = None,
        gain: Optional[float] = None,
        dual: bool = False,
        cache: bool = False,
        mag_zp: Optional[float] = None,
        write_regions_bool: bool = False,
    ):
        # pylint: disable=too-many-arguments
        super().__init__()
        self.output_sub_dir = output_sub_dir
        self.config = config_path

        self.parameters_name = parameter_path
        self.filter_name = filter_path
        self.starnnw_name = starnnw_path
        self.saturation = saturation
        self.verbose_type = verbose_type
        self.checkimage_name = checkimage_name
        self.checkimage_type = checkimage_type
        self.gain = gain
        self.dual = dual
        self.cache = cache
        self.mag_zp = mag_zp
        self.write_regions = write_regions_bool

    def __str__(self) -> str:
        return (
            f"Processor to apply sextractor to images, "
            f"and save detected sources to the '{self.output_sub_dir}' directory."
        )

    def get_sextractor_output_dir(self) -> str:
        """
        Get the directory to output

        :return: output directory
        """
        return get_output_dir(self.output_sub_dir, self.night_sub_dir)

    def _apply_to_images(self, batch: ImageBatch) -> ImageBatch:
        sextractor_out_dir = self.get_sextractor_output_dir()

        try:
            os.makedirs(sextractor_out_dir)
        except OSError:
            pass

        for image in batch:
            if self.gain is None and "GAIN" in image.keys():
                self.gain = image["GAIN"]

            temp_path = get_temp_path(sextractor_out_dir, image[BASE_NAME_KEY])

            if not os.path.exists(temp_path):
                self.save_fits(image, temp_path)

            temp_files = [temp_path]

            mask_path = None

            if LATEST_WEIGHT_SAVE_KEY in image.keys():
                image_mask_path = os.path.join(
                    sextractor_out_dir, image[LATEST_WEIGHT_SAVE_KEY]
                )
                temp_mask_path = get_temp_path(
                    sextractor_out_dir, image[LATEST_WEIGHT_SAVE_KEY]
                )
                if os.path.exists(image_mask_path):
                    shutil.copyfile(image_mask_path, temp_mask_path)
                    mask_path = temp_mask_path
                    temp_files.append(Path(mask_path))
                else:
                    mask_path = None

            if mask_path is None:
                mask_path = self.save_weight_image(image, temp_path)
                temp_files.append(Path(mask_path))

            output_cat = os.path.join(
                sextractor_out_dir, image[BASE_NAME_KEY].replace(".fits", ".cat")
            )

            _, self.checkimage_name = parse_checkimage(
                checkimage_name=self.checkimage_name,
                checkimage_type=self.checkimage_type,
                image=os.path.join(sextractor_out_dir, image[BASE_NAME_KEY]),
            )

            output_cat, checkimage_name = run_sextractor_single(
                img=temp_path,
                config=self.config,
                output_dir=sextractor_out_dir,
                parameters_name=self.parameters_name,
                filter_name=self.filter_name,
                starnnw_name=self.starnnw_name,
                saturation=self.saturation,
                weight_image=mask_path,
                verbose_type=self.verbose_type,
                checkimage_name=self.checkimage_name,
                checkimage_type=self.checkimage_type,
                gain=self.gain,
                catalog_name=output_cat,
            )

            logger.debug(f"Cache save is {self.cache}")
            if not self.cache:
                for temp_file in temp_files:
                    os.remove(temp_file)
                    logger.info(f"Deleted temporary file {temp_file}")

            if self.write_regions:
                output_catalog = get_table_from_ldac(output_cat)

                x_coords = output_catalog["X_IMAGE"]
                y_coords = output_catalog["Y_IMAGE"]

                regions_path = output_cat + ".reg"

                write_regions_file(
                    regions_path=regions_path,
                    x_coords=x_coords,
                    y_coords=y_coords,
                    system="image",
                    region_radius=5,
                )

            image[SEXTRACTOR_HEADER_KEY] = os.path.join(sextractor_out_dir, output_cat)

            if len(checkimage_name) > 0:
                if isinstance(self.checkimage_type, str):
                    self.checkimage_type = [self.checkimage_type]
                for i, checkimg_type in enumerate(self.checkimage_type):
                    image[sextractor_checkimg_map[checkimg_type]] = checkimage_name[i]

        return batch
