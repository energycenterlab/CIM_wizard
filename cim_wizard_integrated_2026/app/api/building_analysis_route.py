"""
Building Analysis Pipeline Route - Executes building-specific calculators
Focuses on physical building properties without demographic calculations
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import uuid

from app.db.database import get_db
from app.core.data_manager import CimWizardDataManager
from app.core.pipeline_executor import CimWizardPipelineExecutor
from app.core.normalizer import normalize_input, validate

router = APIRouter()


def get_pipeline_executor(db: Session):
    """Create pipeline executor with database session"""
    data_manager = CimWizardDataManager(db_session=db)
    executor = CimWizardPipelineExecutor(data_manager)
    return executor, data_manager


@router.post("/execute_building_analysis")
async def execute_building_analysis(
    request_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Execute building analysis calculator chain.

    Input:
    - project_boundary: GeoJSON FeatureCollection or Feature with the project boundary
    - project_name: Optional project name (default: "Building_Analysis")
    - scenario_name: Optional scenario name (default: "Current_State")
    - save_to_db: Whether to save results to database (default: true)
    """
    try:
        request_data = normalize_input("project_scenario", request_data)

        validation_errors = validate("project_scenario", request_data, partial=True)
        if validation_errors:
            print(f"Input validation warnings: {validation_errors}")

        executor, data_manager = get_pipeline_executor(db)

        project_boundary = request_data.get('project_boundary')
        if not project_boundary:
            raise HTTPException(status_code=400, detail="Missing project_boundary in request")

        project_name = request_data.get('project_name', 'Building_Analysis')
        scenario_name = request_data.get('scenario_name', None)
        save_to_db = request_data.get('save_to_db', True)

        project_id = str(uuid.uuid4())

        if not scenario_name:
            scenario_name = 'baseline'
            scenario_id = project_id
        else:
            scenario_id = str(uuid.uuid4())

        data_manager.set_context(
            project_id=project_id,
            scenario_id=scenario_id,
            project_name=project_name,
            scenario_name=scenario_name,
            db_session=db
        )

        if project_boundary.get('type') == 'FeatureCollection':
            features = project_boundary.get('features', [])
            if features:
                scenario_geo_input = features[0]
            else:
                raise HTTPException(status_code=400, detail="FeatureCollection has no features")
        else:
            scenario_geo_input = project_boundary

        data_manager.set_feature('scenario_geo', scenario_geo_input)
        data_manager.set_feature('project_boundary', project_boundary)

        calculation_chain = [
            {"feature_name": "scenario_geo", "method_name": "calculate_from_scenario_geo",
             "description": "Initialize scenario geometry from project boundary"},
            {"feature_name": "scenario_census_boundary", "method_name": "calculate_from_census_api",
             "description": "Get census boundary (simplified for building analysis)"},
            {"feature_name": "building_geo", "method_name": "calculate_from_scenario_census_geo",
             "description": "Extract buildings from the area"},
            {"feature_name": "building_props", "method_name": "init",
             "description": "Initialize building properties"},
            {"feature_name": "building_height", "method_name": "calculate_from_raster_tiles",
             "description": "Calculate building heights from DSM-DTM raster tiles"},
            {"feature_name": "building_area", "method_name": "calculate_from_geometry",
             "description": "Calculate building footprint areas"},
            {"feature_name": "filter_res", "method_name": "calculate_filter_res",
             "description": "Filter residential vs non-residential buildings"},
            {"feature_name": "building_volume", "method_name": "calculate_from_height_and_area",
             "description": "Calculate building volumes (residential buildings only)"},
            {"feature_name": "building_n_floors", "method_name": "estimate_by_height",
             "description": "Estimate number of floors from height (residential only)"},
            {"feature_name": "census_population", "method_name": "calculate_from_census_boundary",
             "description": "Get total population from census zones"},
            {"feature_name": "building_type", "method_name": "by_census_osm",
             "description": "Classify building types using census and OSM data"},
            {"feature_name": "building_population", "method_name": "calculate_from_volume_distribution",
             "description": "Distribute census population to buildings by volume ratio"},
            {"feature_name": "building_n_families", "method_name": "calculate_from_population",
             "description": "Calculate number of families per building"},
            {"feature_name": "building_construction_year", "method_name": "by_census_osm",
             "description": "Estimate construction year, census period, and TABULA classification"},
            {"feature_name": "building_demographic", "method_name": "by_census_osm",
             "description": "Orchestrate demographic calculation (population + families)"},
            {"feature_name": "building_geo_lod12", "method_name": "by_footprint_height",
             "description": "Generate LoD 1.2 3D building geometry from footprint and height"},
            {"feature_name": "envelope_efficiency", "method_name": "assign_random",
             "description": "Assign random envelope efficiency (low/medium/high) per building"},
            {"feature_name": "fmu_assign", "method_name": "frassinetto",
             "description": "Assign FMU file identifier (frassinetto) to all building-scenarios"},
        ]

        results = {}
        successful_calculations = []
        failed_calculations = []
        execution_chain = []
        database_updates = []

        # Feature-name to DB column mapping (used for post-calculation persistence)
        _FEATURE_DB_MAP = {
            "building_height":           ("height",              lambda r: r if isinstance(r, list) else []),
            "building_area":             ("area",                lambda r: r.get('building_areas', []) or [bp.get('area', 0) for bp in r.get('building_properties', [])]),
            "building_volume":           ("volume",              lambda r: r.get('building_volumes', [])),
            "building_n_floors":         ("number_of_floors",    lambda r: r.get('building_floors', [])),
            "filter_res":                ("filter_res",          lambda r: r.get('filter_res', []) if isinstance(r, dict) else []),
            "building_type":             ("type",                lambda r: r.get('building_types', []) if isinstance(r, dict) else (r if isinstance(r, list) else [])),
            "building_population":       ("n_people",            lambda r: r.get('building_populations', []) if isinstance(r, dict) else (r if isinstance(r, list) else [])),
            "building_n_families":       ("n_family",            lambda r: r.get('building_families', []) if isinstance(r, dict) else (r if isinstance(r, list) else [])),
        }

        for step_num, calc_config in enumerate(calculation_chain, 1):
            feature_name = calc_config["feature_name"]
            method_name = calc_config["method_name"]
            description = calc_config["description"]

            print(f"\n=== Step {step_num}/{len(calculation_chain)}: {feature_name} ===")

            success = executor.execute_feature(feature_name, method_name)
            result = data_manager.get_feature(feature_name)

            execution_info = {
                "step": step_num,
                "feature": feature_name,
                "method": method_name,
                "description": description,
                "status": "success" if success else "failed",
            }

            if not success:
                execution_info["error"] = "Unknown error"
                failed_calculations.append(feature_name)
            else:
                successful_calculations.append(feature_name)
                results[feature_name] = result

                if save_to_db and result:
                    db_update_status = {
                        "feature": feature_name,
                        "updated_records": 0,
                        "status": "pending",
                    }
                    try:
                        if feature_name == "scenario_geo":
                            ok = data_manager.save_scenario(
                                project_id, scenario_id,
                                project_name, scenario_name, result
                            )
                            db_update_status["updated_records"] = 1 if ok else 0
                            db_update_status["status"] = "success" if ok else "failed"

                        elif feature_name == "building_geo":
                            buildings = result.get('buildings', [])
                            saved = sum(
                                1 for b in buildings
                                if data_manager.save_building(b)
                            )
                            db_update_status["updated_records"] = saved
                            db_update_status["status"] = "success"

                        elif feature_name == "building_construction_year":
                            if isinstance(result, dict):
                                building_geo_result = results.get('building_geo', {})
                                bldgs = building_geo_result.get('buildings', [])
                                total = 0
                                for col, key in [("const_year", "const_years"),
                                                 ("const_period_census", "const_periods"),
                                                 ("const_tabula", "const_tabulas")]:
                                    vals = result.get(key, [])
                                    if vals:
                                        total += data_manager.upsert_building_properties_batch(
                                            bldgs, project_id, scenario_id, col, vals
                                        )
                                db_update_status["updated_records"] = total
                                db_update_status["status"] = "success"

                        elif feature_name == "building_geo_lod12":
                            from app.models.vector import Building
                            lod12_items = result.get('building_lod12_data', [])
                            updated = 0
                            for item in lod12_items:
                                bid = item.get('building_id')
                                if not bid:
                                    continue
                                bldg = db.query(Building).filter_by(
                                    building_id=bid, lod=0
                                ).first()
                                if bldg:
                                    bldg.building_surfaces_lod12 = {
                                        'surfaces': item.get('surfaces'),
                                        'metadata': item.get('metadata'),
                                    }
                                    updated += 1
                            db.commit()
                            db_update_status["updated_records"] = updated
                            db_update_status["status"] = "success"

                        elif feature_name in _FEATURE_DB_MAP:
                            col_name, extractor = _FEATURE_DB_MAP[feature_name]
                            values = extractor(result)
                            if values:
                                building_geo_result = results.get('building_geo', {})
                                updated = data_manager.upsert_building_properties_batch(
                                    building_geo_result.get('buildings', []),
                                    project_id, scenario_id, col_name, values,
                                )
                                db_update_status["updated_records"] = updated
                                db_update_status["status"] = "success"
                            else:
                                db_update_status["status"] = "success"
                                db_update_status["note"] = "No values to persist"

                        else:
                            db_update_status["status"] = "success"
                            db_update_status["note"] = "No direct DB column"

                        database_updates.append(db_update_status)
                    except Exception as e:
                        db_update_status["status"] = "failed"
                        db_update_status["error"] = str(e)
                        database_updates.append(db_update_status)
                        import traceback
                        traceback.print_exc()

            execution_chain.append(execution_info)

        building_geo_result = results.get('building_geo', {})
        total_buildings = building_geo_result.get('total_buildings', 0)

        response = {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "project_name": project_name,
            "scenario_name": scenario_name,
            "execution_chain": execution_chain,
            "successful_calculations": successful_calculations,
            "failed_calculations": failed_calculations,
            "results": results,
            "database_updates": database_updates if save_to_db else [],
            "summary": {
                "total_buildings": total_buildings,
                "buildings_with_height": len(results.get('building_height', [])) if isinstance(results.get('building_height'), list) else 0,
                "buildings_with_area": len(results.get('building_area', {}).get('building_properties', [])),
                "buildings_with_volume": len(results.get('building_volume', {}).get('building_volumes', [])),
                "buildings_with_floors": len(results.get('building_n_floors', {}).get('building_floors', [])),
                "buildings_with_filter_res": results.get('filter_res', {}).get('total_buildings', 0) if results.get('filter_res') else 0,
                "residential_buildings": results.get('filter_res', {}).get('residential_count', 0) if results.get('filter_res') else 0,
                "census_population": results.get('census_population') if results.get('census_population') else 0,
                "buildings_with_population": len(results.get('building_population', {}).get('building_populations', [])) if isinstance(results.get('building_population'), dict) else 0,
                "buildings_with_families": len(results.get('building_n_families', {}).get('building_families', [])) if isinstance(results.get('building_n_families'), dict) else 0,
                "buildings_with_construction_year": 1 if results.get('building_construction_year') else 0,
            },
            "metadata": {
                "total_steps": len(calculation_chain),
                "successful_steps": len(successful_calculations),
                "failed_steps": len(failed_calculations),
                "success_rate": f"{(len(successful_calculations) / len(calculation_chain) * 100):.1f}%",
                "database_updates_enabled": save_to_db,
                "pipeline_version": "2.0.0",
            },
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lod12_geojson")
async def get_lod12_geojson(
    project_id: str,
    scenario_id: str,
    db: Session = Depends(get_db),
):
    """
    Return LoD 1.2 building surfaces as a GeoJSON FeatureCollection.

    Each semantic surface (wall, roof, ground) is emitted as a separate
    Feature with full 3D (Z) coordinates.  The result is directly usable
    by CesiumJS with ``clampToGround: false`` and ``perPositionHeight: true``.

    Query params:
        project_id  – UUID of the project
        scenario_id – UUID of the scenario
    """
    from sqlalchemy import and_
    from app.models.vector import Building, BuildingProperties

    rows = (
        db.query(Building)
        .join(
            BuildingProperties,
            Building.building_id == BuildingProperties.building_id,
        )
        .filter(
            and_(
                BuildingProperties.project_id == project_id,
                BuildingProperties.scenario_id == scenario_id,
            )
        )
        .filter(Building.building_surfaces_lod12.isnot(None))
        .all()
    )

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No LoD 1.2 data found for this project/scenario",
        )

    features: List[Dict[str, Any]] = []

    for bldg in rows:
        lod12 = bldg.building_surfaces_lod12
        surfaces = lod12.get("surfaces", {})
        metadata = lod12.get("metadata", {})
        building_height = metadata.get("building_height")

        shared_props = {
            "building_id": bldg.building_id,
            "lod": 1.2,
            "building_height": building_height,
        }

        for wall in surfaces.get("wall_surfaces", []):
            features.append({
                "type": "Feature",
                "geometry": wall.get("geometry"),
                "properties": {
                    **shared_props,
                    "surface_type": "WallSurface",
                    "surface_id": wall.get("surface_id"),
                    "area_m2": wall.get("properties", {}).get("area_m2"),
                    "orientation": wall.get("properties", {}).get("orientation"),
                    "azimuth_degrees": wall.get("properties", {}).get("azimuth_degrees"),
                },
            })

        roof = surfaces.get("roof_surface")
        if roof:
            features.append({
                "type": "Feature",
                "geometry": roof.get("geometry"),
                "properties": {
                    **shared_props,
                    "surface_type": "RoofSurface",
                    "surface_id": roof.get("surface_id"),
                    "area_m2": roof.get("properties", {}).get("area_m2"),
                    "roof_type": roof.get("properties", {}).get("roof_type"),
                },
            })

        ground = surfaces.get("ground_surface")
        if ground:
            features.append({
                "type": "Feature",
                "geometry": ground.get("geometry"),
                "properties": {
                    **shared_props,
                    "surface_type": "GroundSurface",
                    "surface_id": ground.get("surface_id"),
                    "area_m2": ground.get("properties", {}).get("area_m2"),
                },
            })

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "total_buildings": len(rows),
            "total_surfaces": len(features),
            "lod": 1.2,
            "coordinate_system": "EPSG:4326",
            "height_reference": "relative_to_ground",
        },
    }
