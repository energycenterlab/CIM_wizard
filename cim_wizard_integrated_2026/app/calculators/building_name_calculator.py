"""
Building Name Calculator - Assigns sequential names (BUI-0001, BUI-0002, …)
to buildings within a scenario. Stores in cim_vector.cim_wizard_building.building_name
"""
from typing import Optional, List

from app.calculators.base_calculator import BaseCalculator


class BuildingNameCalculator(BaseCalculator):

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    def assign_sequential(self) -> Optional[List[str]]:
        """Assign BUI-#### names to buildings in order of appearance."""

        self.log_info("Starting building name assignment")

        building_geo = self.get_feature("building_geo")
        if not building_geo:
            self.log_error("No building_geo data")
            return None

        buildings = building_geo.get("buildings", [])
        if not buildings:
            self.log_error("No buildings in building_geo")
            return None

        names = [f"BUI-{i + 1:04d}" for i in range(len(buildings))]
        self.data_manager.set_feature("building_name", names)

        # Persist to cim_wizard_building.building_name
        try:
            session = self.data_manager._require_session()
            from app.models.vector import Building
            for i, building in enumerate(buildings):
                bid = building.get("building_id")
                if bid:
                    bldg = session.query(Building).filter_by(building_id=bid).first()
                    if bldg:
                        bldg.building_name = names[i]
            session.commit()
        except Exception as e:
            self.log_warning(f"DB save building_name failed: {e}")

        self.log_success("assign_sequential",
                         f"Named {len(buildings)} buildings (BUI-0001 .. BUI-{len(buildings):04d})")
        return names
