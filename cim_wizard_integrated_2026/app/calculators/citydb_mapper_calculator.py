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

from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_GeomFromGeoJSON, ST_SetSRID, ST_AsGeoJSON

from app.calculators.base_calculator import BaseCalculator
from app.core.geo_metric import METRIC_EPSG, to_metric
from app.models.citydb import (
    Ng2Building,
    Ng2BuildingPartition,
    Ng2ThemSurfToThermalZone,
    Ng2ThematicSurface,
    ObjectClass,
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
OC_CEILING_SURFACE = 30
OC_FLOOR_SURFACE = 32
OC_ROOF_SURFACE = 33
OC_WALL_SURFACE = 34
OC_GROUND_SURFACE = 35

# Energy ADE ThermalZone.  The ADE ships its tables but is not registered in
# ``citydb.objectclass`` on this deployment, so no canonical id exists;
# ``_resolve_objectclass_id`` prefers a registered id when one is present.
# ``cityobject.objectclass_id`` has no FK, so this fallback is safe.
OC_THERMAL_ZONE = 26100

# Generic-attribute datatype codes
DT_STRING = 1
DT_INTEGER = 2
DT_REAL = 3

# Unit-of-measure strings written into the Energy ADE *_uom columns
UOM_DEGREE = "deg"
UOM_AREA = "m2"
UOM_VOLUME = "m3"


class CitydbMapperCalculator(BaseCalculator):
    """Maps CIM Wizard buildings to 3DCityDB tables and produces CityJSON."""

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)
        # Resolved citydb.objectclass ids, keyed by unqualified class name.
        self._objectclass_cache: Dict[str, Tuple[Optional[int]]] = {}

    # ------------------------------------------------------------------
    # POST helper -- write to 3DCityDB tables via ORM
    # ------------------------------------------------------------------

    def map_scenario_to_citydb(
        self,
        project_id: str,
        scenario_id: str,
        lod12_method: str = "by_footprint_height",
        force_lod12: bool = False,
        force_remap: bool = False,
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
        zones_written = 0
        faces_written = 0

        for props, building in rows:
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

                n_zones, n_faces = self._map_building(
                    session, building, props, citymodel,
                    force_remap=force_remap,
                )
                mapped += 1
                zones_written += n_zones
                faces_written += n_faces
            except Exception as e:
                logger.warning(
                    "Failed to map building %s: %s", building.building_id, e,
                )
                session.rollback()

        session.commit()
        return {
            "citymodel_id": citymodel.id,
            "gmlid": scenario_id,
            "scenario_id": scenario_id,
            "lod12_method": lod12_method,
            "lod12_generated": lod12_generated,
            "mapped_buildings": mapped,
            "thermal_zones_written": zones_written,
            "envelope_surfaces_written": faces_written,
            "total_buildings": len(rows),
            "storage": "citydb (3DCityDB + Energy ADE 2.0 ng2_* tables)",
            "reference_system": f"EPSG:{METRIC_EPSG} (CityJSON export)",
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

        if method == "by_mixed_use":
            n_families = int(props.n_family) if props.n_family else max(1, n_floors - 1) * 2
            return lod12_calc.generate_lod12_mixed_use(
                geom, height, n_floors, n_families,
            )
        if method == "by_footprint_height_floors":
            return lod12_calc.generate_lod12_with_floors(geom, height, n_floors)

        raw = lod12_calc._generate_lod12_surfaces(geom, height)
        if raw is None:
            return None
        return {
            "surfaces": raw,
            "storeys": None,
            "thermal_zones": None,
            "metadata": {
                "building_height": height,
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
        self, session, building, props, citymodel: CityModel,
        force_remap: bool = False,
    ):
        """Map one building into citydb.

        Returns ``(zones_written, envelope_surfaces_written)``.
        """
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
            if not force_remap:
                return 0, 0
            self._purge_building_from_citydb(session, existing.id)

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
        session.flush()

        lod12 = building.building_surfaces_lod12 or {}
        surfaces = lod12.get("surfaces") or {}
        thermal_zones = lod12.get("thermal_zones") or []

        # Zones first: the boundary surfaces link back to them via
        # ng2_them_surf_to_thermal_zone.
        zone_ids = self._map_thermal_zones(
            session, co.id, citymodel, bid, surfaces, thermal_zones, props,
        )

        faces = 0
        if surfaces:
            u_vals = TABULA_U_VALUES.get(props.const_tabula or "", {})
            faces = self._map_surfaces(session, co.id, surfaces, u_vals, zone_ids)

        if thermal_zones:
            self._store_multi_thermal_zone_attrs(session, co.id, thermal_zones, props)
        else:
            self._store_thermal_zone_attrs(session, co.id, props)

        session.flush()
        return len(zone_ids), faces

    @staticmethod
    def _purge_building_from_citydb(session, building_co_id: int) -> None:
        """Delete every citydb row belonging to one building.

        3DCityDB's ``citydb_pkg`` on this deployment only ships the v5
        ``delete_feature`` helpers, which do not touch the v4 tables in use
        here, and none of the relevant foreign keys cascade -- so the rows are
        removed explicitly, children before parents.
        """
        ts_ids = [
            r[0] for r in session.query(ThematicSurface.id)
            .filter(ThematicSurface.building_id == building_co_id).all()
        ]
        parts = session.query(
            Ng2BuildingPartition.id, Ng2BuildingPartition.lod1_solid_id
        ).filter(Ng2BuildingPartition.building_id == building_co_id).all()
        zone_ids = [r[0] for r in parts]

        co_ids = ts_ids + zone_ids + [building_co_id]

        def _wipe(model, column, values):
            if values:
                session.query(model).filter(column.in_(values)).delete(
                    synchronize_session=False
                )

        _wipe(Ng2ThemSurfToThermalZone,
              Ng2ThemSurfToThermalZone.thematic_surface_id, ts_ids)
        _wipe(Ng2ThemSurfToThermalZone,
              Ng2ThemSurfToThermalZone.thermal_zone_id, zone_ids)
        _wipe(Ng2ThematicSurface, Ng2ThematicSurface.id, ts_ids)
        _wipe(Ng2BuildingPartition, Ng2BuildingPartition.id, zone_ids)
        session.query(Ng2Building).filter(
            Ng2Building.id == building_co_id
        ).delete(synchronize_session=False)

        _wipe(CityObjectGenericAttrib,
              CityObjectGenericAttrib.cityobject_id, co_ids)
        _wipe(SurfaceGeometry, SurfaceGeometry.cityobject_id, co_ids)
        _wipe(ThematicSurface, ThematicSurface.id, ts_ids)
        session.query(CityBuilding).filter(
            CityBuilding.id == building_co_id
        ).delete(synchronize_session=False)
        _wipe(CityObjectMember, CityObjectMember.cityobject_id, co_ids)
        _wipe(CityObject, CityObject.id, co_ids)
        session.flush()

    # ---- Energy ADE thermal zones (ng2_building_partition) ----

    def _resolve_objectclass_id(self, session, local_name: str) -> Optional[int]:
        """Look up a registered objectclass id by its unqualified class name.

        ``classname`` is namespace-qualified (``core:Building``,
        ``energy:ThermalZone``), and the Energy ADE may not be registered at
        all, in which case this returns ``None``.
        """
        cached = self._objectclass_cache.get(local_name)
        if cached is not None:
            return cached[0]

        row = (
            session.query(ObjectClass.id)
            .filter(ObjectClass.classname.op("~*")(f"(^|:){local_name}$"))
            .first()
        )
        resolved = row[0] if row else None
        self._objectclass_cache[local_name] = (resolved,)
        return resolved

    def _map_thermal_zones(
        self,
        session,
        building_co_id: int,
        citymodel: CityModel,
        bid: str,
        surfaces: dict,
        thermal_zones: List[dict],
        props,
    ) -> Dict[str, int]:
        """Create one Energy ADE ThermalZone per LoD 1.2 zone.

        Each zone becomes a ``cityobject`` + ``ng2_building_partition`` pair
        with its extruded solid in ``surface_geometry``.  Attributes without
        an ADE column (volume, floor area, z-range, storey/apartment index,
        TABULA archetype) go into ``cityobject_genericattrib``.

        Returns a mapping of LoD 1.2 ``zone_id`` -> partition id.
        """
        if not thermal_zones:
            return {}

        from app.calculators.building_geo_lod12_calculator import extrude_zone_shell

        ring = _footprint_ring(surfaces)
        oc_zone = self._resolve_objectclass_id(session, "ThermalZone")

        # ng2_building_partition.building_id references ng2_building, which
        # extends the core building row.
        if not session.get(Ng2Building, building_co_id):
            session.add(Ng2Building(
                id=building_co_id,
                type=props.type,
                basement_thm_status=(
                    "unheated"
                    if any(z.get("storey_index") == -1 for z in thermal_zones)
                    else None
                ),
            ))
            session.flush()

        zone_ids: Dict[str, int] = {}

        for tz in thermal_zones:
            zone_id = tz.get("zone_id")
            if not zone_id:
                continue

            zco = CityObject(
                objectclass_id=oc_zone or OC_THERMAL_ZONE,
                gmlid=f"{bid}__{zone_id}",
                name=zone_id,
                description=tz.get("usage"),
            )
            session.add(zco)
            session.flush()
            session.add(CityObjectMember(
                citymodel_id=citymodel.id, cityobject_id=zco.id,
            ))

            solid_id = self._insert_zone_solid(
                session, zco.id, extrude_zone_shell(
                    ring, tz.get("z_min"), tz.get("z_max"),
                ) if ring else None,
            )

            session.add(Ng2BuildingPartition(
                id=zco.id,
                objectclass_id=oc_zone,
                type=tz.get("usage"),
                is_heated=1 if tz.get("is_heated") else 0,
                is_cooled=1 if tz.get("is_cooled") else 0,
                num_of_rooms=1 if tz.get("apartment_index") else None,
                building_id=building_co_id,
                lod1_solid_id=solid_id,
            ))
            zone_ids[zone_id] = zco.id

            self._store_zone_generic_attribs(session, zco.id, tz, props)

        session.flush()
        return zone_ids

    @staticmethod
    def _insert_zone_solid(
        session, zone_co_id: int, shell: Optional[dict]
    ) -> Optional[int]:
        """Store a zone shell as a solid in ``surface_geometry``.

        One root row flagged ``is_solid`` plus one child row per face, which
        is how 3DCityDB v4 represents a gml:Solid exterior shell.
        """
        if not shell or not shell.get("coordinates"):
            return None

        root = SurfaceGeometry(
            gmlid=f"solid-{zone_co_id}",
            is_solid=1,
            is_composite=0,
            cityobject_id=zone_co_id,
        )
        session.add(root)
        session.flush()
        root.root_id = root.id

        for i, face in enumerate(shell["coordinates"]):
            session.add(SurfaceGeometry(
                gmlid=f"solid-{zone_co_id}-f{i + 1}",
                parent_id=root.id,
                root_id=root.id,
                geometry=ST_SetSRID(
                    ST_GeomFromGeoJSON(
                        _json.dumps({"type": "Polygon", "coordinates": face})
                    ),
                    4326,
                ),
                cityobject_id=zone_co_id,
            ))

        session.flush()
        return root.id

    @staticmethod
    def _read_zones_from_ade(session, building_co_id: int) -> List[dict]:
        """Rebuild zone dicts from ng2_building_partition + generic attribs."""
        rows = (
            session.query(Ng2BuildingPartition, CityObject)
            .join(CityObject, Ng2BuildingPartition.id == CityObject.id)
            .filter(Ng2BuildingPartition.building_id == building_co_id)
            .all()
        )
        if not rows:
            return []

        zone_ids = [part.id for part, _ in rows]
        ga_rows = (
            session.query(CityObjectGenericAttrib)
            .filter(CityObjectGenericAttrib.cityobject_id.in_(zone_ids))
            .all()
        )
        by_zone: Dict[int, Dict[str, Any]] = {}
        for ga in ga_rows:
            by_zone.setdefault(ga.cityobject_id, {})[ga.attrname] = _ga_typed_value(ga)

        zones: List[dict] = []
        for part, zco in rows:
            attrs = by_zone.get(part.id, {})
            zones.append({
                "zone_id": zco.name,
                "usage": part.type,
                "volume_m3": _safe_float(attrs.get("volume")),
                "floor_area_m2": _safe_float(attrs.get("floorArea")),
                "is_heated": bool(part.is_heated),
                "is_cooled": bool(part.is_cooled),
                "storey_index": _safe_int(attrs.get("storeyIndex")),
                "apartment_index": _safe_int(attrs.get("apartmentIndex")),
                "z_min": _safe_float(attrs.get("zMin")),
                "z_max": _safe_float(attrs.get("zMax")),
            })

        zones.sort(
            key=lambda z: (z.get("storey_index") or 0, z.get("apartment_index") or 0)
        )
        return zones

    @staticmethod
    def _store_zone_generic_attribs(session, zone_co_id: int, tz: dict, props):
        """Zone attributes that Energy ADE has no column for."""
        entries: List[Tuple[str, int, str, Any, Optional[str]]] = [
            ("volume", DT_REAL, "realval", tz.get("volume_m3"), UOM_VOLUME),
            ("floorArea", DT_REAL, "realval", tz.get("floor_area_m2"), UOM_AREA),
            ("zMin", DT_REAL, "realval", tz.get("z_min"), "m"),
            ("zMax", DT_REAL, "realval", tz.get("z_max"), "m"),
            ("storeyIndex", DT_INTEGER, "intval", tz.get("storey_index"), None),
            ("apartmentIndex", DT_INTEGER, "intval", tz.get("apartment_index"), None),
            ("usage", DT_STRING, "strval", tz.get("usage"), None),
            ("tabulaArchetype", DT_STRING, "strval", props.const_tabula, None),
        ]
        for name, dtype, col, value, unit in entries:
            if value is None:
                continue
            ga = CityObjectGenericAttrib(
                attrname=name,
                datatype=dtype,
                unit=unit,
                cityobject_id=zone_co_id,
            )
            setattr(ga, col, value)
            session.add(ga)

    # ---- LOD 1.2 surfaces ----

    def _map_surfaces(
        self,
        session,
        building_co_id: int,
        surfaces: dict,
        u_vals: dict,
        zone_ids: Optional[Dict[str, int]] = None,
    ) -> int:
        """Map LoD 1.2 boundary surfaces into citydb.

        Each face becomes a ``cityobject`` + ``thematic_surface`` pair (core
        CityGML) plus an ``ng2_thematic_surface`` row carrying the Energy ADE
        ThermalBoundary physics: azimuth, inclination and total surface area.
        Faces belonging to a zone are linked through
        ``ng2_them_surf_to_thermal_zone``.

        Returns the number of surfaces written.
        """
        zone_ids = zone_ids or {}
        written = 0

        def _insert_one(surf, oc_id, u_value, surf_label):
            nonlocal written
            geojson_geom = (surf or {}).get("geometry")
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
                geometry=ST_SetSRID(ST_GeomFromGeoJSON(geojson_str), 4326),
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

            # Energy ADE ThermalBoundary physics
            sp = surf.get("properties") or {}
            azimuth = sp.get("azimuth_degrees")
            tilt = sp.get("tilt_degrees")
            area = sp.get("area_m2")
            session.add(Ng2ThematicSurface(
                id=ts_co.id,
                total_surf_area=area,
                total_surf_area_uom=UOM_AREA if area is not None else None,
                azimuth=azimuth,
                azimuth_uom=UOM_DEGREE if azimuth is not None else None,
                inclination=tilt,
                inclination_uom=UOM_DEGREE if tilt is not None else None,
            ))

            zone_pk = zone_ids.get(surf.get("zone_id") or sp.get("zone_id"))
            if zone_pk:
                session.add(Ng2ThemSurfToThermalZone(
                    thematic_surface_id=ts_co.id,
                    thermal_zone_id=zone_pk,
                ))

            if u_value is not None:
                session.add(
                    CityObjectGenericAttrib(
                        attrname="u_value_w_m2k",
                        datatype=DT_REAL,
                        realval=u_value,
                        unit="W/m2K",
                        cityobject_id=ts_co.id,
                    )
                )

            written += 1

        for wall in surfaces.get("wall_surfaces", []):
            _insert_one(
                wall,
                OC_WALL_SURFACE,
                u_vals.get("wall"),
                wall.get("surface_id", "wall"),
            )

        roof = surfaces.get("roof_surface")
        if roof:
            _insert_one(
                roof,
                OC_ROOF_SURFACE,
                u_vals.get("roof"),
                roof.get("surface_id", "roof"),
            )

        ground = surfaces.get("ground_surface")
        if ground:
            _insert_one(
                ground,
                OC_GROUND_SURFACE,
                u_vals.get("ground"),
                ground.get("surface_id", "ground"),
            )

        for floor_surf in surfaces.get("floor_surfaces", []):
            _insert_one(
                floor_surf,
                OC_FLOOR_SURFACE,
                None,
                floor_surf.get("surface_id", "floor"),
            )

        return written

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
                (f"{prefix}:z_min", DT_REAL, "realval", tz.get("z_min")),
                (f"{prefix}:z_max", DT_REAL, "realval", tz.get("z_max")),
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

        builder = _CityJSONBuilder()

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

            builder.add_building(
                bid, building_attrs, surfaces, u_vals,
                thermal_zones=thermal_zones,
            )
            if thermal_zones:
                builder.add_thermal_zones(
                    bid, thermal_zones, footprint_ring=_footprint_ring(surfaces),
                )
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

        builder = _CityJSONBuilder()

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
            tz_count = ga_map.get("thermalZone_count")
            multi_zone = tz_count is not None and int(tz_count) > 1

            reconstructed_zones: List[dict] = []
            if multi_zone:
                # Prefer the Energy ADE partitions; fall back to the legacy
                # ``tz:*`` generic attributes for scenarios mapped before
                # zones were stored natively.
                reconstructed_zones = self._read_zones_from_ade(session, co.id)
                if not reconstructed_zones:
                    reconstructed_zones = _reconstruct_zones_from_ga(ga_map)
            else:
                tz_attrs: Dict[str, Any] = {"isCooled": False, "isHeated": True}
                for ga in gen_attrs:
                    val = _ga_typed_value(ga)
                    if val is None:
                        continue
                    if ga.attrname == "thermalZone_volume_m3":
                        tz_attrs["volume"] = round(float(val), 2)
                        attrs["volume"] = round(float(val), 2)
                    elif ga.attrname == "thermalZone_floorArea_m2":
                        tz_attrs["floorArea"] = round(float(val), 2)
                        attrs["footprintArea"] = round(float(val), 2)
                    elif ga.attrname == "thermalZone_numberOfFloors":
                        tz_attrs["numberOfFloors"] = int(val)
                    elif ga.attrname == "energySystem_envelopeEfficiency":
                        tz_attrs["envelopeEfficiency"] = val
                    elif ga.attrname == "energySystem_fmuFile":
                        tz_attrs["energySystemModel"] = val

            surface_rows = (
                session.query(
                    ThematicSurface,
                    CityObject,
                    func.ST_AsGeoJSON(SurfaceGeometry.geometry).label("geojson"),
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

            boundaries: List[List[List[int]]] = []
            sem_surfaces: List[dict] = []
            sem_values: List[Optional[int]] = []
            ground_ring: Optional[list] = None

            for ts, ts_co, geojson_str in surface_rows:
                if not geojson_str:
                    continue

                geojson = _json.loads(geojson_str)
                sem_type = _OC_SEM_TYPE.get(ts.objectclass_id, "GenericSurface")

                if ts.objectclass_id in (OC_GROUND_SURFACE, OC_ROOF_SURFACE):
                    rings = geojson.get("coordinates") or []
                    if rings and len(rings[0]) >= 4 and (
                        ground_ring is None
                        or ts.objectclass_id == OC_GROUND_SURFACE
                    ):
                        ground_ring = rings[0]

                u_attr = (
                    session.query(CityObjectGenericAttrib)
                    .filter(
                        CityObjectGenericAttrib.cityobject_id == ts.id,
                        CityObjectGenericAttrib.attrname == "u_value_w_m2k",
                    )
                    .first()
                )

                sem_entry: Dict[str, Any] = {"type": sem_type}
                if u_attr and u_attr.realval is not None:
                    sem_entry["u_value"] = u_attr.realval

                for ring in geojson.get("coordinates", []):
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

            if multi_zone and reconstructed_zones:
                children = [f"{bid}-{rz['zone_id']}" for rz in reconstructed_zones]
                builder._city_objects[bid] = {
                    "type": "Building",
                    "attributes": {k: v for k, v in attrs.items() if v is not None},
                    "geometry": geometry,
                    "children": children,
                }
                builder.add_thermal_zones(
                    bid, reconstructed_zones, footprint_ring=ground_ring,
                )
            else:
                builder._city_objects[bid] = {
                    "type": "Building",
                    "attributes": {k: v for k, v in attrs.items() if v is not None},
                    "geometry": geometry,
                    "children": [f"{bid}-z1"],
                }
                builder._city_objects[f"{bid}-z1"] = {
                    "type": "+Energy-ThermalZone",
                    "attributes": {k: v for k, v in tz_attrs.items() if v is not None},
                    "parents": [bid],
                }

        return builder.build(citymodel_id)


# ── Helper utilities ─────────────────────────────────────────────────

def _footprint_ring(surfaces: dict) -> Optional[list]:
    """Footprint ring of a building, taken from its ground or roof surface.

    Used to extrude thermal-zone solids; only X/Y are read, so the stored Z
    and the winding order of the source surface do not matter.
    """
    for key in ("ground_surface", "roof_surface"):
        surf = (surfaces or {}).get(key)
        coords = ((surf or {}).get("geometry") or {}).get("coordinates") or []
        if coords and len(coords[0]) >= 4:
            return coords[0]
    return None


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
            "z_min": _safe_float(fields.get("z_min")),
            "z_max": _safe_float(fields.get("z_max")),
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


# ======================================================================
# CityJSON v1.1 builder (internal)
# ======================================================================


class _CityJSONBuilder:
    """Accumulates CityObjects and a shared vertex list, then serialises
    everything into a spec-compliant CityJSON v1.1 dict.

    Input coordinates are EPSG:4326 lon/lat with Z already in metres.  They
    are reprojected to METRIC_EPSG on the way in, because CityJSON viewers
    treat all three axes as the same unit: leaving X/Y in degrees makes a
    building roughly 25000x taller than the district is wide, which renders
    as a single vertical line.
    """

    def __init__(self):
        self._raw_vertices: List[Tuple[float, float, float]] = []
        self._vertex_map: Dict[Tuple[float, float, float], int] = {}
        self._city_objects: Dict[str, dict] = {}

    # ---- vertex handling ----

    def _vidx(self, x: float, y: float, z: float) -> int:
        easting, northing = to_metric(x, y)
        key = (round(easting, 3), round(northing, 3), round(z, 3))
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

    def _zone_solid(
        self, ring: list, z_min: float, z_max: float
    ) -> Optional[dict]:
        """Extruded Solid for one thermal zone, with semantic faces.

        Same shell as ``extrude_zone_shell`` / the notebook's
        ``extrude_zone_solid``: floor slab + ceiling slab + one wall per edge.
        """
        if not ring or len(ring) < 4 or z_min is None or z_max is None:
            return None

        shell: List[List[List[int]]] = []
        sem_surfaces: List[dict] = []
        sem_values: List[int] = []

        def _face(coords, sem_type):
            shell.append([self._ring_to_indices(coords)])
            sem_surfaces.append({"type": sem_type})
            sem_values.append(len(sem_surfaces) - 1)

        _face([[p[0], p[1], z_min] for p in ring], "FloorSurface")
        _face([[p[0], p[1], z_max] for p in ring], "CeilingSurface")
        for i in range(len(ring) - 1):
            p1, p2 = ring[i], ring[i + 1]
            _face([
                [p1[0], p1[1], z_min],
                [p2[0], p2[1], z_min],
                [p2[0], p2[1], z_max],
                [p1[0], p1[1], z_max],
                [p1[0], p1[1], z_min],
            ], "WallSurface")

        return {
            "type": "Solid",
            "lod": "1.2",
            "boundaries": [shell],
            "semantics": {"surfaces": sem_surfaces, "values": [sem_values]},
        }

    def add_thermal_zones(
        self,
        building_id: str,
        thermal_zones: List[dict],
        footprint_ring: Optional[list] = None,
    ):
        """Create one ``+Energy-ThermalZone`` child per zone definition.

        When *footprint_ring* is supplied, each zone also carries its own
        extruded Solid between ``z_min`` and ``z_max`` so the zones are
        actually visible in a viewer instead of being attribute-only.
        """
        for tz in thermal_zones:
            tz_id = f"{building_id}-{tz['zone_id']}"
            attrs: Dict[str, Any] = {
                "usage": tz.get("usage"),
                "isCooled": tz.get("is_cooled", False),
                "isHeated": tz.get("is_heated", True),
            }
            if tz.get("volume_m3") is not None:
                attrs["volume"] = round(tz["volume_m3"], 2)
            if tz.get("floor_area_m2") is not None:
                attrs["floorArea"] = round(tz["floor_area_m2"], 2)
            if tz.get("storey_index") is not None:
                attrs["storeyIndex"] = tz["storey_index"]
            if tz.get("apartment_index") is not None:
                attrs["apartmentIndex"] = tz["apartment_index"]

            entry: Dict[str, Any] = {
                "type": "+Energy-ThermalZone",
                "attributes": {k: v for k, v in attrs.items() if v is not None},
                "parents": [building_id],
            }

            solid = self._zone_solid(
                footprint_ring, tz.get("z_min"), tz.get("z_max"),
            ) if footprint_ring else None
            if solid:
                entry["geometry"] = [solid]

            self._city_objects[tz_id] = entry

    # ---- serialise ----

    def build(self, scenario_id: str) -> dict:
        reference_system = f"https://www.opengis.net/def/crs/EPSG/0/{METRIC_EPSG}"

        if not self._raw_vertices:
            return {
                "type": "CityJSON",
                "version": "1.1",
                "metadata": {
                    "identifier": scenario_id,
                    "referenceSystem": reference_system,
                },
                "CityObjects": {},
                "vertices": [],
            }

        xs = [v[0] for v in self._raw_vertices]
        ys = [v[1] for v in self._raw_vertices]
        zs = [v[2] for v in self._raw_vertices]

        # All three axes are metres now, so a uniform millimetre quantum keeps
        # the model correctly proportioned.
        translate = [min(xs), min(ys), min(zs)]
        scale = [0.001, 0.001, 0.001]

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
                "referenceSystem": reference_system,
                "geographicalExtent": [
                    min(xs), min(ys), min(zs),
                    max(xs), max(ys), max(zs),
                ],
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
