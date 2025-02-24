# import logging
from winterdrp.processors.base_processor import BaseImageProcessor
from winterdrp.processors.bias import BiasCalibrator
from winterdrp.processors.dark import DarkCalibrator
from winterdrp.processors.flat import FlatCalibrator, SkyFlatCalibrator
from winterdrp.processors.mask import MaskPixels
from winterdrp.processors.utils.image_saver import ImageSaver

#
# logger = logging.getLogger(__name__)
#
#
# def get_processor(processor_name, open_fits, *args, **kwargs):
#
#     try:
#         processor = BaseProcessor.subclasses[processor_name]
#     except KeyError:
#         err = f"Processor type '{processor_name}' not recognised. " \
#               f"The following processors are available: {BaseProcessor.subclasses.keys()}"
#         logger.error(err)
#         raise KeyError(err)
#
#     return processor(open_fits, *args, **kwargs)
