"""
Script containing the various
:class:`~winterdrp.processors.base_processor.BaseProcessor`
lists which are used to build configurations for the
:class:`~winterdrp.pipelines.summer.summer_pipeline.SummerPipeline`.
"""
from winterdrp.downloader.get_test_data import get_test_data_dir
from winterdrp.paths import BASE_NAME_KEY, GAIN_KEY, core_fields
from winterdrp.pipelines.summer.config import (  # summer_weight_path,
    DB_NAME,
    PIPELINE_NAME,
    SUMMER_PIXEL_SCALE,
    get_summer_schema_path,
    psfex_config_path,
    scamp_path,
    sextractor_astrometry_config,
    sextractor_candidates_config,
    sextractor_photometry_config,
    summer_cal_requirements,
    summer_mask_path,
    swarp_config_path,
)
from winterdrp.pipelines.summer.config.schema import summer_schema_dir
from winterdrp.pipelines.summer.generator import (
    summer_astrometric_catalog_generator,
    summer_photometric_catalog_generator,
    summer_reference_image_generator,
    summer_reference_image_resampler,
    summer_reference_psfex,
    summer_reference_sextractor,
)
from winterdrp.pipelines.summer.load_summer_image import (
    load_proc_summer_image,
    load_raw_summer_image,
)
from winterdrp.processors import BiasCalibrator, FlatCalibrator
from winterdrp.processors.astromatic import PSFex, Scamp, Sextractor, Swarp
from winterdrp.processors.autoastrometry import AutoAstrometry
from winterdrp.processors.candidates.candidate_detector import DetectCandidates
from winterdrp.processors.candidates.utils import DataframeWriter, RegionsWriter
from winterdrp.processors.cosmic_rays import LACosmicCleaner
from winterdrp.processors.csvlog import CSVLog
from winterdrp.processors.database.database_exporter import DatabaseImageExporter
from winterdrp.processors.database.database_modifier import ModifyImageDatabaseSeq
from winterdrp.processors.mask import MaskPixels
from winterdrp.processors.photcal import PhotCalibrator
from winterdrp.processors.photometry.aperture_photometry import (
    CandidateAperturePhotometry,
)
from winterdrp.processors.photometry.psf_photometry import CandidatePSFPhotometry
from winterdrp.processors.reference import Reference
from winterdrp.processors.utils import (
    ImageBatcher,
    ImageLoader,
    ImageSaver,
    ImageSelector,
)
from winterdrp.processors.utils.cal_hunter import CalHunter
from winterdrp.processors.utils.header_annotate import HeaderEditor
from winterdrp.processors.utils.simulate_realtime import RealtimeImageSimulator
from winterdrp.processors.zogy.zogy import (
    ZOGY,
    ZOGYPrepare,
    default_summer_catalog_purifier,
)

load_raw = [
    ImageLoader(load_image=load_raw_summer_image),
]

load_test = [
    ImageLoader(
        input_img_dir=get_test_data_dir(),
        input_sub_dir="raw",
        load_image=load_raw_summer_image,
    ),
]

load_test_proc = [
    ImageLoader(
        input_img_dir=get_test_data_dir(),
        input_sub_dir="processed",
        load_image=load_proc_summer_image,
    ),
    ImageSelector((BASE_NAME_KEY, "SUMMER_20220816_042349_Camera0.resamp.fits")),
]

sim_realtime = [
    RealtimeImageSimulator(
        input_img_dir=get_test_data_dir(),
        input_img_names=[
            "summer/20220402/raw/SUMMER_20220402_193104_Camera0.fits",
            "summer/20220402/raw/SUMMER_20220402_214324_Camera0.fits",
        ],
        output_dir=get_test_data_dir(),
        output_dir_name="raw",
    )
]

build_log = [
    CSVLog(
        export_keys=[
            "UTC",
            "FIELDID",
            "FILTERID",
            "EXPTIME",
            "OBSTYPE",
            "RA",
            "DEC",
            "TARGTYPE",
            "PROGID",
            "PROGPI",
            BASE_NAME_KEY,
        ]
        + core_fields
    ),
]

load_processed = [
    ImageLoader(input_sub_dir="processed", load_image=load_proc_summer_image)
]

export_raw = [
    DatabaseImageExporter(
        db_name=DB_NAME,
        db_table="exposures",
        schema_path=get_summer_schema_path("exposures"),
        has_foreign_keys=True,
        schema_dir=summer_schema_dir,
        duplicate_protocol="ignore",
        q3c_bool=False,
    ),
    MaskPixels(mask_path=summer_mask_path),
    DatabaseImageExporter(
        db_name=DB_NAME,
        db_table="raw",
        schema_path=get_summer_schema_path("raw"),
        duplicate_protocol="replace",
    ),
    ImageSelector(("OBSTYPE", ["BIAS", "FLAT", "SCIENCE"])),
]

