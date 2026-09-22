"""
Footprint collection: several orchestrations over the same core classes.

``collect`` reads one source. ``collect_all`` reads several and stacks them, keeping the
source column so the rows stay attributable. ``conflate`` reads several and resolves them
into one building per reference footprint. None of them adds geometry logic: the work belongs
to core, and the worker sizing belongs to the runner.

An orchestration is where a use case decides which core classes to call and in what order.
Another app module is free to compose the same classes differently.
"""

from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd
import pandas as pd

from city_information_modeler.core import schema
from city_information_modeler.core.conflation import BuildingConflator, SourceFrames
from city_information_modeler.core.sources import FOOTPRINT_SOURCES
from city_information_modeler.parallel import Runner

# DBGT first: it is surveyed at building detail and publishes the construction period, so it
# defines what counts as one building. BDTRE then fills the gaps it leaves.
DEFAULT_PRIORITY: Tuple[str, ...] = ("dbgt", "bdtre")


def collect(
    boundary_geojson: Dict[str, Any],
    source_name: str = "dbgt",
    runner: Optional[Runner] = None,
    **source_settings: Any,
) -> gpd.GeoDataFrame:
    """Read building footprints from one source.

    Args:
        boundary_geojson: Boundary in EPSG:4326.
        source_name: Key in ``core.sources.FOOTPRINT_SOURCES``.
        runner: Runner to execute with. A new one reads ``config/compute.yaml``.
        **source_settings: Passed to the source class, for example ``principal_only``.

    Returns:
        A GeoDataFrame with ``schema.STANDARD_COLUMNS``.
    """
    source = build_source(source_name, **source_settings)
    runner = runner or Runner()
    return runner.run(source.fetch_buildings, boundary_geojson)


def collect_all(
    boundary_geojson: Dict[str, Any],
    source_names: Optional[List[str]] = None,
    runner: Optional[Runner] = None,
) -> gpd.GeoDataFrame:
    """Read the same boundary from several sources and stack the answers.

    Rows keep their ``source`` column, so nothing is silently merged. Deciding which source
    wins for a given building is conflation, and does not belong here.
    """
    source_names = source_names or sorted(FOOTPRINT_SOURCES)
    runner = runner or Runner()

    collected: List[gpd.GeoDataFrame] = []
    for source_name in source_names:
        collected.append(collect(boundary_geojson, source_name, runner))

    return stack(collected)


def collect_by_source(
    boundary_geojson: Dict[str, Any],
    source_names: Tuple[str, ...] = DEFAULT_PRIORITY,
    runner: Optional[Runner] = None,
) -> Dict[str, gpd.GeoDataFrame]:
    """Read the same boundary from several sources, keeping each answer separate."""
    runner = runner or Runner()

    frames: Dict[str, gpd.GeoDataFrame] = {}
    for source_name in source_names:
        frames[source_name] = collect(boundary_geojson, source_name, runner)
    return frames


def conflate(
    boundary_geojson: Dict[str, Any],
    priority: Tuple[str, ...] = DEFAULT_PRIORITY,
    runner: Optional[Runner] = None,
    conflator: Optional[BuildingConflator] = None,
) -> gpd.GeoDataFrame:
    """Read several sources and resolve them into one building per reference footprint.

    The first name in ``priority`` defines the buildings and supplies the geometry; the rest
    fill in the fields it left empty. Every resolved field group carries an ``_origin`` column
    naming the source it came from.
    """
    frames = collect_by_source(boundary_geojson, priority, runner)
    return conflate_frames(frames, priority, runner, conflator)


def conflate_frames(
    frames: Dict[str, gpd.GeoDataFrame],
    priority: Tuple[str, ...] = DEFAULT_PRIORITY,
    runner: Optional[Runner] = None,
    conflator: Optional[BuildingConflator] = None,
) -> gpd.GeoDataFrame:
    """Conflate frames that were already read, so one fetch can feed several settings."""
    conflator = conflator or BuildingConflator()
    runner = runner or Runner()
    return runner.run(conflator.conflate, SourceFrames(frames=frames, priority=priority))


def conflation_gain(conflated_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """How many buildings each source ended up supplying each field group.

    This is the number that says whether conflating was worth it: a group where the
    enrichment source contributed nothing did not need to be conflated at all.
    """
    from city_information_modeler.core.conflation import CONFLATION_GROUPS

    rows: List[Dict[str, Any]] = []
    for group in CONFLATION_GROUPS:
        origins = conflated_gdf[group.origin_column]
        row: Dict[str, Any] = {"field_group": group.name}
        row["filled"] = int(origins.notna().sum())
        row["filled_share"] = float(origins.notna().mean())
        for source_name in origins.dropna().unique():
            row[f"from_{source_name}"] = int((origins == source_name).sum())
        rows.append(row)

    return pd.DataFrame(rows).set_index("field_group").fillna(0)


def coverage(buildings_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """How completely each source filled the attributes, as a fraction per source."""
    attributes = ["height_m", "construction_year", "n_floors", "name"]

    rows: List[Dict[str, Any]] = []
    for source_name, group in buildings_gdf.groupby("source", dropna=False):
        row: Dict[str, Any] = {"source": source_name, "buildings": len(group)}
        row["usage_known"] = float((group["usage"] != "unknown").mean())
        for attribute in attributes:
            row[attribute] = float(group[attribute].notna().mean())
        rows.append(row)

    return pd.DataFrame(rows).set_index("source")


def build_source(source_name: str, **source_settings: Any):
    """Instantiate a footprint source by name."""
    if source_name not in FOOTPRINT_SOURCES:
        available = ", ".join(sorted(FOOTPRINT_SOURCES))
        raise ValueError(f"unknown source {source_name!r}; available: {available}")
    return FOOTPRINT_SOURCES[source_name](**source_settings)


def stack(frames: List[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    """Stack standard-schema frames, keeping the CRS."""
    filled = [frame for frame in frames if not frame.empty]
    if not filled:
        return schema.empty_buildings()

    stacked = pd.concat(filled, ignore_index=True)
    return gpd.GeoDataFrame(stacked, geometry="geometry", crs=filled[0].crs)
