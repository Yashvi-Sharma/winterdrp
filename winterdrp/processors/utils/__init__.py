"""
Module for general utility processors such as I/O and interacting with metadata
"""
from winterdrp.processors.utils.header_annotate import HeaderAnnotator
from winterdrp.processors.utils.header_reader import HeaderReader
from winterdrp.processors.utils.image_loader import ImageLoader
from winterdrp.processors.utils.image_saver import ImageSaver
from winterdrp.processors.utils.image_selector import (
    ImageBatcher,
    ImageDebatcher,
    ImageSelector,
    select_from_images,
)
