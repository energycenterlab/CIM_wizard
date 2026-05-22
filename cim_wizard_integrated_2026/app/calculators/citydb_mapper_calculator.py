"""
CityDB Mapper Calculator

Maps CIM Wizard building data to 3DCityDB v4 schema (ORM-based) and
generates CityJSON v1.1 output with Energy ADE extensions.

Mapping:
  project-scenario  ->  citydb.citymodel  (gmlid = scenario_id)
  building          ->  citydb.cityobject + citydb.building (gmlid = building_id)
  LOD1.2 surfaces   ->  citydb.surface_geometry + citydb.thematic_surface
  thermal zone      ->  CityJSON "+Energy-ThermalZone" (id = building_id + "-z1")
  TABULA U-values   ->  citydb.cityobject_genericattrib on thematic surfaces
  energy system     ->  CityJSON attributes (envelope_efficiency, fmu_file)
"""

import json as _json
import logging
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_GeomFromEWKT, ST_AsEWKT, ST_AsGeoJSON, ST_Force3D

from app.calculators.base_calculator import BaseCalculator
from app.models.citydb import (
    CityModel,
    CityObject,
    CityObjectMember,
    CityBuilding,
    ThematicSurface,
    SurfaceGeometry,
    CityObjectGenericAttrib,
    Ng2Building,
    Ng2ThematicSurface,
    Ng2BuildingPartition,
    Ng2LayeredConstruction,
)

logger = logging.getLogger(__name__)

# Italian TABULA residential U-values (W/m2K) by construction period
TABULA_U_VALUES: Dict[str, Dict[str, float]] = {
    "TABULA_1": {"wall": 1.70, "roof": 2.20, "ground": 1.60},
    "TABULA_2": {"wall": 1.60, "roof": 2.00, "ground": 1.50},
    "TABULA_3": {"wall": 1.48, "roof": 1.80, "ground": 1.40},
    "TABULA_4": {"wall": 1.30, "roof": 1.60, "ground": 1.20},
    "TABULA_5": {"wall": 1.10, "roof": 1.20, "ground": 1.00},
    "TABULA_6": {"wall": 0.80, "roof": 0.80, "ground": 0.80},
    "TABULA_7": {"wall": 0.50, "roof": 0.40, "ground": 0.50},
}

TABULA_CONSTR_WEIGHT: Dict[str, str] = {
    "TABULA_1": "heavy",
    "TABULA_2": "heavy",
    "TABULA_3": "heavy",
    "TABULA_4": "medium",
    "TABULA_5": "medium",
    "TABULA_6": "light",
    "TABULA_7": "light",
}

ENVELOPE_CONSTR_WEIGHT: Dict[str, str] = {
    "low": "heavy",
    "medium": "medium",
    "high": "light",
}

# 3DCityDB v4 objectclass IDs (CityGML 2.0)
OC_BUILDING = 26
OC_CEILING_SURFACE = 30
OC_FLOOR_SURFACE = 32
OC_ROOF_SURFACE = 33
OC_WALL_SURFACE = 34
OC_GROUND_SURFACE = 35

# Generic-attribute datatype codes
DT_STRING = 1
DT_INTEGER = 2
DT_REAL = 3


def _utm_srid_for(lon: float, lat: float) -> int:
    """Return EPSG code of the UTM zone containing the given lon/lat."""
    zone = int((lon + 180.0) / 6.0) + 1
    if zone < 1:
        zone = 1
    if zone > 60:
        zone = 60
    return 32600 + zone if lat >= 0 else 32700 + zone


def _looks_geographic(x: float, y: float) -> bool:
    """True when x/y look like WGS84 degrees (not projected metres)."""
    return abs(x) <= 180.0 and abs(y) <= 90.0


def _polygon_geojson_to_ewkt(geojson_geom: dict, srid: int = 4326) -> Optional[str]:
    """Convert a GeoJSON Polygon (2D or 3D) to PostGIS EWKT 'POLYGON Z((...))'.

    Forces 3D output (Z defaults to 0 for missing coordinates). This bypasses
    ST_GeomFromGeoJSON which can silently drop Z under geographic SRIDs.
    """
    if not geojson_geom or geojson_geom.get("type") != "Polygon":
        return None
    rings = geojson_geom.get("coordinates", [])
    if not rings:
        return None

    ring_parts: List[str] = []
    for ring in rings:
        if not ring:
            continue
        pts: List[str] = []
        for c in ring:
            x = float(c[0])
            y = float(c[1])
            z = float(c[2]) if len(c) > 2 else 0.0
            pts.append(f"{x} {y} {z}")
        if pts and pts[0] != pts[-1]:
            pts.append(pts[0])
        ring_parts.append("(" + ", ".join(pts) + ")")
    if not ring_parts:
        return None
    return f"SRID={srid};POLYGON Z(" + ", ".join(ring_parts) + ")"


def _constr_weight_from_props(props) -> Optional[str]:
    tabula = getattr(props, "const_tabula", None) or ""
    if tabula in TABULA_CONSTR_WEIGHT:
        return TABULA_CONSTR_WEIGHT[tabula]
    env = getattr(props, "envelope_efficiency", None)
    if env in ENVELOPE_CONSTR_WEIGHT:
        return ENVELOPE_CONSTR_WEIGHT[env]
    return None


def _add_generic_attrib(
    session: Session,
    cityobject_id: int,
    name: str,
    value: Any,
    *,
    unit: Optional[str] = None,
):
    if value is None:
        return
    if isinstance(value, bool):
        value = str(value)
    if isinstance(value, str):
        ga = CityObjectGenericAttrib(
            attrname=name, datatype=DT_STRING, strval=value,
            cityobject_id=cityobject_id,
        )
    elif isinstance(value, int) and not isinstance(value, bool):
        ga = CityObjectGenericAttrib(
            attrname=name, datatype=DT_INTEGER, intval=value,
            cityobject_id=cityobject_id,
        )
    elif isinstance(value, float):
        ga = CityObjectGenericAttrib(
            attrname=name, datatype=DT_REAL, realval=float(value),
            cityobject_id=cityobject_id, unit=unit,
        )
    else:
        ga = CityObjectGenericAttrib(
            attrname=name, datatype=DT_STRING, strval=str(value),
            cityobject_id=cityobject_id,
        )
    session.add(ga)


