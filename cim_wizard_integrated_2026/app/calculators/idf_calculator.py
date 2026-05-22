"""
IDF Calculator — generate EnergyPlus IDF files from CityDB-mapped buildings.

This is the "IDF extractor" stage at the end of the CIM Wizard pipeline.
It reads CityJSON v1.1 produced from the ``citydb`` schema (mapped by the
pre-sim CityDB mapper) and emits one IDF file per building plus an index
JSON describing the export.

Inputs
------
- CityDB-mapped CityModel for ``citymodel_id`` (== scenario_id)
- ``schedule`` feature (e.g. from ScheduleCalculator.typical_residential_it)
- ``occupants`` feature (e.g. from OccupantCalculator.typical_residential_it)

Methods
-------
from_citydb
    Read CityJSON from the citydb schema and emit IDF files.
from_cityjson
    Emit IDF files from a CityJSON dict already in memory.

The IDF emitter is intentionally lightweight (no eppy / archetypal
dependency).  Geometry surfaces are written as ``BuildingSurface:Detailed``
objects with vertex coordinates taken from CityJSON.  Materials and
constructions come from TABULA U-values via simple ``Material:NoMass``.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.calculators.base_calculator import BaseCalculator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_OUTPUT_DIR = "exports/idf"
DEFAULT_TERRAIN = "City"
DEFAULT_NORTH_AXIS = 0.0
DEFAULT_TIMESTEP = 6        # 10-minute timestep
DEFAULT_HVAC_MODE = "ideal_loads"

# Surface-type → outside boundary defaults
SURFACE_BOUNDARY = {
    "WallSurface":   ("Wall",    "Outdoors", "SunExposed",   "WindExposed"),
    "RoofSurface":   ("Roof",    "Outdoors", "SunExposed",   "WindExposed"),
    "GroundSurface": ("Floor",   "Ground",   "NoSun",        "NoWind"),
    "FloorSurface":  ("Floor",   "Adiabatic", "NoSun",       "NoWind"),
    "CeilingSurface":("Ceiling", "Adiabatic", "NoSun",       "NoWind"),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_name(text: str) -> str:
    """Sanitize an IDF identifier (no spaces, no commas, no semicolons)."""
    if not text:
        return "X"
    return (
        text.replace(",", "-")
        .replace(";", "-")
        .replace(" ", "_")
        .replace("\n", "")
        .replace("\r", "")
    )


def _resolve_vertices(cityjson: Dict[str, Any]) -> List[Tuple[float, float, float]]:
    """Apply CityJSON transform (scale + translate) to integer vertices."""
    raw = cityjson.get("vertices") or []
    transform = cityjson.get("transform") or {}
    scale = transform.get("scale") or [1.0, 1.0, 1.0]
    translate = transform.get("translate") or [0.0, 0.0, 0.0]
    out: List[Tuple[float, float, float]] = []
    for v in raw:
        x = float(v[0]) * float(scale[0]) + float(translate[0])
        y = float(v[1]) * float(scale[1]) + float(translate[1])
        z = float(v[2]) * float(scale[2]) + float(translate[2])
        out.append((x, y, z))
    return out


def _u_to_resistance(u_value: float) -> float:
    """Convert U-value (W/m2K) to thermal resistance (m2K/W)."""
    if u_value is None or u_value <= 0:
        return 1.0
    return 1.0 / float(u_value)


def _surface_vertices(boundaries: list, vertices: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
    """Return the vertex coordinates of the first ring of a surface polygon."""
    if not boundaries:
        return []
    ring_indices = boundaries[0]
    pts: List[Tuple[float, float, float]] = []
    for idx in ring_indices:
        if 0 <= idx < len(vertices):
            pts.append(vertices[idx])
    # IDF surfaces should not repeat the first vertex at the end
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    return pts


# ---------------------------------------------------------------------------
# IDF emitter
# ---------------------------------------------------------------------------

class _IDFEmitter:
    """Build an EnergyPlus IDF text from CityJSON + schedule + occupant data."""

    def __init__(
        self,
        building_id: str,
        building_obj: Dict[str, Any],
        thermal_zones: List[Dict[str, Any]],
        vertices: List[Tuple[float, float, float]],
        schedule_template: Optional[Dict[str, Any]] = None,
        occupant_template: Optional[Dict[str, Any]] = None,
        hvac_mode: str = DEFAULT_HVAC_MODE,
    ):
        self.bid = _safe_name(building_id)
        self.building_obj = building_obj
        self.thermal_zones = thermal_zones or []
        self.vertices = vertices
        self.schedule_template = schedule_template
        self.occupant_template = occupant_template
        self.hvac_mode = hvac_mode

        self._lines: List[str] = []
        self._materials: Dict[str, float] = {}     # name -> u_value
        self._constructions: Dict[str, str] = {}   # surface-type -> material name

    # ---------- header ----------

    def _emit_header(self):
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self._lines.append(
            f"! IDF generated by CIM Wizard IDF Calculator on {ts}\n"
            f"! Building: {self.bid}\n"
            f"! HVAC mode: {self.hvac_mode}\n"
        )
        self._lines.append("Version,9.5;")
        self._lines.append(
            "SimulationControl,\n"
            "  Yes, ! Do Zone Sizing Calculation\n"
            "  Yes, ! Do System Sizing Calculation\n"
            "  No,  ! Do Plant Sizing Calculation\n"
            "  No,  ! Run Simulation for Sizing Periods\n"
            "  Yes; ! Run Simulation for Weather File Run Periods\n"
        )
        self._lines.append(
            f"Building,\n"
            f"  {self.bid}, ! Name\n"
            f"  {DEFAULT_NORTH_AXIS:.2f}, ! North Axis (deg)\n"
            f"  {DEFAULT_TERRAIN}, ! Terrain\n"
            f"  0.04, ! Loads Convergence Tolerance Value\n"
            f"  0.40, ! Temperature Convergence Tolerance Value (deltaC)\n"
            f"  FullExterior, ! Solar Distribution\n"
            f"  25, ! Maximum Number of Warmup Days\n"
            f"  6;  ! Minimum Number of Warmup Days\n"
        )
        self._lines.append(f"Timestep,{DEFAULT_TIMESTEP};")
        self._lines.append(
            "RunPeriod,\n"
            "  AnnualRun, ! Name\n"
            "  1, ! Begin Month\n"
            "  1, ! Begin Day\n"
            "  ,  ! Begin Year\n"
            "  12, ! End Month\n"
            "  31, ! End Day\n"
            "  ,  ! End Year\n"
            "  Sunday, ! Day of Week for Start Day\n"
            "  Yes, ! Use Weather File Holidays and Special Days\n"
            "  Yes, ! Use Weather File Daylight Saving Period\n"
            "  No,  ! Apply Weekend Holiday Rule\n"
            "  Yes, ! Use Weather File Rain Indicators\n"
            "  Yes; ! Use Weather File Snow Indicators\n"
        )
        self._lines.append("GlobalGeometryRules,UpperLeftCorner,Counterclockwise,Relative;")

    # ---------- schedules ----------

    def _emit_schedules(self):
        """Emit a minimal set of compact schedules used by people/lights/HVAC."""
        self._lines.append("ScheduleTypeLimits,Fraction,0,1,Continuous;")
        self._lines.append("ScheduleTypeLimits,Temperature,-60,200,Continuous;")
        self._lines.append("ScheduleTypeLimits,OnOff,0,1,Discrete;")

        # Occupancy schedule (fall back to a flat 0.5 if no template)
        occ = self._profile_to_compact(
            "OccSched_" + self.bid,
            "Fraction",
            self._profiles_get("occupancy", default=0.5),
        )
        self._lines.append(occ)

        heat = self._profile_to_compact(
            "HeatSetpoint_" + self.bid,
            "Temperature",
            self._heating_setpoint_profile(),
        )
        self._lines.append(heat)

        cool = self._profile_to_compact(
            "CoolSetpoint_" + self.bid,
            "Temperature",
            self._cooling_setpoint_profile(),
        )
        self._lines.append(cool)

        always_on = self._profile_to_compact(
            "AlwaysOn_" + self.bid, "OnOff", {"weekday": [1] * 24, "weekend": [1] * 24}
        )
        self._lines.append(always_on)

    def _profiles_get(self, kind: str, default: float = 0.0) -> Dict[str, List[float]]:
        if not self.schedule_template:
            return {"weekday": [default] * 24, "weekend": [default] * 24}
        profiles = self.schedule_template.get("profiles", {}).get(kind)
        if not profiles:
            return {"weekday": [default] * 24, "weekend": [default] * 24}
        return profiles

    def _heating_setpoint_profile(self) -> Dict[str, List[float]]:
        setpoints = (self.schedule_template or {}).get("setpoints", {})
        set_h = float(setpoints.get("heating_C", 20.0))
        set_b = float(setpoints.get("heating_setback_C", 16.0))
        prof = self._profiles_get("heating", default=1.0)
        wk = [set_h if v else set_b for v in prof["weekday"]]
        we = [set_h if v else set_b for v in prof["weekend"]]
        return {"weekday": wk, "weekend": we}

    def _cooling_setpoint_profile(self) -> Dict[str, List[float]]:
        setpoints = (self.schedule_template or {}).get("setpoints", {})
        set_c = float(setpoints.get("cooling_C", 26.0))
        set_b = float(setpoints.get("cooling_setback_C", 28.0))
        prof = self._profiles_get("cooling", default=1.0)
        wk = [set_c if v else set_b for v in prof["weekday"]]
        we = [set_c if v else set_b for v in prof["weekend"]]
        return {"weekday": wk, "weekend": we}

    @staticmethod
    def _profile_to_compact(name: str, type_limits: str, profile: Dict[str, List[float]]) -> str:
        wk = profile.get("weekday") or [0.0] * 24
        we = profile.get("weekend") or wk
        lines: List[str] = [
            f"Schedule:Compact,",
            f"  {name},",
            f"  {type_limits},",
            f"  Through: 12/31,",
            f"  For: Weekdays,",
        ]
        for hr, v in enumerate(wk, start=1):
            lines.append(f"  Until: {hr:02d}:00, {v:.2f},")
        lines.append("  For: AllOtherDays,")
        for hr, v in enumerate(we, start=1):
            terminator = ";" if hr == 24 else ","
            lines.append(f"  Until: {hr:02d}:00, {v:.2f}{terminator}")
        return "\n".join(lines)

    # ---------- materials & constructions ----------

    def _emit_constructions(self, surfaces: List[Dict[str, Any]]):
        # Aggregate one Material:NoMass per (surface_type, u_value)
        for s in surfaces:
            stype = s.get("type") or s.get("surface_type") or "WallSurface"
            u = s.get("u_value")
            if u is None:
                continue
            mat_name = f"Mat_{_safe_name(stype)}_U{u:.2f}_{self.bid}"
            constr_name = f"Constr_{_safe_name(stype)}_U{u:.2f}_{self.bid}"
            self._materials[mat_name] = float(u)
            self._constructions[stype] = constr_name

            self._lines.append(
                f"Material:NoMass,\n"
                f"  {mat_name}, ! Name\n"
                f"  Smooth, ! Roughness\n"
                f"  {_u_to_resistance(float(u)):.4f}, ! Thermal Resistance (m2-K/W)\n"
                f"  0.9, ! Thermal Absorptance\n"
                f"  0.7, ! Solar Absorptance\n"
                f"  0.7; ! Visible Absorptance\n"
            )

            self._lines.append(
                f"Construction,\n"
                f"  {constr_name}, ! Name\n"
                f"  {mat_name};   ! Layer\n"
            )

        # Default fallback construction (used when a surface has no u_value)
        self._lines.append(
            "Material:NoMass,\n"
            f"  Mat_DEFAULT_{self.bid}, ! Name\n"
            "  Smooth,\n"
            "  1.0, ! R = 1.0 m2-K/W\n"
            "  0.9, 0.7, 0.7;"
        )
        self._lines.append(
            f"Construction,\n"
            f"  Constr_DEFAULT_{self.bid},\n"
            f"  Mat_DEFAULT_{self.bid};\n"
        )

    # ---------- zones & surfaces ----------

    def _emit_zones_and_surfaces(self, surfaces: List[Dict[str, Any]]):
        if not self.thermal_zones:
            # Default single-zone fallback
            self.thermal_zones = [{"zone_id": "z1", "usage": "residential"}]

        # Map building-level surfaces to a default zone (the first zone)
        zone_names: List[str] = []
        for tz in self.thermal_zones:
            zid = _safe_name(tz.get("zone_id", "z"))
            zone_name = f"Zone_{self.bid}_{zid}"
            zone_names.append(zone_name)
            self._lines.append(
                f"Zone,\n"
                f"  {zone_name}, ! Name\n"
                f"  0, ! Direction of Relative North\n"
                f"  0, 0, 0, ! X, Y, Z Origin\n"
                f"  1, ! Type\n"
                f"  1, ! Multiplier\n"
                f", , autocalculate, autocalculate;"
            )

        default_zone = zone_names[0]

        # People / Lights / Infiltration per zone
        for zone_name in zone_names:
            people_count = (
                int((self.occupant_template or {}).get("num_of_occupants", 0))
                if self.occupant_template else 0
            )
            heat_diss_W = float(
                (self.occupant_template or {}).get("heat_dissipation_W", 120.0)
            )
            self._lines.append(
                f"People,\n"
                f"  Occ_{zone_name}, ! Name\n"
                f"  {zone_name}, ! Zone\n"
                f"  OccSched_{self.bid}, ! Number of People Schedule\n"
                f"  People, ! Calculation Method\n"
                f"  {max(people_count, 0)}, ! Number of People\n"
                f"  , , 0.3, 0.7, , AlwaysOn_{self.bid}, ! Activity Level Schedule\n"
                f"  {heat_diss_W:.1f};\n"
            )

            self._lines.append(
                f"ZoneInfiltration:DesignFlowRate,\n"
                f"  Infil_{zone_name}, ! Name\n"
                f"  {zone_name}, ! Zone\n"
                f"  AlwaysOn_{self.bid}, ! Schedule\n"
                f"  AirChanges/Hour,\n"
                f"  , , , 0.5;\n"
            )

            # Ideal-loads system (default HVAC)
            if self.hvac_mode == "ideal_loads":
                self._lines.append(
                    f"HVACTemplate:Zone:IdealLoadsAirSystem,\n"
                    f"  {zone_name}, ! Zone Name\n"
                    f"  HeatSetpoint_{self.bid}, ! Heating Availability Schedule\n"
                    f"  CoolSetpoint_{self.bid}; ! Cooling Availability Schedule\n"
                )

        # Surfaces
        for s_idx, s in enumerate(surfaces):
            stype = s.get("type") or s.get("surface_type") or "WallSurface"
            mapping = SURFACE_BOUNDARY.get(stype, SURFACE_BOUNDARY["WallSurface"])
            class_name, outside_bc, sun_exp, wind_exp = mapping

            constr = self._constructions.get(stype, f"Constr_DEFAULT_{self.bid}")
            verts = _surface_vertices(s.get("boundaries", []), self.vertices)
            if len(verts) < 3:
                continue
            surf_name = f"Surf_{self.bid}_{s_idx:04d}"
            lines: List[str] = [
                "BuildingSurface:Detailed,",
                f"  {surf_name}, ! Name",
                f"  {class_name}, ! Class",
                f"  {constr}, ! Construction",
                f"  {default_zone}, ! Zone Name",
                f"  ,  ! Space Name",
                f"  {outside_bc}, ! Outside Boundary Condition",
                f"  ,  ! Outside Boundary Condition Object",
                f"  {sun_exp}, ! Sun Exposure",
                f"  {wind_exp}, ! Wind Exposure",
                "  autocalculate, ! View Factor to Ground",
                f"  {len(verts)}, ! Number of Vertices",
            ]
            for v_idx, (x, y, z) in enumerate(verts):
                terminator = ";" if v_idx == len(verts) - 1 else ","
                lines.append(f"  {x:.3f}, {y:.3f}, {z:.3f}{terminator}")
            self._lines.append("\n".join(lines))

    # ---------- build ----------

    def build(self, surfaces: List[Dict[str, Any]]) -> str:
        self._emit_header()
        self._emit_schedules()
        self._emit_constructions(surfaces)
        self._emit_zones_and_surfaces(surfaces)
        return "\n\n".join(self._lines) + "\n"


# ---------------------------------------------------------------------------
# CityJSON → per-building geometry extraction
# ---------------------------------------------------------------------------

def _extract_building_payloads(cityjson: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return one dict per Building CityObject with surfaces and thermal zones."""
    city_objects = cityjson.get("CityObjects", {}) or {}
    vertices = _resolve_vertices(cityjson)

    payloads: List[Dict[str, Any]] = []
    for bid, obj in city_objects.items():
        if obj.get("type") != "Building":
            continue
        # Surfaces with semantics
        surfaces: List[Dict[str, Any]] = []
        for geom in obj.get("geometry", []) or []:
            sem = (geom.get("semantics") or {}).get("surfaces") or []
            sem_values = (geom.get("semantics") or {}).get("values") or []
            sem_values_flat = sem_values[0] if sem_values and isinstance(sem_values[0], list) else sem_values
            for face_idx, bounds in enumerate((geom.get("boundaries") or [[]])[0] or []):
                semantic = None
                if face_idx < len(sem_values_flat):
                    s_idx = sem_values_flat[face_idx]
                    if s_idx is not None and 0 <= s_idx < len(sem):
                        semantic = sem[s_idx]
                surfaces.append({
                    "type": (semantic or {}).get("type", "WallSurface"),
                    "u_value": (semantic or {}).get("u_value"),
                    "boundaries": [bounds] if bounds else [],
                })

        # Thermal zones — pull from child CityObjects
        thermal_zones: List[Dict[str, Any]] = []
        for child_id in obj.get("children", []) or []:
            child = city_objects.get(child_id)
            if not child or child.get("type") != "+Energy-ThermalZone":
                continue
            attrs = child.get("attributes", {})
            thermal_zones.append({
                "zone_id": child_id.split("-")[-1] if "-" in child_id else child_id,
                "usage": attrs.get("usage"),
                "volume_m3": _first_energy_value(attrs.get("energy-volume")),
                "floor_area_m2": _first_energy_value(attrs.get("energy-floorArea")),
                "is_heated": bool(attrs.get("energy-isHeated", True)),
                "is_cooled": bool(attrs.get("energy-isCooled", False)),
            })

        payloads.append({
            "building_id": bid,
            "building_obj": obj,
            "surfaces": surfaces,
            "thermal_zones": thermal_zones,
            "vertices": vertices,
        })
    return payloads


