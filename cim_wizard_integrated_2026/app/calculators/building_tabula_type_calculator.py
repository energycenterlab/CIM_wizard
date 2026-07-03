"""
Building TABULA Type Calculator

Derives TABULA typology codes from construction year (or const_tabula period)
and building usage type (residential / non-residential).

Output column: cim_wizard_building_properties.tabula_type
Format:        IT.{USAGE}.{TABULA_PERIOD}
Examples:      IT.RES.TABULA_5, IT.NRES.TABULA_3

Also backfills const_tabula when missing but const_year is available.
"""
from typing import Any, Dict, List, Optional, Tuple

from app.calculators.base_calculator import BaseCalculator

# Italian TABULA construction periods (aligned with building_construction_year_calculator)
TABULA_YEAR_RANGES: List[Tuple[int, int, str]] = [
    (0, 1900, "TABULA_1"),
    (1901, 1920, "TABULA_2"),
    (1921, 1945, "TABULA_3"),
    (1946, 1960, "TABULA_4"),
    (1961, 1975, "TABULA_5"),
    (1976, 1990, "TABULA_6"),
    (1991, 9999, "TABULA_7"),
]

USAGE_SEGMENT = {
    "residential": "RES",
    "non-residential": "NRES",
    "others": "NRES",
    "commercial": "COM",
    "industrial": "IND",
    "office": "OFF",
}


class BuildingTabulaTypeCalculator(BaseCalculator):
    """Assign TABULA typology string from construction year + building type."""

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    @staticmethod
    def period_from_year(year: Optional[int]) -> Optional[str]:
        if year is None:
            return None
        try:
            y = int(year)
        except (TypeError, ValueError):
            return None
        for start, end, period in TABULA_YEAR_RANGES:
            if start <= y <= end:
                return period
        return "TABULA_7"

    @staticmethod
    def usage_segment(building_type: Optional[str]) -> str:
        if not building_type:
            return "UNK"
        key = str(building_type).strip().lower()
        return USAGE_SEGMENT.get(key, key.upper().replace("-", "")[:8] or "UNK")

    @staticmethod
    def compose_tabula_type(building_type: Optional[str], period: Optional[str]) -> Optional[str]:
        if not period:
            return None
        usage = BuildingTabulaTypeCalculator.usage_segment(building_type)
        return f"IT.{usage}.{period}"

    def from_year_and_type(self) -> Optional[Dict[str, Any]]:
        """
        Pipeline entry point.

        Reads:
          - building_construction_year  (const_years, const_tabulas)
          - building_type               (building_types)
          - building_geo                (building list for DB upsert)

        Writes feature ``building_tabula_type`` with parallel lists:
          - tabula_types
          - const_tabulas  (backfill when year known but period missing)
        """
        construction = self.pipeline.get_feature_safely(
            "building_construction_year", calculator_name=self.calculator_name
        )
        type_data = self.pipeline.get_feature_safely(
            "building_type", calculator_name=self.calculator_name
        )
        building_geo = self.pipeline.get_feature_safely(
            "building_geo", calculator_name=self.calculator_name
        )

        if not building_geo:
            self.pipeline.log_error(self.calculator_name, "building_geo not available")
            return None

        buildings = building_geo.get("buildings", [])
        num_buildings = len(buildings)
        if num_buildings == 0:
            self.pipeline.log_error(self.calculator_name, "No buildings in building_geo")
            return None

        const_years: List[Optional[int]] = []
        const_tabulas: List[Optional[str]] = []
        building_types: List[Optional[str]] = []

        if construction:
            const_years = construction.get("const_years") or []
            const_tabulas = construction.get("const_tabulas") or []
        if type_data:
            building_types = type_data.get("building_types") or []

        tabula_types: List[Optional[str]] = []
        out_const_tabulas: List[Optional[str]] = []
        assigned = 0

        for i in range(num_buildings):
            btype = building_types[i] if i < len(building_types) else None
            year = const_years[i] if i < len(const_years) else None
            period = const_tabulas[i] if i < len(const_tabulas) else None

            if not period and year is not None:
                period = self.period_from_year(year)

            ttype = self.compose_tabula_type(btype, period)
            tabula_types.append(ttype)
            out_const_tabulas.append(period)

            if ttype:
                assigned += 1

        self.pipeline.log_info(
            self.calculator_name,
            f"Assigned tabula_type to {assigned}/{num_buildings} buildings",
        )

        result = {
            "tabula_types": tabula_types,
            "const_tabulas": out_const_tabulas,
            "total_assigned": assigned,
            "total_buildings": num_buildings,
        }
        self.data_manager.set_feature("building_tabula_type", result)
        return result