class CitydbMapperCalculator(BaseCalculator):
    """Maps CIM Wizard buildings to 3DCityDB tables and produces CityJSON."""

    # ------------------------------------------------------------------
    # POST helper -- write to 3DCityDB tables via ORM
    # ------------------------------------------------------------------

    def map_scenario_to_citydb(
        self,
        project_id: str,
        scenario_id: str,
        lod12_method: str = "by_footprint_height",
        force_lod12: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate LOD 1.2 geometry and persist every building in a
        project-scenario into the ``citydb`` schema.

        ``lod12_method`` selects the LOD 1.2 generation strategy:
            * ``"by_footprint_height"``        – basic single-zone
            * ``"by_footprint_height_floors"`` – per-storey zones
            * ``"by_mixed_use"``               – basement + commercial + residential

        Set ``force_lod12=True`` to regenerate LOD 1.2 even for buildings
        that already have it (e.g. to switch from basic to mixed-use).
        """
        session: Session = self.data_manager.db_session

        from app.models.vector import Building, BuildingProperties
        from app.calculators.building_geo_lod12_calculator import (
            BuildingGeoLod12Calculator,
        )

        citymodel = self._upsert_citymodel(session, scenario_id, project_id)

        rows = (
            session.query(BuildingProperties, Building)
            .join(Building, Building.building_id == BuildingProperties.building_id)
            .filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == scenario_id,
                    BuildingProperties.lod == 0,
                )
            )
            .all()
        )

        lod12_calc = BuildingGeoLod12Calculator(self.pipeline)
        lod12_generated = 0
        mapped = 0

        for props, building in rows:
            bid = building.building_id
            try:
                if force_lod12 or not building.building_surfaces_lod12:
                    lod12 = self._run_lod12(
                        lod12_calc, lod12_method, building, props,
                    )
                    if lod12:
                        building.building_surfaces_lod12 = {
                            "surfaces": lod12.get("surfaces"),
                            "storeys": lod12.get("storeys"),
                            "thermal_zones": lod12.get("thermal_zones"),
                            "metadata": lod12.get("metadata"),
                        }
                        lod12_generated += 1

                self._map_building(
                    session, building, props, citymodel,
                    refresh_surfaces=force_lod12,
                )
                mapped += 1
            except Exception as e:
                logger.warning("Failed to map building %s: %s", bid, e)
                session.rollback()

        session.commit()
        return {
            "citymodel_id": citymodel.id,
            "gmlid": scenario_id,
            "scenario_id": scenario_id,
            "lod12_method": lod12_method,
            "lod12_generated": lod12_generated,
            "mapped_buildings": mapped,
            "total_buildings": len(rows),
        }

    def delete_citymodel_from_citydb(self, citymodel_id: str) -> Dict[str, Any]:
        """Delete one mapped CityModel (scenario) and all mapper-created rows."""
        session: Session = self.data_manager.db_session

        citymodel = (
            session.query(CityModel)
            .filter(CityModel.gmlid == citymodel_id)
            .first()
        )
        if not citymodel:
            return {
                "citymodel_id": citymodel_id,
                "deleted": False,
                "message": "CityModel not found",
            }

        member_ids: Set[int] = {
            row[0]
            for row in session.query(CityObjectMember.cityobject_id)
            .filter(CityObjectMember.citymodel_id == citymodel.id)
            .all()
        }

        building_rows = (
            session.query(CityObject.id, CityObject.gmlid)
            .filter(
                CityObject.id.in_(member_ids),
                CityObject.objectclass_id == OC_BUILDING,
            )
            .all()
            if member_ids
            else []
        )
        building_ids: Set[int] = {row[0] for row in building_rows}
        building_gmlids: List[str] = [row[1] for row in building_rows]

        surface_ids: Set[int] = (
            {
                row[0]
                for row in session.query(ThematicSurface.id)
                .filter(ThematicSurface.building_id.in_(building_ids))
                .all()
            }
            if building_ids
            else set()
        )

        partition_ids: Set[int] = (
            {
                row[0]
                for row in session.query(Ng2BuildingPartition.id)
                .filter(Ng2BuildingPartition.building_id.in_(building_ids))
                .all()
            }
            if building_ids
            else set()
        )

        layered_gmlids = [f"{gmlid}-constr-wall" for gmlid in building_gmlids]
        layered_ids: Set[int] = (
            {
                row[0]
                for row in session.query(CityObject.id)
                .filter(CityObject.gmlid.in_(layered_gmlids))
                .all()
            }
            if layered_gmlids
            else set()
        )

        all_cityobject_ids: Set[int] = set()
        all_cityobject_ids.update(building_ids)
        all_cityobject_ids.update(surface_ids)
        all_cityobject_ids.update(partition_ids)
        all_cityobject_ids.update(layered_ids)

        try:
            if surface_ids:
                session.query(SurfaceGeometry).filter(
                    SurfaceGeometry.cityobject_id.in_(surface_ids)
                ).delete(synchronize_session=False)

            if all_cityobject_ids:
                session.query(CityObjectGenericAttrib).filter(
                    CityObjectGenericAttrib.cityobject_id.in_(all_cityobject_ids)
                ).delete(synchronize_session=False)

            if surface_ids:
                session.query(Ng2ThematicSurface).filter(
                    Ng2ThematicSurface.id.in_(surface_ids)
                ).delete(synchronize_session=False)
                session.query(ThematicSurface).filter(
                    ThematicSurface.id.in_(surface_ids)
                ).delete(synchronize_session=False)

            if partition_ids:
                session.query(Ng2BuildingPartition).filter(
                    Ng2BuildingPartition.id.in_(partition_ids)
                ).delete(synchronize_session=False)

            if layered_ids:
                session.query(Ng2LayeredConstruction).filter(
                    Ng2LayeredConstruction.id.in_(layered_ids)
                ).delete(synchronize_session=False)

            if building_ids:
                session.query(Ng2Building).filter(
                    Ng2Building.id.in_(building_ids)
                ).delete(synchronize_session=False)
                session.query(CityBuilding).filter(
                    CityBuilding.id.in_(building_ids)
                ).delete(synchronize_session=False)

            session.query(CityObjectMember).filter(
                CityObjectMember.citymodel_id == citymodel.id
            ).delete(synchronize_session=False)

            if all_cityobject_ids:
                session.query(CityObject).filter(
                    CityObject.id.in_(all_cityobject_ids)
                ).delete(synchronize_session=False)

            session.query(CityModel).filter(
                CityModel.id == citymodel.id
            ).delete(synchronize_session=False)
            session.commit()
        except Exception:
            session.rollback()
            raise

        return {
            "citymodel_id": citymodel_id,
            "deleted": True,
            "deleted_counts": {
                "buildings": len(building_ids),
                "surfaces": len(surface_ids),
                "thermal_partitions": len(partition_ids),
                "layered_constructions": len(layered_ids),
                "cityobjects": len(all_cityobject_ids),
            },
        }

    def map_post_sim_outputs_to_citydb(
        self,
        project_id: str,
        scenario_id: str,
        lod: int = 0,
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        """Map simulator outputs (outputs schema) to mapped CityDB buildings.

        Stores aggregated KPIs as ``cityobject_genericattrib`` on building
        CityObjects belonging to the CityModel identified by ``scenario_id``.
        """
        session: Session = self.data_manager.db_session
        from app.models.outputs import BuildingFrassinetto3, Battery, HeatingFrassinettoHp2

        citymodel = (
            session.query(CityModel)
            .filter(CityModel.gmlid == scenario_id)
            .first()
        )
        if not citymodel:
            return {
                "citymodel_id": scenario_id,
                "updated": False,
                "message": "CityModel not found. Run pre-sim mapper first.",
            }

        try:
            scenario_uuid = uuid.UUID(str(scenario_id))
        except ValueError:
            return {
                "citymodel_id": scenario_id,
                "updated": False,
                "message": "scenario_id is not a valid UUID for outputs schema",
            }

        building_rows = (
            session.query(CityObject.id, CityObject.gmlid)
            .join(CityObjectMember, CityObjectMember.cityobject_id == CityObject.id)
            .filter(
                CityObjectMember.citymodel_id == citymodel.id,
                CityObject.objectclass_id == OC_BUILDING,
            )
            .all()
        )

        bmap: Dict[str, int] = {}
        building_uuids: List[uuid.UUID] = []
        for co_id, gmlid in building_rows:
            if not gmlid:
                continue
            try:
                bu = uuid.UUID(str(gmlid))
            except ValueError:
                continue
            bmap[str(bu)] = co_id
            building_uuids.append(bu)

        if not building_uuids:
            return {
                "citymodel_id": scenario_id,
                "project_id": project_id,
                "updated": False,
                "message": "No UUID-based mapped buildings found in citymodel",
            }

        bf_rows = (
            session.query(
                BuildingFrassinetto3.building_id.label("bid"),
                func.count(BuildingFrassinetto3.time_step).label("samples"),
                func.avg(BuildingFrassinetto3.t_building).label("t_building_avg"),
                func.max(BuildingFrassinetto3.t_building).label("t_building_max"),
                func.avg(BuildingFrassinetto3.heating_load_target).label("heating_load_avg"),
                func.max(BuildingFrassinetto3.heating_load_target).label("heating_load_max"),
            )
            .filter(
                BuildingFrassinetto3.project_id == project_id,
                BuildingFrassinetto3.scenario_id == scenario_uuid,
                BuildingFrassinetto3.lod == lod,
                BuildingFrassinetto3.building_id.in_(building_uuids),
            )
            .group_by(BuildingFrassinetto3.building_id)
            .all()
        )
        bf_map = {str(r.bid): r for r in bf_rows}

        batt_rows = (
            session.query(
                Battery.building_id.label("bid"),
                func.count(Battery.time_step).label("samples"),
                func.avg(Battery.soc).label("soc_avg"),
                func.min(Battery.soc).label("soc_min"),
                func.max(Battery.soc).label("soc_max"),
                func.avg(Battery.p_net_batt).label("p_net_batt_avg"),
                func.max(Battery.p_net_batt).label("p_net_batt_max"),
            )
            .filter(
                Battery.project_id == project_id,
                Battery.scenario_id == scenario_uuid,
                Battery.lod == lod,
                Battery.building_id.in_(building_uuids),
            )
            .group_by(Battery.building_id)
            .all()
        )
        batt_map = {str(r.bid): r for r in batt_rows}

        hp_rows = (
            session.query(
                HeatingFrassinettoHp2.building_id.label("bid"),
                func.count(HeatingFrassinettoHp2.time_step).label("samples"),
                func.avg(HeatingFrassinettoHp2.cop).label("cop_avg"),
                func.max(HeatingFrassinettoHp2.cop).label("cop_max"),
                func.avg(HeatingFrassinettoHp2.en_el).label("en_el_avg"),
                func.avg(HeatingFrassinettoHp2.en_auxel).label("en_auxel_avg"),
                func.avg(HeatingFrassinettoHp2.qt_return).label("qt_return_avg"),
            )
            .filter(
                HeatingFrassinettoHp2.project_id == project_id,
                HeatingFrassinettoHp2.scenario_id == scenario_uuid,
                HeatingFrassinettoHp2.lod == lod,
                HeatingFrassinettoHp2.building_id.in_(building_uuids),
            )
            .group_by(HeatingFrassinettoHp2.building_id)
            .all()
        )
        hp_map = {str(r.bid): r for r in hp_rows}

        if not bf_map and not batt_map and not hp_map:
            return {
                "citymodel_id": scenario_id,
                "project_id": project_id,
                "lod": lod,
                "updated": False,
                "message": "No simulation outputs found for project/scenario/lod",
                "mapped_buildings": len(building_uuids),
            }

        updated_buildings = 0
        for b_uuid in bmap:
            co_id = bmap[b_uuid]
            bf = bf_map.get(b_uuid)
            batt = batt_map.get(b_uuid)
            hp = hp_map.get(b_uuid)
            if not bf and not batt and not hp:
                continue

            if overwrite:
                session.query(CityObjectGenericAttrib).filter(
                    CityObjectGenericAttrib.cityobject_id == co_id,
                    CityObjectGenericAttrib.attrname.like("postSim_%"),
                ).delete(synchronize_session=False)

            _add_generic_attrib(session, co_id, "postSim_projectId", project_id)
            _add_generic_attrib(session, co_id, "postSim_scenarioId", scenario_id)
            _add_generic_attrib(session, co_id, "postSim_lod", int(lod))

            if bf:
                _add_generic_attrib(session, co_id, "postSim_building_samples", int(bf.samples))
                _add_generic_attrib(session, co_id, "postSim_tBuilding_avg_C", _safe_float(bf.t_building_avg), unit="C")
                _add_generic_attrib(session, co_id, "postSim_tBuilding_max_C", _safe_float(bf.t_building_max), unit="C")
                _add_generic_attrib(session, co_id, "postSim_heatingLoadTarget_avg_W", _safe_float(bf.heating_load_avg), unit="W")
                _add_generic_attrib(session, co_id, "postSim_heatingLoadTarget_max_W", _safe_float(bf.heating_load_max), unit="W")

            if batt:
                _add_generic_attrib(session, co_id, "postSim_battery_samples", int(batt.samples))
                _add_generic_attrib(session, co_id, "postSim_batterySOC_avg", _safe_float(batt.soc_avg))
                _add_generic_attrib(session, co_id, "postSim_batterySOC_min", _safe_float(batt.soc_min))
                _add_generic_attrib(session, co_id, "postSim_batterySOC_max", _safe_float(batt.soc_max))
                _add_generic_attrib(session, co_id, "postSim_batteryPnet_avg_W", _safe_float(batt.p_net_batt_avg), unit="W")
                _add_generic_attrib(session, co_id, "postSim_batteryPnet_max_W", _safe_float(batt.p_net_batt_max), unit="W")

            if hp:
                _add_generic_attrib(session, co_id, "postSim_hp_samples", int(hp.samples))
                _add_generic_attrib(session, co_id, "postSim_hpCOP_avg", _safe_float(hp.cop_avg))
                _add_generic_attrib(session, co_id, "postSim_hpCOP_max", _safe_float(hp.cop_max))
                _add_generic_attrib(session, co_id, "postSim_hpEnEl_avg_W", _safe_float(hp.en_el_avg), unit="W")
                _add_generic_attrib(session, co_id, "postSim_hpEnAuxEl_avg_W", _safe_float(hp.en_auxel_avg), unit="W")
                _add_generic_attrib(session, co_id, "postSim_hpQtReturn_avg_W", _safe_float(hp.qt_return_avg), unit="W")

            updated_buildings += 1

        session.commit()
        return {
            "citymodel_id": scenario_id,
            "project_id": project_id,
            "lod": lod,
            "updated": True,
            "overwrite": overwrite,
            "mapped_buildings": len(building_uuids),
            "updated_buildings": updated_buildings,
            "outputs_coverage": {
                "building_frassinetto3": len(bf_map),
                "battery": len(batt_map),
                "heating_frassinetto_hp2": len(hp_map),
            },
        }

    @staticmethod
    def _run_lod12(lod12_calc, method: str, building, props) -> Optional[dict]:
        """Invoke the right LOD 1.2 generation method for a single building.

        Always returns a dict with top-level keys ``surfaces``,
        ``storeys`` (may be ``None``), ``thermal_zones`` (may be ``None``),
        and ``metadata``, or ``None`` on failure.
        """
        geom = None
        if building.building_geometry:
            from geoalchemy2.shape import to_shape
            from shapely.geometry import mapping
            try:
                geom = mapping(to_shape(building.building_geometry))
            except Exception:
                geom = None

        if not geom:
            return None

        height = props.height or 12.0
        n_floors = int(props.number_of_floors) if props.number_of_floors else max(1, round(height / 3.0))
        z_offset = float(building.z_value) if building.z_value is not None else 0.0

        if method == "by_mixed_use":
            n_families = int(props.n_family) if props.n_family else max(1, n_floors - 1) * 2
            return lod12_calc.generate_lod12_mixed_use(
                geom, height, n_floors, n_families, z_offset=z_offset,
            )
        if method == "by_footprint_height_floors":
            return lod12_calc.generate_lod12_with_floors(geom, height, n_floors, z_offset=z_offset)

        raw = lod12_calc._generate_lod12_surfaces(geom, height, z_offset=z_offset)
        if raw is None:
            return None
        return {
            "surfaces": raw,
            "storeys": None,
            "thermal_zones": None,
            "metadata": {
                "building_height": height,
                "z_offset": z_offset,
                "generation_method": "footprint_height",
            },
        }

    # ---- citymodel ----

    def _upsert_citymodel(
        self, session: Session, scenario_id: str, project_id: str
    ) -> CityModel:
        existing = (
            session.query(CityModel)
            .filter(CityModel.gmlid == scenario_id)
            .first()
        )
        if existing:
            return existing

        cm = CityModel(
            gmlid=scenario_id,
            name=f"CIM-Scenario-{scenario_id[:8]}",
            description=f"project {project_id}",
        )
        session.add(cm)
        session.flush()
        return cm

    # ---- single building ----

    def _map_building(
        self,
        session,
        building,
        props,
        citymodel: CityModel,
        refresh_surfaces: bool = False,
    ):
        bid = str(building.building_id)

        existing = (
            session.query(CityObject)
            .filter(
                and_(
                    CityObject.gmlid == bid,
                    CityObject.objectclass_id == OC_BUILDING,
                )
            )
            .first()
        )
        if existing:
            # Building already in citydb — skip insert but still refresh surfaces
            # when force_lod12 regenerated building_surfaces_lod12 in vector tables.
            lod12 = building.building_surfaces_lod12
            if refresh_surfaces and lod12:
                u_vals = TABULA_U_VALUES.get(props.const_tabula or "", {})
                self._delete_building_surfaces(session, existing.id)
                self._delete_building_energy_attribs(session, existing.id)
                self._map_surfaces(
                    session, existing.id, lod12.get("surfaces") or {}, u_vals,
                )
                thermal_zones = lod12.get("thermal_zones")
                if thermal_zones:
                    self._store_multi_thermal_zone_attrs(
                        session, existing.id, thermal_zones, props,
                    )
                else:
                    self._store_thermal_zone_attrs(session, existing.id, props)
                self._apply_building_energy_mapping(
                    session, existing.id, bid, building, props, lod12, u_vals,
                )
                session.flush()
            return existing

        co = CityObject(
            objectclass_id=OC_BUILDING,
            gmlid=bid,
            name=building.building_name or f"BUI-{bid[:8]}",
        )
        session.add(co)
        session.flush()

        cb = CityBuilding(
            id=co.id,
            objectclass_id=OC_BUILDING,
            measured_height=props.height,
            measured_height_unit="m" if props.height else None,
            storeys_above_ground=int(props.number_of_floors) if props.number_of_floors else None,
        )
        session.add(cb)

        member = CityObjectMember(
            citymodel_id=citymodel.id,
            cityobject_id=co.id,
        )
        session.add(member)

        lod12 = building.building_surfaces_lod12
        if lod12:
            u_vals = TABULA_U_VALUES.get(props.const_tabula or "", {})
            self._map_surfaces(session, co.id, lod12.get("surfaces") or {}, u_vals)

        thermal_zones = (lod12 or {}).get("thermal_zones")
        if thermal_zones:
            self._store_multi_thermal_zone_attrs(session, co.id, thermal_zones, props)
        else:
            self._store_thermal_zone_attrs(session, co.id, props)

        self._apply_building_energy_mapping(
            session, co.id, bid, building, props, lod12, u_vals,
        )

        session.flush()
        return co

    # ---- LOD 1.2 surfaces ----

    def _delete_building_surfaces(self, session: Session, building_co_id: int):
        """Remove all thematic surfaces and their PostGIS geometry for a building."""
        ts_rows = (
            session.query(ThematicSurface.id)
            .filter(ThematicSurface.building_id == building_co_id)
            .all()
        )
        ts_ids = [row[0] for row in ts_rows]
        if not ts_ids:
            return

        session.query(SurfaceGeometry).filter(
            SurfaceGeometry.cityobject_id.in_(ts_ids)
        ).delete(synchronize_session=False)

        session.query(CityObjectGenericAttrib).filter(
            CityObjectGenericAttrib.cityobject_id.in_(ts_ids)
        ).delete(synchronize_session=False)

        session.query(ThematicSurface).filter(
            ThematicSurface.building_id == building_co_id
        ).delete(synchronize_session=False)

        session.query(CityObject).filter(
            CityObject.id.in_(ts_ids),
            CityObject.objectclass_id.in_([
                OC_CEILING_SURFACE,
                OC_FLOOR_SURFACE,
                OC_ROOF_SURFACE,
                OC_WALL_SURFACE,
                OC_GROUND_SURFACE,
            ]),
        ).delete(synchronize_session=False)

    def _delete_building_energy_attribs(self, session: Session, building_co_id: int):
        """Clear CIM / thermal generic attributes before re-insert."""
        session.query(CityObjectGenericAttrib).filter(
            CityObjectGenericAttrib.cityobject_id == building_co_id,
            or_(
                CityObjectGenericAttrib.attrname.like("thermalZone%"),
                CityObjectGenericAttrib.attrname.like("tz:%"),
                CityObjectGenericAttrib.attrname.like("energySystem_%"),
                CityObjectGenericAttrib.attrname.like("cim_%"),
            ),
        ).delete(synchronize_session=False)

    def _delete_ng2_partitions(self, session: Session, building_co_id: int):
        part_ids = [
            row[0]
            for row in session.query(Ng2BuildingPartition.id)
            .filter(Ng2BuildingPartition.building_id == building_co_id)
            .all()
        ]
        if not part_ids:
            return
        session.query(Ng2BuildingPartition).filter(
            Ng2BuildingPartition.id.in_(part_ids)
        ).delete(synchronize_session=False)
        session.query(CityObjectGenericAttrib).filter(
            CityObjectGenericAttrib.cityobject_id.in_(part_ids)
        ).delete(synchronize_session=False)
        session.query(CityObject).filter(
            CityObject.id.in_(part_ids)
        ).delete(synchronize_session=False)

    def _energy_objectclass_id(self, session: Session, classname_part: str) -> Optional[int]:
        from sqlalchemy import text

        row = session.execute(
            text(
                "SELECT id FROM citydb.objectclass "
                "WHERE classname ILIKE :pat ORDER BY id LIMIT 1"
            ),
            {"pat": f"%{classname_part}%"},
        ).first()
        return int(row[0]) if row else None

    def _upsert_ng2_building(self, session: Session, building_co_id: int, props, building):
        row = session.query(Ng2Building).filter(Ng2Building.id == building_co_id).first()
        if row is None:
            row = Ng2Building(id=building_co_id)
            session.add(row)

        row.type = props.type or row.type
        row.constr_weight = _constr_weight_from_props(props) or row.constr_weight
        row.is_protected = 0

    def _store_building_cim_attribs(self, session: Session, co_id: int, props, building):
        """CIM Wizard properties as queryable generic attributes."""
        _add_generic_attrib(session, co_id, "cim_buildingType", props.type)
        _add_generic_attrib(session, co_id, "cim_constYear", props.const_year)
        _add_generic_attrib(session, co_id, "cim_constTabula", props.const_tabula)
        _add_generic_attrib(session, co_id, "cim_constPeriodCensus", props.const_period_census)
        _add_generic_attrib(session, co_id, "cim_nPeople", props.n_people)
        _add_generic_attrib(session, co_id, "cim_nFamilies", props.n_family)
        _add_generic_attrib(session, co_id, "cim_geometrySource", building.building_geometry_source)
        if building.z_value is not None:
            _add_generic_attrib(session, co_id, "cim_terrainHeight", float(building.z_value), unit="m")
        if props.area is not None:
            _add_generic_attrib(session, co_id, "cim_footprintArea_m2", float(props.area), unit="m^2")
        if props.volume is not None:
            _add_generic_attrib(session, co_id, "cim_volume_m3", float(props.volume), unit="m^3")

    def _upsert_ng2_thematic_surface(
        self, session: Session, ts_co_id: int, surf_props: Optional[dict],
    ):
        if not surf_props:
            return
        row = session.query(Ng2ThematicSurface).filter(Ng2ThematicSurface.id == ts_co_id).first()
        if row is None:
            row = Ng2ThematicSurface(id=ts_co_id)
            session.add(row)

        area = surf_props.get("area_m2")
        if area is not None:
            row.total_surf_area = float(area)
            row.total_surf_area_uom = "m^2"
            row.opaque_surf_area = float(area)
            row.opaque_surf_area_uom = "m^2"
        az = surf_props.get("azimuth_degrees")
        if az is not None:
            row.azimuth = float(az)
            row.azimuth_uom = "degrees"
        incl = surf_props.get("inclination_degrees")
        if incl is not None:
            row.inclination = float(incl)
            row.inclination_uom = "degrees"
        elif surf_props.get("surface_type") == "RoofSurface":
            row.inclination = 0.0
            row.inclination_uom = "degrees"

    def _store_surface_cim_attribs(
        self, session: Session, ts_co_id: int, surf_props: Optional[dict],
    ):
        if not surf_props:
            return
        _add_generic_attrib(
            session, ts_co_id, "cim_orientation",
            surf_props.get("orientation"),
        )
        _add_generic_attrib(
            session, ts_co_id, "cim_azimuth_deg",
            surf_props.get("azimuth_degrees"), unit="degrees",
        )
        _add_generic_attrib(
            session, ts_co_id, "cim_wallLength_m",
            surf_props.get("length_m"), unit="m",
        )
        _add_generic_attrib(
            session, ts_co_id, "cim_surfaceArea_m2",
            surf_props.get("area_m2"), unit="m^2",
        )

    def _upsert_ng2_layered_construction(
        self, session: Session, building_co_id: int, bid: str, tabula: str, u_vals: dict,
    ):
        """One TABULA-based opaque construction per building (wall U-value).

        ng2_layered_construction.id must reference citydb.cityobject (Energy ADE FK).
        """
        wall_u = u_vals.get("wall")
        if wall_u is None:
            return
        lc_oc = self._energy_objectclass_id(session, "LayeredConstruction")
        if lc_oc is None:
            return

        gmlid = f"{bid}-constr-wall"
        lc_co = session.query(CityObject).filter(CityObject.gmlid == gmlid).first()
        if lc_co is None:
            lc_co = CityObject(
                objectclass_id=lc_oc,
                gmlid=gmlid,
                name=f"TABULA-{tabula or 'wall'}-wall",
            )
            session.add(lc_co)
            session.flush()

        row = session.query(Ng2LayeredConstruction).filter(
            Ng2LayeredConstruction.id == lc_co.id
        ).first()
        if row is None:
            row = Ng2LayeredConstruction(id=lc_co.id, objectclass_id=lc_oc)
            session.add(row)
        elif row.objectclass_id is None:
            row.objectclass_id = lc_oc
        row.u_value = float(wall_u)
        row.u_value_uom = "W/(m^2K)"
        row.library_code = tabula or None

    def _map_ng2_thermal_partitions(
        self, session: Session, building_co_id: int, bid: str,
        thermal_zones: List[dict], props,
    ):
        """Persist each thermal zone as ng2_building_partition + cityobject."""
        tz_oc = self._energy_objectclass_id(session, "ThermalZone")
        if tz_oc is None:
            return

        self._delete_ng2_partitions(session, building_co_id)

        for tz in thermal_zones:
            zid = tz.get("zone_id", "tz-unknown")
            gmlid = f"{bid}-{zid}"
            existing = session.query(CityObject).filter(CityObject.gmlid == gmlid).first()
            if existing:
                tz_co = existing
            else:
                tz_co = CityObject(objectclass_id=tz_oc, gmlid=gmlid, name=zid)
                session.add(tz_co)
                session.flush()

            part = session.query(Ng2BuildingPartition).filter(
                Ng2BuildingPartition.id == tz_co.id
            ).first()
            if part is None:
                part = Ng2BuildingPartition(id=tz_co.id, objectclass_id=tz_oc)
                session.add(part)

            part.building_id = building_co_id
            part.type = tz.get("usage")
            part.is_heated = 1 if tz.get("is_heated", True) else 0
            part.is_cooled = 1 if tz.get("is_cooled", False) else 0
            if tz.get("volume_m3") is not None:
                part.heat_capacity = float(tz["volume_m3"])
            part.infiltration_rate_uom = "1/h"

    def _apply_building_energy_mapping(
        self,
        session: Session,
        building_co_id: int,
        bid: str,
        building,
        props,
        lod12: Optional[dict],
        u_vals: dict,
    ):
        """Write ng2_* tables and extended generic attributes for one building."""
        self._upsert_ng2_building(session, building_co_id, props, building)
        self._store_building_cim_attribs(session, building_co_id, props, building)
        self._upsert_ng2_layered_construction(
            session, building_co_id, bid, props.const_tabula or "", u_vals,
        )

        thermal_zones = (lod12 or {}).get("thermal_zones")
        if thermal_zones:
            self._map_ng2_thermal_partitions(
                session, building_co_id, bid, thermal_zones, props,
            )

    def _map_surfaces(
        self, session, building_co_id: int, surfaces: dict, u_vals: dict
    ):
        def _insert_one(geojson_geom, oc_id, u_value, surf_label, surf_props=None):
            if not geojson_geom or not geojson_geom.get("coordinates"):
                return

            ewkt = _polygon_geojson_to_ewkt(geojson_geom, srid=4326)
            if ewkt is None:
                return

            ts_co = CityObject(
                objectclass_id=oc_id,
                gmlid=f"{building_co_id}-{surf_label}",
                name=f"{surf_label}-{building_co_id}",
            )
            session.add(ts_co)
            session.flush()

            sg_root = SurfaceGeometry(
                gmlid=f"ms-{ts_co.id}",
                is_solid=0,
                is_composite=0,
                cityobject_id=ts_co.id,
            )
            session.add(sg_root)
            session.flush()
            sg_root.root_id = sg_root.id

            sg_poly = SurfaceGeometry(
                gmlid=f"poly-{ts_co.id}",
                parent_id=sg_root.id,
                root_id=sg_root.id,
                geometry=ST_Force3D(ST_GeomFromEWKT(ewkt)),
                cityobject_id=ts_co.id,
            )
            session.add(sg_poly)

            ts = ThematicSurface(
                id=ts_co.id,
                objectclass_id=oc_id,
                building_id=building_co_id,
                lod2_multi_surface_id=sg_root.id,
            )
            session.add(ts)
            session.flush()

            if u_value is not None:
                session.add(
                    CityObjectGenericAttrib(
                        attrname="u_value_w_m2k",
                        datatype=DT_REAL,
                        realval=u_value,
                        cityobject_id=ts_co.id,
                    )
                )

            props_dict = surf_props or {}
            self._upsert_ng2_thematic_surface(session, ts_co.id, props_dict)
            self._store_surface_cim_attribs(session, ts_co.id, props_dict)

        for wall in surfaces.get("wall_surfaces", []):
            _insert_one(
                wall.get("geometry"),
                OC_WALL_SURFACE,
                u_vals.get("wall"),
                wall.get("surface_id", "wall"),
                wall.get("properties"),
            )

        roof = surfaces.get("roof_surface")
        if roof:
            _insert_one(
                roof.get("geometry"),
                OC_ROOF_SURFACE,
                u_vals.get("roof"),
                roof.get("surface_id", "roof"),
                roof.get("properties"),
            )

        ground = surfaces.get("ground_surface")
        if ground:
            _insert_one(
                ground.get("geometry"),
                OC_GROUND_SURFACE,
                u_vals.get("ground"),
                ground.get("surface_id", "ground"),
                ground.get("properties"),
            )

        for floor_surf in surfaces.get("floor_surfaces", []):
            _insert_one(
                floor_surf.get("geometry"),
                OC_FLOOR_SURFACE,
                None,
                floor_surf.get("surface_id", "floor"),
                floor_surf.get("properties"),
            )

    # ---- generic attributes for thermal zone data (legacy single zone) ----

    def _store_thermal_zone_attrs(self, session, co_id: int, props):
        entries: List[Tuple[str, int, str, Any]] = []

        if props.volume is not None:
            entries.append(("thermalZone_volume_m3", DT_REAL, "realval", props.volume))
        if props.area is not None:
            entries.append(("thermalZone_floorArea_m2", DT_REAL, "realval", props.area))
        if props.number_of_floors is not None:
            entries.append(("thermalZone_numberOfFloors", DT_REAL, "realval", props.number_of_floors))
        if props.envelope_efficiency:
            entries.append(("energySystem_envelopeEfficiency", DT_STRING, "strval", props.envelope_efficiency))
        if props.fmu_file:
            entries.append(("energySystem_fmuFile", DT_STRING, "strval", props.fmu_file))

        for name, dtype, col, value in entries:
            ga = CityObjectGenericAttrib(
                attrname=name,
                datatype=dtype,
                cityobject_id=co_id,
            )
            setattr(ga, col, value)
            session.add(ga)

    # ---- generic attributes for multiple thermal zones ----

    def _store_multi_thermal_zone_attrs(
        self, session, co_id: int, thermal_zones: List[dict], props,
    ):
        """Persist per-zone metadata as generic attributes on the building.

        Each zone attribute is prefixed with ``tz:<zone_id>:``, making the
        zones discoverable and queryable from the generic-attribute table.
        Global energy-system attributes are stored without a prefix.
        """
        session.add(CityObjectGenericAttrib(
            attrname="thermalZone_count",
            datatype=DT_INTEGER, intval=len(thermal_zones),
            cityobject_id=co_id,
        ))

        for tz in thermal_zones:
            zid = tz.get("zone_id", "tz-unknown")
            prefix = f"tz:{zid}"

            zone_entries: List[Tuple[str, int, str, Any]] = [
                (f"{prefix}:usage", DT_STRING, "strval", tz.get("usage")),
                (f"{prefix}:volume_m3", DT_REAL, "realval", tz.get("volume_m3")),
                (f"{prefix}:floor_area_m2", DT_REAL, "realval", tz.get("floor_area_m2")),
                (f"{prefix}:is_heated", DT_STRING, "strval", str(tz.get("is_heated", True))),
                (f"{prefix}:is_cooled", DT_STRING, "strval", str(tz.get("is_cooled", False))),
                (f"{prefix}:storey_index", DT_INTEGER, "intval", tz.get("storey_index")),
            ]
            if tz.get("apartment_index") is not None:
                zone_entries.append(
                    (f"{prefix}:apartment_index", DT_INTEGER, "intval", tz["apartment_index"])
                )

            for name, dtype, col, value in zone_entries:
                if value is None:
                    continue
                ga = CityObjectGenericAttrib(
                    attrname=name, datatype=dtype, cityobject_id=co_id,
                )
                setattr(ga, col, value)
                session.add(ga)

        if props.envelope_efficiency:
            session.add(CityObjectGenericAttrib(
                attrname="energySystem_envelopeEfficiency",
                datatype=DT_STRING, strval=props.envelope_efficiency,
                cityobject_id=co_id,
            ))
        if props.fmu_file:
            session.add(CityObjectGenericAttrib(
                attrname="energySystem_fmuFile",
                datatype=DT_STRING, strval=props.fmu_file,
                cityobject_id=co_id,
            ))

    # ------------------------------------------------------------------
    # GET helper -- generate CityJSON v1.1 from CIM Wizard data
    # ------------------------------------------------------------------

    def generate_cityjson(
        self, project_id: str, scenario_id: str
    ) -> Dict[str, Any]:
        """
        Build a CityJSON v1.1 document from CIM Wizard tables.

        Each building with LOD 1.2 data becomes a ``Building`` CityObject
        with a ``Solid`` geometry, semantic surfaces (Wall / Roof / Ground)
        carrying TABULA U-values, and a child ``+Energy-ThermalZone`` object.
        """
        session: Session = self.data_manager.db_session

        from app.models.vector import Building, BuildingProperties

        rows = (
            session.query(BuildingProperties, Building)
            .join(Building, Building.building_id == BuildingProperties.building_id)
            .filter(
                and_(
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == scenario_id,
                    BuildingProperties.lod == 0,
                )
            )
            .all()
        )

        builder = _CityJSONBuilder(use_utm_for_display=True)

        for props, building in rows:
            bid = str(building.building_id)
            lod12 = building.building_surfaces_lod12 or {}
            surfaces = lod12.get("surfaces", {})
            thermal_zones = lod12.get("thermal_zones")
            u_vals = TABULA_U_VALUES.get(props.const_tabula or "", {})

            building_attrs: Dict[str, Any] = {}
            if props.height is not None:
                building_attrs["measuredHeight"] = round(props.height, 2)
            if props.area is not None:
                building_attrs["footprintArea"] = round(props.area, 2)
                building_attrs["+energy-floorArea"] = [
                    {"energy-type": "grossFloorArea", "energy-value": round(props.area, 2)}
                ]
            if props.volume is not None:
                building_attrs["volume"] = round(props.volume, 2)
                building_attrs["+energy-volume"] = [
                    {"energy-type": "grossVolume", "energy-value": round(props.volume, 2)}
                ]
            if props.const_year is not None:
                building_attrs["yearOfConstruction"] = props.const_year
            if props.type:
                building_attrs["+energy-buildingType"] = props.type
            if props.const_tabula:
                building_attrs["constTabula"] = props.const_tabula
                cw = TABULA_CONSTR_WEIGHT.get(props.const_tabula or "")
                if cw:
                    building_attrs["+energy-constructionWeight"] = cw
            if props.number_of_floors is not None:
                building_attrs["storeysAboveGround"] = int(props.number_of_floors)
            if building.building_name:
                building_attrs["name"] = building.building_name
            if building.z_value is not None:
                building_attrs["terrainHeight"] = round(building.z_value, 2)
            if props.envelope_efficiency:
                building_attrs["envelopeEfficiency"] = props.envelope_efficiency
            if props.fmu_file:
                building_attrs["energySystemModel"] = props.fmu_file
            if props.n_people is not None:
                building_attrs["nPeople"] = int(props.n_people)
            if props.n_family is not None:
                building_attrs["nFamilies"] = int(props.n_family)

            builder.add_building(
                bid, building_attrs, surfaces, u_vals,
                thermal_zones=thermal_zones,
            )
            if thermal_zones:
                builder.add_thermal_zones(bid, thermal_zones)
            else:
                builder.add_thermal_zone(bid, props)

        return builder.build(scenario_id)

    # ------------------------------------------------------------------
    # GET helper -- generate CityJSON v1.1 from 3DCityDB tables
    # ------------------------------------------------------------------

    def generate_cityjson_from_citydb(
        self, citymodel_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Build a CityJSON v1.1 document by reading directly from the
        ``citydb`` schema tables.  ``citymodel_id`` is the CityModel.gmlid
        (equal to the scenario_id used during mapping).

        Returns ``None`` when no CityModel with that gmlid exists.
        """
        session: Session = self.data_manager.db_session

        citymodel = (
            session.query(CityModel)
            .filter(CityModel.gmlid == citymodel_id)
            .first()
        )
        if not citymodel:
            return None

        building_rows = (
            session.query(CityObject, CityBuilding)
            .join(CityObjectMember, CityObject.id == CityObjectMember.cityobject_id)
            .join(CityBuilding, CityObject.id == CityBuilding.id)
            .filter(
                CityObjectMember.citymodel_id == citymodel.id,
                CityObject.objectclass_id == OC_BUILDING,
            )
            .all()
        )

        # UTM zone hint from surface-geometry centroid (building.envelope is
        # often NULL in citydb).  Actual lon/lat→metre conversion happens in
        # _CityJSONBuilder via pyproj on the first geographic vertex.
        target_srid = 4326
        centroid_row = (
            session.query(
                func.ST_X(
                    func.ST_Centroid(
                        func.ST_Collect(SurfaceGeometry.geometry)
                    )
                ).label("lon"),
                func.ST_Y(
                    func.ST_Centroid(
                        func.ST_Collect(SurfaceGeometry.geometry)
                    )
                ).label("lat"),
            )
            .join(ThematicSurface, ThematicSurface.id == SurfaceGeometry.cityobject_id)
            .join(CityObjectMember, CityObjectMember.cityobject_id == ThematicSurface.building_id)
            .filter(
                CityObjectMember.citymodel_id == citymodel.id,
                SurfaceGeometry.geometry.isnot(None),
            )
            .first()
        )
        if centroid_row and centroid_row.lon is not None and centroid_row.lat is not None:
            target_srid = _utm_srid_for(float(centroid_row.lon), float(centroid_row.lat))

        builder = _CityJSONBuilder(target_srid=target_srid, use_utm_for_display=True)

        for co, cb in building_rows:
            bid = co.gmlid

            gen_attrs = (
                session.query(CityObjectGenericAttrib)
                .filter(CityObjectGenericAttrib.cityobject_id == co.id)
                .all()
            )

            attrs: Dict[str, Any] = {}
            if co.name:
                attrs["name"] = co.name
            if cb.measured_height is not None:
                attrs["measuredHeight"] = round(cb.measured_height, 2)
            if cb.storeys_above_ground is not None:
                attrs["storeysAboveGround"] = int(cb.storeys_above_ground)

            ga_map = {ga.attrname: _ga_typed_value(ga) for ga in gen_attrs}
            ng2_b = session.query(Ng2Building).filter(Ng2Building.id == co.id).first()
            attrs = _enrich_building_attrs_from_db(attrs, ga_map, ng2_b)

            tz_count = ga_map.get("thermalZone_count")
            multi_zone = tz_count is not None and int(tz_count) > 1

            reconstructed_zones: List[dict] = []
            if multi_zone:
                reconstructed_zones = _reconstruct_zones_from_ga(ga_map)
            else:
                tz_attrs: Dict[str, Any] = {
                    "energy-isCooled": False,
                    "energy-isHeated": True,
                }
                for ga in gen_attrs:
                    val = _ga_typed_value(ga)
                    if val is None:
                        continue
                    if ga.attrname == "thermalZone_volume_m3":
                        tz_attrs["energy-volume"] = [
                            {"energy-type": "grossVolume", "energy-value": round(float(val), 2)}
                        ]
                        attrs["volume"] = round(float(val), 2)
                    elif ga.attrname == "thermalZone_floorArea_m2":
                        tz_attrs["energy-floorArea"] = [
                            {"energy-type": "grossFloorArea", "energy-value": round(float(val), 2)}
                        ]
                        attrs["footprintArea"] = round(float(val), 2)
                    elif ga.attrname == "thermalZone_numberOfFloors":
                        attrs["storeysAboveGround"] = int(val)
                    elif ga.attrname == "energySystem_envelopeEfficiency":
                        attrs["envelopeEfficiency"] = val
                    elif ga.attrname == "energySystem_fmuFile":
                        attrs["energySystemModel"] = val

            geom_expr = func.ST_AsEWKT(ST_Force3D(SurfaceGeometry.geometry))

            surface_rows = (
                session.query(
                    ThematicSurface,
                    CityObject,
                    geom_expr.label("ewkt"),
                )
                .join(CityObject, ThematicSurface.id == CityObject.id)
                .outerjoin(
                    SurfaceGeometry,
                    and_(
                        SurfaceGeometry.cityobject_id == ThematicSurface.id,
                        SurfaceGeometry.geometry.isnot(None),
                    ),
                )
                .filter(ThematicSurface.building_id == co.id)
                .all()
            )

            ng2_surfaces = {
                row.id: row
                for row in session.query(Ng2ThematicSurface)
                .join(ThematicSurface, Ng2ThematicSurface.id == ThematicSurface.id)
                .filter(ThematicSurface.building_id == co.id)
                .all()
            }

            boundaries: List[List[List[int]]] = []
            sem_surfaces: List[dict] = []
            sem_values: List[Optional[int]] = []

            for ts, ts_co, ewkt_str in surface_rows:
                if not ewkt_str:
                    continue

                rings = _parse_polygon_ewkt(ewkt_str)
                if not rings:
                    continue

                sem_type = _OC_SEM_TYPE.get(ts.objectclass_id, "GenericSurface")

                surf_ga = {
                    ga.attrname: _ga_typed_value(ga)
                    for ga in session.query(CityObjectGenericAttrib)
                    .filter(CityObjectGenericAttrib.cityobject_id == ts.id)
                    .all()
                }

                u_attr = surf_ga.get("u_value_w_m2k")

                sem_entry: Dict[str, Any] = {"type": sem_type}
                if u_attr is not None:
                    sem_entry["u_value"] = float(u_attr)

                ng2_ts = ng2_surfaces.get(ts.id)
                if ng2_ts:
                    if ng2_ts.azimuth is not None:
                        sem_entry["azimuth"] = float(ng2_ts.azimuth)
                    if ng2_ts.inclination is not None:
                        sem_entry["inclination"] = float(ng2_ts.inclination)
                    if ng2_ts.total_surf_area is not None:
                        sem_entry["area"] = float(ng2_ts.total_surf_area)
                if surf_ga.get("cim_orientation"):
                    sem_entry["orientation"] = surf_ga["cim_orientation"]

                for ring in rings:
                    indices = builder._ring_to_indices(ring)
                    boundaries.append([indices])
                    sem_surfaces.append(sem_entry)
                    sem_values.append(len(sem_surfaces) - 1)

            geometry: list = []
            if boundaries:
                geom_entry: Dict[str, Any] = {
                    "type": "Solid",
                    "lod": "1.2",
                    "boundaries": [boundaries],
                }
                if sem_surfaces:
                    geom_entry["semantics"] = {
                        "surfaces": sem_surfaces,
                        "values": [sem_values],
                    }
                geometry.append(geom_entry)

            clean_attrs = {k: v for k, v in attrs.items() if v is not None}

            if multi_zone and reconstructed_zones:
                children = [f"{bid}-{rz['zone_id']}" for rz in reconstructed_zones]
                builder._city_objects[bid] = {
                    "type": "Building",
                    "attributes": clean_attrs,
                    "geometry": geometry,
                    "children": children,
                }
                builder.add_thermal_zones(bid, reconstructed_zones)
            else:
                builder._city_objects[bid] = {
                    "type": "Building",
                    "attributes": clean_attrs,
                    "geometry": geometry,
                    "children": [f"{bid}-z1"],
                }
                builder._city_objects[f"{bid}-z1"] = {
                    "type": "+Energy-ThermalZone",
                    "attributes": {
                        k: v for k, v in tz_attrs.items()
                        if v is not None and v != []
                    },
                    "parents": [bid],
                }

        return builder.build(citymodel_id)


# ── Helper utilities ─────────────────────────────────────────────────


def _parse_polygon_ewkt(ewkt: str) -> List[List[List[float]]]:
    """Parse a PostGIS EWKT polygon string into rings of [x, y, z] points.

    Accepts ``SRID=...;POLYGON Z((...))``, ``POLYGON Z((...))`` or 2D forms.
    Returns ``[]`` for non-polygon types or malformed input.
    """
    if not ewkt:
        return []

    body = ewkt.split(";", 1)[1] if ";" in ewkt else ewkt
    body = body.strip()
    upper = body.upper()
    if upper.startswith("POLYGON Z"):
        body = body[len("POLYGON Z"):].strip()
    elif upper.startswith("POLYGONZ"):
        body = body[len("POLYGONZ"):].strip()
    elif upper.startswith("POLYGON"):
        body = body[len("POLYGON"):].strip()
    else:
        return []

    if body.startswith("(") and body.endswith(")"):
        body = body[1:-1].strip()

    rings: List[List[List[float]]] = []
    depth = 0
    start = -1
    for i, ch in enumerate(body):
        if ch == "(":
            if depth == 0:
                start = i + 1
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start >= 0:
                ring_str = body[start:i]
                ring: List[List[float]] = []
                for pt_str in ring_str.split(","):
                    parts = pt_str.strip().split()
                    if len(parts) < 2:
                        continue
                    try:
                        x = float(parts[0])
                        y = float(parts[1])
                        z = float(parts[2]) if len(parts) > 2 else 0.0
                    except ValueError:
                        continue
                    ring.append([x, y, z])
                if ring:
                    rings.append(ring)
                start = -1
    return rings


_OC_SEM_TYPE = {
    OC_CEILING_SURFACE: "CeilingSurface",
    OC_FLOOR_SURFACE: "FloorSurface",
    OC_ROOF_SURFACE: "RoofSurface",
    OC_WALL_SURFACE: "WallSurface",
    OC_GROUND_SURFACE: "GroundSurface",
}


def _reconstruct_zones_from_ga(ga_map: Dict[str, Any]) -> List[dict]:
    """Rebuild thermal-zone dicts from ``tz:<zone_id>:*`` generic attributes."""
    zone_ids: Dict[str, Dict[str, Any]] = {}
    for key, val in ga_map.items():
        if not key.startswith("tz:"):
            continue
        parts = key.split(":", 2)
        if len(parts) < 3:
            continue
        zid, field = parts[1], parts[2]
        zone_ids.setdefault(zid, {"zone_id": zid})[field] = val

    zones: List[dict] = []
    for zid, fields in zone_ids.items():
        zones.append({
            "zone_id": zid,
            "usage": fields.get("usage"),
            "volume_m3": _safe_float(fields.get("volume_m3")),
            "floor_area_m2": _safe_float(fields.get("floor_area_m2")),
            "is_heated": str(fields.get("is_heated", "True")).lower() == "true",
            "is_cooled": str(fields.get("is_cooled", "False")).lower() == "true",
            "storey_index": _safe_int(fields.get("storey_index")),
            "apartment_index": _safe_int(fields.get("apartment_index")),
        })

    zones.sort(key=lambda z: (z.get("storey_index") or 0, z.get("apartment_index") or 0))
    return zones


def _safe_float(v) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _safe_int(v) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def _ga_typed_value(ga: CityObjectGenericAttrib):
    """Extract the Python-typed value from a generic-attribute row."""
    if ga.datatype == DT_STRING:
        return ga.strval
    if ga.datatype == DT_REAL:
        return ga.realval
    if ga.datatype == DT_INTEGER:
        return ga.intval
    return ga.strval or ga.realval or ga.intval


def _enrich_building_attrs_from_db(
    attrs: Dict[str, Any],
    ga_map: Dict[str, Any],
    ng2_b: Optional[Ng2Building],
) -> Dict[str, Any]:
    """Merge generic-attrib + ng2_building into CityJSON Building attributes."""
    out = dict(attrs)

    if ng2_b:
        if ng2_b.type:
            out["+energy-buildingType"] = ng2_b.type
        if ng2_b.constr_weight:
            out["+energy-constructionWeight"] = ng2_b.constr_weight

    vol = ga_map.get("thermalZone_volume_m3") or ga_map.get("cim_volume_m3")
    if vol is not None:
        out["volume"] = round(float(vol), 2)
        out["+energy-volume"] = [
            {"energy-type": "grossVolume", "energy-value": round(float(vol), 2)}
        ]

    area = ga_map.get("thermalZone_floorArea_m2") or ga_map.get("cim_footprintArea_m2")
    if area is not None:
        out["footprintArea"] = round(float(area), 2)
        out["+energy-floorArea"] = [
            {"energy-type": "grossFloorArea", "energy-value": round(float(area), 2)}
        ]

    for ga_key, out_key in (
        ("cim_constYear", "yearOfConstruction"),
        ("cim_constTabula", "constTabula"),
        ("cim_nPeople", "nPeople"),
        ("cim_nFamilies", "nFamilies"),
        ("cim_terrainHeight", "terrainHeight"),
        ("energySystem_envelopeEfficiency", "envelopeEfficiency"),
        ("energySystem_fmuFile", "energySystemModel"),
    ):
        if ga_map.get(ga_key) is not None:
            out[out_key] = ga_map[ga_key]

    return {k: v for k, v in out.items() if v is not None}


# ======================================================================
# CityJSON v1.1 builder (internal)
# ======================================================================


class _CityJSONBuilder:
    """Accumulates CityObjects and a shared vertex list, then serialises
    everything into a spec-compliant CityJSON v1.1 dict."""

    def __init__(self, target_srid: int = 4326, use_utm_for_display: bool = False):
        self._raw_vertices: List[Tuple[float, float, float]] = []
        self._vertex_map: Dict[Tuple[float, float, float], int] = {}
        self._city_objects: Dict[str, dict] = {}
        self._target_srid = target_srid
        self._use_utm_for_display = use_utm_for_display
        self._utm_transformer = None

    def _to_display_coords(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Convert WGS84 lon/lat + height(m) to UTM east/north + height(m) for ninja."""
        if not self._use_utm_for_display or not _looks_geographic(x, y):
            return x, y, z
        if self._utm_transformer is None:
            from pyproj import Transformer

            self._target_srid = _utm_srid_for(x, y)
            self._utm_transformer = Transformer.from_crs(
                "EPSG:4326",
                f"EPSG:{self._target_srid}",
                always_xy=True,
            )
        east, north = self._utm_transformer.transform(x, y)
        return float(east), float(north), z

    # ---- vertex handling ----

    def _vidx(self, x: float, y: float, z: float) -> int:
        x, y, z = self._to_display_coords(x, y, z)
        key = (round(x, 3), round(y, 3), round(z, 3))
        idx = self._vertex_map.get(key)
        if idx is None:
            idx = len(self._raw_vertices)
            self._vertex_map[key] = idx
            self._raw_vertices.append(key)
        return idx

    def _ring_to_indices(self, ring_coords: list) -> List[int]:
        indices = []
        for c in ring_coords:
            z = c[2] if len(c) > 2 else 0.0
            indices.append(self._vidx(c[0], c[1], z))
        return indices

    # ---- add building ----

    def add_building(
        self,
        building_id: str,
        attrs: dict,
        surfaces: dict,
        u_vals: dict,
        thermal_zones: Optional[List[dict]] = None,
    ):
        boundaries: List[List[List[int]]] = []
        sem_surfaces: List[dict] = []
        sem_values: List[Optional[int]] = []

        def _add_surface(geojson_geom, sem_type, u_key):
            if not geojson_geom or not geojson_geom.get("coordinates"):
                return
            for ring_coords in geojson_geom["coordinates"]:
                indices = self._ring_to_indices(ring_coords)
                boundaries.append([indices])
                sem_entry: Dict[str, Any] = {"type": sem_type}
                uv = u_vals.get(u_key)
                if uv is not None:
                    sem_entry["u_value"] = uv
                sem_surfaces.append(sem_entry)
                sem_values.append(len(sem_surfaces) - 1)

        for wall in surfaces.get("wall_surfaces", []):
            _add_surface(wall.get("geometry"), "WallSurface", "wall")

        roof = surfaces.get("roof_surface")
        if roof:
            _add_surface(roof.get("geometry"), "RoofSurface", "roof")

        ground = surfaces.get("ground_surface")
        if ground:
            _add_surface(ground.get("geometry"), "GroundSurface", "ground")

        for floor_s in surfaces.get("floor_surfaces", []):
            _add_surface(floor_s.get("geometry"), "FloorSurface", None)

        geometry = []
        if boundaries:
            geom_entry: Dict[str, Any] = {
                "type": "Solid",
                "lod": "1.2",
                "boundaries": [boundaries],
            }
            if sem_surfaces:
                geom_entry["semantics"] = {
                    "surfaces": sem_surfaces,
                    "values": [sem_values],
                }
            geometry.append(geom_entry)

        clean_attrs = {k: v for k, v in attrs.items() if v is not None}

        if thermal_zones:
            children = [f"{building_id}-{tz['zone_id']}" for tz in thermal_zones]
        else:
            children = [f"{building_id}-z1"]

        self._city_objects[building_id] = {
            "type": "Building",
            "attributes": clean_attrs,
            "geometry": geometry,
            "children": children,
        }

    # ---- add thermal zone(s) ----

    def add_thermal_zone(self, building_id: str, props):
        """Legacy single-zone thermal zone from BuildingProperties."""
        tz_id = f"{building_id}-z1"
        attrs: Dict[str, Any] = {
            "energy-isCooled": False,
            "energy-isHeated": True,
        }
        if props.volume is not None:
            attrs["energy-volume"] = [
                {"energy-type": "grossVolume", "energy-value": round(props.volume, 2)}
            ]
        if props.area is not None:
            attrs["energy-floorArea"] = [
                {"energy-type": "grossFloorArea", "energy-value": round(props.area, 2)}
            ]

        self._city_objects[tz_id] = {
            "type": "+Energy-ThermalZone",
            "attributes": attrs,
            "parents": [building_id],
        }

    def add_thermal_zones(self, building_id: str, thermal_zones: List[dict]):
        """Create one ``+Energy-ThermalZone`` child per zone definition."""
        for tz in thermal_zones:
            tz_id = f"{building_id}-{tz['zone_id']}"
            attrs: Dict[str, Any] = {
                "energy-isCooled": tz.get("is_cooled", False),
                "energy-isHeated": tz.get("is_heated", True),
            }
            if tz.get("usage"):
                attrs["usage"] = tz["usage"]
            if tz.get("volume_m3") is not None:
                attrs["energy-volume"] = [
                    {"energy-type": "grossVolume", "energy-value": round(tz["volume_m3"], 2)}
                ]
            if tz.get("floor_area_m2") is not None:
                attrs["energy-floorArea"] = [
                    {"energy-type": "grossFloorArea", "energy-value": round(tz["floor_area_m2"], 2)}
                ]
            if tz.get("storey_index") is not None:
                attrs["storeyIndex"] = tz["storey_index"]
            if tz.get("apartment_index") is not None:
                attrs["apartmentIndex"] = tz["apartment_index"]

            self._city_objects[tz_id] = {
                "type": "+Energy-ThermalZone",
                "attributes": {k: v for k, v in attrs.items() if v is not None},
                "parents": [building_id],
            }

    # ---- serialise ----

    def build(self, scenario_id: str) -> dict:
        ref_system = f"urn:ogc:def:crs:EPSG::{self._target_srid}"

        if not self._raw_vertices:
            return {
                "type": "CityJSON",
                "version": "1.1",
                "metadata": {
                    "identifier": scenario_id,
                    "referenceSystem": ref_system,
                },
                "CityObjects": {},
                "vertices": [],
            }

        xs = [v[0] for v in self._raw_vertices]
        ys = [v[1] for v in self._raw_vertices]
        zs = [v[2] for v in self._raw_vertices]

        translate = [min(xs), min(ys), min(zs)]
        # Millimetre precision on all axes when coordinates are in metres (UTM).
        if self._utm_transformer is not None or self._target_srid != 4326:
            scale = [0.001, 0.001, 0.001]
        else:
            scale = [0.0000001, 0.0000001, 0.001]

        int_vertices = []
        for v in self._raw_vertices:
            int_vertices.append([
                round((v[0] - translate[0]) / scale[0]),
                round((v[1] - translate[1]) / scale[1]),
                round((v[2] - translate[2]) / scale[2]),
            ])

        metadata = {
            "identifier": scenario_id,
            "referenceSystem": ref_system,
            "geographicalExtent": [
                min(xs), min(ys), min(zs),
                max(xs), max(ys), max(zs),
            ],
        }

        return {
            "type": "CityJSON",
            "version": "1.1",
            "transform": {"scale": scale, "translate": translate},
            "metadata": metadata,
            "extensions": {
                "Energy": {
                    "url": "https://raw.githubusercontent.com/ozgetufan/cjenergy/master/schemas/extensions/energy.ext.json",
                    "version": "1.0",
                }
            },
            "CityObjects": self._city_objects,
            "vertices": int_vertices,
        }
