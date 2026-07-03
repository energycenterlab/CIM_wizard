#!/usr/bin/env python3
"""Generate citygml-energyade-field-mapping.csv from schema dictionary + CIM rules."""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_CSV = ROOT / "cim-database" / "citydb_schema_dictionary.csv"
OUT_CSV = Path(__file__).resolve().parent / "citygml-energyade-field-mapping.csv"

GEO_DIRECT = {
    "address.multi_point",
    "citymodel.envelope",
    "cityobject.envelope",
    "feature.envelope",
    "geometry_data.geometry",
    "geometry_data.implicit_geometry",
    "surface_data.gt_reference_point",
    "surface_geometry.geometry",
    "surface_geometry.solid_geometry",
    "property.val_implicitgeom_refpoint",
    "ng2_cityobject.ref_point",
    "ng2_weather_data.position",
}
GEO_FK_TABLES = {
    "building",
    "appearance",
    "thematic_surface",
    "appear_to_surface_data",
    "surface_data_mapping",
    "implicit_geometry",
    "ng2_building_partition",
    "ng2_solar_collector",
}
DB_INIT_TABLES = {
    "ade",
    "codelist",
    "codelist_entry",
    "database_srs",
    "datatype",
    "namespace",
    "objectclass",
}
DEFERRED_OCCUPANTS = {"ng2_occupants"}
DEFERRED_SCHEDULES = {"ng2_schedule", "ng2_schedule_component"}
DEFERRED_WEATHER = {"ng2_weather_data"}
POSTSIM_TABLES = {"ng2_resource", "ng2_storage_device"}

# TABULA archetype extraction (building_tabula_archetype_calculator + materiale-tabula XLS)
TABULA_CALC = "building_tabula_archetype_calculator"
TABULA_CIM = "cim-database/materiale-tabula + tabula_archetype_code"

NG2_TABULA_METHOD: dict[str, str] = {
    "ng2_building": "tabula_extract_ng2_building",
    "ng2_layered_construction": "tabula_extract_layered_construction",
    "ng2_qualified_attribute": "tabula_extract_qualified_attribute",
    "ng2_material": "tabula_extract_material_layers",
    "ng2_layer": "tabula_extract_material_layers",
    "ng2_opening": "tabula_extract_opening",
    "ng2_optical_property": "tabula_extract_optical_property",
    "ng2_thematic_surface": "tabula_extract_thematic_surface",
}
NO_PLAN_TABLES = {
    "address",
    "ng2_address_to_building_unit",
    "feature",
    "property",
    "geometry_data",
    "appearance",
    "appear_to_surface_data",
    "surface_data",
    "surface_data_mapping",
    "tex_image",
    "implicit_geometry",
    "ng2_ctyobj_relation",
    "ng2_energy_perf_cert",
    "ng2_library",
    "ng2_suitability",
    "ng2_urban_function_area",
}

