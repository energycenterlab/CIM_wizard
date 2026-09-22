"""
BDTRE footprint source (Base Dati Territoriale di Riferimento degli Enti, Regione Piemonte).

WFS endpoint: https://geoservices.csi.it/ms/wfs/taims/rp-01/taimswfs/bdtre_imm

Layers read:
  ``edifc``   Edificio           footprint, building type, use, status, name, survey dates
  ``un_vol``  Unita volumetrica  volume units carrying the building height in metres

Behaviour of the live endpoint, verified against it:

- Output is always EPSG:32632. ``srsName`` is ignored, so the bounding box is sent in
  metres and the answer is reprojected to EPSG:4326 here.
- One GetFeature returns at most 1000 features and does not report that it truncated.
  A 5x5 km box around Torino holds ~19500 buildings, so WFS 2.0.0 ``startIndex`` paging
  is used to read them all.
- ``un_vol`` is captured at 1:10000 and ``edifc`` at 1:2000, but the footprints still line
  up: a representative-point join gives the same height as a largest-overlap join and
  covers ~98% of footprints.
- ``edifc`` holds principal buildings only; garages and sheds live in the separate
  ``edi_min`` layer, which this class does not read.
- ``edifc_ided`` and ``edifc_idag`` are empty in Torino, so the ``uuid`` attribute is the
  stable official identifier and the one building_uuid is derived from.
- BDTRE publishes no construction year. ``survey_year`` carries the cadastre survey year
  instead, which is a different thing: 95% of Torino shares the single date 2019-11-30 and
  every survey year is 1991 or later. Using it as a construction year would put every
  building in the newest TABULA period, so ``construction_year`` stays null unless
  ``construction_year_from_survey`` is switched on deliberately.

Stateless: the class holds immutable settings only, and every method returns a new frame.
"""

from dataclasses import dataclass
from typing import Any, Dict

import geopandas as gpd
import pandas as pd

from city_information_modeler.core import boundary as boundary_module
from city_information_modeler.core import schema, wfs
from city_information_modeler.core.contracts import (
    MERGE_CONCAT_DEDUP,
    SPLIT_SPATIAL_TILES,
    WORKLOAD_IO,
    parallelizable,
)
from city_information_modeler.core.geometry import GEODETIC_EPSG, METRIC_EPSG

WFS_URL = "https://geoservices.csi.it/ms/wfs/taims/rp-01/taimswfs/bdtre_imm"
FOOTPRINT_LAYER = "edifc"
VOLUME_LAYER = "un_vol"
SOURCE_EPSG = METRIC_EPSG
SOURCE_NAME = "bdtre"

# The server refuses count > 1000 and silently truncates a request without it.
PAGE_SIZE = 1000

# BDTRE writes the building use in Italian. Map it to the shared usage vocabulary.
USAGE_MAP: Dict[str, str] = {
    "residenziale": "residential",
    "abitativa": "residential",
    "residenziale e commerciale": "mixed_residential_commercial",
    "residenziale e produttivo": "mixed_residential_industrial",
    "residenziale e ufficio pubblico": "mixed_residential_public",
    "uso misto di altro tipo": "mixed_other",
    "commerciale": "commercial",
    "sede di banca": "commercial",
    "strutture ricettive": "accommodation",
    "industriale": "industrial",
    "produttivo": "industrial",
    "istruzione": "education",
    "sede di scuola": "education",
    "universita": "education",
    "università": "education",
    "sanita": "health",
    "sanità": "health",
    "luogo di culto": "religious",
    "museo": "culture",
    "cinema": "culture",
    "teatro, auditorium": "culture",
    "sede di attivita culturali": "culture",
    "sede di attività culturali": "culture",
    "sede di attivita sportive": "sport",
    "sede di attività sportive": "sport",
    "militare": "military",
    "servizio pubblico": "public",
    "sede di citta' metropolitana": "public",
    "sede di poste-telegrafi": "public",
    "servizi di trasporto": "transport",
    "stazione passeggeri ferroviaria": "transport",
    "altro": "other",
}


