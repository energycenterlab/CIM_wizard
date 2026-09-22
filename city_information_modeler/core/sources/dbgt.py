"""
DBGT footprint source (Database Geotopografico, Comune di Torino).

WFS endpoint:
  https://geomap.reteunitaria.piemonte.it/ws/siccms/coto-01/wfsg01/wfs_sicc140_edificato_dbgt
Layer: ``Edificato``   Native CRS: EPSG:3003 (Gauss-Boaga West)

The richest source for Torino: the only one publishing a construction period, and it also
carries height, floor count, usage and ground/eave elevations.

Behaviour of the live endpoint, verified against it:

- Output is always EPSG:3003, reprojected to EPSG:4326 here.
- No feature cap: a 14x11 km box returned all 111995 features in one request, so no paging
  is needed. WFS 2.0.0 is not supported by this server at all.
- The layer mixes two groups. ``EDIFICI PRINCIPALI`` are real buildings; ``EDIFICI MINORI
  (O DI PERTINENZA)`` are garages, sheds and porticos with no usage or height at all.
  ``principal_only`` keeps the principal ones, which matches what BDTRE's ``edifc``
  contains, so the two sources stay comparable.
- There is no identifier of any kind, so ``building_uuid`` is derived from the rounded
  footprint. That was unique across all 41282 buildings of a test area.
- ``epoca_costruzione`` mixes exact years ("2017"), ranges ("1919 - 1945") and an open
  lower bound ("1918 (al ..)"). All three are parsed; the raw text is kept in
  ``construction_period`` so a different period mapping can be applied later.

Stateless: the class holds immutable settings only, and every method returns a new frame.
"""

from dataclasses import dataclass
from typing import Any, Dict

import geopandas as gpd
import pandas as pd

from city_information_modeler.core import boundary as boundary_module
from city_information_modeler.core import schema, wfs
from city_information_modeler.core.contracts import (
    MERGE_CONCAT,
    MERGE_CONCAT_DEDUP,
    SPLIT_ROW_BATCHES,
    SPLIT_SPATIAL_TILES,
    WORKLOAD_CPU,
    WORKLOAD_IO,
    parallelizable,
)
from city_information_modeler.core.geometry import GEODETIC_EPSG

WFS_URL = (
    "https://geomap.reteunitaria.piemonte.it/ws/siccms/coto-01/wfsg01/"
    "wfs_sicc140_edificato_dbgt"
)
BUILDING_LAYER = "Edificato"
SOURCE_EPSG = 3003
SOURCE_NAME = "dbgt"

MINOR_GROUP_TOKEN = "MINORI"

# Any four-digit year from 1600 onwards; the layer holds nothing older.
YEAR_PATTERN = r"(1[6-9]\d{2}|20\d{2})"
# Marks an open lower bound, as in "1918 (al ..)" meaning "up to 1918".
OPEN_LOWER_BOUND_PATTERN = r"al\s*\.\."

# categoria_uso is hierarchical, with " - " between levels. The full strings published
# today are mapped here; unknown values fall back to their first level below.
USAGE_MAP: Dict[str, str] = {
    "residenziale": "residential",
    "commerciale": "commercial",
    "commerciale - terziario": "commercial",
    "commerciale - sede di supermercato, ipermercato": "commercial",
    "commerciale - mercato": "commercial",
    "industriale": "industrial",
    "industriale - stabilimento": "industrial",
    "industriale - impianto tecnologico": "industrial",
    "industriale - impianto di produzione energia": "industrial",
    "agricolturale": "agricultural",
    "militare": "military",
    "militare - caserma": "military",
    "carcere, istituto di pena": "public",
    "servizio pubblico": "public",
    "amministrativo": "public",
    "amministrativo - sede regione": "public",
    "amministrativo - sede ambasciata o consolato": "public",
    "luogo di culto": "religious",
    "strutture ricettive": "accommodation",
    "strutture ricettive - struttura alberghiera": "accommodation",
    "servizi - istruzione": "education",
    "servizi - istruzione - sede di scuola": "education",
    "servizi - istruzione - università": "education",
    "servizi - istruzione - laboratorio di ricerca": "education",
    "servizi - sede di ospedale": "health",
    "servizi - sede clinica": "health",
    "servizi - sanità": "health",
    "servizi - sede servizi sanitari asl": "health",
    "servizi - sede di servizio socio assistenziale": "health",
    "servizi - sede forze dell'ordine": "public",
    "servizi - sede di vigili del fuoco": "public",
    "servizi - sede di poste / telegrafi": "public",
    "servizi - sede di tribunale": "public",
    "servizi trasporto-parcheggio multipiano o coperto": "transport",
    "ferroviario": "transport",
    "ferroviario - stazione passeggeri": "transport",
    "ferroviario - deposito": "transport",
    "ferroviario - scalo merci": "transport",
    "ricreativo": "culture",
    "ricreativo - museo": "culture",
    "ricreativo - cinema": "culture",
    "ricreativo - teatro, auditorium": "culture",
    "ricreativo - biblioteca": "culture",
    "ricreativo - sede di attività culturali": "culture",
    "sede di attività sportive": "sport",
    "sede di attività sportive - palestra": "sport",
    "sede di attività sportive - piscina coperta": "sport",
    "sede di attività sportive - palaghiaccio": "sport",
}