# Explicit per-column overrides: (table, column) -> dict
COLUMN_RULES: dict[tuple[str, str], dict] = {
    # citymodel
    ("citymodel", "gmlid"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_project_scenario.scenario_id",
        "logic": "Map scenario UUID to CityModel gmlid.",
        "status": "MAPPED",
    },
    ("citymodel", "name"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_project_scenario.scenario_id",
        "logic": "Synthetic name CIM-Scenario-{scenario_id[:8]}.",
        "status": "MAPPED",
    },
    ("citymodel", "description"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_project_scenario.project_id",
        "logic": "Description text project {project_id}.",
        "status": "MAPPED",
    },
    ("citymodel", "envelope"): {
        "calculator": "ctdb_envelope_calculator",
        "method": "ctdb_citymodel_envelope",
        "cim_source": "citydb.surface_geometry.geometry",
        "logic": "ST_Envelope(ST_Collect(member building surface geometries)).",
        "status": "PLANNED-1",
    },
    # cityobject building
    ("cityobject", "gmlid"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_building.building_id",
        "logic": "Map building UUID to building CityObject gmlid.",
        "status": "MAPPED",
    },
    ("cityobject", "name"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_building.building_name",
        "logic": "building_name or fallback BUI-{building_id[:8]}.",
        "status": "MAPPED",
    },
    ("cityobject", "objectclass_id"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "constant:26",
        "logic": "Fixed objectclass_id=26 (Building).",
        "status": "MAPPED",
    },
    ("cityobject", "creation_date"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "db_default",
        "logic": "PostgreSQL default now() on insert.",
        "status": "MAPPED",
    },
    ("cityobject", "envelope"): {
        "calculator": "ctdb_envelope_calculator",
        "method": "ctdb_citymodel_envelope",
        "cim_source": "citydb.surface_geometry.geometry",
        "logic": "ST_Envelope of all surfaces belonging to this building.",
        "status": "PLANNED-1",
    },
    # building
    ("building", "measured_height"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_building_properties.height",
        "logic": "Direct copy from building_properties.height.",
        "status": "MAPPED",
    },
    ("building", "measured_height_unit"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "constant:m",
        "logic": "Literal m when height present.",
        "status": "MAPPED",
    },
    ("building", "storeys_above_ground"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_building_properties.number_of_floors",
        "logic": "Cast number_of_floors to integer storeys_above_ground.",
        "status": "MAPPED",
    },
    ("building", "storeys_below_ground"): {
        "calculator": "ctdb_building_semantic_calculator",
        "method": "ctdb_from_cim",
        "cim_source": "cim_vector.cim_wizard_building.building_surfaces_lod12.metadata",
        "logic": "Count basement storeys from mixed-use LOD1.2 metadata when available.",
        "status": "PLANNED-1",
    },
    ("building", "lod0_footprint_id"): {
        "calculator": "ctdb_geometry_calculator",
        "method": "ctdb_map_lod12_surfaces",
        "cim_source": "cim_vector.cim_wizard_building.building_geometry",
        "logic": "Optional: persist footprint polygon as LoD0 surface_geometry FK.",
        "status": "SCHEMA",
    },
    # cityobject_member
    ("cityobject_member", "citymodel_id"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_project_scenario.scenario_id",
        "logic": "Link building CityObject to scenario CityModel.",
        "status": "MAPPED",
    },
    ("cityobject_member", "cityobject_id"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_building.building_id",
        "logic": "Link building CityObject as citymodel member.",
        "status": "MAPPED",
    },
    # surface_geometry
    ("surface_geometry", "geometry"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_building.building_surfaces_lod12.surfaces.*.geometry",
        "logic": "GeoJSON Polygon from LOD1.2 wall/roof/ground/floor to PostGIS PolygonZ EPSG:4326.",
        "status": "MAPPED",
    },
    ("surface_geometry", "gmlid"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_building.building_surfaces_lod12.surfaces.*.surface_id",
        "logic": "Synthetic ms-/poly- gmlid from surface cityobject id.",
        "status": "MAPPED",
    },
    # thematic_surface
    ("thematic_surface", "building_id"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_building.building_id",
        "logic": "FK to parent building cityobject.id.",
        "status": "MAPPED",
    },
    ("thematic_surface", "lod2_multi_surface_id"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_building.building_surfaces_lod12",
        "logic": "FK to surface_geometry root node for LOD1.2 polygon tree.",
        "status": "MAPPED",
    },
    ("thematic_surface", "objectclass_id"): {
        "calculator": "citydb_mapper_calculator",
        "method": "map_scenario_to_citydb",
        "cim_source": "cim_vector.cim_wizard_building.building_surfaces_lod12.surfaces.*.surface_type",
        "logic": "Map Wall=34 Roof=33 Ground=35 Floor=32 from surface_type.",
        "status": "MAPPED",
    },
    # ng2_building
    ("ng2_building", "type"): {
        "calculator": TABULA_CALC,
        "method": "tabula_extract_ng2_building",
        "cim_source": "tabula_envelope_json + cim_wizard_building_properties.type",
        "logic": "Map usage type and archetype class to ng2_building.type.",
        "status": "PLANNED-1",
    },
    ("ng2_building", "constr_weight"): {
        "calculator": TABULA_CALC,
        "method": "tabula_extract_ng2_building",
        "cim_source": "TABULA_Codici_costruzioni.xlsx + const_tabula",
        "logic": "Derive light/medium/heavy from TABULA period; fallback envelope_efficiency.",
        "status": "PLANNED-1",
    },
    # ng2_thematic_surface
    ("ng2_thematic_surface", "total_surf_area"): {
        "calculator": "ctdb_thematic_surface_calculator",
        "method": "ctdb_from_lod12",
        "cim_source": "building_surfaces_lod12.surfaces.*.properties.area_m2",
        "logic": "Copy computed area_m2 per wall/roof/ground/floor surface.",
        "status": "PLANNED-1",
    },
    ("ng2_thematic_surface", "azimuth"): {
        "calculator": "ctdb_thematic_surface_calculator",
        "method": "ctdb_from_lod12",
        "cim_source": "building_surfaces_lod12.surfaces.wall_surfaces[].properties.azimuth_degrees",
        "logic": "Copy wall azimuth; roof/ground defaults per surface type.",
        "status": "PLANNED-1",
    },
    ("ng2_thematic_surface", "inclination"): {
        "calculator": "ctdb_thematic_surface_calculator",
        "method": "ctdb_from_lod12",
        "cim_source": "building_surfaces_lod12.surfaces.*.properties.inclination_degrees",
        "logic": "Copy inclination; flat roof default 0 deg.",
        "status": "PLANNED-1",
    },
    # ng2_building_partition
    ("ng2_building_partition", "type"): {
        "calculator": "ctdb_thermal_partition_calculator",
        "method": "ctdb_from_lod12",
        "cim_source": "building_surfaces_lod12.thermal_zones[].usage",
        "logic": "One thermal zone per building level (storey); type from zone usage.",
        "status": "PLANNED-1",
    },
    ("ng2_building_partition", "is_heated"): {
        "calculator": "ctdb_thermal_partition_calculator",
        "method": "ctdb_from_lod12",
        "cim_source": "building_surfaces_lod12.thermal_zones[].is_heated",
        "logic": "Copy heated flag per storey thermal zone.",
        "status": "PLANNED-1",
    },
    ("ng2_building_partition", "is_cooled"): {
        "calculator": "ctdb_thermal_partition_calculator",
        "method": "ctdb_from_lod12",
        "cim_source": "building_surfaces_lod12.thermal_zones[].is_cooled",
        "logic": "Copy cooled flag per storey thermal zone.",
        "status": "PLANNED-1",
    },
    ("ng2_building_partition", "heat_capacity"): {
        "calculator": "ctdb_thermal_partition_calculator",
        "method": "ctdb_from_lod12",
        "cim_source": "building_surfaces_lod12.thermal_zones[].volume_m3",
        "logic": "Use zone volume_m3 as effective thermal capacity proxy.",
        "status": "PLANNED-1",
    },
    # ng2_layered_construction
    ("ng2_layered_construction", "u_value"): {
        "calculator": TABULA_CALC,
        "method": "tabula_extract_layered_construction",
        "cim_source": "component XLS Dati.Trasmittanza (Wall/Roof/Floor/Ceiling_*)",
        "logic": "U-value per element from Politecnico component workbook assigned to archetype slot.",
        "status": "PLANNED-1",
    },
    ("ng2_layered_construction", "g_value"): {
        "calculator": TABULA_CALC,
        "method": "tabula_extract_layered_construction",
        "cim_source": "TABULA window typology defaults",
        "logic": "Window g-value for window layered_construction row.",
        "status": "PLANNED-1",
    },
    ("ng2_layered_construction", "library_code"): {
        "calculator": TABULA_CALC,
        "method": "tabula_extract_layered_construction",
        "cim_source": "construction code e.g. Wall_06.02",
        "logic": "Store TABULA construction code as library_code on layered_construction.",
        "status": "PLANNED-1",
    },
    # ng2_cityobject
    ("ng2_cityobject", "ref_point"): {
        "calculator": "ctdb_ref_point_calculator",
        "method": "ctdb_footprint_centroid",
        "cim_source": "cim_vector.cim_wizard_building.building_geometry + z_value",
        "logic": "Footprint centroid at z_value terrain height (sea level floor reference).",
        "status": "PLANNED-1",
    },
    # ng2_device
    ("ng2_device", "model"): {
        "calculator": "ctdb_hvac_calculator",
        "method": "ctdb_from_fmu_archetype",
        "cim_source": "cim_vector.cim_wizard_building_properties.fmu_file",
        "logic": "Map fmu_file identifier to heat-pump archetype model name.",
        "status": "PLANNED-3",
    },
    # ng2_opening
    ("ng2_opening", "area"): {
        "calculator": TABULA_CALC,
        "method": "tabula_extract_opening",
        "cim_source": "building_surfaces_lod12 + tabula_glazing_ratio",
        "logic": "Wall area × TABULA-period glazing ratio per orientation.",
        "status": "PLANNED-3",
    },
    # ng2_solar_collector
    ("ng2_solar_collector", "module_area"): {
        "calculator": "ctdb_solar_collector_calculator",
        "method": "ctdb_from_pv",
        "cim_source": "cim_vector.pv.area_reale",
        "logic": "PV polygon area linked via building.pv_ids.",
        "status": "PLANNED-3",
    },
    ("ng2_solar_collector", "lod2_multi_surface_id"): {
        "calculator": "ctdb_solar_collector_calculator",
        "method": "ctdb_from_pv",
        "cim_source": "cim_vector.pv.pv_geometry",
        "logic": "Persist PV multipolygon as surface_geometry FK.",
        "status": "PLANNED-3",
    },
    # ng2_utl_ntw_connection
    ("ng2_utl_ntw_connection", "network_type"): {
        "calculator": "ctdb_utility_connection_calculator",
        "method": "ctdb_from_grid",
        "cim_source": "cim_vector.cim_wizard_project_scenario.grid_id",
        "logic": "When grid_id set, write electricity consumer connection.",
        "status": "PLANNED-3",
    },
}

