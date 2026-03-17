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
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_GeomFromGeoJSON, ST_SetSRID, ST_Force2D

from app.calculators.base_calculator import BaseCalculator
from app.models.citydb import (
    CityModel,
    CityObject,
    CityObjectMember,
    CityBuilding,
    ThematicSurface,
    SurfaceGeometry,
    CityObjectGenericAttrib,
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

# 3DCityDB v4 objectclass IDs (CityGML 2.0)
OC_BUILDING = 26
OC_ROOF_SURFACE = 33
OC_WALL_SURFACE = 34
OC_GROUND_SURFACE = 35

# Generic-attribute datatype codes
DT_STRING = 1
DT_INTEGER = 2
DT_REAL = 3


class CitydbMapperCalculator(BaseCalculator):
    """Maps CIM Wizard buildings to 3DCityDB tables and produces CityJSON."""

    # ------------------------------------------------------------------
    # POST helper -- write to 3DCityDB tables via ORM
    # ------------------------------------------------------------------

    def map_scenario_to_citydb(
        self, project_id: str, scenario_id: str
    ) -> Dict[str, Any]:
        """
        Persist every building in a project-scenario into the ``citydb``
        schema.  Idempotent: skips buildings already mapped.
        """
        session: Session = self.data_manager.db_session

        from app.models.vector import Building, BuildingProperties

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

        mapped = 0
        for props, building in rows:
            try:
                self._map_building(session, building, props, citymodel)
                mapped += 1
            except Exception as e:
                logger.warning(
                    "Failed to map building %s: %s", building.building_id, e
                )
                session.rollback()

        session.commit()
        return {
            "citymodel_id": citymodel.id,
            "scenario_id": scenario_id,
            "mapped_buildings": mapped,
            "total_buildings": len(rows),
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

    def _map_building(self, session, building, props, citymodel: CityModel):
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
            self._map_surfaces(session, co.id, lod12.get("surfaces", {}), u_vals)

        self._store_thermal_zone_attrs(session, co.id, props)

        session.flush()
        return co

    # ---- LOD 1.2 surfaces ----

    def _map_surfaces(
        self, session, building_co_id: int, surfaces: dict, u_vals: dict
    ):
        def _insert_one(geojson_geom, oc_id, u_value, surf_label):
            if not geojson_geom or not geojson_geom.get("coordinates"):
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

            geojson_str = _json.dumps(geojson_geom)
            sg_poly = SurfaceGeometry(
                gmlid=f"poly-{ts_co.id}",
                parent_id=sg_root.id,
                root_id=sg_root.id,
                geometry=ST_Force2D(ST_SetSRID(ST_GeomFromGeoJSON(geojson_str), 4326)),
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

            if u_value is not None:
                session.add(
                    CityObjectGenericAttrib(
                        attrname="u_value_w_m2k",
                        datatype=DT_REAL,
                        realval=u_value,
                        cityobject_id=ts_co.id,
                    )
                )

        for wall in surfaces.get("wall_surfaces", []):
            _insert_one(
                wall.get("geometry"),
                OC_WALL_SURFACE,
                u_vals.get("wall"),
                wall.get("surface_id", "wall"),
            )

        roof = surfaces.get("roof_surface")
        if roof:
            _insert_one(
                roof.get("geometry"),
                OC_ROOF_SURFACE,
                u_vals.get("roof"),
                roof.get("surface_id", "roof"),
            )

        ground = surfaces.get("ground_surface")
        if ground:
            _insert_one(
                ground.get("geometry"),
                OC_GROUND_SURFACE,
                u_vals.get("ground"),
                ground.get("surface_id", "ground"),
            )

    # ---- generic attributes for thermal zone data ----

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

        builder = _CityJSONBuilder()

        for props, building in rows:
            bid = str(building.building_id)
            lod12 = building.building_surfaces_lod12 or {}
            surfaces = lod12.get("surfaces", {})
            u_vals = TABULA_U_VALUES.get(props.const_tabula or "", {})

            building_attrs: Dict[str, Any] = {}
            if props.height is not None:
                building_attrs["measuredHeight"] = round(props.height, 2)
            if props.area is not None:
                building_attrs["footprintArea"] = round(props.area, 2)
            if props.volume is not None:
                building_attrs["volume"] = round(props.volume, 2)
            if props.const_year is not None:
                building_attrs["yearOfConstruction"] = props.const_year
            if props.number_of_floors is not None:
                building_attrs["storeysAboveGround"] = int(props.number_of_floors)
            if building.building_name:
                building_attrs["name"] = building.building_name
            if building.z_value is not None:
                building_attrs["terrainHeight"] = round(building.z_value, 2)

            builder.add_building(bid, building_attrs, surfaces, u_vals)
            builder.add_thermal_zone(bid, props)

        return builder.build(scenario_id)


# ======================================================================
# CityJSON v1.1 builder (internal)
# ======================================================================


class _CityJSONBuilder:
    """Accumulates CityObjects and a shared vertex list, then serialises
    everything into a spec-compliant CityJSON v1.1 dict."""

    def __init__(self):
        self._raw_vertices: List[Tuple[float, float, float]] = []
        self._vertex_map: Dict[Tuple[float, float, float], int] = {}
        self._city_objects: Dict[str, dict] = {}

    # ---- vertex handling ----

    def _vidx(self, x: float, y: float, z: float) -> int:
        key = (round(x, 7), round(y, 7), round(z, 3))
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

        self._city_objects[building_id] = {
            "type": "Building",
            "attributes": clean_attrs,
            "geometry": geometry,
            "children": [f"{building_id}-z1"],
        }

    # ---- add thermal zone ----

    def add_thermal_zone(self, building_id: str, props):
        tz_id = f"{building_id}-z1"
        attrs: Dict[str, Any] = {"isCooled": False, "isHeated": True}
        if props.volume is not None:
            attrs["volume"] = round(props.volume, 2)
        if props.area is not None:
            attrs["floorArea"] = round(props.area, 2)
        if props.number_of_floors is not None:
            attrs["numberOfFloors"] = int(props.number_of_floors)
        if props.envelope_efficiency:
            attrs["envelopeEfficiency"] = props.envelope_efficiency
        if props.fmu_file:
            attrs["energySystemModel"] = props.fmu_file

        self._city_objects[tz_id] = {
            "type": "+Energy-ThermalZone",
            "attributes": attrs,
            "parents": [building_id],
        }

    # ---- serialise ----

    def build(self, scenario_id: str) -> dict:
        if not self._raw_vertices:
            return {
                "type": "CityJSON",
                "version": "1.1",
                "metadata": {
                    "identifier": scenario_id,
                    "referenceSystem": "urn:ogc:def:crs:EPSG::4326",
                },
                "CityObjects": {},
                "vertices": [],
            }

        xs = [v[0] for v in self._raw_vertices]
        ys = [v[1] for v in self._raw_vertices]
        zs = [v[2] for v in self._raw_vertices]

        translate = [min(xs), min(ys), min(zs)]
        scale = [0.0000001, 0.0000001, 0.001]

        int_vertices = []
        for v in self._raw_vertices:
            int_vertices.append([
                round((v[0] - translate[0]) / scale[0]),
                round((v[1] - translate[1]) / scale[1]),
                round((v[2] - translate[2]) / scale[2]),
            ])

        return {
            "type": "CityJSON",
            "version": "1.1",
            "transform": {"scale": scale, "translate": translate},
            "metadata": {
                "identifier": scenario_id,
                "referenceSystem": "urn:ogc:def:crs:EPSG::4326",
            },
            "extensions": {
                "Energy": {
                    "url": "https://cityjson.org/extensions/download/energy.ext.json",
                    "version": "1.0",
                }
            },
            "CityObjects": self._city_objects,
            "vertices": int_vertices,
        }
