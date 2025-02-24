"""
Module for Catalog base class
"""
import logging
from abc import ABC
from pathlib import Path

import astropy.table

from winterdrp.data import Image
from winterdrp.paths import BASE_NAME_KEY
from winterdrp.utils.ldac_tools import save_table_as_ldac

logger = logging.getLogger(__name__)


class ABCatalog:
    """
    Abstract class for catalog objects
    """

    @property
    def abbreviation(self):
        """
        Abbreviation for naming catalog files
        """
        raise NotImplementedError()

    def __init__(
        self,
        search_radius_arcmin: float,
    ):
        self.search_radius_arcmin = search_radius_arcmin


class BaseCatalog(ABCatalog, ABC):
    """
    Base class for catalog objects
    """

    def __init__(
        self, *args, min_mag: float, max_mag: float, filter_name: str, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.min_mag = min_mag
        self.max_mag = max_mag
        self.filter_name = filter_name

    def get_catalog(self, ra_deg: float, dec_deg: float) -> astropy.table.Table:
        """
        Returns a catalog centered on ra/dec

        :param ra_deg: RA
        :param dec_deg: Dec
        :return: Catalog
        """
        raise NotImplementedError()

    def write_catalog(self, image: Image, output_dir: str | Path) -> Path:
        """
        Generates a custom catalog for an image

        :param image: Image
        :param output_dir: output directory for catalog
        :return: path of catalog
        """
        ra_deg = image["CRVAL1"]
        dec_deg = image["CRVAL2"]

        base_name = Path(image[BASE_NAME_KEY]).with_suffix(".ldac").name

        cat = self.get_catalog(ra_deg=ra_deg, dec_deg=dec_deg)

        output_path = self.get_output_path(output_dir, base_name)
        output_path.unlink(missing_ok=True)

        logger.info(f"Saving catalog to {output_path}")

        save_table_as_ldac(cat, output_path)

        return output_path

    def get_output_path(self, output_dir: Path, base_name: str | Path) -> Path:
        """
        Get save path for catalog

        :param output_dir: Output directory for catalog
        :param base_name: Base name for catalog
        :return: Full output path
        """
        cat_base_name = Path(base_name).with_suffix(f".{self.abbreviation}.cat")
        return output_dir.joinpath(cat_base_name)


class BaseXMatchCatalog(ABCatalog, ABC):
    """
    Base Catalog for crossmatching
    """

    @property
    def catalog_name(self):
        """
        Name of catalog
        """
        raise NotImplementedError

    @property
    def projection(self):
        raise NotImplementedError

    @property
    def column_names(self):
        """
        Name of columns
        """
        raise NotImplementedError

    @property
    def column_dtypes(self):
        """
        dtype of columns
        """
        raise NotImplementedError

    def __init__(self, *args, num_sources: int = 1, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_radius_arcsec = self.search_radius_arcmin * 60.0
        self.num_sources = num_sources

    def query(self, coords: dict) -> dict:
        """
        Query coords for result

        :param coords: ra/dec
        :return: crossmatch
        """
        raise NotImplementedError