TABLE_DEFAULT_CALC: dict[str, tuple[str, str, str]] = {
    "ng2_building": (TABULA_CALC, "tabula_extract_ng2_building", "PLANNED-1"),
    "ng2_building_partition": ("ctdb_thermal_partition_calculator", "ctdb_from_lod12", "PLANNED-1"),
    "ng2_layered_construction": (TABULA_CALC, "tabula_extract_layered_construction", "PLANNED-1"),
    "ng2_thematic_surface": (TABULA_CALC, "tabula_extract_thematic_surface", "PLANNED-1"),
    "ng2_them_surf_to_thermal_zone": ("ctdb_surf_zone_adjacency_calculator", "ctdb_from_lod12", "PLANNED-1"),
    "ng2_qualified_attribute": (TABULA_CALC, "tabula_extract_qualified_attribute", "PLANNED-1"),
    "ng2_material": (TABULA_CALC, "tabula_extract_material_layers", "PLANNED-3"),
    "ng2_layer": (TABULA_CALC, "tabula_extract_material_layers", "PLANNED-3"),
    "ng2_opening": (TABULA_CALC, "tabula_extract_opening", "PLANNED-3"),
    "ng2_optical_property": (TABULA_CALC, "tabula_extract_optical_property", "PLANNED-3"),
    "ng2_device": ("ctdb_hvac_calculator", "ctdb_from_fmu_archetype", "PLANNED-3"),
    "ng2_device_operation": ("ctdb_device_operation_calculator", "ctdb_from_archetype", "PLANNED-3"),
    "ng2_refurbishment_measure": ("ctdb_refurbishment_calculator", "ctdb_from_envelope_efficiency", "PLANNED-3"),
    "ng2_solar_collector": ("ctdb_solar_collector_calculator", "ctdb_from_pv", "PLANNED-3"),
    "ng2_utl_ntw_connection": ("ctdb_utility_connection_calculator", "ctdb_from_grid", "PLANNED-3"),
}

