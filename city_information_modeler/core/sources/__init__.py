"""Footprint sources. Each one maps its own fields onto ``core.schema.STANDARD_COLUMNS``."""

from city_information_modeler.core.sources.bdtre import BdtreFootprintSource
from city_information_modeler.core.sources.dbgt import DbgtFootprintSource

FOOTPRINT_SOURCES = {
    "bdtre": BdtreFootprintSource,
    "dbgt": DbgtFootprintSource,
}

__all__ = ["BdtreFootprintSource", "DbgtFootprintSource", "FOOTPRINT_SOURCES"]
