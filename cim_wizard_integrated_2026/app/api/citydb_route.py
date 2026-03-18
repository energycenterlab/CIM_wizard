"""
3DCityDB REST endpoints — hierarchical read-access to CityGML data stored
in the ``citydb`` schema.

URL hierarchy (all mounted under the router prefix):

    /cityjson/{citymodel_id}                                          → CityJSON v1.1
    /{citymodel_id}                                                   → CityModel metadata
    /{citymodel_id}/cityobjects/{cityobject_id}                       → any CityObject
    /{citymodel_id}/buildings                                         → list buildings
    /{citymodel_id}/buildings/{building_id}                           → building detail
    /{citymodel_id}/buildings/{building_id}/surfaces                  → list surfaces
    /{citymodel_id}/buildings/{building_id}/surfaces/{surface_id}     → surface detail

``citymodel_id`` is the CityModel.gmlid which equals the scenario_id used
during the /map_to_citydb step.  ``building_id`` is the CityObject.gmlid
(original building UUID).  ``surface_id`` is the thematic-surface
CityObject.gmlid (e.g. "42-wall-N").
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Any, Dict, List, Optional
import json as _json

from app.db.database import get_db
from app.core.data_manager import CimWizardDataManager
from app.core.pipeline_executor import CimWizardPipelineExecutor
from app.models.citydb import (
    CityModel,
    CityObject,
    CityObjectMember,
    CityBuilding,
    ThematicSurface,
    SurfaceGeometry,
    CityObjectGenericAttrib,
)
from geoalchemy2.functions import ST_AsGeoJSON

router = APIRouter()

OC_BUILDING = 26
OC_ROOF_SURFACE = 33
OC_WALL_SURFACE = 34
OC_GROUND_SURFACE = 35

_OC_LABEL: Dict[int, str] = {
    25: "BuildingPart",
    26: "Building",
    33: "RoofSurface",
    34: "WallSurface",
    35: "GroundSurface",
}


# ── internal helpers ─────────────────────────────────────────────────


def _geom_to_geojson(db: Session, geom) -> Optional[dict]:
    if geom is None:
        return None
    raw = db.scalar(ST_AsGeoJSON(geom))
    return _json.loads(raw) if raw else None


def _ga_value(ga: CityObjectGenericAttrib):
    if ga.datatype == 1:
        return ga.strval
    if ga.datatype == 3:
        return ga.realval
    if ga.datatype == 2:
        return ga.intval
    return ga.strval or ga.realval or ga.intval


def _ga_dict(db: Session, cityobject_id: int) -> Dict[str, Any]:
    rows = (
        db.query(CityObjectGenericAttrib)
        .filter(CityObjectGenericAttrib.cityobject_id == cityobject_id)
        .all()
    )
    return {r.attrname: _ga_value(r) for r in rows}


def _resolve_citymodel(db: Session, citymodel_id: str) -> CityModel:
    cm = db.query(CityModel).filter(CityModel.gmlid == citymodel_id).first()
    if not cm:
        raise HTTPException(404, detail=f"CityModel '{citymodel_id}' not found")
    return cm


def _resolve_building(
    db: Session, cm: CityModel, building_id: str
) -> tuple:
    """Return (CityObject, CityBuilding) for a building inside a CityModel."""
    row = (
        db.query(CityObject, CityBuilding)
        .join(CityObjectMember, CityObject.id == CityObjectMember.cityobject_id)
        .join(CityBuilding, CityObject.id == CityBuilding.id)
        .filter(
            CityObjectMember.citymodel_id == cm.id,
            CityObject.gmlid == building_id,
            CityObject.objectclass_id == OC_BUILDING,
        )
        .first()
    )
    if not row:
        raise HTTPException(
            404,
            detail=f"Building '{building_id}' not found in CityModel '{cm.gmlid}'",
        )
    return row


def _serialize_co(db: Session, co: CityObject) -> dict:
    """Serialize a CityObject row to a JSON-friendly dict."""
    return {
        "id": co.id,
        "gmlid": co.gmlid,
        "name": co.name,
        "objectclass_id": co.objectclass_id,
        "type": _OC_LABEL.get(co.objectclass_id, f"objectclass_{co.objectclass_id}"),
        "description": co.description,
        "envelope": _geom_to_geojson(db, co.envelope),
        "creation_date": co.creation_date.isoformat() if co.creation_date else None,
        "termination_date": co.termination_date.isoformat() if co.termination_date else None,
        "last_modification_date": (
            co.last_modification_date.isoformat() if co.last_modification_date else None
        ),
    }


# ── CityJSON full document ──────────────────────────────────────────


@router.get("/cityjson/{citymodel_id}")
async def get_cityjson(citymodel_id: str, db: Session = Depends(get_db)):
    """
    Return a CityJSON v1.1 document for the given city model.

    ``citymodel_id`` equals the ``scenario_id`` used during the
    ``POST /map_to_citydb`` step.  The document is assembled from the
    3DCityDB ``citydb`` schema (buildings, thematic surfaces, geometry,
    generic attributes including TABULA U-values and Energy ADE data).
    """
    data_manager = CimWizardDataManager(db_session=db)
    executor = CimWizardPipelineExecutor(data_manager)

    from app.calculators.citydb_mapper_calculator import CitydbMapperCalculator

    calc = CitydbMapperCalculator(executor)
    result = calc.generate_cityjson_from_citydb(citymodel_id)

    if result is None:
        raise HTTPException(404, detail=f"CityModel '{citymodel_id}' not found")
    if not result.get("CityObjects"):
        raise HTTPException(404, detail="CityModel exists but has no mapped buildings")
    return result


# ── CityModel detail ────────────────────────────────────────────────


@router.get("/{citymodel_id}")
async def get_citymodel_detail(citymodel_id: str, db: Session = Depends(get_db)):
    """
    CityModel metadata: envelope (bounding box), name, description,
    creation date, and a member-count breakdown by object class.
    """
    cm = _resolve_citymodel(db, citymodel_id)

    member_counts: Dict[str, int] = {}
    rows = (
        db.query(CityObject.objectclass_id, func.count(CityObject.id))
        .join(CityObjectMember, CityObject.id == CityObjectMember.cityobject_id)
        .filter(CityObjectMember.citymodel_id == cm.id)
        .group_by(CityObject.objectclass_id)
        .all()
    )
    total = 0
    for oc_id, cnt in rows:
        label = _OC_LABEL.get(oc_id, f"objectclass_{oc_id}")
        member_counts[label] = cnt
        total += cnt

    return {
        "id": cm.id,
        "gmlid": cm.gmlid,
        "name": cm.name,
        "description": cm.description,
        "envelope": _geom_to_geojson(db, cm.envelope),
        "creation_date": cm.creation_date.isoformat() if cm.creation_date else None,
        "last_modification_date": (
            cm.last_modification_date.isoformat() if cm.last_modification_date else None
        ),
        "lineage": cm.lineage,
        "members": {"total": total, **member_counts},
    }


# ── Generic CityObject ──────────────────────────────────────────────


@router.get("/{citymodel_id}/cityobjects/{cityobject_id}")
async def get_cityobject(
    citymodel_id: str,
    cityobject_id: int,
    db: Session = Depends(get_db),
):
    """
    Return all stored data for any CityObject that belongs to the given
    CityModel.  ``cityobject_id`` is the numeric database primary key.
    """
    cm = _resolve_citymodel(db, citymodel_id)

    co = (
        db.query(CityObject)
        .join(CityObjectMember, CityObject.id == CityObjectMember.cityobject_id)
        .filter(
            CityObjectMember.citymodel_id == cm.id,
            CityObject.id == cityobject_id,
        )
        .first()
    )
    if not co:
        raise HTTPException(
            404,
            detail=f"CityObject {cityobject_id} not found in CityModel '{citymodel_id}'",
        )

    result = _serialize_co(db, co)
    result["generic_attributes"] = _ga_dict(db, co.id)

    if co.objectclass_id == OC_BUILDING:
        cb = db.query(CityBuilding).filter(CityBuilding.id == co.id).first()
        if cb:
            result["building"] = {
                "measured_height": cb.measured_height,
                "measured_height_unit": cb.measured_height_unit,
                "storeys_above_ground": (
                    int(cb.storeys_above_ground) if cb.storeys_above_ground else None
                ),
                "storeys_below_ground": (
                    int(cb.storeys_below_ground) if cb.storeys_below_ground else None
                ),
            }

    if co.objectclass_id in (OC_WALL_SURFACE, OC_ROOF_SURFACE, OC_GROUND_SURFACE):
        ts = db.query(ThematicSurface).filter(ThematicSurface.id == co.id).first()
        if ts:
            result["thematic_surface"] = {
                "building_id": ts.building_id,
                "surface_type": _OC_LABEL.get(ts.objectclass_id),
            }

    return result


# ── Buildings list ───────────────────────────────────────────────────


@router.get("/{citymodel_id}/buildings")
async def list_buildings(citymodel_id: str, db: Session = Depends(get_db)):
    """
    List all buildings that belong to the CityModel.  Each entry includes
    basic building properties plus a summary of its generic attributes
    (energy system, thermal zone data).
    """
    cm = _resolve_citymodel(db, citymodel_id)

    rows = (
        db.query(CityObject, CityBuilding)
        .join(CityObjectMember, CityObject.id == CityObjectMember.cityobject_id)
        .join(CityBuilding, CityObject.id == CityBuilding.id)
        .filter(
            CityObjectMember.citymodel_id == cm.id,
            CityObject.objectclass_id == OC_BUILDING,
        )
        .all()
    )

    buildings: List[dict] = []
    for co, cb in rows:
        ga = _ga_dict(db, co.id)
        surface_count = (
            db.query(func.count(ThematicSurface.id))
            .filter(ThematicSurface.building_id == co.id)
            .scalar()
        )
        buildings.append({
            "id": co.id,
            "gmlid": co.gmlid,
            "name": co.name,
            "measured_height": cb.measured_height,
            "storeys_above_ground": (
                int(cb.storeys_above_ground) if cb.storeys_above_ground else None
            ),
            "envelope_efficiency": ga.get("energySystem_envelopeEfficiency"),
            "fmu_file": ga.get("energySystem_fmuFile"),
            "thermal_zone_volume_m3": ga.get("thermalZone_volume_m3"),
            "thermal_zone_floor_area_m2": ga.get("thermalZone_floorArea_m2"),
            "surface_count": surface_count,
        })

    return {
        "citymodel_id": citymodel_id,
        "total_buildings": len(buildings),
        "buildings": buildings,
    }


# ── Building detail ──────────────────────────────────────────────────


@router.get("/{citymodel_id}/buildings/{building_id}")
async def get_building_detail(
    citymodel_id: str,
    building_id: str,
    db: Session = Depends(get_db),
):
    """
    Full detail for a single building inside the CityModel.

    Returns the building's physical properties, all generic attributes
    (thermal zone data, energy system type & efficiency, FMU file),
    and a list of its thematic surfaces with U-values.
    """
    cm = _resolve_citymodel(db, citymodel_id)
    co, cb = _resolve_building(db, cm, building_id)

    ga = _ga_dict(db, co.id)

    surfaces_rows = (
        db.query(ThematicSurface, CityObject)
        .join(CityObject, ThematicSurface.id == CityObject.id)
        .filter(ThematicSurface.building_id == co.id)
        .all()
    )

    surfaces: List[dict] = []
    for ts, ts_co in surfaces_rows:
        ts_ga = _ga_dict(db, ts.id)
        surfaces.append({
            "id": ts.id,
            "gmlid": ts_co.gmlid,
            "surface_type": _OC_LABEL.get(ts.objectclass_id, f"objectclass_{ts.objectclass_id}"),
            "u_value_w_m2k": ts_ga.get("u_value_w_m2k"),
        })

    return {
        "id": co.id,
        "gmlid": co.gmlid,
        "name": co.name,
        "envelope": _geom_to_geojson(db, co.envelope),
        "creation_date": co.creation_date.isoformat() if co.creation_date else None,
        "building": {
            "measured_height": cb.measured_height,
            "measured_height_unit": cb.measured_height_unit,
            "storeys_above_ground": (
                int(cb.storeys_above_ground) if cb.storeys_above_ground else None
            ),
            "storeys_below_ground": (
                int(cb.storeys_below_ground) if cb.storeys_below_ground else None
            ),
        },
        "energy_system": {
            "envelope_efficiency": ga.get("energySystem_envelopeEfficiency"),
            "fmu_file": ga.get("energySystem_fmuFile"),
        },
        "thermal_zone": {
            "volume_m3": ga.get("thermalZone_volume_m3"),
            "floor_area_m2": ga.get("thermalZone_floorArea_m2"),
            "number_of_floors": (
                int(ga["thermalZone_numberOfFloors"])
                if ga.get("thermalZone_numberOfFloors") is not None
                else None
            ),
        },
        "generic_attributes": ga,
        "surfaces": surfaces,
    }


# ── Surfaces list for a building ────────────────────────────────────


@router.get("/{citymodel_id}/buildings/{building_id}/surfaces")
async def list_surfaces(
    citymodel_id: str,
    building_id: str,
    db: Session = Depends(get_db),
):
    """
    List all thematic surfaces (wall, roof, ground) that belong to a
    building.  Each entry includes the surface type, U-value, and a
    flag indicating whether geometry is stored.
    """
    cm = _resolve_citymodel(db, citymodel_id)
    co, _cb = _resolve_building(db, cm, building_id)

    rows = (
        db.query(ThematicSurface, CityObject)
        .join(CityObject, ThematicSurface.id == CityObject.id)
        .filter(ThematicSurface.building_id == co.id)
        .all()
    )

    surfaces: List[dict] = []
    for ts, ts_co in rows:
        ts_ga = _ga_dict(db, ts.id)
        has_geom = (
            db.query(SurfaceGeometry.id)
            .filter(
                SurfaceGeometry.cityobject_id == ts.id,
                SurfaceGeometry.geometry.isnot(None),
            )
            .first()
            is not None
        )
        surfaces.append({
            "id": ts.id,
            "gmlid": ts_co.gmlid,
            "name": ts_co.name,
            "surface_type": _OC_LABEL.get(ts.objectclass_id, f"objectclass_{ts.objectclass_id}"),
            "u_value_w_m2k": ts_ga.get("u_value_w_m2k"),
            "has_geometry": has_geom,
        })

    return {
        "citymodel_id": citymodel_id,
        "building_id": building_id,
        "total_surfaces": len(surfaces),
        "surfaces": surfaces,
    }


# ── Surface detail ───────────────────────────────────────────────────


@router.get("/{citymodel_id}/buildings/{building_id}/surfaces/{surface_id}")
async def get_surface_detail(
    citymodel_id: str,
    building_id: str,
    surface_id: str,
    db: Session = Depends(get_db),
):
    """
    Full detail for a single thematic surface, including its GeoJSON
    geometry and all generic attributes (U-value, etc.).

    ``surface_id`` is the thematic-surface CityObject.gmlid.
    """
    cm = _resolve_citymodel(db, citymodel_id)
    co, _cb = _resolve_building(db, cm, building_id)

    ts_row = (
        db.query(ThematicSurface, CityObject)
        .join(CityObject, ThematicSurface.id == CityObject.id)
        .filter(
            ThematicSurface.building_id == co.id,
            CityObject.gmlid == surface_id,
        )
        .first()
    )
    if not ts_row:
        raise HTTPException(
            404,
            detail=(
                f"Surface '{surface_id}' not found for building '{building_id}' "
                f"in CityModel '{citymodel_id}'"
            ),
        )

    ts, ts_co = ts_row
    ts_ga = _ga_dict(db, ts.id)

    geom_rows = (
        db.query(
            SurfaceGeometry.id,
            SurfaceGeometry.gmlid,
            func.ST_AsGeoJSON(SurfaceGeometry.geometry).label("geojson"),
        )
        .filter(
            SurfaceGeometry.cityobject_id == ts.id,
            SurfaceGeometry.geometry.isnot(None),
        )
        .all()
    )

    geometries: List[dict] = []
    for sg_id, sg_gmlid, geojson_str in geom_rows:
        geometries.append({
            "surface_geometry_id": sg_id,
            "gmlid": sg_gmlid,
            "geometry": _json.loads(geojson_str) if geojson_str else None,
        })

    return {
        "id": ts.id,
        "gmlid": ts_co.gmlid,
        "name": ts_co.name,
        "surface_type": _OC_LABEL.get(ts.objectclass_id, f"objectclass_{ts.objectclass_id}"),
        "building_id": ts.building_id,
        "building_gmlid": building_id,
        "envelope": _geom_to_geojson(db, ts_co.envelope),
        "creation_date": ts_co.creation_date.isoformat() if ts_co.creation_date else None,
        "u_value_w_m2k": ts_ga.get("u_value_w_m2k"),
        "generic_attributes": ts_ga,
        "geometries": geometries,
    }