cal_hunter = [
    CalHunter(load_image=load_raw_summer_image, requirements=summer_cal_requirements),
]

test_cr = [
    MaskPixels(mask_path=summer_mask_path),
    BiasCalibrator(),
    ImageSelector(("OBSTYPE", ["FLAT", "SCIENCE"])),
    ImageBatcher(split_key="filter"),
    FlatCalibrator(),
    ImageSelector(("OBSTYPE", ["SCIENCE"])),
    LACosmicCleaner(effective_gain_key=GAIN_KEY, readnoise=2),
    ImageSaver(output_dir_name="crclean"),
]

process_raw = [
    BiasCalibrator(),
    ImageSelector(("OBSTYPE", ["FLAT", "SCIENCE"])),
    ImageBatcher(split_key="filter"),
    FlatCalibrator(),
    ImageBatcher(split_key=BASE_NAME_KEY),
    ImageSelector(("OBSTYPE", ["SCIENCE"])),
    LACosmicCleaner(effective_gain_key=GAIN_KEY, readnoise=2),
    ImageSaver(output_dir_name="detrend", write_mask=True),
    AutoAstrometry(pa=0, inv=True, pixel_scale=SUMMER_PIXEL_SCALE),
    ImageSaver(output_dir_name="detrend", write_mask=True),
    Sextractor(
        output_sub_dir="sextractor",
        # TODO: work out why this was ever here...
        # weight_image=summer_weight_path,
        checkimage_name=None,
        checkimage_type=None,
        **sextractor_astrometry_config
    ),
    Scamp(
        ref_catalog_generator=summer_astrometric_catalog_generator,
        scamp_config_path=scamp_path,
    ),
    Swarp(
        swarp_config_path=swarp_config_path,
        # TODO: work out why this was ever here...
        # imgpixsize=2400
    ),
    ImageSaver(output_dir_name="processed", write_mask=True),
    Sextractor(
        output_sub_dir="photprocess",
        checkimage_type="BACKGROUND_RMS",
        **sextractor_photometry_config
    ),
    PhotCalibrator(ref_catalog_generator=summer_photometric_catalog_generator),
    ImageSaver(
        output_dir_name="processed",
        # TODO: work out why this was ever here...
        # additional_headers=["PROCIMG"],
        write_mask=True,
    ),
    HeaderEditor(edit_keys="procflag", values=1),
    DatabaseImageExporter(
        db_name=DB_NAME,
        db_table="proc",
        schema_path=get_summer_schema_path("proc"),
        duplicate_protocol="replace",
    ),
    ModifyImageDatabaseSeq(
        db_name=DB_NAME,
        db_table="raw",
        schema_path=get_summer_schema_path("raw"),
        db_alter_columns="procflag",
    ),
]

standard_summer_reduction = export_raw + cal_hunter + process_raw


subtract = [
    ImageBatcher(split_key=BASE_NAME_KEY),
    ImageSelector(("OBSTYPE", "SCIENCE")),
    Reference(
        ref_image_generator=summer_reference_image_generator,
        ref_psfex=summer_reference_psfex,
        sextractor=summer_reference_sextractor,
        swarp_resampler=summer_reference_image_resampler,
    ),
    Sextractor(
        output_sub_dir="subtract",
        cache=False,
        write_regions_bool=True,
        **sextractor_photometry_config
    ),
    PSFex(config_path=psfex_config_path, output_sub_dir="subtract", norm_fits=True),
    ImageSaver(output_dir_name="ref"),
    ZOGYPrepare(
        output_sub_dir="subtract",
        sci_zp_header_key="ZP_AUTO",
        catalog_purifier=default_summer_catalog_purifier,
    ),
    ZOGY(output_sub_dir="subtract"),
]

export_diff_to_db = [
    DatabaseImageExporter(
        db_name=PIPELINE_NAME,
        db_table="diff",
        schema_path=get_summer_schema_path("diff"),
    ),
]

extract_candidates = [
    DetectCandidates(output_sub_dir="subtract", **sextractor_candidates_config),
    RegionsWriter(output_dir_name="candidates"),
    CandidatePSFPhotometry(),
    CandidateAperturePhotometry(
        aper_diameters=[8, 40],
        phot_cutout_size=100,
        bkg_in_diameters=[25, 90],
        bkg_out_diameters=[40, 100],
        col_suffix_list=["", "big"],
    ),
    DataframeWriter(output_dir_name="candidates"),
]

imsub = subtract + export_diff_to_db + extract_candidates
