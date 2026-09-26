"""
Archetype assignment: one orchestration over the stateless archetype mapper.

``assign_archetypes`` filters nothing and invents nothing: it loads the census
periods, classes, envelope and system tables from ``config/archetypes/``,
builds the mapper from ``mapping_rules.yaml``, and calls period, class and
attachment steps in order. Another app module may compose the same steps
differently, for example attaching only the envelope for a fabric-first study.
"""

from pathlib import Path
from typing import Dict, Optional

import geopandas as gpd
import pandas as pd
import yaml

from city_information_modeler.core.archetypes import ArchetypeMapper
from city_information_modeler.parallel import Runner

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config" / "archetypes"


def load_references(config_dir: Path = CONFIG_DIR) -> Dict[str, pd.DataFrame]:
    """Read every archetype reference table and the mapping rules."""
    config_dir = Path(config_dir)
    references = {}
    for name in (
        "periods",
        "building_classes",
        "envelope_archetypes",
        "systems",
        "stock_weights",
        "episcope_piedmont_aggregates",
    ):
        references[name] = pd.read_csv(config_dir / f"{name}.csv")
    with open(config_dir / "mapping_rules.yaml", encoding="utf-8") as handle:
        references["rules"] = yaml.safe_load(handle)
    return references


def build_mapper(rules: dict) -> ArchetypeMapper:
    """Build the mapper from the thresholds in ``mapping_rules.yaml``."""
    census_thresholds = rules["census_class_thresholds"]
    fallback_thresholds = rules["fallback_class_thresholds"]
    return ArchetypeMapper(
        residential_usages=tuple(rules["residential_usages"]),
        mixed_residential_usages=tuple(rules["mixed_residential_usages"]),
        sfh_dwellings=int(census_thresholds["sfh_dwellings"]),
        mfh_max_dwellings=int(census_thresholds["mfh_max_dwellings"]),
        sfh_max_floors=int(fallback_thresholds["sfh_max_floors"]),
        sfh_max_height_m=float(fallback_thresholds["sfh_max_height_m"]),
        mfh_max_floors=int(fallback_thresholds["mfh_max_floors"]),
        mfh_max_height_m=float(fallback_thresholds["mfh_max_height_m"]),
    )


def assign_archetypes(
    buildings_gdf: gpd.GeoDataFrame,
    config_dir: Path = CONFIG_DIR,
    runner: Optional[Runner] = None,
    attach_envelope: bool = True,
    attach_systems: bool = True,
) -> gpd.GeoDataFrame:
    """Attach census periods, classes, envelope and systems to building rows.

    Args:
        buildings_gdf: Footprint frame with the shared schema columns
            (``construction_year``, ``usage``, ``n_floors``, ``height_m`` and,
            where available, ``n_dwellings`` from the census).
        config_dir: Folder holding the archetype CSVs and mapping rules.
        runner: Runner to execute with. A new one reads ``config/compute.yaml``.
        attach_envelope: Join the TABULA/URBEM envelope row.
        attach_systems: Join the URBEM system row.

    Returns:
        A new GeoDataFrame with the provenance columns from mapping rules.
    """
    references = load_references(config_dir)
    mapper = build_mapper(references["rules"])
    runner = runner or Runner()

    result = runner.run(
        mapper.assign_period, buildings_gdf, references["periods"]
    )
    result = runner.run(mapper.assign_class, result)
    if attach_envelope:
        result = runner.run(
            mapper.attach_envelope, result, references["envelope_archetypes"]
        )
    if attach_systems:
        result = runner.run(
            mapper.attach_systems, result, references["systems"]
        )
    return result
