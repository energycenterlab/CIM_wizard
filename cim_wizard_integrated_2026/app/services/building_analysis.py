"""Synchronous building-analysis pipeline (runs in Celery or sync HTTP)."""

from typing import Any, Callable, Dict, Optional
import uuid

from sqlalchemy.orm import Session

from app.core.data_manager import CimWizardDataManager
from app.core.pipeline_executor import CimWizardPipelineExecutor
from app.core.normalizer import normalize_input, validate

ProgressCb = Optional[Callable[[int, int, str], None]]


CALCULATION_CHAIN = [
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
    {"feature_name": "building_tabula_type", "method_name": "from_year_and_type",
     "description": "Derive TABULA typology code from construction year + building type"},
    {"feature_name": "building_demographic", "method_name": "by_census_osm",
     "description": "Orchestrate demographic calculation (population + families)"},
    {"feature_name": "envelope_efficiency", "method_name": "assign_random",
     "description": "Assign random envelope efficiency (low/medium/high) per building"},
    {"feature_name": "fmu_assign", "method_name": "frassinetto",
     "description": "Assign FMU file identifier (frassinetto) to all building-scenarios"},
    {"feature_name": "building_z_value", "method_name": "calculate_from_dtm",
     "description": "Calculate average DTM z-value at building footprint"},
    {"feature_name": "building_name", "method_name": "assign_sequential",
     "description": "Assign sequential building names (BUI-0001, BUI-0002, …)"},
]

_FEATURE_DB_MAP = {
    "building_height":           ("height",              lambda r: r if isinstance(r, list) else []),
    "building_area":             ("area",                lambda r: r.get('building_areas', []) or [bp.get('area', 0) for bp in r.get('building_properties', [])]),
    "building_volume":           ("volume",              lambda r: r.get('building_volumes', [])),
    "building_n_floors":         ("number_of_floors",    lambda r: r.get('building_floors', [])),
    "filter_res":                ("filter_res",          lambda r: r.get('filter_res', []) if isinstance(r, dict) else []),
    "building_type":             ("type",                lambda r: r.get('building_types', []) if isinstance(r, dict) else (r if isinstance(r, list) else [])),
    "building_population":       ("n_people",            lambda r: r.get('building_populations', []) if isinstance(r, dict) else (r if isinstance(r, list) else [])),
    "building_n_families":       ("n_family",            lambda r: r.get('building_families', []) if isinstance(r, dict) else (r if isinstance(r, list) else [])),
    "building_tabula_type":      ("tabula_type",         lambda r: r.get('tabula_types', []) if isinstance(r, dict) else []),
}


def allocate_project_ids(request_data: dict) -> dict:
    project_name = request_data.get("project_name", "Building_Analysis")
    scenario_name = request_data.get("scenario_name", None)
    project_id = str(uuid.uuid4())
    if not scenario_name:
        scenario_name = "baseline"
        scenario_id = project_id
    else:
        scenario_id = str(uuid.uuid4())
    return {
        "project_id": project_id,
        "scenario_id": scenario_id,
        "project_name": project_name,
        "scenario_name": scenario_name,
    }


def scenario_geo_from_boundary(project_boundary: dict) -> dict:
    if not project_boundary:
        raise ValueError("Missing project_boundary in request")
    if project_boundary.get("type") == "FeatureCollection":
        features = project_boundary.get("features", [])
        if not features:
            raise ValueError("FeatureCollection has no features")
        return features[0]
    return project_boundary


def job_summary(response: dict) -> dict:
    """Slim payload stored on the job row (full geometries live in the DB)."""
    return {
        "project_id": response.get("project_id"),
        "scenario_id": response.get("scenario_id"),
        "project_name": response.get("project_name"),
        "scenario_name": response.get("scenario_name"),
        "successful_calculations": response.get("successful_calculations"),
        "failed_calculations": response.get("failed_calculations"),
        "database_updates": response.get("database_updates"),
        "summary": response.get("summary"),
        "metadata": response.get("metadata"),
    }


