"""
Network Gateway Routes - Endpoints for cim_network schema
Grid lines and buses from network_scenarios, scenario_lines, scenario_buses,
network_lines, and network_buses tables.
Uses raw SQL with dynamic column reflection to return all attributes.
"""

import json
from datetime import date, datetime
from typing import List, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from app.db.database import get_db, engine
from app.models.network import NetworkScenario

router = APIRouter()

# Cache reflected column info: (non-geom cols, has_geometry)
_LINE_COLS_CACHE = None
_BUS_COLS_CACHE = None


def _get_line_columns() -> Tuple[List[str], bool]:
    """Get (non-geometry column names, has_geometry) for network_lines."""
    global _LINE_COLS_CACHE
    if _LINE_COLS_CACHE is not None:
        return _LINE_COLS_CACHE
    inspector = inspect(engine)
    cols = inspector.get_columns("network_lines", schema="cim_network")
    all_names = [c["name"] for c in cols]
    has_geom = "geometry" in all_names
    non_geom = [n for n in all_names if n != "geometry"]
    _LINE_COLS_CACHE = (non_geom, has_geom)
    return _LINE_COLS_CACHE


def _get_bus_columns() -> Tuple[List[str], bool]:
    """Get (non-geometry column names, has_geometry) for network_buses."""
    global _BUS_COLS_CACHE
    if _BUS_COLS_CACHE is not None:
        return _BUS_COLS_CACHE
    inspector = inspect(engine)
    cols = inspector.get_columns("network_buses", schema="cim_network")
    all_names = [c["name"] for c in cols]
    has_geom = "geometry" in all_names
    non_geom = [n for n in all_names if n != "geometry"]
    _BUS_COLS_CACHE = (non_geom, has_geom)
    return _BUS_COLS_CACHE


def _row_to_dict(row, geom_key: str = "geometry") -> dict:
    """Convert a Row to dict, parsing geometry GeoJSON and serializing dates."""
    d = dict(row._mapping) if hasattr(row, "_mapping") else dict(row)
    # geometry comes as GeoJSON string from ST_AsGeoJSON; parse to dict if needed
    if geom_key in d and d[geom_key] is not None:
        val = d[geom_key]
        if isinstance(val, str):
            try:
                d[geom_key] = json.loads(val)
            except json.JSONDecodeError:
                pass
    # serialize datetime/date for JSON
    for k, v in list(d.items()):
        if isinstance(v, (datetime, date)):
            d[k] = v.isoformat()
    return d


def _fetch_lines(db: Session, scenario_id: str, limit: int, offset: int) -> list:
    """Fetch lines with all attributes using raw SQL."""
    cols, has_geom = _get_line_columns()
    parts = [f'nl."{c}"' for c in cols]
    if has_geom:
        parts.append("ST_AsGeoJSON(nl.geometry)::text AS geometry")
    select_list = ", ".join(parts) if parts else "nl.line_id"
    sql = text(f"""
        SELECT {select_list}
        FROM cim_network.network_lines nl
        JOIN cim_network.scenario_lines sl ON sl.line_id = nl.line_id
        WHERE sl.scenario_id = :scenario_id
        ORDER BY nl.line_id
        LIMIT :limit OFFSET :offset
    """)
    result = db.execute(sql, {"scenario_id": scenario_id, "limit": limit, "offset": offset})
    return [_row_to_dict(row) for row in result]


def _fetch_buses(db: Session, scenario_id: str, limit: int, offset: int) -> list:
    """Fetch buses with all attributes using raw SQL."""
    cols, has_geom = _get_bus_columns()
    parts = [f'nb."{c}"' for c in cols]
    if has_geom:
        parts.append("ST_AsGeoJSON(nb.geometry)::text AS geometry")
    select_list = ", ".join(parts) if parts else "nb.bus_id"
    sql = text(f"""
        SELECT {select_list}
        FROM cim_network.network_buses nb
        JOIN cim_network.scenario_buses sb ON sb.bus_id = nb.bus_id
        WHERE sb.scenario_id = :scenario_id
        ORDER BY nb.bus_id
        LIMIT :limit OFFSET :offset
    """)
    result = db.execute(sql, {"scenario_id": scenario_id, "limit": limit, "offset": offset})
    return [_row_to_dict(row) for row in result]


@router.get("/scenarios")
async def get_network_scenarios(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all network scenarios"""
    try:
        scenarios = (
            db.query(NetworkScenario)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [{"scenario_id": s.scenario_id} for s in scenarios]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/lines/{scenario_id}")
async def get_network_lines(
    scenario_id: str,
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get grid lines for a network scenario.
    Joins scenario_lines with network_lines on line_id.
    Returns all attributes (geometry + other columns) for each line.
    """
    try:
        return _fetch_lines(db, scenario_id, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/buses/{scenario_id}")
async def get_network_buses(
    scenario_id: str,
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get grid buses for a network scenario.
    Joins scenario_buses with network_buses on bus_id.
    Returns all attributes (geometry + other columns) for each bus.
    """
    try:
        return _fetch_buses(db, scenario_id, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/grid/{scenario_id}")
async def get_network_grid(
    scenario_id: str,
    limit_lines: int = Query(1000, ge=1, le=10000),
    limit_buses: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get both grid lines and buses for a network scenario in one response.
    Returns all attributes for each line and bus.
    """
    try:
        lines = _fetch_lines(db, scenario_id, limit_lines, offset)
        buses = _fetch_buses(db, scenario_id, limit_buses, offset)
        return {
            "scenario_id": scenario_id,
            "lines": lines,
            "buses": buses,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/health")
async def network_health():
    """Health check for network gateway routes"""
    return {"status": "healthy", "service": "network_gateway"}