@dataclass(frozen=True)
class BdtreFootprintSource:
    """Read building footprints and attributes from BDTRE.

    Frozen so an instance is immutable and picklable: a worker process can be handed a
    copy and produce the same answer as any other worker.
    """

    timeout_s: int = wfs.REQUEST_TIMEOUT_S
    clip_to_boundary: bool = True
    construction_year_from_survey: bool = False

    @parallelizable(
        split=SPLIT_SPATIAL_TILES,
        merge=MERGE_CONCAT_DEDUP,
        workload=WORKLOAD_IO,
        split_arg="boundary_geojson",
        dedup_on="building_uuid",
    )
    def fetch_buildings(self, boundary_geojson: Dict[str, Any]) -> gpd.GeoDataFrame:
        """Read every BDTRE building inside a boundary, with its attributes and height.

        Args:
            boundary_geojson: FeatureCollection, Feature, Polygon or MultiPolygon in
                EPSG:4326.

        Returns:
            A GeoDataFrame in EPSG:4326 with ``schema.STANDARD_COLUMNS``.
        """
        boundary_gdf = boundary_module.to_gdf(boundary_geojson)
        bbox = boundary_module.bbox_in_crs(boundary_gdf, SOURCE_EPSG)

        footprints_gdf = wfs.fetch_paged(
            WFS_URL, FOOTPRINT_LAYER, bbox, SOURCE_EPSG, PAGE_SIZE, self.timeout_s
        )
        if footprints_gdf.empty:
            return schema.empty_buildings()

        volumes_gdf = wfs.fetch_paged(
            WFS_URL, VOLUME_LAYER, bbox, SOURCE_EPSG, PAGE_SIZE, self.timeout_s
        )
        footprints_gdf = self.attach_heights(footprints_gdf, volumes_gdf)

        footprints_gdf = footprints_gdf.to_crs(epsg=GEODETIC_EPSG)
        if self.clip_to_boundary:
            footprints_gdf = boundary_module.clip(footprints_gdf, boundary_gdf)
        if footprints_gdf.empty:
            return schema.empty_buildings()

        return self.normalize(footprints_gdf)

    @parallelizable(
        split=SPLIT_SPATIAL_TILES,
        merge=MERGE_CONCAT_DEDUP,
        workload=WORKLOAD_IO,
        split_arg="boundary_geojson",
        dedup_on="uuid",
    )
    def fetch_footprint_layer(self, boundary_geojson: Dict[str, Any]) -> gpd.GeoDataFrame:
        """Read the raw ``edifc`` layer, unmapped, for inspecting what BDTRE publishes."""
        boundary_gdf = boundary_module.to_gdf(boundary_geojson)
        bbox = boundary_module.bbox_in_crs(boundary_gdf, SOURCE_EPSG)
        return wfs.fetch_paged(
            WFS_URL, FOOTPRINT_LAYER, bbox, SOURCE_EPSG, PAGE_SIZE, self.timeout_s
        )

    def attach_heights(
        self,
        footprints_gdf: gpd.GeoDataFrame,
        volumes_gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Copy ``un_vol`` heights onto footprints and count volume units per footprint.

        A footprint can hold several volume units of different heights. The tallest is
        taken as the building height, which matches how LoD 1.2 extrusion uses it.
        """
        footprints_gdf = footprints_gdf.reset_index(drop=True)

        if volumes_gdf.empty or "un_vol_av" not in volumes_gdf.columns:
            footprints_gdf["height_m"] = pd.Series(
                pd.NA, index=footprints_gdf.index, dtype="Float64"
            )
            footprints_gdf["volume_units"] = 0
            footprints_gdf["height_source"] = None
            return footprints_gdf

        # un_vol_av is the volume height in metres, delivered as text and sometimes blank.
        volume_heights = pd.to_numeric(volumes_gdf["un_vol_av"], errors="coerce")
        volume_points = gpd.GeoDataFrame(
            {"height_m": volume_heights.to_numpy()},
            geometry=volumes_gdf.geometry.representative_point(),
            crs=volumes_gdf.crs,
        )
        volume_points = volume_points[volume_points["height_m"].notna()]

        joined = gpd.sjoin(
            footprints_gdf[["geometry"]],
            volume_points,
            how="left",
            predicate="contains",
        )
        per_footprint = joined.groupby(level=0)["height_m"].agg(["max", "count"])

        footprints_gdf["height_m"] = per_footprint["max"]
        footprints_gdf["volume_units"] = per_footprint["count"].astype(int)
        footprints_gdf["height_source"] = None
        footprints_gdf.loc[
            footprints_gdf["height_m"].notna(), "height_source"
        ] = "bdtre_un_vol"
        return footprints_gdf

    @parallelizable(
        split="row_batches",
        merge="concat",
        workload="cpu",
        split_arg="footprints_gdf",
        min_rows_per_split=5000,
    )
    def normalize(self, footprints_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Map BDTRE attributes onto the shared building schema."""
        source = footprints_gdf.reset_index(drop=True)
        standard = gpd.GeoDataFrame(
            {"geometry": source.geometry}, geometry="geometry", crs=source.crs
        )

        standard["source"] = SOURCE_NAME
        standard["source_id"] = schema.clean_text(source["uuid"])
        standard["building_uuid"] = schema.building_uuids(
            SOURCE_NAME, standard["source_id"]
        )

        standard["usage_raw"] = schema.clean_text(source["edifc_uso"])
        standard["usage"] = (
            standard["usage_raw"].str.lower().map(USAGE_MAP).fillna("unknown")
        )
        standard["building_type"] = schema.clean_text(source["edifc_ty"])
        standard["status"] = schema.clean_text(source["edifc_stat"])
        standard["name"] = schema.clean_text(source["edifc_nome"])
        standard["is_monument"] = (
            source["edifc_mon"].astype("string").str.strip().eq("1").fillna(False)
        )

        # The edifc layer holds principal buildings; minor ones are in edi_min.
        standard["building_group"] = "principal"
        standard["is_minor_building"] = False

        standard["height_m"] = source["height_m"]
        standard["height_source"] = source["height_source"]
        standard["volume_units"] = source["volume_units"]

        standard["survey_date"] = schema.clean_text(source["data_acq"])
        standard["update_date"] = schema.clean_text(source["data_agg"])
        standard["valid_until"] = schema.clean_text(source["data_fin"])
        standard["survey_year"] = self.survey_years(standard["survey_date"])

        standard["data_supplier"] = schema.clean_text(source["ente_for"])
        standard["data_producer"] = schema.clean_text(source["ente_prod"])
        standard["production_method"] = schema.clean_text(source["modo_prod"])
        standard["acquisition_scale"] = schema.clean_text(source["sc_acq"])

        if self.construction_year_from_survey:
            standard["construction_year"] = standard["survey_year"]
            standard["construction_year_source"] = "bdtre_survey_year_proxy"

        return schema.to_standard_schema(standard)

    @staticmethod
    def survey_years(survey_date: pd.Series) -> pd.Series:
        """Year of the cadastre survey. This is not the construction year."""
        return pd.to_datetime(survey_date, errors="coerce").dt.year.astype("Int64")