def run_building_analysis(
    db: Session,
    request_data: dict,
    project_id: str,
    scenario_id: str,
    on_progress: ProgressCb = None,
) -> dict:
    request_data = normalize_input("project_scenario", request_data)
    validation_errors = validate("project_scenario", request_data, partial=True)
    if validation_errors:
        print(f"Input validation warnings: {validation_errors}")

    data_manager = CimWizardDataManager(db_session=db)
    executor = CimWizardPipelineExecutor(data_manager)

    project_boundary = request_data.get("project_boundary")
    scenario_geo_input = scenario_geo_from_boundary(project_boundary)

    project_name = request_data.get("project_name", "Building_Analysis")
    scenario_name = request_data.get("scenario_name") or "baseline"
    save_to_db = request_data.get("save_to_db", True)

    data_manager.set_context(
        project_id=project_id,
        scenario_id=scenario_id,
        project_name=project_name,
        scenario_name=scenario_name,
        db_session=db,
    )
    data_manager.set_feature("scenario_geo", scenario_geo_input)
    data_manager.set_feature("project_boundary", project_boundary)

    results: Dict[str, Any] = {}
    successful_calculations = []
    failed_calculations = []
    execution_chain = []
    database_updates = []

    total = len(CALCULATION_CHAIN)
    for step_num, calc_config in enumerate(CALCULATION_CHAIN, 1):
        feature_name = calc_config["feature_name"]
        method_name = calc_config["method_name"]
        description = calc_config["description"]

        print(f"\n=== Step {step_num}/{total}: {feature_name} ===")
        if on_progress:
            on_progress(step_num, total, feature_name)

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
                            project_name, scenario_name, result,
                        )
                        db_update_status["updated_records"] = 1 if ok else 0
                        db_update_status["status"] = "success" if ok else "failed"

                    elif feature_name == "building_geo":
                        buildings = result.get("buildings", [])
                        saved = sum(1 for b in buildings if data_manager.save_building(b))
                        db_update_status["updated_records"] = saved
                        db_update_status["status"] = "success"

                    elif feature_name == "building_construction_year":
                        if isinstance(result, dict):
                            bldgs = results.get("building_geo", {}).get("buildings", [])
                            total_upd = 0
                            for col, key in [
                                ("const_year", "const_years"),
                                ("const_period_census", "const_periods"),
                                ("const_tabula", "const_tabulas"),
                            ]:
                                vals = result.get(key, [])
                                if vals:
                                    total_upd += data_manager.upsert_building_properties_batch(
                                        bldgs, project_id, scenario_id, col, vals,
                                    )
                            db_update_status["updated_records"] = total_upd
                            db_update_status["status"] = "success"

                    elif feature_name == "building_tabula_type":
                        if isinstance(result, dict):
                            bldgs = results.get("building_geo", {}).get("buildings", [])
                            total_upd = 0
                            for col, key in [
                                ("tabula_type", "tabula_types"),
                                ("const_tabula", "const_tabulas"),
                            ]:
                                vals = result.get(key, [])
                                if vals:
                                    total_upd += data_manager.upsert_building_properties_batch(
                                        bldgs, project_id, scenario_id, col, vals,
                                    )
                            db_update_status["updated_records"] = total_upd
                            db_update_status["status"] = "success"

                    elif feature_name in _FEATURE_DB_MAP:
                        col_name, extractor = _FEATURE_DB_MAP[feature_name]
                        values = extractor(result)
                        if values:
                            bldgs = results.get("building_geo", {}).get("buildings", [])
                            updated = data_manager.upsert_building_properties_batch(
                                bldgs, project_id, scenario_id, col_name, values,
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

    building_geo_result = results.get("building_geo", {})
    total_buildings = building_geo_result.get("total_buildings", 0)

    return {
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
            "buildings_with_height": len(results.get("building_height", [])) if isinstance(results.get("building_height"), list) else 0,
            "buildings_with_area": len(results.get("building_area", {}).get("building_properties", [])),
            "buildings_with_volume": len(results.get("building_volume", {}).get("building_volumes", [])),
            "buildings_with_floors": len(results.get("building_n_floors", {}).get("building_floors", [])),
            "buildings_with_filter_res": results.get("filter_res", {}).get("total_buildings", 0) if results.get("filter_res") else 0,
            "residential_buildings": results.get("filter_res", {}).get("residential_count", 0) if results.get("filter_res") else 0,
            "census_population": results.get("census_population") if results.get("census_population") else 0,
            "buildings_with_population": len(results.get("building_population", {}).get("building_populations", [])) if isinstance(results.get("building_population"), dict) else 0,
            "buildings_with_families": len(results.get("building_n_families", {}).get("building_families", [])) if isinstance(results.get("building_n_families"), dict) else 0,
            "buildings_with_construction_year": 1 if results.get("building_construction_year") else 0,
        },
        "metadata": {
            "total_steps": total,
            "successful_steps": len(successful_calculations),
            "failed_steps": len(failed_calculations),
            "success_rate": f"{(len(successful_calculations) / total * 100):.1f}%",
            "database_updates_enabled": save_to_db,
            "pipeline_version": "2.0.0",
        },
    }


def run_assign_pv(db: Session, project_id: str, scenario_id: str, lod: int, offset_m: float) -> dict:
    from app.calculators.pv_generator_calculator import PvGeneratorCalculator

    data_manager = CimWizardDataManager(db_session=db)
    executor = CimWizardPipelineExecutor(data_manager)
    calc = PvGeneratorCalculator(executor)
    result = calc.assign_pv_to_buildings(
        project_id, scenario_id, lod=int(lod), offset_m=offset_m,
    )
    if not result:
        raise RuntimeError("PV assignment failed")
    return result


def run_map_to_citydb(
    db: Session,
    project_id: str,
    scenario_id: str,
    lod12_method: str,
    force_lod12: bool = False,
    force_remap: bool = False,
) -> dict:
    from app.calculators.citydb_mapper_calculator import CitydbMapperCalculator

    data_manager = CimWizardDataManager(db_session=db)
    executor = CimWizardPipelineExecutor(data_manager)
    calc = CitydbMapperCalculator(executor)
    return calc.map_scenario_to_citydb(
        project_id, scenario_id, lod12_method,
        force_lod12=force_lod12, force_remap=force_remap,
    )
