"""
Script for testing the error handling in ..module::winterdrp.errors
"""
import logging

from winterdrp.data import Dataset, ImageBatch
from winterdrp.errors import ImageNotFoundError
from winterdrp.pipelines import get_pipeline
from winterdrp.testing import BaseTestCase

logger = logging.getLogger(__name__)

pipeline = get_pipeline(
    instrument="summer", selected_configurations=["test"], night="20220401"
)

expected_error = {
    "processor_name": "winterdrp.processors.utils.image_loader",
    "contents": [],
    "known_error_bool": True,
    "non_critical_bool": False,
}


class TestErrors(BaseTestCase):

    """Class for testing errors in ..module::winterdrp.errors"""

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def test_pipeline(self):
        self.logger.info("\n\n Testing summer pipeline \n\n")

        _, errorstack = pipeline.reduce_images(
            Dataset(ImageBatch()), catch_all_errors=True
        )

        errorstack.summarise_error_stack(verbose=True)

        self.assertEqual(len(errorstack.failed_images), 0)
        self.assertEqual(len(errorstack.noncritical_reports), 0)
        self.assertEqual(len(errorstack.reports), 1)

        err = errorstack.reports[0]

        self.assertTrue(isinstance(err.error, ImageNotFoundError))

        for key, exp in expected_error.items():
            self.assertEqual(exp, getattr(err, key))