# Fallback on the first level of categoria_uso, for values added after this mapping.
PREFIX_USAGE_MAP: Dict[str, str] = {
    "residenziale": "residential",
    "commerciale": "commercial",
    "industriale": "industrial",
    "agricolturale": "agricultural",
    "militare": "military",
    "servizio pubblico": "public",
    "amministrativo": "public",
    "luogo di culto": "religious",
    "strutture ricettive": "accommodation",
    "ricreativo": "culture",
    "sede di attività sportive": "sport",
    "ferroviario": "transport",
    "servizi": "public",
}


@dataclass(frozen=True)
class DbgtFootprintSource:
    """Read building footprints and attributes from DBGT.

    Frozen so an instance is immutable and picklable: a worker process can be handed a
    copy and produce the same answer as any other worker.
    """

    timeout_s: int = wfs.REQUEST_TIMEOUT_S
    clip_to_boundary: bool = True
    principal_only: bool = True

    @parallelizable(
        split=SPLIT_SPATIAL_TILES,
        merge=MERGE_CONCAT_DEDUP,
        workload=WORKLOAD_IO,
        split_arg="boundary_geojson",
        dedup_on="building_uuid",
    )
    def fetch_buildings(self, boundary_geojson: Dict[str, Any]) -> gpd.GeoDataFrame:
        """Read every DBGT building inside a boundary, with all published attributes.

        Args:
            boundary_geojson: FeatureCollection, Feature, Polygon or MultiPolygon in
                EPSG:4326.

        Returns:
            A GeoDataFrame in EPSG:4326 with ``schema.STANDARD_COLUMNS``.
        """
        boundary_gdf = boundary_module.to_gdf(boundary_geojson)
        bbox = boundary_module.bbox_in_crs(boundary_gdf, SOURCE_EPSG)

        buildings_gdf = wfs.fetch_single(
            WFS_URL, BUILDING_LAYER, bbox, SOURCE_EPSG, self.timeout_s
        )
        if buildings_gdf.empty:
            return schema.empty_buildings()

        buildings_gdf = buildings_gdf.to_crs(epsg=GEODETIC_EPSG)
        if self.clip_to_boundary:
            buildings_gdf = boundary_module.clip(buildings_gdf, boundary_gdf)
        if self.principal_only and not buildings_gdf.empty:
            buildings_gdf = self.keep_principal_buildings(buildings_gdf)
        if buildings_gdf.empty:
            return schema.empty_buildings()

        return self.normalize(buildings_gdf)

    @parallelizable(
        split=SPLIT_SPATIAL_TILES,
        merge=MERGE_CONCAT,
        workload=WORKLOAD_IO,
        split_arg="boundary_geojson",
    )
    def fetch_building_layer(self, boundary_geojson: Dict[str, Any]) -> gpd.GeoDataFrame:
        """Read the raw ``Edificato`` layer, unmapped, for inspecting what DBGT publishes."""
        boundary_gdf = boundary_module.to_gdf(boundary_geojson)
        bbox = boundary_module.bbox_in_crs(boundary_gdf, SOURCE_EPSG)
        return wfs.fetch_single(
            WFS_URL, BUILDING_LAYER, bbox, SOURCE_EPSG, self.timeout_s
        )

    @staticmethod
    def keep_principal_buildings(buildings_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Drop the minor/ancillary group, which carries no usage, height or floor count."""
        group = buildings_gdf["gruppo"].astype("string").fillna("")
        is_principal = ~group.str.contains(MINOR_GROUP_TOKEN, case=False, na=False)
        return buildings_gdf[is_principal].reset_index(drop=True)

    @parallelizable(
        split=SPLIT_ROW_BATCHES,
        merge=MERGE_CONCAT,
        workload=WORKLOAD_CPU,
        split_arg="buildings_gdf",
        min_rows_per_split=5000,
    )
    def normalize(self, buildings_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Map DBGT attributes onto the shared building schema."""
        source = buildings_gdf.reset_index(drop=True)
        standard = gpd.GeoDataFrame(
            {"geometry": source.geometry}, geometry="geometry", crs=source.crs
        )

        standard["source"] = SOURCE_NAME
        standard["source_id"] = schema.geometry_keys(source)
        standard["building_uuid"] = schema.building_uuids(
            SOURCE_NAME, standard["source_id"]
        )

        standard["usage_raw"] = schema.clean_text(source["categoria_uso"])
        standard["usage"] = self.map_usage(standard["usage_raw"])
        standard["building_type"] = schema.clean_text(source["descrizione"])

        group = schema.clean_text(source["gruppo"])
        standard["building_group"] = group
        standard["is_minor_building"] = group.fillna("").str.contains(
            MINOR_GROUP_TOKEN, case=False, na=False
        )

        standard["name"] = schema.clean_text(source["nome"])
        historic = schema.clean_text(source["valenza_storica"])
        standard["is_monument"] = historic.str.lower().eq("monumentale").fillna(False)

        standard["ground_elevation_m"] = pd.to_numeric(
            source["qt_suolo"], errors="coerce"
        )
        standard["eave_elevation_m"] = pd.to_numeric(
            source["qt_gronda"], errors="coerce"
        )
        standard = self.attach_heights(standard, source)

        standard["n_floors"] = pd.to_numeric(
            source["numero_piani"], errors="coerce"
        ).astype("Int64")

        standard = self.attach_construction_period(standard, source)

        return schema.to_standard_schema(standard)

    @staticmethod
    def map_usage(usage_raw: pd.Series) -> pd.Series:
        """Map categoria_uso to the shared usage vocabulary, falling back to its first level."""
        lowered = usage_raw.str.lower()
        mapped = lowered.map(USAGE_MAP)

        first_level = lowered.str.split(" - ").str[0].str.strip()
        fallback = first_level.map(PREFIX_USAGE_MAP)

        return mapped.fillna(fallback).fillna("unknown")

    @staticmethod
    def attach_heights(
        standard: gpd.GeoDataFrame,
        source: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Take the published height, falling back to eave elevation minus ground elevation."""
        published = pd.to_numeric(source["altezza_edificio"], errors="coerce")
        published = published.where(published > 0)

        elevation_difference = (
            standard["eave_elevation_m"] - standard["ground_elevation_m"]
        )
        elevation_difference = elevation_difference.where(elevation_difference > 0)

        standard["height_m"] = published.fillna(elevation_difference)

        standard["height_source"] = None
        standard.loc[
            standard["height_m"].notna(), "height_source"
        ] = "dbgt_eave_minus_ground"
        standard.loc[published.notna(), "height_source"] = "dbgt_altezza_edificio"
        return standard

    @staticmethod
    def attach_construction_period(
        standard: gpd.GeoDataFrame,
        source: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Parse epoca_costruzione into a range and a representative year.

        Handles the three published shapes: an exact year, a closed range, and an open
        lower bound written as "1918 (al ..)".
        """
        period = schema.clean_text(source["epoca_costruzione"])
        standard["construction_period"] = period

        years = period.str.extract(rf"{YEAR_PATTERN}\D*{YEAR_PATTERN}?")
        first_year = pd.to_numeric(years[0], errors="coerce")
        second_year = pd.to_numeric(years[1], errors="coerce")

        is_range = second_year.notna()
        is_open_lower_bound = period.str.contains(
            OPEN_LOWER_BOUND_PATTERN, case=False, na=False, regex=True
        )

        year_from = first_year.where(~is_open_lower_bound)
        year_to = second_year.fillna(first_year)
        representative = ((first_year + second_year) / 2).where(is_range, first_year)

        standard["construction_year_from"] = year_from.astype("Int64")
        standard["construction_year_to"] = year_to.astype("Int64")
        standard["construction_year"] = representative.round().astype("Int64")

        standard["construction_year_source"] = None
        standard.loc[
            standard["construction_year"].notna(), "construction_year_source"
        ] = "dbgt_epoca_costruzione"
        return standard