GENERIC_ATTRIB_ROWS = [
    # (attrname, datatype, calculator, method, cim_source, logic, status, cityobject_scope)
    ("u_value_w_m2k", "numeric", TABULA_CALC, "tabula_extract_surface_u_value",
     "tabula_envelope_json.components + LOD1.2 surface slot",
     "Per-surface U from archetype component code (Wall/Roof/Floor); replaces coarse TABULA_U_VALUES.", "PLANNED-1", "surface"),
    ("thermalZone_volume_m3", "numeric", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "cim_wizard_building_properties.volume",
     "Single-zone mode: copy building volume.", "MAPPED", "building"),
    ("thermalZone_floorArea_m2", "numeric", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "cim_wizard_building_properties.area",
     "Single-zone mode: copy footprint area.", "MAPPED", "building"),
    ("thermalZone_numberOfFloors", "numeric", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "cim_wizard_building_properties.number_of_floors",
     "Single-zone mode: copy storey count.", "MAPPED", "building"),
    ("energySystem_envelopeEfficiency", "text", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "cim_wizard_building_properties.envelope_efficiency",
     "Copy low/medium/high envelope efficiency label.", "MAPPED", "building"),
    ("energySystem_fmuFile", "text", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "cim_wizard_building_properties.fmu_file",
     "Copy FMU archetype file identifier.", "MAPPED", "building"),
    ("thermalZone_count", "integer", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "building_surfaces_lod12.thermal_zones[]",
     "Multi-zone: count of storey-level thermal zones.", "MAPPED", "building"),
    ("tz:{zone_id}:usage", "text", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "building_surfaces_lod12.thermal_zones[].usage",
     "Multi-zone: per-zone usage type (one zone per building level).", "MAPPED", "building"),
    ("tz:{zone_id}:volume_m3", "numeric", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "building_surfaces_lod12.thermal_zones[].volume_m3",
     "Multi-zone: per-zone air volume from LOD1.2 storey slice.", "MAPPED", "building"),
    ("tz:{zone_id}:floor_area_m2", "numeric", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "building_surfaces_lod12.thermal_zones[].floor_area_m2",
     "Multi-zone: per-zone floor area.", "MAPPED", "building"),
    ("tz:{zone_id}:is_heated", "integer", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "building_surfaces_lod12.thermal_zones[].is_heated",
     "Multi-zone: heated flag per storey zone.", "MAPPED", "building"),
    ("tz:{zone_id}:is_cooled", "integer", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "building_surfaces_lod12.thermal_zones[].is_cooled",
     "Multi-zone: cooled flag per storey zone.", "MAPPED", "building"),
    ("tz:{zone_id}:storey_index", "integer", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "building_surfaces_lod12.thermal_zones[].storey_index",
     "Multi-zone: storey index links zone to floor surfaces.", "MAPPED", "building"),
    ("tz:{zone_id}:apartment_index", "integer", "citydb_mapper_calculator", "map_scenario_to_citydb",
     "building_surfaces_lod12.thermal_zones[].apartment_index",
     "Mixed-use: apartment sub-zone index when present.", "MAPPED", "building"),
    # CIM mirror (planned)
    ("cim_building_id", "text", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building.building_id", "Mirror building UUID for round-trip queries.", "PLANNED-1", "building"),
    ("cim_height", "numeric", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.height", "Mirror calculated height.", "PLANNED-1", "building"),
    ("cim_area", "numeric", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.area", "Mirror footprint area.", "PLANNED-1", "building"),
    ("cim_volume", "numeric", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.volume", "Mirror building volume.", "PLANNED-1", "building"),
    ("cim_number_of_floors", "numeric", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.number_of_floors", "Mirror storey count.", "PLANNED-1", "building"),
    ("cim_type", "text", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.type", "Mirror OSM-derived usage type.", "PLANNED-1", "building"),
    ("cim_const_period_census", "text", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.const_period_census", "Mirror census construction period band.", "PLANNED-1", "building"),
    ("cim_const_year", "integer", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.const_year", "Mirror estimated construction year.", "PLANNED-1", "building"),
    ("cim_const_tabula", "text", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.const_tabula", "Mirror TABULA period code TABULA_1…7.", "PLANNED-1", "building"),
    ("cim_n_people", "integer", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.n_people", "Mirror census-derived population count.", "PLANNED-1", "building"),
    ("cim_n_family", "integer", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.n_family", "Mirror household count.", "PLANNED-1", "building"),
    ("cim_envelope_efficiency", "text", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.envelope_efficiency", "Mirror envelope efficiency class.", "PLANNED-1", "building"),
    ("cim_fmu_file", "text", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.fmu_file", "Mirror assigned FMU archetype.", "PLANNED-1", "building"),
    ("cim_filter_res", "boolean", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building_properties.filter_res", "Mirror residential vs non-residential filter flag.", "PLANNED-1", "building"),
    ("cim_z_value", "numeric", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building.z_value", "Mirror terrain/floor height above sea level.", "PLANNED-1", "building"),
    ("cim_census_id", "integer", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building.census_id", "Mirror census tract link.", "PLANNED-1", "building"),
    ("cim_lod", "integer", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building.lod", "Mirror geometry LOD level.", "PLANNED-1", "building"),
    ("cim_building_geometry_source", "text", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building.building_geometry_source", "Mirror footprint source (OSM/census/etc.).", "PLANNED-1", "building"),
    ("cim_pv_ids", "text", "ctdb_attrib_calculator", "ctdb_cim_genericattrib_mirror",
     "cim_wizard_building.pv_ids", "Comma-joined PV UUID list for reverse lookup.", "PLANNED-1", "building"),
    # TABULA-derived genericattrib (from archetype XLS via tabula_extract_genericattrib)
    ("tabula_period_code", "text", TABULA_CALC, "tabula_extract_genericattrib",
     "tabula_envelope_json.const_tabula", "Copy TABULA_1…TABULA_7 period code.", "PLANNED-1", "building"),
    ("tabula_archetype_code", "text", TABULA_CALC, "tabula_extract_genericattrib",
     "TABULA_Codici_costruzioni.Codice ed.", "Full archetype code e.g. SFH_05.", "PLANNED-1", "building"),
    ("tabula_u_wall", "numeric", TABULA_CALC, "tabula_extract_genericattrib",
     "component Wall_*.Dati.Trasmittanza", "Primary wall U-value W/m²K from XLS.", "PLANNED-1", "building"),
    ("tabula_u_wall_2", "numeric", TABULA_CALC, "tabula_extract_genericattrib",
     "component Wall_*.Dati.Trasmittanza (Parete2)", "Secondary wall U when archetype has two wall types.", "PLANNED-1", "building"),
    ("tabula_u_roof", "numeric", TABULA_CALC, "tabula_extract_genericattrib",
     "component Roof_*.Dati.Trasmittanza", "Roof U-value W/m²K from XLS.", "PLANNED-1", "building"),
    ("tabula_u_ground", "numeric", TABULA_CALC, "tabula_extract_genericattrib",
     "component Floor_*.Dati.Trasmittanza (Solaio1)", "Ground/floor slab U-value W/m²K.", "PLANNED-1", "building"),
    ("tabula_u_ceiling", "numeric", TABULA_CALC, "tabula_extract_genericattrib",
     "component Ceiling_*.Dati.Trasmittanza", "Attic ceiling U when present in archetype.", "PLANNED-1", "building"),
    ("tabula_g_window", "numeric", TABULA_CALC, "tabula_extract_genericattrib",
     "TABULA window typology", "Window solar/g-value default.", "PLANNED-1", "building"),
    ("tabula_envelope_class", "text", TABULA_CALC, "tabula_extract_genericattrib",
     "envelope KPI derivation", "Derived envelope performance label.", "PLANNED-1", "building"),
    ("tabula_constr_weight", "text", TABULA_CALC, "tabula_extract_genericattrib",
     "archetype epoca", "Light/medium/heavy construction weight from period.", "PLANNED-1", "building"),
    ("tabula_glazing_ratio", "numeric", TABULA_CALC, "tabula_extract_genericattrib",
     "TABULA defaults", "Glazed-to-opaque ratio for tabula_extract_opening.", "PLANNED-3", "building"),
    ("tabula_building_class", "text", TABULA_CALC, "tabula_extract_genericattrib",
     "archetype prefix SFH/MFH/TH/AB", "TABULA building class segment.", "PLANNED-1", "building"),
    # Post-simulation genericattrib (examples)
    ("postSim_meanIndoorTemp_C", "numeric", "ctdb_postsim_calculator", "ctdb_genericattrib_from_outputs",
     "outputs.building_frassinetto3", "Mean indoor temperature from simulation.", "POSTSIM", "building"),
    ("postSim_annualHeating_kWh", "numeric", "ctdb_postsim_calculator", "ctdb_genericattrib_from_outputs",
     "outputs.heating_frassinetto_hp2", "Annual heating energy aggregate.", "POSTSIM", "building"),
    ("postSim_batterySOC_pct", "numeric", "ctdb_postsim_calculator", "ctdb_genericattrib_from_outputs",
     "outputs.battery", "Battery state-of-charge time series summary.", "POSTSIM", "building"),
    ("postSim_hpCOP", "numeric", "ctdb_postsim_calculator", "ctdb_genericattrib_from_outputs",
     "outputs.heating_frassinetto_hp2", "Seasonal COP of heat pump.", "POSTSIM", "building"),
]


def simplify_type(pg_type: str, column: str, fk_to: str) -> str:
    if column == "id" and fk_to:
        return "fk"
    if column.endswith("_id") and fk_to:
        return "fk"
    t = pg_type.lower()
    if "geometry" in t:
        return "geometry"
    if t in ("text", "varchar", "character varying") or t.startswith("varchar"):
        return "text"
    if t in ("integer", "bigint", "smallint", "numeric") and "id" in column:
        return "fk" if fk_to else "integer"
    if t in ("integer", "bigint", "smallint"):
        return "integer"
    if t in ("double precision", "real", "numeric"):
        return "numeric"
    if "timestamp" in t or t == "date" or t == "time":
        return "timestamp"
    if t == "jsonb":
        return "json"
    if t == "bytea":
        return "binary"
    if t == "boolean":
        return "boolean"
    return "text"


def geo_role(table: str, column: str) -> str:
    key = f"{table}.{column}"
    if key in GEO_DIRECT:
        return "GEO-DIRECT"
    if table in GEO_FK_TABLES and column.endswith("_id"):
        return "GEO-FK"
    if table == "property" and "implicitgeom" in column:
        return "GEO-DIRECT"
    if table == "property" and column.endswith("_id"):
        return "GEO-FK"
    return "GEO-NONE"


def default_status(table: str) -> str:
    if table in DB_INIT_TABLES:
        return "DB-INIT"
    if table in DEFERRED_OCCUPANTS:
        return "DEFERRED-OCCUPANTS"
    if table in DEFERRED_SCHEDULES:
        return "DEFERRED-SCHEDULES"
    if table in DEFERRED_WEATHER:
        return "DEFERRED-WEATHER"
    if table in POSTSIM_TABLES:
        return "POSTSIM"
    if table == "ng2_time_series":
        return "DEFERRED-SCHEDULES"
    if table in NO_PLAN_TABLES:
        return "SCHEMA"
    if table in TABLE_DEFAULT_CALC:
        return TABLE_DEFAULT_CALC[table][2]
    return "SCHEMA"


def default_rule(table: str, column: str, description: str) -> dict:
    key = (table, column)
    if key in COLUMN_RULES:
        return COLUMN_RULES[key]

    status = default_status(table)

    if column == "id" and status == "DB-INIT":
        return {
            "calculator": "—",
            "method": "—",
            "cim_source": "—",
            "logic": "Populated at database initialization.",
            "status": status,
        }

    if table in DEFERRED_OCCUPANTS:
        return {
            "calculator": "—",
            "method": "—",
            "cim_source": "—",
            "logic": "DEFERRED-OCCUPANTS: requires occupant template library beyond n_people/n_family.",
            "status": status,
        }
    if table in DEFERRED_SCHEDULES:
        return {
            "calculator": "—",
            "method": "—",
            "cim_source": "—",
            "logic": "DEFERRED-SCHEDULES: requires committed hourly profile dataset.",
            "status": status,
        }
    if table in DEFERRED_WEATHER:
        return {
            "calculator": "—",
            "method": "—",
            "cim_source": "—",
            "logic": "DEFERRED-WEATHER: requires EPW/station binding on scenario.",
            "status": status,
        }
    if table in POSTSIM_TABLES or (table == "ng2_time_series" and status == "POSTSIM"):
        calc = "ctdb_postsim_calculator"
        method = {
            "ng2_resource": "ctdb_resource_from_outputs",
            "ng2_storage_device": "ctdb_storage_device_from_outputs",
        }.get(table, "ctdb_genericattrib_from_outputs")
        return {
            "calculator": calc,
            "method": method,
            "cim_source": "outputs.*",
            "logic": "POSTSIM: aggregate simulator outputs after run completes.",
            "status": "POSTSIM",
        }
    if table == "ng2_time_series":
        return {
            "calculator": "—",
            "method": "—",
            "cim_source": "—",
            "logic": "DEFERRED-SCHEDULES / DEFERRED-WEATHER / POSTSIM depending on series role.",
            "status": status,
        }

    if table in TABLE_DEFAULT_CALC:
        calc, method, st = TABLE_DEFAULT_CALC[table]
        cim = {
            "ng2_building": TABULA_CIM,
            "ng2_building_partition": "building_surfaces_lod12.thermal_zones[] (one zone per level)",
            "ng2_them_surf_to_thermal_zone": "building_surfaces_lod12 surfaces + thermal_zones storey_index",
            "ng2_layered_construction": TABULA_CIM,
            "ng2_thematic_surface": "tabula_envelope_json + building_surfaces_lod12",
            "ng2_qualified_attribute": "tabula_envelope_json envelope KPIs",
            "ng2_material": "Caratteristiche componente layer stack",
            "ng2_layer": "ng2_layered_construction layer rows",
            "ng2_opening": "LOD1.2 wall area × tabula_glazing_ratio",
            "ng2_optical_property": "TABULA window g-value",
            "ng2_device": "cim_wizard_building_properties.fmu_file",
            "ng2_device_operation": "fmu archetype metadata",
            "ng2_refurbishment_measure": "envelope_efficiency=high → retrofit hint",
            "ng2_solar_collector": "cim_wizard_building.pv_ids → cim_vector.pv",
            "ng2_utl_ntw_connection": "cim_wizard_project_scenario.grid_id",
        }.get(table, TABULA_CIM if table in NG2_TABULA_METHOD else "cim_vector building + properties")
        return {
            "calculator": calc,
            "method": method,
            "cim_source": cim,
            "logic": f"Fill {table}.{column} via {method} from TABULA archetype catalog + component XLS.",
            "status": st,
        }

    if table in NO_PLAN_TABLES or table in DB_INIT_TABLES:
        return {
            "calculator": "—",
            "method": "—",
            "cim_source": "—",
            "logic": "Out of scope for current CIM→CityDB pipeline." if table in NO_PLAN_TABLES else "Database metadata table.",
            "status": status,
        }

    # PK / FK auto
    if column == "id":
        return {
            "calculator": "citydb_mapper_calculator",
            "method": "map_scenario_to_citydb",
            "cim_source": "db_sequence",
            "logic": "Auto-generated PK from PostgreSQL sequence on insert.",
            "status": "MAPPED" if table in {"cityobject", "surface_geometry", "citymodel"} else "SCHEMA",
        }
    if column.endswith("_id") or column.endswith("_codespace"):
        return {
            "calculator": "—",
            "method": "—",
            "cim_source": "—",
            "logic": "FK or codespace column filled implicitly by parent row insert.",
            "status": "SCHEMA",
        }

    return {
        "calculator": "—",
        "method": "—",
        "cim_source": "—",
        "logic": description or "Not mapped.",
        "status": "SCHEMA",
    }


def main() -> None:
    rows: list[dict] = []
    row_id = 0

    with SCHEMA_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            row_id += 1
            table = r["table"]
            column = r["column"]
            addr = f"citydb.{table}.{column}"
            rule = default_rule(table, column, r.get("description", ""))
            rows.append({
                "row_id": row_id,
                "citydb_address": addr,
                "pg_type": r["type"],
                "attribute_type": simplify_type(r["type"], column, r.get("fk_to", "")),
                "geo_role": geo_role(table, column),
                "status": rule["status"],
                "calculator": rule["calculator"],
                "method": rule["method"],
                "cim_source": rule["cim_source"],
                "logic": rule["logic"],
            })

    # genericattrib container columns (EAV structure)
    for col, pg_t, desc in [
        ("id", "bigint", "PK"),
        ("parent_genattrib_id", "bigint", "nested FK"),
        ("root_genattrib_id", "bigint", "nested FK"),
        ("attrname", "varchar(256)", "attribute name key"),
        ("datatype", "numeric", "type code 1=str 2=int 3=real"),
        ("strval", "varchar(4000)", "string value slot"),
        ("intval", "integer", "integer value slot"),
        ("realval", "double precision", "real value slot"),
        ("urival", "varchar(4000)", "URI value slot"),
        ("dateval", "timestamptz", "date value slot"),
        ("unit", "varchar(4000)", "unit of measure"),
        ("cityobject_id", "bigint", "FK to cityobject"),
    ]:
        if not any(x["citydb_address"] == f"citydb.cityobject_genericattrib.{col}" for x in rows):
            continue  # already in schema rows

    # Virtual genericattrib attrname rows
    for attrname, attr_type, calc, method, cim, logic, status, scope in GENERIC_ATTRIB_ROWS:
        row_id += 1
        val_col = {"text": "strval", "numeric": "realval", "integer": "intval", "boolean": "intval"}.get(attr_type, "strval")
        rows.append({
            "row_id": row_id,
            "citydb_address": f"citydb.cityobject_genericattrib.{attrname}→{val_col}",
            "pg_type": attr_type,
            "attribute_type": attr_type,
            "geo_role": "GEO-NONE",
            "status": status,
            "calculator": calc,
            "method": method,
            "cim_source": cim,
            "logic": f"[{scope}] {logic}",
        })

    # LOD12 JSON leaf paths (virtual — source for ng2_* and geometry)
    lod12_paths = [
        ("building_surfaces_lod12.surfaces.wall_surfaces[].geometry", "geometry", "citydb_mapper_calculator",
         "map_scenario_to_citydb", "cim_wizard_building.building_surfaces_lod12", "Wall PolygonZ per orientation.", "MAPPED"),
        ("building_surfaces_lod12.surfaces.roof_surface.geometry", "geometry", "citydb_mapper_calculator",
         "map_scenario_to_citydb", "cim_wizard_building.building_surfaces_lod12", "Roof polygon at building height.", "MAPPED"),
        ("building_surfaces_lod12.surfaces.ground_surface.geometry", "geometry", "citydb_mapper_calculator",
         "map_scenario_to_citydb", "cim_wizard_building.building_surfaces_lod12", "Ground/floor slab at z=0 relative.", "MAPPED"),
        ("building_surfaces_lod12.surfaces.floor_surfaces[].geometry", "geometry", "citydb_mapper_calculator",
         "map_scenario_to_citydb", "cim_wizard_building.building_surfaces_lod12", "Inter-storey floor/ceiling polygons.", "MAPPED"),
        ("building_surfaces_lod12.surfaces.wall_surfaces[].properties.area_m2", "numeric", "ctdb_thematic_surface_calculator",
         "ctdb_from_lod12", "cim_wizard_building.building_surfaces_lod12", "Pre-computed wall area.", "PLANNED-1"),
        ("building_surfaces_lod12.surfaces.wall_surfaces[].properties.azimuth_degrees", "numeric", "ctdb_thematic_surface_calculator",
         "ctdb_from_lod12", "cim_wizard_building.building_surfaces_lod12", "Wall outward normal azimuth.", "PLANNED-1"),
        ("building_surfaces_lod12.surfaces.wall_surfaces[].tabula.construction_code", "text", TABULA_CALC,
         "tabula_extract_surface_assignment", "tabula_envelope_json", "Assign Parete1/2/3 construction code to wall by index/area.", "PLANNED-1"),
        ("building_surfaces_lod12.surfaces.wall_surfaces[].tabula.u_value", "numeric", TABULA_CALC,
         "tabula_extract_surface_assignment", "component XLS Dati.Trasmittanza", "Per-wall U from assigned TABULA component.", "PLANNED-1"),
        ("building_surfaces_lod12.surfaces.roof_surface.tabula.u_value", "numeric", TABULA_CALC,
         "tabula_extract_surface_assignment", "Copertura component", "Roof U from archetype Copertura slot.", "PLANNED-1"),
        ("building_surfaces_lod12.surfaces.ground_surface.tabula.u_value", "numeric", TABULA_CALC,
         "tabula_extract_surface_assignment", "Solaio1 component", "Ground slab U from archetype Solaio1 slot.", "PLANNED-1"),
        ("building_surfaces_lod12.thermal_zones[].zone_id", "text", "ctdb_thermal_partition_calculator",
         "ctdb_from_lod12", "cim_wizard_building.building_surfaces_lod12", "Thermal zone id (z1, z2, … per level).", "PLANNED-1"),
        ("building_surfaces_lod12.thermal_zones[].storey_index", "integer", "ctdb_thermal_partition_calculator",
         "ctdb_from_lod12", "cim_wizard_building.building_surfaces_lod12", "Links zone to building level / floor surfaces.", "PLANNED-1"),
        ("building_surfaces_lod12.metadata.building_height", "numeric", "building_geo_lod12_calculator",
         "generate_lod12_surfaces", "cim_wizard_building_properties.height", "LOD1.2 extrusion height reference.", "CALCULATED"),
    ]
    for path, attr_type, calc, method, cim, logic, status in lod12_paths:
        row_id += 1
        rows.append({
            "row_id": row_id,
            "citydb_address": f"cim_vector.{path}",
            "pg_type": "json/jsonb",
            "attribute_type": attr_type,
            "geo_role": "GEO-DIRECT" if attr_type == "geometry" else "GEO-NONE",
            "status": status,
            "calculator": calc,
            "method": method,
            "cim_source": cim,
            "logic": logic,
        })

    # CIM vector source columns (inputs — may map to citydb or genericattrib)
    CIM_SOURCE_ROWS = [
        ("cim_vector.cim_wizard_building.building_id", "text", "citydb_mapper_calculator", "map_scenario_to_citydb",
         "cim_wizard_building.building_id", "Primary key UUID → cityobject.gmlid.", "MAPPED"),
        ("cim_vector.cim_wizard_building.building_geometry", "geometry", "building_geo_calculator", "calculate_building_geometry",
         "OSM/census footprint", "Footprint polygon; input to LOD1.2 extrusion.", "CALCULATED"),
        ("cim_vector.cim_wizard_building.building_geometry_source", "text", "building_geo_calculator", "calculate_building_geometry",
         "data source tag", "Source label (osm, census, …).", "CALCULATED"),
        ("cim_vector.cim_wizard_building.building_surfaces_lod12", "json", "building_geo_lod12_calculator", "generate_lod12_surfaces",
         "footprint + height + floors", "Semantic walls/roof/ground/floors + thermal_zones JSON.", "CALCULATED"),
        ("cim_vector.cim_wizard_building.z_value", "numeric", "building_z_value_calculator", "calculate_z_value",
         "DEM/terrain", "Floor height above sea level → ref_point Z and CityJSON terrainHeight.", "CALCULATED"),
        ("cim_vector.cim_wizard_building.building_name", "text", "building_name_calculator", "assign_building_names",
         "OSM addr / synthetic", "→ cityobject.name.", "MAPPED"),
        ("cim_vector.cim_wizard_building.pv_ids", "array_uuid", "pv_generator_calculator", "generate_pv",
         "cim_vector.pv", "UUID list linking building to PV roof polygons.", "CALCULATED"),
        ("cim_vector.cim_wizard_building.census_id", "integer", "building_construction_year_calculator", "assign_construction_period",
         "census tract", "Links building to census boundary for period assignment.", "CALCULATED"),
        ("cim_vector.cim_wizard_building_properties.height", "numeric", "building_height_calculator", "calculate_height",
         "OSM tags / rules", "→ building.measured_height.", "MAPPED"),
        ("cim_vector.cim_wizard_building_properties.area", "numeric", "building_area_calculator", "calculate_area",
         "footprint geometry", "→ genericattrib cim_area / thermalZone_floorArea_m2.", "CALCULATED"),
        ("cim_vector.cim_wizard_building_properties.volume", "numeric", "building_volume_calculator", "calculate_volume",
         "area × height", "→ genericattrib cim_volume / thermalZone_volume_m3.", "CALCULATED"),
        ("cim_vector.cim_wizard_building_properties.number_of_floors", "numeric", "building_n_floors_calculator", "calculate_floors",
         "height + filter_res", "→ building.storeys_above_ground; drives LOD1.2 storey count.", "MAPPED"),
        ("cim_vector.cim_wizard_building_properties.type", "text", "building_type_calculator", "derive_from_filter_res",
         "filter_res boolean", "residential/others → ng2_building.type.", "CALCULATED"),
        ("cim_vector.cim_wizard_building_properties.const_tabula", "text", "building_construction_year_calculator", "assign_tabula_period",
         "census period", "TABULA_1…TABULA_7 → U-values, constructions, tabula_* genericattrib.", "CALCULATED"),
        ("cim_vector.cim_wizard_building_properties.const_period_census", "text", "building_construction_year_calculator", "assign_construction_period",
         "census", "Census construction period band.", "CALCULATED"),
        ("cim_vector.cim_wizard_building_properties.const_year", "integer", "building_construction_year_calculator", "assign_construction_year",
         "census", "Estimated year → yearOfConstruction genericattrib.", "CALCULATED"),
        ("cim_vector.cim_wizard_building_properties.envelope_efficiency", "text", "envelope_efficiency_calculator", "classify_envelope",
         "const_tabula + type", "low/medium/high → energySystem_envelopeEfficiency.", "MAPPED"),
        ("cim_vector.cim_wizard_building_properties.fmu_file", "text", "fmu_assign_calculator", "assign_fmu",
         "building type + scenario", "HVAC archetype id → ng2_device via ctdb_hvac_calculator.", "MAPPED"),
        ("cim_vector.cim_wizard_building_properties.n_people", "integer", "building_demographic_calculator", "distribute_population",
         "census volume", "→ cim_n_people genericattrib; ng2_occupants DEFERRED.", "CALCULATED"),
        ("cim_vector.cim_wizard_building_properties.n_family", "integer", "building_demographic_calculator", "distribute_families",
         "census", "→ cim_n_family genericattrib.", "CALCULATED"),
        ("cim_vector.cim_wizard_building_properties.filter_res", "boolean", "building_residential_filter_calculator", "calculate_filter_res",
         "area + height + OSM", "Residential gate for volume/floors/construction calculators.", "CALCULATED"),
        # TABULA extraction → cim_wizard_building_properties (Phase 1)
        ("cim_vector.cim_wizard_building_properties.tabula_type", "text", "building_tabula_type_calculator", "tabula_extract_type_label",
         "const_year + building_type", "IT.{USAGE}.{TABULA_PERIOD} label.", "PLANNED-1"),
        ("cim_vector.cim_wizard_building_properties.tabula_archetype_code", "text", TABULA_CALC, "tabula_extract_archetype_catalog",
         "TABULA_Codici_costruzioni.xlsx", "Resolve SFH_05 / MFH_05 / TH_05 / AB_05 from tabula_type + floors.", "PLANNED-1"),
        ("cim_vector.cim_wizard_building_properties.tabula_envelope_json", "json", TABULA_CALC, "tabula_extract_archetype_catalog",
         "all component XLS per archetype row", "Full envelope document: components, layers, U, dynamic props.", "PLANNED-1"),
        ("cim_vector.cim_wizard_building_properties.tabula_u_roof", "numeric", TABULA_CALC, "tabula_extract_archetype_catalog",
         "Roof_*.Dati.Trasmittanza", "Scalar roof U for queries.", "PLANNED-1"),
        ("cim_vector.cim_wizard_building_properties.tabula_u_wall", "numeric", TABULA_CALC, "tabula_extract_archetype_catalog",
         "Wall_*.Dati.Trasmittanza (Parete1)", "Scalar primary wall U.", "PLANNED-1"),
        ("cim_vector.cim_wizard_building_properties.tabula_u_wall_2", "numeric", TABULA_CALC, "tabula_extract_archetype_catalog",
         "Wall_*.Dati.Trasmittanza (Parete2)", "Scalar secondary wall U when present.", "PLANNED-1"),
        ("cim_vector.cim_wizard_building_properties.tabula_u_ground", "numeric", TABULA_CALC, "tabula_extract_archetype_catalog",
         "Floor_*.Dati.Trasmittanza (Solaio1)", "Scalar ground/floor U.", "PLANNED-1"),
        ("cim_vector.cim_wizard_building_properties.tabula_u_ceiling", "numeric", TABULA_CALC, "tabula_extract_archetype_catalog",
         "Ceiling_*.Dati.Trasmittanza", "Scalar attic ceiling U when present.", "PLANNED-1"),
        ("cim_vector.cim_wizard_building_properties.tabula_building_class", "text", TABULA_CALC, "tabula_extract_archetype_catalog",
         "archetype prefix", "SFH / MFH / TH / AB segment.", "PLANNED-1"),
    ]
    for addr, attr_type, calc, method, cim, logic, status in CIM_SOURCE_ROWS:
        row_id += 1
        rows.append({
            "row_id": row_id,
            "citydb_address": addr,
            "pg_type": attr_type,
            "attribute_type": attr_type,
            "geo_role": "GEO-DIRECT" if attr_type == "geometry" else "GEO-NONE",
            "status": status,
            "calculator": calc,
            "method": method,
            "cim_source": cim,
            "logic": logic,
        })

    fieldnames = [
        "row_id", "citydb_address", "pg_type", "attribute_type", "geo_role",
        "status", "calculator", "method", "cim_source", "logic",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