def _first_energy_value(attr: Any) -> Optional[float]:
    if not attr:
        return None
    if isinstance(attr, list) and attr:
        first = attr[0]
        if isinstance(first, dict):
            return first.get("energy-value")
    if isinstance(attr, (int, float)):
        return float(attr)
    return None


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------

class IDFCalculator(BaseCalculator):
    """Generate EnergyPlus IDF files from CityDB-mapped buildings."""

    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def from_citydb(
        self,
        citymodel_id: Optional[str] = None,
        output_dir: Optional[str] = None,
        hvac_mode: str = DEFAULT_HVAC_MODE,
    ) -> Optional[Dict[str, Any]]:
        """Read CityJSON from the citydb schema and emit IDF files.

        ``citymodel_id`` defaults to ``self.scenario_id`` when not provided.
        """
        try:
            from app.calculators.citydb_mapper_calculator import CitydbMapperCalculator

            cm_id = citymodel_id or self.scenario_id
            if not cm_id:
                self.log_error("citymodel_id (scenario_id) is required")
                return None

            mapper = CitydbMapperCalculator(self.pipeline)
            cityjson = mapper.generate_cityjson_from_citydb(cm_id)
            if not cityjson or not cityjson.get("CityObjects"):
                self.log_error(
                    f"No CityJSON available for CityModel '{cm_id}'. "
                    "Run pre-sim-ctdbmapper first."
                )
                return None

            return self._emit_from_cityjson(cityjson, output_dir, hvac_mode, cm_id)
        except Exception as e:
            self.log_failure("from_citydb", str(e))
            return None

    def from_cityjson(
        self,
        cityjson: Dict[str, Any],
        output_dir: Optional[str] = None,
        hvac_mode: str = DEFAULT_HVAC_MODE,
        citymodel_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Emit IDF files from a CityJSON dict already in memory."""
        try:
            cm_id = citymodel_id or (cityjson.get("metadata") or {}).get("identifier") or "scenario"
            return self._emit_from_cityjson(cityjson, output_dir, hvac_mode, cm_id)
        except Exception as e:
            self.log_failure("from_cityjson", str(e))
            return None

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _emit_from_cityjson(
        self,
        cityjson: Dict[str, Any],
        output_dir: Optional[str],
        hvac_mode: str,
        citymodel_id: str,
    ) -> Dict[str, Any]:
        out_root = Path(output_dir or DEFAULT_OUTPUT_DIR) / _safe_name(citymodel_id)
        out_root.mkdir(parents=True, exist_ok=True)

        schedule_feature = self.get_feature("schedule") or {}
        occupants_feature = self.get_feature("occupants") or {}

        schedule_template = schedule_feature.get("template") if isinstance(schedule_feature, dict) else None
        occupant_by_bid = self._occupant_map(occupants_feature)
        schedule_by_bid = self._schedule_map(schedule_feature)

        payloads = _extract_building_payloads(cityjson)
        emitted: List[Dict[str, Any]] = []
        for p in payloads:
            bid = p["building_id"]
            building_schedule = schedule_by_bid.get(bid, schedule_template)
            occupant = occupant_by_bid.get(bid)

            emitter = _IDFEmitter(
                building_id=bid,
                building_obj=p["building_obj"],
                thermal_zones=p["thermal_zones"],
                vertices=p["vertices"],
                schedule_template=building_schedule,
                occupant_template=occupant,
                hvac_mode=hvac_mode,
            )
            idf_text = emitter.build(p["surfaces"])
            idf_path = out_root / f"{_safe_name(bid)}.idf"
            idf_path.write_text(idf_text, encoding="utf-8")
            emitted.append({
                "building_id": bid,
                "idf_path": str(idf_path),
                "surfaces": len(p["surfaces"]),
                "thermal_zones": len(p["thermal_zones"]),
            })

        index = {
            "citymodel_id": citymodel_id,
            "output_dir": str(out_root),
            "method": "from_citydb",
            "hvac_mode": hvac_mode,
            "total_buildings": len(emitted),
            "buildings": emitted,
            "schedule_library_code": (schedule_feature or {}).get("library_code"),
            "occupant_library_code": (occupants_feature or {}).get("library_code"),
        }
        index_path = out_root / "index.json"
        index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

        self.set_feature("idf_export", index)
        self.log_success(
            "from_citydb",
            f"Emitted {len(emitted)} IDF files under {out_root}",
        )
        return index

    @staticmethod
    def _occupant_map(occupants_feature: Any) -> Dict[str, Dict[str, Any]]:
        if not isinstance(occupants_feature, dict):
            return {}
        out: Dict[str, Dict[str, Any]] = {}
        for entry in occupants_feature.get("assignments") or []:
            if not entry:
                continue
            bid = entry.get("building_id")
            if bid:
                out[bid] = entry.get("occupants") or {}
        return out

    @staticmethod
    def _schedule_map(schedule_feature: Any) -> Dict[str, Dict[str, Any]]:
        if not isinstance(schedule_feature, dict):
            return {}
        out: Dict[str, Dict[str, Any]] = {}
        for entry in schedule_feature.get("assignments") or []:
            if not entry:
                continue
            bid = entry.get("building_id")
            if bid:
                out[bid] = entry.get("schedule") or {}
        return out
