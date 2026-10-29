# CityGML and Energy ADE column classification

Every column in `citydb_schema_dictionary_1141.csv`. The file is the 3DCityDB relational schema for CityGML 2.0 plus Energy ADE 3.0 (tables prefixed `ng3_`). It contains 1148 columns in 95 tables.

## Counts

Columns fall into three groups of tables. **Administrative** columns are primary keys, foreign keys, and gml identifiers. **Real** columns are thematic values, units of measure, code-list namespaces, and geometry stored on the row.

| Group | Tables | Columns | Administrative | Real | Values | Units | Code lists | Geometry |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Metadata catalog | 8 | 41 | 16 | 25 | 25 | 0 | 0 | 0 |
| Core | 8 | 77 | 28 | 49 | 33 | 1 | 3 | 12 |
| Building | 9 | 124 | 56 | 68 | 28 | 3 | 13 | 24 |
| Energy ADE | 29 | 398 | 86 | 312 | 193 | 74 | 43 | 2 |
| **Core + Building + Energy** | 46 | 599 | 170 | 429 | 254 | 78 | 59 | 38 |
| Other CityGML modules | 41 | 508 | 225 | 283 | 92 | 5 | 60 | 126 |
| **All tables** | 95 | 1148 | 411 | 737 | 371 | 83 | 119 | 164 |

Other CityGML modules, one by one:

| Group | Tables | Columns | Administrative | Real | Values | Units | Code lists | Geometry |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Appearance | 5 | 43 | 15 | 28 | 21 | 0 | 3 | 4 |
| Bridge | 9 | 135 | 63 | 72 | 18 | 0 | 15 | 39 |
| CityFurniture | 1 | 32 | 10 | 22 | 3 | 0 | 3 | 16 |
| CityObjectGroup | 2 | 14 | 6 | 8 | 4 | 0 | 3 | 1 |
| Generics | 1 | 38 | 12 | 26 | 3 | 0 | 3 | 20 |
| LandUse | 1 | 13 | 7 | 6 | 3 | 0 | 3 | 0 |
| Relief | 8 | 30 | 17 | 13 | 4 | 1 | 0 | 8 |
| Transportation | 2 | 27 | 12 | 15 | 7 | 0 | 7 | 1 |
| Tunnel | 7 | 97 | 48 | 49 | 14 | 0 | 12 | 23 |
| Vegetation | 2 | 54 | 20 | 34 | 11 | 4 | 7 | 12 |
| WaterBody | 3 | 25 | 15 | 10 | 4 | 0 | 4 | 2 |

### How to read the split

Core, Building, and Energy ADE together are 599 columns in 46 tables: 170 administrative (28.4%) and 429 real (71.6%).

Energy ADE is where the thematic payload sits: 193 values, 74 units, 43 code-list namespaces, and 2 geometry columns, against 86 administrative columns. A measured quantity is stored as a pair, the number beside its unit, so the unit columns are real and they repeat a quantity rather than adding a new one.

The other modules hold 508 columns, 225 of them administrative (44.3%). Level-of-detail geometry links (`lod0` through `lod4`) account for 145 administrative columns in the whole schema: 32 in Core, Building, and Energy ADE, and 113 in the other modules. Bridge, tunnel, vegetation, and city furniture repeat the same block of geometry foreign keys at several levels of detail, which is why their administrative share is high.

The metadata catalog is 41 columns in 8 tables. 16 are keys or links. 25 describe the registry entries (class names, schema documents, the coordinate-system name, ADE version).

14 tables are only foreign keys. They connect two other tables: `schema_referencing`, `schema_to_objectclass`, `cityobject_member`, `generalization`, `address_to_building`, `opening_to_them_surface`, `ng3_them_surf_to_thermal_zone`, `ng3_address_to_building_unit`, `appear_to_surface_data`, `bridge_open_to_them_srf`, `address_to_bridge`, `relief_feat_to_rel_comp`, `tunnel_open_to_them_srf`, `waterbod_to_waterbnd_srf`. 3 feature tables also have no value column (`thematic_surface`, `bridge_thematic_surface`, `tunnel_thematic_surface`): the surface type is `objectclass_id`, and the shape is a foreign key to `surface_geometry`. Thermal numbers for those surfaces are the columns of `ng3_thematic_surface`.

Across the whole schema the 1148 columns are 411 administrative (35.8%) and 737 real (64.2%). Of the real columns, 371 are values, 83 are units, 119 are code-list namespaces, and 164 are geometry.

## Rules

The table group follows the 3DCityDB module the table belongs to.

- **Metadata catalog.** ADE registry, class catalogue, XML schemas, aggregation facts, the database coordinate system, and the internal index table.
- **Core.** The city object, the city model, generic attributes, external references, generalization, boundary-representation geometry, and implicit prototypes.
- **Building.** Building, installation, room, furniture, thematic surface, opening, and address. `address` is also used by bridges; the bridge link itself is `address_to_bridge` in the Bridge module.
- **Energy ADE.** Every table whose name starts with `ng3_` (Energy ADE 3.0).
- **Other modules.** Appearance, Bridge, CityFurniture, CityObjectGroup, Generics, LandUse, Relief, Transportation, Tunnel, Vegetation, and WaterBody.

The column kind is independent of the table group. A metadata table still has value columns. A building table still has key columns.

- **Administrative, key.** `id`, and `database_srs.srid`. On a feature table, `id` is also the parent table's id (CityGML inheritance). It is counted once. The attribute note names the parent.
- **Administrative, link.** Integer or bigint foreign keys, including `objectclass_id` and the `lod*_solid_id` / `lod*_brep_id` / `lod*_multi_surface_id` geometry pointers.
- **Administrative, identifier.** `gmlid`, `gmlid_codespace`, and `adeid`.
- **Real, value.** The thematic fact: a height, a class code, a date, a name, a flag, a file layout field.
- **Real, unit.** `*_uom`, `*_unit`, `uom`, and `unit`. The unit of a sibling value.
- **Real, codespace.** `*_codespace` other than `gmlid_codespace`. The vocabulary of a sibling code.
- **Real, geometry.** Coordinates stored on the row, rasters, placement matrices (`lod*_implicit_transformation`, `world_to_texture`), and the flags that describe a geometry node (`is_solid`, `is_xlink`, `is_reverse`, `is_triangulated`, `is_composite` on `surface_geometry`, `is_texture_parametrization`).

CityGML lifecycle columns (`creation_date`, `termination_date`, `lineage`, `updating_person`, `reason_for_update`, `last_modification_date`) are values. They describe the feature.

`datastream_id`, `observation_id`, `sensor_id`, `network_id`, and `network_node_id` are varchar identifiers of an external sensor service or utility network. They are values.

## Tables

One row per table. Administrative is keys, foreign keys, and gml identifiers. Real is values, units, code lists, and geometry.

### Metadata catalog

#### Metadata

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `ade` | 10 | 2 | 8 | 8 | 0 | 0 | 0 | Registry of Application Domain Extensions installed in this database. |
| `aggregation_info` | 6 | 2 | 4 | 4 | 0 | 0 | 0 | UML aggregation facts used by the importer: parent class, child class, and how many children are allowed. |
| `database_srs` | 2 | 1 | 1 | 1 | 0 | 0 | 0 | The coordinate reference system every geometry in the database is stored in. |
| `index_table` | 2 | 1 | 1 | 1 | 0 | 0 | 0 | Internal index helper. It is not a CityGML feature. |
| `objectclass` | 8 | 4 | 4 | 4 | 0 | 0 | 0 | Catalogue of CityGML and ADE classes, and the table that stores each class. |
| `schema` | 9 | 2 | 7 | 7 | 0 | 0 | 0 | XML schemas registered for CityGML and for each ADE. |
| `schema_referencing` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Which registered schema references which other schema. |
| `schema_to_objectclass` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Which object classes a registered schema defines. |

### Core, Building, and Energy ADE

#### Core

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `cityobject` | 17 | 4 | 13 | 11 | 0 | 1 | 1 | Base row of every city object: identifier, name, envelope, and lineage. |
| `cityobject_genericattrib` | 16 | 5 | 11 | 8 | 1 | 1 | 1 | Attributes that have no column of their own, stored as a name plus one typed value. |
| `citymodel` | 13 | 3 | 10 | 8 | 0 | 1 | 1 | The city model document that collects city objects. |
| `cityobject_member` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Membership of a city object in a city model. |
| `external_reference` | 5 | 2 | 3 | 3 | 0 | 0 | 0 | Pointer from a city object to an identifier in an external information system. |
| `generalization` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Link from a detailed feature to the coarser feature that generalizes it. |
| `surface_geometry` | 14 | 6 | 8 | 0 | 0 | 0 | 8 | Shared boundary-representation tree: surfaces, composites, and solids. |
| `implicit_geometry` | 8 | 4 | 4 | 3 | 0 | 0 | 1 | Reusable prototype geometry, placed on a feature by a point and a transformation. |

#### Building

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `address` | 12 | 3 | 9 | 8 | 0 | 0 | 1 | Postal address. Buildings and bridges both point at this table. |
| `address_to_building` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Links an address to a building. |
| `building` | 39 | 14 | 25 | 11 | 3 | 4 | 7 | Building and BuildingPart: class, function, usage, height, storeys, and LOD geometry. |
| `building_installation` | 25 | 10 | 15 | 3 | 0 | 3 | 9 | Something fixed to a building or a room, such as a balcony, stair, or chimney. |
| `building_furniture` | 14 | 5 | 9 | 3 | 0 | 3 | 3 | Furniture inside a room, modelled at LOD4. |
| `thematic_surface` | 8 | 8 | 0 | 0 | 0 | 0 | 0 | Wall, roof, ground, or closure surface. The type is objectclass_id and the shape is a foreign key, so the table has no value column. |
| `opening` | 11 | 7 | 4 | 0 | 0 | 0 | 4 | Door or window. |
| `opening_to_them_surface` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Links an opening to the thematic surface it cuts. |
| `room` | 11 | 5 | 6 | 3 | 0 | 3 | 0 | Interior room of a building at LOD4. |

#### Energy ADE

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `ng3_building` | 8 | 1 | 7 | 5 | 0 | 2 | 0 | Energy attributes of a CityGML building: type, protection, construction weight, attic and basement. |
| `ng3_building_partition` | 35 | 11 | 24 | 16 | 6 | 2 | 0 | Thermal zone, usage zone, or building unit. objectclass_id says which of the three. |
| `ng3_thematic_surface` | 20 | 1 | 19 | 10 | 9 | 0 | 0 | Energy attributes of a CityGML thematic surface: areas, orientation, view factors, heat capacity. |
| `ng3_opening` | 11 | 1 | 10 | 5 | 5 | 0 | 0 | Energy attributes of a CityGML opening: area, orientation, and view factors. |
| `ng3_them_surf_to_thermal_zone` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Links a thematic surface to the thermal zone it bounds. |
| `ng3_address_to_building_unit` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Links a postal address to a building unit. |
| `ng3_cityobject` | 3 | 2 | 1 | 0 | 0 | 0 | 1 | Energy extension of any city object: a reference point and an optional layered construction. |
| `ng3_ctyobj_relation` | 5 | 3 | 2 | 1 | 0 | 1 | 0 | Typed relation from an energy city object to another city object. |
| `ng3_layered_construction` | 12 | 4 | 8 | 4 | 3 | 1 | 0 | Construction assembly: U-value, g-value, glazing ratio, and an optional library entry. |
| `ng3_layer` | 5 | 3 | 2 | 1 | 1 | 0 | 0 | One layer of a layered construction: thickness and material. |
| `ng3_material` | 22 | 3 | 19 | 10 | 8 | 1 | 0 | Solid or gas material: conductivity, density, embodied energy, and related properties. |
| `ng3_optical_property` | 7 | 3 | 4 | 3 | 1 | 0 | 0 | Optical fraction of a construction over a wavelength range (reflectance, transmittance, and similar). |
| `ng3_library` | 6 | 2 | 4 | 3 | 0 | 1 | 0 | Library that materials, constructions, and schedules can be taken from. |
| `ng3_device` | 31 | 4 | 27 | 17 | 9 | 1 | 0 | Energy device installed on a city object: heat pump, boiler, shading, or a generic device. |
| `ng3_device_operation` | 6 | 3 | 3 | 2 | 0 | 1 | 0 | One operation mode of a device, with a yearly efficiency and a schedule. |
| `ng3_solar_collector` | 20 | 4 | 16 | 9 | 5 | 2 | 0 | Solar thermal or photovoltaic collector. Stored as a specialization of a device. |
| `ng3_storage_device` | 14 | 2 | 12 | 6 | 4 | 2 | 0 | Thermal store or battery. Stored as a specialization of a device. |
| `ng3_schedule` | 22 | 4 | 18 | 12 | 4 | 2 | 0 | Time schedule used by zones and devices: constant, dual-value, or backed by a time series. |
| `ng3_schedule_component` | 8 | 3 | 5 | 3 | 1 | 1 | 0 | One piece of a composite schedule, with a repeat count and a gap. |
| `ng3_occupants` | 20 | 3 | 17 | 9 | 4 | 4 | 0 | People in a building partition: count, metabolic heat, diet, income, and education. |
| `ng3_energy_perf_cert` | 12 | 3 | 9 | 7 | 1 | 1 | 0 | Energy performance certificate of a building or a building partition. |
| `ng3_qualified_attribute` | 10 | 4 | 6 | 4 | 1 | 1 | 0 | Named numeric attribute of a building or partition, with a description and a source. |
| `ng3_refurbishment_measure` | 9 | 3 | 6 | 4 | 0 | 2 | 0 | Refurbishment applied to a building or partition, with a start and an end. |
| `ng3_resource` | 34 | 4 | 30 | 18 | 6 | 6 | 0 | Energy, water, waste, or other resource flow: amount, end use, cost, and CO2. |
| `ng3_time_series` | 38 | 2 | 36 | 29 | 4 | 3 | 0 | Time series, stored as a value list, a file, or a sensor feed. |
| `ng3_weather_data` | 12 | 3 | 9 | 4 | 1 | 3 | 1 | Weather variable attached to a city object, as a yearly value or a time series. |
| `ng3_suitability` | 8 | 3 | 5 | 3 | 1 | 1 | 0 | Suitability of a city object for a use, with a reason and a score. |
| `ng3_utl_ntw_connection` | 11 | 2 | 9 | 6 | 0 | 3 | 0 | How a city object is connected to a utility network. |
| `ng3_urban_function_area` | 5 | 1 | 4 | 2 | 0 | 2 | 0 | Functional classification of a city object group (an urban area). |

### Other modules

#### Appearance

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `appearance` | 9 | 5 | 4 | 3 | 0 | 1 | 0 | Visual theme applied to one city object or to a whole city model. |
| `appear_to_surface_data` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Links an appearance to the surface data (material or texture) it uses. |
| `surface_data` | 22 | 5 | 17 | 15 | 0 | 1 | 1 | X3D material or texture that an appearance can reference. |
| `tex_image` | 5 | 1 | 4 | 3 | 0 | 1 | 0 | Image file or embedded bytes behind a texture. |
| `textureparam` | 5 | 2 | 3 | 0 | 0 | 0 | 3 | How one texture sits on one surface: texture coordinates, or a world-to-texture matrix. |

#### Bridge

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `bridge` | 28 | 12 | 16 | 6 | 0 | 3 | 7 | Bridge and BridgePart: class, function, usage, years, and LOD geometry. |
| `bridge_constr_element` | 33 | 11 | 22 | 3 | 0 | 3 | 16 | Structural member of a bridge, such as a pylon or a girder. |
| `bridge_installation` | 25 | 10 | 15 | 3 | 0 | 3 | 9 | Installation on a bridge or inside a bridge room. |
| `bridge_thematic_surface` | 9 | 9 | 0 | 0 | 0 | 0 | 0 | Semantic surface of a bridge. The type is objectclass_id and the shape is a foreign key, so the table has no value column. |
| `bridge_opening` | 11 | 7 | 4 | 0 | 0 | 0 | 4 | Opening in a bridge surface. |
| `bridge_open_to_them_srf` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Links a bridge opening to a bridge thematic surface. |
| `bridge_room` | 11 | 5 | 6 | 3 | 0 | 3 | 0 | Interior room of a bridge. |
| `bridge_furniture` | 14 | 5 | 9 | 3 | 0 | 3 | 3 | Furniture inside a bridge room. |
| `address_to_bridge` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Links an address to a bridge. |

#### CityFurniture

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `city_furniture` | 32 | 10 | 22 | 3 | 0 | 3 | 16 | Street furniture and similar objects, such as a bench, lamp, or sign. |

#### CityObjectGroup

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `cityobjectgroup` | 11 | 4 | 7 | 3 | 0 | 3 | 1 | Named group of city objects, with an optional geometry of the group itself. |
| `group_to_cityobject` | 3 | 2 | 1 | 1 | 0 | 0 | 0 | Membership of a city object in a group, together with the member's role. |

#### Generics

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `generic_cityobject` | 38 | 12 | 26 | 3 | 0 | 3 | 20 | City object that does not belong to another CityGML module. |

#### LandUse

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `land_use` | 13 | 7 | 6 | 3 | 0 | 3 | 0 | Land-use area. |

#### Relief

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `relief_feature` | 3 | 2 | 1 | 1 | 0 | 0 | 0 | Relief feature that groups relief components. |
| `relief_component` | 4 | 2 | 2 | 1 | 0 | 0 | 1 | Shared row of every relief component: level of detail and footprint. |
| `relief_feat_to_rel_comp` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Links a relief feature to its components. |
| `tin_relief` | 8 | 3 | 5 | 1 | 1 | 0 | 3 | Relief component stored as a triangulated irregular network. |
| `breakline_relief` | 4 | 2 | 2 | 0 | 0 | 0 | 2 | Relief component made of break lines and ridge or valley lines. |
| `masspoint_relief` | 3 | 2 | 1 | 0 | 0 | 0 | 1 | Relief component made of height points. |
| `raster_relief` | 4 | 3 | 1 | 1 | 0 | 0 | 0 | Relief component given as a raster. |
| `grid_coverage` | 2 | 1 | 1 | 0 | 0 | 0 | 1 | Raster grid referenced by a raster relief. |

#### Transportation

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `transportation_complex` | 13 | 6 | 7 | 3 | 0 | 3 | 1 | Road, railway, track, or square. |
| `traffic_area` | 14 | 6 | 8 | 4 | 0 | 4 | 0 | Traffic surface that belongs to a transportation complex. |

#### Tunnel

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `tunnel` | 27 | 12 | 15 | 5 | 0 | 3 | 7 | Tunnel and TunnelPart: class, function, usage, years, and LOD geometry. |
| `tunnel_installation` | 25 | 10 | 15 | 3 | 0 | 3 | 9 | Installation on a tunnel or inside a hollow space. |
| `tunnel_thematic_surface` | 8 | 8 | 0 | 0 | 0 | 0 | 0 | Semantic surface of a tunnel. The type is objectclass_id and the shape is a foreign key, so the table has no value column. |
| `tunnel_opening` | 10 | 6 | 4 | 0 | 0 | 0 | 4 | Opening in a tunnel surface. |
| `tunnel_open_to_them_srf` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Links a tunnel opening to a tunnel thematic surface. |
| `tunnel_hollow_space` | 11 | 5 | 6 | 3 | 0 | 3 | 0 | Interior hollow space of a tunnel. |
| `tunnel_furniture` | 14 | 5 | 9 | 3 | 0 | 3 | 3 | Furniture inside a tunnel hollow space. |

#### Vegetation

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `plant_cover` | 18 | 10 | 8 | 4 | 1 | 3 | 0 | Area of vegetation, such as a wood, a row, or a bed. |
| `solitary_vegetat_object` | 36 | 10 | 26 | 7 | 3 | 4 | 12 | A single plant, with species, height, trunk, and crown. |

#### WaterBody

| Table | Columns | Admin | Real | Values | Units | Code lists | Geometry | What it stores |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `waterbody` | 16 | 8 | 8 | 3 | 0 | 3 | 2 | River, lake, or other water body. |
| `waterboundary_surface` | 7 | 5 | 2 | 1 | 0 | 1 | 0 | Semantic surface of a water body, such as the water surface or the water ground. |
| `waterbod_to_waterbnd_srf` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | Links a water body to its boundary surfaces. |

## Attributes

Every column, in schema order, with the kind assigned above.

### Metadata

#### `ade`

Registry of Application Domain Extensions installed in this database.

10 columns: 2 administrative (1 key, 0 links, 1 identifier) and 8 real (8 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | integer | admin, key | Primary key of the ADE registry entry. |
| `adeid` | varchar | admin, identifier | Stable identifier of the ADE. |
| `name` | varchar | real, value | Name of the ADE. |
| `description` | varchar | real, value | What this ADE covers. |
| `version` | varchar | real, value | Version of the ADE. |
| `db_prefix` | varchar | real, value | Table-name prefix of this ADE. Energy ADE 3.0 uses ng3. |
| `xml_schemamapping_file` | text | real, value | Schema-mapping file the importer uses for this ADE. |
| `drop_db_script` | text | real, value | SQL that removes this ADE from the database. |
| `creation_date` | timestamptz | real, value | When this ADE was registered in the database. |
| `creation_person` | varchar | real, value | Person who registered this ADE. |

#### `aggregation_info`

UML aggregation facts used by the importer: parent class, child class, and how many children are allowed.

6 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 4 real (4 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `child_id` | integer | admin, link | Foreign key to objectclass.id. The child class in this aggregation. |
| `parent_id` | integer | admin, link | Foreign key to objectclass.id. The parent class in this aggregation. |
| `join_table_or_column_name` | varchar | real, value | Join table or column that stores this UML aggregation. |
| `min_occurs` | integer | real, value | Minimum number of child objects in this aggregation. |
| `max_occurs` | integer | real, value | Maximum number of child objects in this aggregation. |
| `is_composite` | numeric | real, value | 1 when the parent owns the child (UML composition). |

#### `database_srs`

The coordinate reference system every geometry in the database is stored in.

2 columns: 1 administrative (1 key, 0 links, 0 identifiers) and 1 real (1 value, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `srid` | integer | admin, key | Primary key. EPSG code used for every geometry in this database. |
| `gml_srs_name` | varchar | real, value | gml:srsName written into exported GML for this coordinate system. |

#### `index_table`

Internal index helper. It is not a CityGML feature.

2 columns: 1 administrative (1 key, 0 links, 0 identifiers) and 1 real (1 value, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | integer | admin, key | Primary key of the internal index entry. |
| `obj` | geometry | real, value | Opaque value held by the internal index. It is not a CityGML attribute. |

#### `objectclass`

Catalogue of CityGML and ADE classes, and the table that stores each class.

8 columns: 4 administrative (1 key, 3 links, 0 identifiers) and 4 real (4 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | integer | admin, key | Primary key of the class catalogue entry. |
| `is_ade_class` | numeric | real, value | 1 when this class comes from an ADE. |
| `is_toplevel` | numeric | real, value | 1 when this class may appear as a top-level city object. |
| `classname` | varchar | real, value | CityGML or ADE class name. |
| `tablename` | varchar | real, value | Database table that stores this class. |
| `superclass_id` | integer | admin, link | Foreign key to objectclass.id. The immediate parent class. |
| `baseclass_id` | integer | admin, link | Foreign key to objectclass.id. The root class of this inheritance branch. |
| `ade_id` | integer | admin, link | Foreign key to ade.id. The ADE this class or schema belongs to. |

#### `schema`

XML schemas registered for CityGML and for each ADE.

9 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 7 real (7 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | integer | admin, key | Primary key of the registered XML schema. |
| `is_ade_root` | numeric | real, value | 1 when this schema is the root schema of an ADE. |
| `citygml_version` | varchar | real, value | CityGML version this schema belongs to. |
| `xml_namespace_uri` | varchar | real, value | XML namespace URI of this schema. |
| `xml_namespace_prefix` | varchar | real, value | XML namespace prefix of this schema. |
| `xml_schema_location` | varchar | real, value | Schema-location hint for this XML schema. |
| `xml_schemafile` | bytea | real, value | The XML schema document, stored as bytes. |
| `xml_schemafile_type` | varchar | real, value | File type of the stored schema document. |
| `ade_id` | integer | admin, link | Foreign key to ade.id. The ADE this class or schema belongs to. |

#### `schema_referencing`

Which registered schema references which other schema.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `referencing_id` | integer | admin, link | Foreign key to schema.id. The schema that references another schema. |
| `referenced_id` | integer | admin, link | Foreign key to schema.id. The schema that is referenced. |

#### `schema_to_objectclass`

Which object classes a registered schema defines.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `schema_id` | integer | admin, link | Foreign key to schema.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |

### Core

#### `cityobject`

Base row of every city object: identifier, name, envelope, and lineage.

17 columns: 4 administrative (1 key, 1 link, 2 identifiers) and 13 real (11 values, 0 units, 1 code list, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of a city object. Subclass tables reuse this same value. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `gmlid` | varchar | admin, identifier | CityGML gml:id of this object. |
| `gmlid_codespace` | varchar | admin, identifier | Namespace of gml:id. |
| `name` | varchar | real, value | Name of the object. |
| `name_codespace` | varchar | real, codespace | Code-list namespace of `name`. Names the vocabulary of that value. |
| `description` | varchar | real, value | Free-text description. |
| `envelope` | geometry | real, geometry | Bounding box of the feature or the city model. |
| `creation_date` | timestamptz | real, value | When the feature or the city model was created. |
| `termination_date` | timestamptz | real, value | When the feature or the city model stopped being valid. |
| `relative_to_terrain` | varchar | real, value | Where the feature sits relative to the terrain. |
| `relative_to_water` | varchar | real, value | Where the feature sits relative to the water surface. |
| `last_modification_date` | timestamptz | real, value | When the feature or the city model was last updated. |
| `updating_person` | varchar | real, value | Who last updated the feature or the city model. |
| `reason_for_update` | varchar | real, value | Why the feature or the city model was last updated. |
| `lineage` | varchar | real, value | How the feature was produced or changed. |
| `xml_source` | text | real, value | XML fragment of this city object, kept by 3DCityDB. |

#### `cityobject_genericattrib`

Attributes that have no column of their own, stored as a name plus one typed value.

16 columns: 5 administrative (1 key, 4 links, 0 identifiers) and 11 real (8 values, 1 unit, 1 code list, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the generic attribute. |
| `parent_genattrib_id` | bigint | admin, link | Foreign key to cityobject_genericattrib.id. Parent of a nested generic-attribute set. |
| `root_genattrib_id` | bigint | admin, link | Foreign key to cityobject_genericattrib.id. Root of a nested generic-attribute set. |
| `attrname` | varchar | real, value | Name of the generic attribute. |
| `datatype` | integer | real, value | Which value column holds this generic attribute (string, integer, measure, URI, date, blob, or geometry). |
| `strval` | varchar | real, value | Generic attribute value stored as text. |
| `intval` | integer | real, value | Generic attribute value stored as an integer. |
| `realval` | float | real, value | Generic attribute value stored as a real number. |
| `urival` | varchar | real, value | Generic attribute value stored as a URI. |
| `dateval` | timestamptz | real, value | Generic attribute value stored as a date. |
| `unit` | varchar | real, unit | Unit of the generic attribute value. |
| `genattribset_codespace` | varchar | real, codespace | Code-list namespace of a nested generic-attribute set. |
| `blobval` | bytea | real, value | Generic attribute value stored as bytes. |
| `geomval` | geometry | real, geometry | Generic attribute value stored as a geometry. |
| `surface_geometry_id` | bigint | admin, link | Foreign key to surface_geometry.id. |
| `cityobject_id` | bigint | admin, link | Foreign key to cityobject.id. The feature this row belongs to. |

#### `citymodel`

The city model document that collects city objects.

13 columns: 3 administrative (1 key, 0 links, 2 identifiers) and 10 real (8 values, 0 units, 1 code list, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the city model. |
| `gmlid` | varchar | admin, identifier | CityGML gml:id of this object. |
| `gmlid_codespace` | varchar | admin, identifier | Namespace of gml:id. |
| `name` | varchar | real, value | Name of the object. |
| `name_codespace` | varchar | real, codespace | Code-list namespace of `name`. Names the vocabulary of that value. |
| `description` | varchar | real, value | Free-text description. |
| `envelope` | geometry | real, geometry | Bounding box of the feature or the city model. |
| `creation_date` | timestamptz | real, value | When the feature or the city model was created. |
| `termination_date` | timestamptz | real, value | When the feature or the city model stopped being valid. |
| `last_modification_date` | timestamptz | real, value | When the feature or the city model was last updated. |
| `updating_person` | varchar | real, value | Who last updated the feature or the city model. |
| `reason_for_update` | varchar | real, value | Why the feature or the city model was last updated. |
| `lineage` | varchar | real, value | How the feature was produced or changed. |

#### `cityobject_member`

Membership of a city object in a city model.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `citymodel_id` | bigint | admin, link | Foreign key to citymodel.id. |
| `cityobject_id` | bigint | admin, link | Foreign key to cityobject.id. The feature this row belongs to. |

#### `external_reference`

Pointer from a city object to an identifier in an external information system.

5 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 3 real (3 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the external reference. |
| `infosys` | varchar | real, value | Name of the external information system. |
| `name` | varchar | real, value | Name the external system gives this object. |
| `uri` | varchar | real, value | URI of the object in the external information system. |
| `cityobject_id` | bigint | admin, link | Foreign key to cityobject.id. The feature this row belongs to. |

#### `generalization`

Link from a detailed feature to the coarser feature that generalizes it.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `cityobject_id` | bigint | admin, link | Foreign key to cityobject.id. The feature this row belongs to. |
| `generalizes_to_id` | bigint | admin, link | Foreign key to cityobject.id. The coarser feature this one generalizes to. |

#### `surface_geometry`

Shared boundary-representation tree: surfaces, composites, and solids.

14 columns: 6 administrative (1 key, 3 links, 2 identifiers) and 8 real (0 values, 0 units, 0 code lists, 8 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the geometry node. |
| `gmlid` | varchar | admin, identifier | CityGML gml:id of this object. |
| `gmlid_codespace` | varchar | admin, identifier | Namespace of gml:id. |
| `parent_id` | bigint | admin, link | Foreign key to surface_geometry.id. The parent geometry node. |
| `root_id` | bigint | admin, link | Foreign key to surface_geometry.id. Root node of this geometry tree. |
| `is_solid` | numeric | real, geometry | 1 when this node is the root of a solid. |
| `is_composite` | numeric | real, geometry | 1 when the child nodes form one composite geometry. |
| `is_triangulated` | numeric | real, geometry | 1 when this node is a triangulated surface. |
| `is_xlink` | numeric | real, geometry | 1 when this node is a link to another geometry rather than its own coordinates. |
| `is_reverse` | numeric | real, geometry | 1 when the surface orientation is reversed against its parent. |
| `solid_geometry` | geometry | real, geometry | Solid geometry cached on this node. |
| `geometry` | geometry | real, geometry | Surface or curve geometry of this node. |
| `implicit_geometry` | geometry | real, geometry | Point used when this geometry node places an implicit prototype. |
| `cityobject_id` | bigint | admin, link | Foreign key to cityobject.id. The feature this row belongs to. |

#### `implicit_geometry`

Reusable prototype geometry, placed on a feature by a point and a transformation.

8 columns: 4 administrative (1 key, 1 link, 2 identifiers) and 4 real (3 values, 0 units, 0 code lists, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the prototype geometry. |
| `gmlid` | varchar | admin, identifier | CityGML gml:id of this object. |
| `gmlid_codespace` | varchar | admin, identifier | Namespace of gml:id. |
| `mime_type` | varchar | real, value | MIME type of the embedded prototype. |
| `reference_to_library` | varchar | real, value | URI of a prototype stored outside the database. |
| `library_object` | bytea | real, value | Prototype embedded in the database. |
| `relative_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Prototype geometry in its local frame. |
| `relative_other_geom` | geometry | real, geometry | Prototype geometry that is not a boundary representation, in the prototype's local frame. |

### Building

#### `address`

Postal address. Buildings and bridges both point at this table.

12 columns: 3 administrative (1 key, 0 links, 2 identifiers) and 9 real (8 values, 0 units, 0 code lists, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the address. |
| `gmlid` | varchar | admin, identifier | CityGML gml:id of this object. |
| `gmlid_codespace` | varchar | admin, identifier | Namespace of gml:id. |
| `street` | varchar | real, value | Street name. |
| `house_number` | varchar | real, value | House number. |
| `po_box` | varchar | real, value | Post-office box. |
| `zip_code` | varchar | real, value | Postal code. |
| `city` | varchar | real, value | City of the address. |
| `state` | varchar | real, value | State or region of the address. |
| `country` | varchar | real, value | Country of the address. |
| `multi_point` | geometry | real, geometry | Point location of the address. |
| `xal_source` | text | real, value | The address in its original xAL XML. |

#### `address_to_building`

Links an address to a building.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `building_id` | bigint | admin, link | Foreign key to building.id. |
| `address_id` | bigint | admin, link | Foreign key to address.id. |

#### `building`

Building and BuildingPart: class, function, usage, height, storeys, and LOD geometry.

39 columns: 14 administrative (1 key, 13 links, 0 identifiers) and 25 real (11 values, 3 units, 4 code lists, 7 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `building_parent_id` | bigint | admin, link | Foreign key to building.id. The parent building or building part. |
| `building_root_id` | bigint | admin, link | Foreign key to building.id. The root of the building hierarchy. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `year_of_construction` | date | real, value | Year of construction. |
| `year_of_demolition` | date | real, value | Year of demolition. |
| `roof_type` | varchar | real, value | Shape of the roof. |
| `roof_type_codespace` | varchar | real, codespace | Code-list namespace of `roof_type`. Names the vocabulary of that value. |
| `measured_height` | float | real, value | Measured height of the building. |
| `measured_height_unit` | varchar | real, unit | Unit of measure of `measured_height`. |
| `storeys_above_ground` | numeric | real, value | Number of storeys above ground. |
| `storeys_below_ground` | numeric | real, value | Number of storeys below ground. |
| `storey_heights_above_ground` | varchar | real, value | Height of each storey above ground. |
| `storey_heights_ag_unit` | varchar | real, unit | Unit of measure of `storey_heights_above_ground`. |
| `storey_heights_below_ground` | varchar | real, value | Height of each storey below ground. |
| `storey_heights_bg_unit` | varchar | real, unit | Unit of measure of `storey_heights_below_ground`. |
| `lod1_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 1. |
| `lod2_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 2. |
| `lod3_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 3. |
| `lod4_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 4. |
| `lod2_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 2. |
| `lod3_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 3. |
| `lod4_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 4. |
| `lod0_footprint_id` | bigint | admin, link | Foreign key to surface_geometry.id. Footprint at LOD 0. |
| `lod0_roofprint_id` | bigint | admin, link | Foreign key to surface_geometry.id. Roof outline at LOD 0. |
| `lod1_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 1. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `lod1_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 1. |
| `lod2_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 2. |
| `lod3_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 3. |
| `lod4_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 4. |

#### `building_installation`

Something fixed to a building or a room, such as a balcony, stair, or chimney.

25 columns: 10 administrative (1 key, 9 links, 0 identifiers) and 15 real (3 values, 0 units, 3 code lists, 9 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `building_id` | bigint | admin, link | Foreign key to building.id. |
| `room_id` | bigint | admin, link | Foreign key to room.id. |
| `lod2_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 2. |
| `lod3_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 3. |
| `lod4_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 4. |
| `lod2_other_geom` | geometry | real, geometry | Geometry at LOD 2 that is not a boundary representation. |
| `lod3_other_geom` | geometry | real, geometry | Geometry at LOD 3 that is not a boundary representation. |
| `lod4_other_geom` | geometry | real, geometry | Geometry at LOD 4 that is not a boundary representation. |
| `lod2_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 2. |
| `lod3_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 3. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod2_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 2. |
| `lod3_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 3. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod2_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 2. |
| `lod3_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 3. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

#### `building_furniture`

Furniture inside a room, modelled at LOD4.

14 columns: 5 administrative (1 key, 4 links, 0 identifiers) and 9 real (3 values, 0 units, 3 code lists, 3 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `room_id` | bigint | admin, link | Foreign key to room.id. |
| `lod4_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 4. |
| `lod4_other_geom` | geometry | real, geometry | Geometry at LOD 4 that is not a boundary representation. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

#### `thematic_surface`

Wall, roof, ground, or closure surface. The type is objectclass_id and the shape is a foreign key, so the table has no value column.

8 columns: 8 administrative (1 key, 7 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `building_id` | bigint | admin, link | Foreign key to building.id. |
| `room_id` | bigint | admin, link | Foreign key to room.id. |
| `building_installation_id` | bigint | admin, link | Foreign key to building_installation.id. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |

#### `opening`

Door or window.

11 columns: 7 administrative (1 key, 6 links, 0 identifiers) and 4 real (0 values, 0 units, 0 code lists, 4 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `address_id` | bigint | admin, link | Foreign key to address.id. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `lod3_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 3. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod3_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 3. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod3_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 3. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

#### `opening_to_them_surface`

Links an opening to the thematic surface it cuts.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `opening_id` | bigint | admin, link | Foreign key to opening.id. |
| `thematic_surface_id` | bigint | admin, link | Foreign key to thematic_surface.id. |

#### `room`

Interior room of a building at LOD4.

11 columns: 5 administrative (1 key, 4 links, 0 identifiers) and 6 real (3 values, 0 units, 3 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `building_id` | bigint | admin, link | Foreign key to building.id. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `lod4_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 4. |

### Energy ADE

#### `ng3_building`

Energy attributes of a CityGML building: type, protection, construction weight, attic and basement.

8 columns: 1 administrative (1 key, 0 links, 0 identifiers) and 7 real (5 values, 0 units, 2 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with building.id. Energy attributes of that building. |
| `type` | varchar | real, value | Energy ADE building type, finer than the CityGML class. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `is_protected` | numeric | real, value | 1 when the building is protected. |
| `constr_weight` | varchar | real, value | Construction weight class (light, medium, heavy). |
| `constr_weight_codespace` | varchar | real, codespace | Code-list namespace of `constr_weight`. Names the vocabulary of that value. |
| `attic_thm_status` | varchar | real, value | Thermal condition of the attic (heated, unheated, and similar). |
| `basement_thm_status` | varchar | real, value | Thermal condition of the basement (heated, unheated, and similar). |

#### `ng3_building_partition`

Thermal zone, usage zone, or building unit. objectclass_id says which of the three.

35 columns: 11 administrative (1 key, 10 links, 0 identifiers) and 24 real (16 values, 6 units, 2 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. ThermalZone, UsageZone, or BuildingUnit. |
| `heat_capacity` | numeric | real, value | Heat capacity. |
| `heat_capacity_uom` | varchar | real, unit | Unit of measure of `heat_capacity`. |
| `infiltration_rate` | numeric | real, value | Outdoor-air infiltration of the zone. |
| `infiltration_rate_uom` | varchar | real, unit | Unit of measure of `infiltration_rate`. |
| `is_cooled` | numeric | real, value | 1 when the zone is cooled. |
| `is_heated` | numeric | real, value | 1 when the zone is heated. |
| `coincides_with_lod2_hull` | numeric | real, value | 1 when the zone volume is the LOD 2 building shell. |
| `coincides_with_lod3_hull` | numeric | real, value | 1 when the zone volume is the LOD 3 building shell. |
| `type` | varchar | real, value | Type of the usage zone or building unit. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `is_primary` | numeric | real, value | 1 when this is the primary usage zone. |
| `num_of_building_units` | integer | real, value | Number of building units in the usage zone. |
| `int_heat_gains` | numeric | real, value | Internal heat gains, total. |
| `int_heat_gains_uom` | varchar | real, unit | Unit of measure of `int_heat_gains`. |
| `int_heat_gains_conv` | numeric | real, value | Convective part of the internal heat gains. |
| `int_heat_gains_conv_uom` | varchar | real, unit | Unit of measure of `int_heat_gains_conv`. |
| `int_heat_gains_lat` | numeric | real, value | Latent part of the internal heat gains. |
| `int_heat_gains_lat_uom` | varchar | real, unit | Unit of measure of `int_heat_gains_lat`. |
| `int_heat_gains_rad` | numeric | real, value | Radiant part of the internal heat gains. |
| `int_heat_gains_rad_uom` | varchar | real, unit | Unit of measure of `int_heat_gains_rad`. |
| `num_of_rooms` | integer | real, value | Number of rooms in the building unit. |
| `owner_name` | varchar | real, value | Name of the building-unit owner. |
| `ownership_type` | varchar | real, value | Kind of ownership. |
| `ownership_type_codespace` | varchar | real, codespace | Code-list namespace of `ownership_type`. Names the vocabulary of that value. |
| `cooling_schedule_id` | bigint | admin, link | Foreign key to ng3_schedule.id. Cooling schedule of the zone. |
| `heating_schedule_id` | bigint | admin, link | Foreign key to ng3_schedule.id. Heating schedule of the zone. |
| `ventilation_schedule_id` | bigint | admin, link | Foreign key to ng3_schedule.id. Ventilation schedule of the zone. |
| `usage_zone_id` | bigint | admin, link | Foreign key to ng3_building_partition.id. The usage zone this row sits in. |
| `thermal_zone_id` | bigint | admin, link | Foreign key to ng3_building_partition.id. The thermal zone. |
| `building_id` | bigint | admin, link | Foreign key to ng3_building.id. The building this energy object belongs to. |
| `lod1_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 1. |
| `lod2_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 2. |
| `lod3_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 3. |

#### `ng3_thematic_surface`

Energy attributes of a CityGML thematic surface: areas, orientation, view factors, heat capacity.

20 columns: 1 administrative (1 key, 0 links, 0 identifiers) and 19 real (10 values, 9 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with thematic_surface.id. Energy attributes of that thematic surface. |
| `total_surf_area` | numeric | real, value | Total area of the thematic surface. |
| `total_surf_area_uom` | varchar | real, unit | Unit of measure of `total_surf_area`. |
| `opaque_surf_area` | numeric | real, value | Opaque area of the thematic surface. |
| `opaque_surf_area_uom` | varchar | real, unit | Unit of measure of `opaque_surf_area`. |
| `open_to_surf_ratio` | numeric | real, value | Fraction of the surface that is openings. |
| `open_to_surf_ratio_uom` | varchar | real, unit | Unit of measure of `open_to_surf_ratio`. |
| `thickness` | numeric | real, value | Thickness. |
| `thickness_uom` | varchar | real, unit | Unit of measure of `thickness`. |
| `azimuth` | numeric | real, value | Direction in the horizontal plane. |
| `azimuth_uom` | varchar | real, unit | Unit of measure of `azimuth`. |
| `inclination` | numeric | real, value | Tilt relative to the horizontal. |
| `inclination_uom` | varchar | real, unit | Unit of measure of `inclination`. |
| `ground_view_factor` | numeric | real, value | Fraction of the view that sees the ground. |
| `ground_view_factor_uom` | varchar | real, unit | Unit of measure of `ground_view_factor`. |
| `sky_view_factor` | numeric | real, value | Fraction of the view that sees the sky. |
| `sky_view_factor_uom` | varchar | real, unit | Unit of measure of `sky_view_factor`. |
| `is_adiabatic` | numeric | real, value | 1 when the surface does not exchange heat. |
| `heat_capacity` | numeric | real, value | Heat capacity. |
| `heat_capacity_uom` | varchar | real, unit | Unit of measure of `heat_capacity`. |

#### `ng3_opening`

Energy attributes of a CityGML opening: area, orientation, and view factors.

11 columns: 1 administrative (1 key, 0 links, 0 identifiers) and 10 real (5 values, 5 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with opening.id. Energy attributes of that opening. |
| `area` | numeric | real, value | Area of the opening. |
| `area_uom` | varchar | real, unit | Unit of measure of `area`. |
| `azimuth` | numeric | real, value | Direction in the horizontal plane. |
| `azimuth_uom` | varchar | real, unit | Unit of measure of `azimuth`. |
| `inclination` | numeric | real, value | Tilt relative to the horizontal. |
| `inclination_uom` | varchar | real, unit | Unit of measure of `inclination`. |
| `ground_view_factor` | numeric | real, value | Fraction of the view that sees the ground. |
| `ground_view_factor_uom` | varchar | real, unit | Unit of measure of `ground_view_factor`. |
| `sky_view_factor` | numeric | real, value | Fraction of the view that sees the sky. |
| `sky_view_factor_uom` | varchar | real, unit | Unit of measure of `sky_view_factor`. |

#### `ng3_them_surf_to_thermal_zone`

Links a thematic surface to the thermal zone it bounds.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `thematic_surface_id` | bigint | admin, link | Foreign key to thematic_surface.id. |
| `thermal_zone_id` | bigint | admin, link | Foreign key to ng3_building_partition.id. The thermal zone. |

#### `ng3_address_to_building_unit`

Links a postal address to a building unit.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `address_id` | bigint | admin, link | Foreign key to address.id. |
| `building_unit_id` | bigint | admin, link | Foreign key to ng3_building_partition.id. The building unit. |

#### `ng3_cityobject`

Energy extension of any city object: a reference point and an optional layered construction.

3 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 1 real (0 values, 0 units, 0 code lists, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. Energy attributes of that city object. |
| `layered_construction_id` | bigint | admin, link | Foreign key to ng3_layered_construction.id. |
| `ref_point` | geometry | real, geometry | Reference point of the energy object. |

#### `ng3_ctyobj_relation`

Typed relation from an energy city object to another city object.

5 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 2 real (1 value, 0 units, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the relation. |
| `ng3_cityobject_id` | bigint | admin, link | Foreign key to ng3_cityobject.id. The energy object on the source side of the relation. |
| `cityobject_id` | bigint | admin, link | Foreign key to cityobject.id. The city object on the target side of the relation. |
| `relation_type` | varchar | real, value | Kind of relation between the two city objects. |
| `relation_type_codespace` | varchar | real, codespace | Code-list namespace of `relation_type`. Names the vocabulary of that value. |

#### `ng3_layered_construction`

Construction assembly: U-value, g-value, glazing ratio, and an optional library entry.

12 columns: 4 administrative (1 key, 3 links, 0 identifiers) and 8 real (4 values, 3 units, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `u_value` | numeric | real, value | Thermal transmittance of the construction. |
| `u_value_uom` | varchar | real, unit | Unit of measure of `u_value`. |
| `g_value` | numeric | real, value | Solar heat gain coefficient of the construction. |
| `g_value_uom` | varchar | real, unit | Unit of measure of `g_value`. |
| `glazing_ratio` | numeric | real, value | Fraction of the construction that is glazed. |
| `glazing_ratio_uom` | varchar | real, unit | Unit of measure of `glazing_ratio`. |
| `library_code` | varchar | real, value | Code of this object in a component library. |
| `library_code_codespace` | varchar | real, codespace | Code-list namespace of `library_code`. Names the vocabulary of that value. |
| `layered_construction_id` | bigint | admin, link | Foreign key to ng3_layered_construction.id. A construction this one is based on. |
| `library_id` | bigint | admin, link | Foreign key to ng3_library.id. |

#### `ng3_layer`

One layer of a layered construction: thickness and material.

5 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 2 real (1 value, 1 unit, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `thickness` | numeric | real, value | Thickness. |
| `thickness_uom` | varchar | real, unit | Unit of measure of `thickness`. |
| `material_id` | bigint | admin, link | Foreign key to ng3_material.id. |
| `layered_construction_id` | bigint | admin, link | Foreign key to ng3_layered_construction.id. |

#### `ng3_material`

Solid or gas material: conductivity, density, embodied energy, and related properties.

22 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 19 real (10 values, 8 units, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Solid material or gas. |
| `library_code` | varchar | real, value | Code of this object in a component library. |
| `library_code_codespace` | varchar | real, codespace | Code-list namespace of `library_code`. Names the vocabulary of that value. |
| `thm_conductivity` | numeric | real, value | Thermal conductivity of the material. |
| `thm_conductivity_uom` | varchar | real, unit | Unit of measure of `thm_conductivity`. |
| `spec_heat_capacity` | numeric | real, value | Specific heat capacity of the material. |
| `spec_heat_capacity_uom` | varchar | real, unit | Unit of measure of `spec_heat_capacity`. |
| `density` | numeric | real, value | Density of the material. |
| `density_uom` | varchar | real, unit | Unit of measure of `density`. |
| `permeance` | numeric | real, value | Vapour permeance of the material. |
| `permeance_uom` | varchar | real, unit | Unit of measure of `permeance`. |
| `porosity` | numeric | real, value | Porosity of the material. |
| `porosity_uom` | varchar | real, unit | Unit of measure of `porosity`. |
| `embodied_carbon` | numeric | real, value | Embodied carbon of the material. |
| `embodied_carbon_uom` | varchar | real, unit | Unit of measure of `embodied_carbon`. |
| `embodied_energy` | numeric | real, value | Embodied energy of the material. |
| `embodied_energy_uom` | varchar | real, unit | Unit of measure of `embodied_energy`. |
| `is_ventilated` | numeric | real, value | 1 when the gas layer is ventilated. |
| `r_value` | numeric | real, value | Thermal resistance of a gas layer. |
| `r_value_uom` | varchar | real, unit | Unit of measure of `r_value`. |
| `library_id` | bigint | admin, link | Foreign key to ng3_library.id. |

#### `ng3_optical_property`

Optical fraction of a construction over a wavelength range (reflectance, transmittance, and similar).

7 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 4 real (3 values, 1 unit, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the optical property. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `fraction` | numeric | real, value | Optical fraction (reflectance, transmittance, or absorptance). |
| `fraction_uom` | varchar | real, unit | Unit of measure of `fraction`. |
| `surface` | varchar | real, value | Which face of the construction this optical fraction refers to. |
| `wavelength_range` | varchar | real, value | Wavelength band this optical fraction applies to. |
| `layered_construction_id` | bigint | admin, link | Foreign key to ng3_layered_construction.id. |

#### `ng3_library`

Library that materials, constructions, and schedules can be taken from.

6 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 4 real (3 values, 0 units, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `type` | varchar | real, value | Kind of library. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `author` | varchar | real, value | Author of the library. |
| `source` | varchar | real, value | Where the library was published or obtained. |

#### `ng3_device`

Energy device installed on a city object: heat pump, boiler, shading, or a generic device.

31 columns: 4 administrative (1 key, 3 links, 0 identifiers) and 27 real (17 values, 9 units, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Device subclass (heat pump, boiler, shading, generic device). |
| `model` | varchar | real, value | Manufacturer model of the device. |
| `num_of_devices` | integer | real, value | How many physical devices this row stands for. |
| `year_of_manufacture` | integer | real, value | Year the device was manufactured. |
| `installed_power` | numeric | real, value | Rated power of the device. |
| `installed_power_uom` | varchar | real, unit | Unit of measure of `installed_power`. |
| `nominal_efficiency` | numeric | real, value | Rated efficiency of the device. |
| `nominal_efficiency_uom` | varchar | real, unit | Unit of measure of `nominal_efficiency`. |
| `efficiency_indicator` | varchar | real, value | Name of the efficiency metric, such as COP or EER. |
| `heat_diss` | numeric | real, value | Heat given off, total. |
| `heat_diss_uom` | varchar | real, unit | Unit of measure of `heat_diss`. |
| `heat_diss_conv` | numeric | real, value | Convective part of the heat given off. |
| `heat_diss_conv_uom` | varchar | real, unit | Unit of measure of `heat_diss_conv`. |
| `heat_diss_lat` | numeric | real, value | Latent part of the heat given off. |
| `heat_diss_lat_uom` | varchar | real, unit | Unit of measure of `heat_diss_lat`. |
| `heat_diss_rad` | numeric | real, value | Radiant part of the heat given off. |
| `heat_diss_rad_uom` | varchar | real, unit | Unit of measure of `heat_diss_rad`. |
| `heat_source` | varchar | real, value | Source a heat pump draws heat from. |
| `cop_source_temp` | numeric | real, value | Source-side temperature used when stating the heat-pump COP. |
| `cop_source_temp_uom` | varchar | real, unit | Unit of measure of `cop_source_temp`. |
| `cop_operation_temp` | numeric | real, value | Output-side temperature used when stating the heat-pump COP. |
| `cop_operation_temp_uom` | varchar | real, unit | Unit of measure of `cop_operation_temp`. |
| `has_condensation` | numeric | real, value | 1 when the boiler is a condensing boiler. |
| `type` | varchar | real, value | Type of shading device. Heat pumps and boilers use other columns. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `installation_side` | varchar | real, value | Side of the opening the shading device is mounted on. |
| `max_cover_ratio` | numeric | real, value | Largest fraction of the opening the shading device can cover. |
| `max_cover_ratio_uom` | varchar | real, unit | Unit of measure of `max_cover_ratio`. |
| `transmittance_id` | bigint | admin, link | Foreign key to ng3_optical_property.id. Transmittance of a shading device. |
| `cityobject_id` | bigint | admin, link | Foreign key to ng3_cityobject.id. The energy city object this row belongs to. |

#### `ng3_device_operation`

One operation mode of a device, with a yearly efficiency and a schedule.

6 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 3 real (2 values, 0 units, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `type` | varchar | real, value | Operation mode of the device. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `yearly_global_efficiency` | numeric | real, value | Efficiency of this operation mode over a year. |
| `schedule_id` | bigint | admin, link | Foreign key to ng3_schedule.id. |
| `device_id` | bigint | admin, link | Foreign key to ng3_device.id. |

#### `ng3_solar_collector`

Solar thermal or photovoltaic collector. Stored as a specialization of a device.

20 columns: 4 administrative (1 key, 3 links, 0 identifiers) and 16 real (9 values, 5 units, 2 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with ng3_device.id. A solar collector is a device. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `type` | varchar | real, value | Collector type (photovoltaic or solar thermal). |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `cell_type` | varchar | real, value | Photovoltaic cell technology. |
| `cell_type_codespace` | varchar | real, codespace | Code-list namespace of `cell_type`. Names the vocabulary of that value. |
| `module_area` | numeric | real, value | Gross module area of the collector. |
| `module_area_uom` | varchar | real, unit | Unit of measure of `module_area`. |
| `azimuth` | numeric | real, value | Direction in the horizontal plane. |
| `azimuth_uom` | varchar | real, unit | Unit of measure of `azimuth`. |
| `inclination` | numeric | real, value | Tilt relative to the horizontal. |
| `inclination_uom` | varchar | real, unit | Unit of measure of `inclination`. |
| `aperture_area` | numeric | real, value | Aperture area of the collector. |
| `aperture_area_uom` | varchar | real, unit | Unit of measure of `aperture_area`. |
| `opt_efficiency` | numeric | real, value | Optical efficiency of the collector. |
| `opt_efficiency_uom` | varchar | real, unit | Unit of measure of `opt_efficiency`. |
| `lin_heat_loss_coeff` | numeric | real, value | Linear heat-loss coefficient of the collector. |
| `quad_heat_loss_coeff` | numeric | real, value | Quadratic heat-loss coefficient of the collector. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |

#### `ng3_storage_device`

Thermal store or battery. Stored as a specialization of a device.

14 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 12 real (6 values, 4 units, 2 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with ng3_device.id. Thermal or battery storage is a device. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `medium` | varchar | real, value | Storage medium (water, phase-change material, and similar). |
| `medium_codespace` | varchar | real, codespace | Code-list namespace of `medium`. Names the vocabulary of that value. |
| `preparation_temp` | numeric | real, value | Temperature the storage is prepared at. |
| `preparation_temp_uom` | varchar | real, unit | Unit of measure of `preparation_temp`. |
| `thm_losses_factor` | numeric | real, value | Thermal-loss factor of the storage. |
| `thm_losses_factor_uom` | varchar | real, unit | Unit of measure of `thm_losses_factor`. |
| `volume` | numeric | real, value | Volume of the storage. |
| `volume_uom` | varchar | real, unit | Unit of measure of `volume`. |
| `batt_techn` | varchar | real, value | Battery technology. |
| `batt_techn_codespace` | varchar | real, codespace | Code-list namespace of `batt_techn`. Names the vocabulary of that value. |
| `power_capacity` | numeric | real, value | Power capacity of the battery. |
| `power_capacity_uom` | varchar | real, unit | Unit of measure of `power_capacity`. |

#### `ng3_schedule`

Time schedule used by zones and devices: constant, dual-value, or backed by a time series.

22 columns: 4 administrative (1 key, 3 links, 0 identifiers) and 18 real (12 values, 4 units, 2 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Schedule subclass (constant, dual, composite, and similar). |
| `library_code` | varchar | real, value | Code of this object in a component library. |
| `library_code_codespace` | varchar | real, codespace | Code-list namespace of `library_code`. Names the vocabulary of that value. |
| `type` | varchar | real, value | Kind of schedule. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `start_time` | time | real, value | Time of day the schedule or series starts. |
| `start_day` | integer | real, value | Day of the month the schedule or series starts. |
| `start_month` | integer | real, value | Month the schedule or series starts. |
| `start_year` | integer | real, value | Year the schedule starts. |
| `time_interval` | numeric | real, value | Time step between successive values. |
| `time_interval_unit` | varchar | real, unit | Unit of measure of `time_interval`. |
| `idle_value` | numeric | real, value | Schedule value outside the occupied period. |
| `idle_value_uom` | varchar | real, unit | Unit of measure of `idle_value`. |
| `usage_value` | numeric | real, value | Schedule value during the occupied period. |
| `usage_value_uom` | varchar | real, unit | Unit of measure of `usage_value`. |
| `start_usage_time` | time | real, value | Time of day the occupied period starts. |
| `end_usage_time` | time | real, value | Time of day the occupied period ends. |
| `constant_value` | numeric | real, value | Single value of a constant schedule. |
| `constant_value_uom` | varchar | real, unit | Unit of measure of `constant_value`. |
| `time_series_id` | bigint | admin, link | Foreign key to ng3_time_series.id. |
| `library_id` | bigint | admin, link | Foreign key to ng3_library.id. |

#### `ng3_schedule_component`

One piece of a composite schedule, with a repeat count and a gap.

8 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 5 real (3 values, 1 unit, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `type` | varchar | real, value | Kind of schedule component. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `repetitions` | integer | real, value | How many times this schedule component repeats. |
| `additional_gap` | numeric | real, value | Extra time gap inserted after this schedule component. |
| `additional_gap_unit` | varchar | real, unit | Unit of measure of `additional_gap`. |
| `parent_schedule_id` | bigint | admin, link | Foreign key to ng3_schedule.id. The composite schedule this component belongs to. |
| `schedule_id` | bigint | admin, link | Foreign key to ng3_schedule.id. The schedule used as this component. |

#### `ng3_occupants`

People in a building partition: count, metabolic heat, diet, income, and education.

20 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 17 real (9 values, 4 units, 4 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `type` | varchar | real, value | Occupant type (household, workplace, and similar). |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `num_of_occupants` | integer | real, value | Number of occupants. |
| `heat_diss` | numeric | real, value | Heat given off, total. |
| `heat_diss_uom` | varchar | real, unit | Unit of measure of `heat_diss`. |
| `heat_diss_conv` | numeric | real, value | Convective part of the heat given off. |
| `heat_diss_conv_uom` | varchar | real, unit | Unit of measure of `heat_diss_conv`. |
| `heat_diss_lat` | numeric | real, value | Latent part of the heat given off. |
| `heat_diss_lat_uom` | varchar | real, unit | Unit of measure of `heat_diss_lat`. |
| `heat_diss_rad` | numeric | real, value | Radiant part of the heat given off. |
| `heat_diss_rad_uom` | varchar | real, unit | Unit of measure of `heat_diss_rad`. |
| `avg_diet_type` | varchar | real, value | Average diet of the occupants. |
| `avg_diet_type_codespace` | varchar | real, codespace | Code-list namespace of `avg_diet_type`. Names the vocabulary of that value. |
| `avg_income_level` | varchar | real, value | Average income level of the occupants. |
| `avg_income_level_codespace` | varchar | real, codespace | Code-list namespace of `avg_income_level`. Names the vocabulary of that value. |
| `avg_instr_level` | varchar | real, value | Average education level of the occupants. |
| `avg_instr_level_codespace` | varchar | real, codespace | Code-list namespace of `avg_instr_level`. Names the vocabulary of that value. |
| `schedule_id` | bigint | admin, link | Foreign key to ng3_schedule.id. |
| `building_partition_id` | bigint | admin, link | Foreign key to ng3_building_partition.id. |

#### `ng3_energy_perf_cert`

Energy performance certificate of a building or a building partition.

12 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 9 real (7 values, 1 unit, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `type` | varchar | real, value | Kind of energy performance certificate. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `label` | varchar | real, value | Label printed on the certificate, such as an energy class. |
| `value` | numeric | real, value | Numeric rating reported on the certificate. |
| `value_uom` | varchar | real, unit | Unit of measure of `value`. |
| `issue_date` | date | real, value | When the certificate was issued. |
| `expiration_date` | date | real, value | When the certificate expires. |
| `cert_method` | varchar | real, value | Method used to produce the certificate. |
| `cert_uri` | varchar | real, value | Link to the certificate document. |
| `building_id` | bigint | admin, link | Foreign key to ng3_building.id. The building this energy object belongs to. |
| `building_partition_id` | bigint | admin, link | Foreign key to ng3_building_partition.id. |

#### `ng3_qualified_attribute`

Named numeric attribute of a building or partition, with a description and a source.

10 columns: 4 administrative (1 key, 3 links, 0 identifiers) and 6 real (4 values, 1 unit, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the qualified attribute. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `type` | varchar | real, value | What this qualified number represents. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `value` | numeric | real, value | The qualified number itself. |
| `value_uom` | varchar | real, unit | Unit of measure of `value`. |
| `description` | varchar | real, value | Free-text description. |
| `source` | varchar | real, value | Where this qualified value comes from. |
| `building_id` | bigint | admin, link | Foreign key to ng3_building.id. The building this energy object belongs to. |
| `building_partition_id` | bigint | admin, link | Foreign key to ng3_building_partition.id. |

#### `ng3_refurbishment_measure`

Refurbishment applied to a building or partition, with a start and an end.

9 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 6 real (4 values, 0 units, 2 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `type` | varchar | real, value | Kind of refurbishment. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `start_date` | date | real, value | When the refurbishment starts. |
| `end_date` | date | real, value | When the refurbishment ends. |
| `library_code` | varchar | real, value | Code of this object in a component library. |
| `library_code_codespace` | varchar | real, codespace | Code-list namespace of `library_code`. Names the vocabulary of that value. |
| `building_id` | bigint | admin, link | Foreign key to ng3_building.id. The building this energy object belongs to. |
| `building_partition_id` | bigint | admin, link | Foreign key to ng3_building_partition.id. |

#### `ng3_resource`

Energy, water, waste, or other resource flow: amount, end use, cost, and CO2.

34 columns: 4 administrative (1 key, 3 links, 0 identifiers) and 30 real (18 values, 6 units, 6 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Resource subclass (energy, water, waste, and similar). |
| `type` | varchar | real, value | Kind of resource (energy carrier group, water, waste, and similar). |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `enduse` | varchar | real, value | What the resource is used for. |
| `enduse_codespace` | varchar | real, codespace | Code-list namespace of `enduse`. Names the vocabulary of that value. |
| `status` | varchar | real, value | Status of the resource record. |
| `operation_type` | varchar | real, value | How the resource flow is operated or accounted. |
| `operation_type_codespace` | varchar | real, codespace | Code-list namespace of `operation_type`. Names the vocabulary of that value. |
| `year` | integer | real, value | Year this resource amount refers to. |
| `amount_type` | varchar | real, value | What the amount represents, such as consumption or production. |
| `amount_type_codespace` | varchar | real, codespace | Code-list namespace of `amount_type`. Names the vocabulary of that value. |
| `amount` | numeric | real, value | Quantity of the resource. |
| `amount_uom` | varchar | real, unit | Unit of measure of `amount`. |
| `time_series_id` | bigint | admin, link | Foreign key to ng3_time_series.id. |
| `is_amount_normalized` | numeric | real, value | 1 when the resource amount has been normalized. |
| `normalization_param` | varchar | real, value | Quantity the amount was divided by, such as floor area. |
| `normalization_value` | numeric | real, value | Value of the normalizing quantity. |
| `normalization_value_uom` | varchar | real, unit | Unit of measure of `normalization_value`. |
| `co2_equivalent` | numeric | real, value | Greenhouse-gas emissions of this resource amount, as CO2 equivalent. |
| `co2_equivalent_uom` | varchar | real, unit | Unit of measure of `co2_equivalent`. |
| `costs_money` | numeric | real, value | Cost of this resource amount. |
| `costs_money_uom` | varchar | real, unit | Unit of measure of `costs_money`. |
| `yields_money` | numeric | real, value | Income produced by this resource amount. |
| `yields_money_uom` | varchar | real, unit | Unit of measure of `yields_money`. |
| `energy_carrier` | varchar | real, value | Energy carrier, such as gas or electricity. |
| `energy_carrier_codespace` | varchar | real, codespace | Code-list namespace of `energy_carrier`. Names the vocabulary of that value. |
| `maximum_load` | numeric | real, value | Peak load of the resource. |
| `maximum_load_uom` | varchar | real, unit | Unit of measure of `maximum_load`. |
| `source` | varchar | real, value | Source of the resource. For energy, the energy source. |
| `source_codespace` | varchar | real, codespace | Code-list namespace of `source`. Names the vocabulary of that value. |
| `is_dangerous` | numeric | real, value | 1 when the waste is hazardous. |
| `is_recyclable` | numeric | real, value | 1 when the waste is recyclable. |
| `cityobject_id` | bigint | admin, link | Foreign key to ng3_cityobject.id. The energy city object this row belongs to. |

#### `ng3_time_series`

Time series, stored as a value list, a file, or a sensor feed.

38 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 36 real (29 values, 4 units, 3 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. How the series is stored (list, file, or sensor). |
| `acquisition_method` | varchar | real, value | How the time-series values were acquired. |
| `acquisition_method_codespace` | varchar | real, codespace | Code-list namespace of `acquisition_method`. Names the vocabulary of that value. |
| `interpolation_type` | varchar | real, value | How to interpolate between time-series values. |
| `source` | varchar | real, value | Where the series was obtained. |
| `period_begin` | timestamptz | real, value | Start of the period the series covers. |
| `period_end` | timestamptz | real, value | End of the period the series covers. |
| `start_time` | time | real, value | Time of day the schedule or series starts. |
| `start_day` | integer | real, value | Day of the month the schedule or series starts. |
| `start_month` | integer | real, value | Month the schedule or series starts. |
| `temporal_extent` | numeric | real, value | Length of time the series covers. |
| `temporal_extent_unit` | varchar | real, unit | Unit of measure of `temporal_extent`. |
| `time_interval` | numeric | real, value | Time step between successive values. |
| `time_interval_unit` | varchar | real, unit | Unit of measure of `time_interval`. |
| `values_list` | text | real, value | Series values stored in one text field. |
| `values_list_uom` | varchar | real, unit | Unit of measure of `values_list`. |
| `uom` | varchar | real, unit | Unit of the values in this time series. |
| `file_uri` | varchar | real, value | URI of a file that holds the series. |
| `num_of_header_lines` | integer | real, value | Header lines to skip in a series file. |
| `field_separator` | varchar | real, value | Column separator in a series file. |
| `record_separator` | varchar | real, value | Row separator in a series file. |
| `value_column_number` | integer | real, value | Which column of a series file holds the values. |
| `decimal_symbol` | varchar | real, value | Character used as the decimal mark in a series file. |
| `auth_type` | varchar | real, value | Authentication used to reach a live sensor feed. |
| `auth_type_codespace` | varchar | real, codespace | Code-list namespace of `auth_type`. Names the vocabulary of that value. |
| `base_url` | varchar | real, value | Base URL of the sensor service. |
| `connection_type` | varchar | real, value | How the series is attached to a live source. |
| `connection_type_codespace` | varchar | real, codespace | Code-list namespace of `connection_type`. Names the vocabulary of that value. |
| `datastream_id` | varchar | real, value | Identifier of the datastream in the sensor service. A text id, not a database foreign key. |
| `link_to_observation` | varchar | real, value | Link to the observation in the sensor service. |
| `link_to_sensor_description` | varchar | real, value | Link to the sensor description. |
| `mqtt_server` | varchar | real, value | MQTT broker that publishes this series. |
| `mqtt_topic` | varchar | real, value | MQTT topic of this series. |
| `observation_id` | varchar | real, value | Identifier of the observation in the sensor service. A text id, not a database foreign key. |
| `observation_property` | varchar | real, value | Quantity the sensor observes. |
| `sensor_id` | varchar | real, value | Identifier of the sensor in the sensor service. A text id, not a database foreign key. |
| `sensor_name` | varchar | real, value | Name of the sensor. |

#### `ng3_weather_data`

Weather variable attached to a city object, as a yearly value or a time series.

12 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 9 real (4 values, 1 unit, 3 code lists, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `type` | varchar | real, value | Kind of weather data set. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `value_type` | varchar | real, value | What the weather number measures. |
| `value_type_codespace` | varchar | real, codespace | Code-list namespace of `value_type`. Names the vocabulary of that value. |
| `yearly_value` | numeric | real, value | Single yearly value of the weather variable. |
| `yearly_value_uom` | varchar | real, unit | Unit of measure of `yearly_value`. |
| `library_code` | varchar | real, value | Code of this object in a component library. |
| `library_code_codespace` | varchar | real, codespace | Code-list namespace of `library_code`. Names the vocabulary of that value. |
| `time_series_id` | bigint | admin, link | Foreign key to ng3_time_series.id. |
| `cityobject_id` | bigint | admin, link | Foreign key to ng3_cityobject.id. The energy city object this row belongs to. |
| `position` | geometry | real, geometry | Point where the weather variable applies. |

#### `ng3_suitability`

Suitability of a city object for a use, with a reason and a score.

8 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 5 real (3 values, 1 unit, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the suitability record. |
| `reason` | varchar | real, value | Why the suitability has this score. |
| `reason_codespace` | varchar | real, codespace | Code-list namespace of `reason`. Names the vocabulary of that value. |
| `value` | numeric | real, value | Suitability score. |
| `value_uom` | varchar | real, unit | Unit of measure of `value`. |
| `description` | varchar | real, value | Free-text description. |
| `schedule_id` | bigint | admin, link | Foreign key to ng3_schedule.id. |
| `cityobject_id` | bigint | admin, link | Foreign key to ng3_cityobject.id. The energy city object this row belongs to. |

#### `ng3_utl_ntw_connection`

How a city object is connected to a utility network.

11 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 9 real (6 values, 0 units, 3 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `network_type` | varchar | real, value | Kind of utility network. |
| `network_type_codespace` | varchar | real, codespace | Code-list namespace of `network_type`. Names the vocabulary of that value. |
| `connection_status` | varchar | real, value | Whether the network connection is active. |
| `function_in_network` | varchar | real, value | Function of this connection inside the network. |
| `function_in_network_codespace` | varchar | real, codespace | Code-list namespace of `function_in_network`. Names the vocabulary of that value. |
| `usage_in_network` | varchar | real, value | How this connection is used inside the network. |
| `usage_in_network_codespace` | varchar | real, codespace | Code-list namespace of `usage_in_network`. Names the vocabulary of that value. |
| `network_id` | varchar | real, value | Identifier of the utility network in the source system. A text id, not a database foreign key. |
| `network_node_id` | varchar | real, value | Identifier of the network node in the source system. A text id, not a database foreign key. |
| `cityobject_id` | bigint | admin, link | Foreign key to ng3_cityobject.id. The energy city object this row belongs to. |

#### `ng3_urban_function_area`

Functional classification of a city object group (an urban area).

5 columns: 1 administrative (1 key, 0 links, 0 identifiers) and 4 real (2 values, 0 units, 2 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobjectgroup.id. Function of that city object group. |
| `type` | varchar | real, value | Kind of urban function area. |
| `type_codespace` | varchar | real, codespace | Code-list namespace of `type`. Names the vocabulary of that value. |
| `code` | varchar | real, value | Code of the urban function. |
| `code_codespace` | varchar | real, codespace | Code-list namespace of `code`. Names the vocabulary of that value. |

### Appearance

#### `appearance`

Visual theme applied to one city object or to a whole city model.

9 columns: 5 administrative (1 key, 2 links, 2 identifiers) and 4 real (3 values, 0 units, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the appearance. |
| `gmlid` | varchar | admin, identifier | CityGML gml:id of this object. |
| `gmlid_codespace` | varchar | admin, identifier | Namespace of gml:id. |
| `name` | varchar | real, value | Name of the object. |
| `name_codespace` | varchar | real, codespace | Code-list namespace of `name`. Names the vocabulary of that value. |
| `description` | varchar | real, value | Free-text description. |
| `theme` | varchar | real, value | Name of the visual theme. |
| `citymodel_id` | bigint | admin, link | Foreign key to citymodel.id. |
| `cityobject_id` | bigint | admin, link | Foreign key to cityobject.id. The feature this row belongs to. |

#### `appear_to_surface_data`

Links an appearance to the surface data (material or texture) it uses.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `surface_data_id` | bigint | admin, link | Foreign key to surface_data.id. |
| `appearance_id` | bigint | admin, link | Foreign key to appearance.id. |

#### `surface_data`

X3D material or texture that an appearance can reference.

22 columns: 5 administrative (1 key, 2 links, 2 identifiers) and 17 real (15 values, 0 units, 1 code list, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the material or texture. |
| `gmlid` | varchar | admin, identifier | CityGML gml:id of this object. |
| `gmlid_codespace` | varchar | admin, identifier | Namespace of gml:id. |
| `name` | varchar | real, value | Name of the object. |
| `name_codespace` | varchar | real, codespace | Code-list namespace of `name`. Names the vocabulary of that value. |
| `description` | varchar | real, value | Free-text description. |
| `is_front` | numeric | real, value | 1 when this material or texture covers the front face. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Selects X3D material, texture, or georeferenced texture. |
| `x3d_shininess` | float | real, value | X3D shininess of the material. |
| `x3d_transparency` | float | real, value | X3D transparency of the material. |
| `x3d_ambient_intensity` | float | real, value | X3D ambient intensity of the material. |
| `x3d_specular_color` | varchar | real, value | X3D specular color. |
| `x3d_diffuse_color` | varchar | real, value | X3D diffuse color. |
| `x3d_emissive_color` | varchar | real, value | X3D emissive color. |
| `x3d_is_smooth` | numeric | real, value | 1 when the X3D material is smooth-shaded. |
| `tex_image_id` | bigint | admin, link | Foreign key to tex_image.id. |
| `tex_texture_type` | varchar | real, value | How specific the texture is: a unique image, a typical image, or unknown. |
| `tex_wrap_mode` | varchar | real, value | Behaviour at the texture edge: wrap, mirror, clamp, or border. |
| `tex_border_color` | varchar | real, value | Border color used when the texture wrap mode is border. |
| `gt_prefer_worldfile` | numeric | real, value | 1 when a world file should place this georeferenced texture. |
| `gt_orientation` | varchar | real, value | Orientation of a georeferenced texture. |
| `gt_reference_point` | geometry | real, geometry | Reference point of a georeferenced texture. |

#### `tex_image`

Image file or embedded bytes behind a texture.

5 columns: 1 administrative (1 key, 0 links, 0 identifiers) and 4 real (3 values, 0 units, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the texture image. |
| `tex_image_uri` | varchar | real, value | URI of the texture image. |
| `tex_image_data` | bytea | real, value | Texture image stored in the database. |
| `tex_mime_type` | varchar | real, value | MIME type of the texture image. |
| `tex_mime_type_codespace` | varchar | real, codespace | Code-list namespace of `tex_mime_type`. Names the vocabulary of that value. |

#### `textureparam`

How one texture sits on one surface: texture coordinates, or a world-to-texture matrix.

5 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 3 real (0 values, 0 units, 0 code lists, 3 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `surface_geometry_id` | bigint | admin, link | Foreign key to surface_geometry.id. |
| `is_texture_parametrization` | numeric | real, geometry | 1 when this row stores an explicit texture parametrization. |
| `world_to_texture` | varchar | real, geometry | Matrix from world coordinates into texture coordinates. |
| `texture_coordinates` | geometry | real, geometry | Texture coordinates on the rings of the surface. |
| `surface_data_id` | bigint | admin, link | Foreign key to surface_data.id. |

### Bridge

#### `bridge`

Bridge and BridgePart: class, function, usage, years, and LOD geometry.

28 columns: 12 administrative (1 key, 11 links, 0 identifiers) and 16 real (6 values, 0 units, 3 code lists, 7 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `bridge_parent_id` | bigint | admin, link | Foreign key to bridge.id. The parent bridge or bridge part. |
| `bridge_root_id` | bigint | admin, link | Foreign key to bridge.id. The root of the bridge hierarchy. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `year_of_construction` | date | real, value | Year of construction. |
| `year_of_demolition` | date | real, value | Year of demolition. |
| `is_movable` | numeric | real, value | 1 when the bridge can move. |
| `lod1_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 1. |
| `lod2_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 2. |
| `lod3_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 3. |
| `lod4_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 4. |
| `lod2_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 2. |
| `lod3_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 3. |
| `lod4_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 4. |
| `lod1_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 1. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `lod1_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 1. |
| `lod2_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 2. |
| `lod3_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 3. |
| `lod4_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 4. |

#### `bridge_constr_element`

Structural member of a bridge, such as a pylon or a girder.

33 columns: 11 administrative (1 key, 10 links, 0 identifiers) and 22 real (3 values, 0 units, 3 code lists, 16 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `bridge_id` | bigint | admin, link | Foreign key to bridge.id. |
| `lod1_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 1. |
| `lod2_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 2. |
| `lod3_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 3. |
| `lod4_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 4. |
| `lod1_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 1. |
| `lod2_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 2. |
| `lod3_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 3. |
| `lod4_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 4. |
| `lod1_other_geom` | geometry | real, geometry | Geometry at LOD 1 that is not a boundary representation. |
| `lod2_other_geom` | geometry | real, geometry | Geometry at LOD 2 that is not a boundary representation. |
| `lod3_other_geom` | geometry | real, geometry | Geometry at LOD 3 that is not a boundary representation. |
| `lod4_other_geom` | geometry | real, geometry | Geometry at LOD 4 that is not a boundary representation. |
| `lod1_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 1. |
| `lod2_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 2. |
| `lod3_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 3. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod1_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 1. |
| `lod2_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 2. |
| `lod3_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 3. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod1_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 1. |
| `lod2_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 2. |
| `lod3_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 3. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

#### `bridge_installation`

Installation on a bridge or inside a bridge room.

25 columns: 10 administrative (1 key, 9 links, 0 identifiers) and 15 real (3 values, 0 units, 3 code lists, 9 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `bridge_id` | bigint | admin, link | Foreign key to bridge.id. |
| `bridge_room_id` | bigint | admin, link | Foreign key to bridge_room.id. |
| `lod2_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 2. |
| `lod3_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 3. |
| `lod4_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 4. |
| `lod2_other_geom` | geometry | real, geometry | Geometry at LOD 2 that is not a boundary representation. |
| `lod3_other_geom` | geometry | real, geometry | Geometry at LOD 3 that is not a boundary representation. |
| `lod4_other_geom` | geometry | real, geometry | Geometry at LOD 4 that is not a boundary representation. |
| `lod2_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 2. |
| `lod3_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 3. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod2_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 2. |
| `lod3_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 3. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod2_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 2. |
| `lod3_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 3. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

#### `bridge_thematic_surface`

Semantic surface of a bridge. The type is objectclass_id and the shape is a foreign key, so the table has no value column.

9 columns: 9 administrative (1 key, 8 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `bridge_id` | bigint | admin, link | Foreign key to bridge.id. |
| `bridge_room_id` | bigint | admin, link | Foreign key to bridge_room.id. |
| `bridge_installation_id` | bigint | admin, link | Foreign key to bridge_installation.id. |
| `bridge_constr_element_id` | bigint | admin, link | Foreign key to bridge_constr_element.id. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |

#### `bridge_opening`

Opening in a bridge surface.

11 columns: 7 administrative (1 key, 6 links, 0 identifiers) and 4 real (0 values, 0 units, 0 code lists, 4 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `address_id` | bigint | admin, link | Foreign key to address.id. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `lod3_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 3. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod3_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 3. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod3_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 3. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

#### `bridge_open_to_them_srf`

Links a bridge opening to a bridge thematic surface.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `bridge_opening_id` | bigint | admin, link | Foreign key to bridge_opening.id. |
| `bridge_thematic_surface_id` | bigint | admin, link | Foreign key to bridge_thematic_surface.id. |

#### `bridge_room`

Interior room of a bridge.

11 columns: 5 administrative (1 key, 4 links, 0 identifiers) and 6 real (3 values, 0 units, 3 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `bridge_id` | bigint | admin, link | Foreign key to bridge.id. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `lod4_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 4. |

#### `bridge_furniture`

Furniture inside a bridge room.

14 columns: 5 administrative (1 key, 4 links, 0 identifiers) and 9 real (3 values, 0 units, 3 code lists, 3 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `bridge_room_id` | bigint | admin, link | Foreign key to bridge_room.id. |
| `lod4_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 4. |
| `lod4_other_geom` | geometry | real, geometry | Geometry at LOD 4 that is not a boundary representation. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

#### `address_to_bridge`

Links an address to a bridge.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `bridge_id` | bigint | admin, link | Foreign key to bridge.id. |
| `address_id` | bigint | admin, link | Foreign key to address.id. |

### CityFurniture

#### `city_furniture`

Street furniture and similar objects, such as a bench, lamp, or sign.

32 columns: 10 administrative (1 key, 9 links, 0 identifiers) and 22 real (3 values, 0 units, 3 code lists, 16 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `lod1_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 1. |
| `lod2_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 2. |
| `lod3_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 3. |
| `lod4_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 4. |
| `lod1_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 1. |
| `lod2_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 2. |
| `lod3_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 3. |
| `lod4_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 4. |
| `lod1_other_geom` | geometry | real, geometry | Geometry at LOD 1 that is not a boundary representation. |
| `lod2_other_geom` | geometry | real, geometry | Geometry at LOD 2 that is not a boundary representation. |
| `lod3_other_geom` | geometry | real, geometry | Geometry at LOD 3 that is not a boundary representation. |
| `lod4_other_geom` | geometry | real, geometry | Geometry at LOD 4 that is not a boundary representation. |
| `lod1_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 1. |
| `lod2_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 2. |
| `lod3_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 3. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod1_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 1. |
| `lod2_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 2. |
| `lod3_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 3. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod1_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 1. |
| `lod2_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 2. |
| `lod3_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 3. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

### CityObjectGroup

#### `cityobjectgroup`

Named group of city objects, with an optional geometry of the group itself.

11 columns: 4 administrative (1 key, 3 links, 0 identifiers) and 7 real (3 values, 0 units, 3 code lists, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation of the group. |
| `other_geom` | geometry | real, geometry | Geometry of the group that is not a boundary representation. |
| `parent_cityobject_id` | bigint | admin, link | Foreign key to cityobject.id. Parent group, when groups are nested. |

#### `group_to_cityobject`

Membership of a city object in a group, together with the member's role.

3 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 1 real (1 value, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `cityobject_id` | bigint | admin, link | Foreign key to cityobject.id. The feature this row belongs to. |
| `cityobjectgroup_id` | bigint | admin, link | Foreign key to cityobjectgroup.id. |
| `role` | varchar | real, value | Role of this city object inside the group. |

### Generics

#### `generic_cityobject`

City object that does not belong to another CityGML module.

38 columns: 12 administrative (1 key, 11 links, 0 identifiers) and 26 real (3 values, 0 units, 3 code lists, 20 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `lod0_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 0. |
| `lod1_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 1. |
| `lod2_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 2. |
| `lod3_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 3. |
| `lod4_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 4. |
| `lod0_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 0. |
| `lod1_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 1. |
| `lod2_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 2. |
| `lod3_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 3. |
| `lod4_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 4. |
| `lod0_other_geom` | geometry | real, geometry | Geometry at LOD 0 that is not a boundary representation. |
| `lod1_other_geom` | geometry | real, geometry | Geometry at LOD 1 that is not a boundary representation. |
| `lod2_other_geom` | geometry | real, geometry | Geometry at LOD 2 that is not a boundary representation. |
| `lod3_other_geom` | geometry | real, geometry | Geometry at LOD 3 that is not a boundary representation. |
| `lod4_other_geom` | geometry | real, geometry | Geometry at LOD 4 that is not a boundary representation. |
| `lod0_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 0. |
| `lod1_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 1. |
| `lod2_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 2. |
| `lod3_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 3. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod0_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 0. |
| `lod1_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 1. |
| `lod2_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 2. |
| `lod3_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 3. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod0_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 0. |
| `lod1_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 1. |
| `lod2_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 2. |
| `lod3_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 3. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

### LandUse

#### `land_use`

Land-use area.

13 columns: 7 administrative (1 key, 6 links, 0 identifiers) and 6 real (3 values, 0 units, 3 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `lod0_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 0. |
| `lod1_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 1. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |

### Relief

#### `relief_feature`

Relief feature that groups relief components.

3 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 1 real (1 value, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `lod` | numeric | real, value | Level of detail of this relief, from 0 to 4. |

#### `relief_component`

Shared row of every relief component: level of detail and footprint.

4 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 2 real (1 value, 0 units, 0 code lists, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `lod` | numeric | real, value | Level of detail of this relief, from 0 to 4. |
| `extent` | geometry | real, geometry | Footprint of the relief component. |

#### `relief_feat_to_rel_comp`

Links a relief feature to its components.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `relief_component_id` | bigint | admin, link | Foreign key to relief_component.id. |
| `relief_feature_id` | bigint | admin, link | Foreign key to relief_feature.id. |

#### `tin_relief`

Relief component stored as a triangulated irregular network.

8 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 5 real (1 value, 1 unit, 0 code lists, 3 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with relief_component.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `max_length` | float | real, value | Longest edge allowed in the TIN. |
| `max_length_unit` | varchar | real, unit | Unit of measure of `max_length`. |
| `stop_lines` | geometry | real, geometry | Lines the TIN must not cross. |
| `break_lines` | geometry | real, geometry | Lines where the relief surface is allowed to break. |
| `control_points` | geometry | real, geometry | Points the TIN is required to keep. |
| `surface_geometry_id` | bigint | admin, link | Foreign key to surface_geometry.id. |

#### `breakline_relief`

Relief component made of break lines and ridge or valley lines.

4 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 2 real (0 values, 0 units, 0 code lists, 2 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with relief_component.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `ridge_or_valley_lines` | geometry | real, geometry | Ridge and valley lines of a breakline relief. |
| `break_lines` | geometry | real, geometry | Lines where the relief surface is allowed to break. |

#### `masspoint_relief`

Relief component made of height points.

3 columns: 2 administrative (1 key, 1 link, 0 identifiers) and 1 real (0 values, 0 units, 0 code lists, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with relief_component.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `relief_points` | geometry | real, geometry | Height points of a mass-point relief. |

#### `raster_relief`

Relief component given as a raster.

4 columns: 3 administrative (1 key, 2 links, 0 identifiers) and 1 real (1 value, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with relief_component.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `raster_uri` | varchar | real, value | URI of the raster file. |
| `coverage_id` | bigint | admin, link | Foreign key to grid_coverage.id. The raster this relief uses. |

#### `grid_coverage`

Raster grid referenced by a raster relief.

2 columns: 1 administrative (1 key, 0 links, 0 identifiers) and 1 real (0 values, 0 units, 0 code lists, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key of the raster coverage. |
| `rasterproperty` | raster | real, geometry | The raster grid itself. |

### Transportation

#### `transportation_complex`

Road, railway, track, or square.

13 columns: 6 administrative (1 key, 5 links, 0 identifiers) and 7 real (3 values, 0 units, 3 code lists, 1 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `lod0_network` | geometry | real, geometry | Network line geometry at LOD 0. |
| `lod1_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 1. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |

#### `traffic_area`

Traffic surface that belongs to a transportation complex.

14 columns: 6 administrative (1 key, 5 links, 0 identifiers) and 8 real (4 values, 0 units, 4 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `surface_material` | varchar | real, value | Material of the traffic surface. |
| `surface_material_codespace` | varchar | real, codespace | Code-list namespace of `surface_material`. Names the vocabulary of that value. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `transportation_complex_id` | bigint | admin, link | Foreign key to transportation_complex.id. |

### Tunnel

#### `tunnel`

Tunnel and TunnelPart: class, function, usage, years, and LOD geometry.

27 columns: 12 administrative (1 key, 11 links, 0 identifiers) and 15 real (5 values, 0 units, 3 code lists, 7 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `tunnel_parent_id` | bigint | admin, link | Foreign key to tunnel.id. The parent tunnel or tunnel part. |
| `tunnel_root_id` | bigint | admin, link | Foreign key to tunnel.id. The root of the tunnel hierarchy. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `year_of_construction` | date | real, value | Year of construction. |
| `year_of_demolition` | date | real, value | Year of demolition. |
| `lod1_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 1. |
| `lod2_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 2. |
| `lod3_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 3. |
| `lod4_terrain_intersection` | geometry | real, geometry | Terrain-intersection curve at LOD 4. |
| `lod2_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 2. |
| `lod3_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 3. |
| `lod4_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 4. |
| `lod1_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 1. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `lod1_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 1. |
| `lod2_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 2. |
| `lod3_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 3. |
| `lod4_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 4. |

#### `tunnel_installation`

Installation on a tunnel or inside a hollow space.

25 columns: 10 administrative (1 key, 9 links, 0 identifiers) and 15 real (3 values, 0 units, 3 code lists, 9 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `tunnel_id` | bigint | admin, link | Foreign key to tunnel.id. |
| `tunnel_hollow_space_id` | bigint | admin, link | Foreign key to tunnel_hollow_space.id. |
| `lod2_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 2. |
| `lod3_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 3. |
| `lod4_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 4. |
| `lod2_other_geom` | geometry | real, geometry | Geometry at LOD 2 that is not a boundary representation. |
| `lod3_other_geom` | geometry | real, geometry | Geometry at LOD 3 that is not a boundary representation. |
| `lod4_other_geom` | geometry | real, geometry | Geometry at LOD 4 that is not a boundary representation. |
| `lod2_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 2. |
| `lod3_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 3. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod2_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 2. |
| `lod3_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 3. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod2_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 2. |
| `lod3_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 3. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

#### `tunnel_thematic_surface`

Semantic surface of a tunnel. The type is objectclass_id and the shape is a foreign key, so the table has no value column.

8 columns: 8 administrative (1 key, 7 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `tunnel_id` | bigint | admin, link | Foreign key to tunnel.id. |
| `tunnel_hollow_space_id` | bigint | admin, link | Foreign key to tunnel_hollow_space.id. |
| `tunnel_installation_id` | bigint | admin, link | Foreign key to tunnel_installation.id. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |

#### `tunnel_opening`

Opening in a tunnel surface.

10 columns: 6 administrative (1 key, 5 links, 0 identifiers) and 4 real (0 values, 0 units, 0 code lists, 4 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `lod3_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 3. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod3_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 3. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod3_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 3. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

#### `tunnel_open_to_them_srf`

Links a tunnel opening to a tunnel thematic surface.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `tunnel_opening_id` | bigint | admin, link | Foreign key to tunnel_opening.id. |
| `tunnel_thematic_surface_id` | bigint | admin, link | Foreign key to tunnel_thematic_surface.id. |

#### `tunnel_hollow_space`

Interior hollow space of a tunnel.

11 columns: 5 administrative (1 key, 4 links, 0 identifiers) and 6 real (3 values, 0 units, 3 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `tunnel_id` | bigint | admin, link | Foreign key to tunnel.id. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `lod4_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 4. |

#### `tunnel_furniture`

Furniture inside a tunnel hollow space.

14 columns: 5 administrative (1 key, 4 links, 0 identifiers) and 9 real (3 values, 0 units, 3 code lists, 3 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `tunnel_hollow_space_id` | bigint | admin, link | Foreign key to tunnel_hollow_space.id. |
| `lod4_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 4. |
| `lod4_other_geom` | geometry | real, geometry | Geometry at LOD 4 that is not a boundary representation. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

### Vegetation

#### `plant_cover`

Area of vegetation, such as a wood, a row, or a bed.

18 columns: 10 administrative (1 key, 9 links, 0 identifiers) and 8 real (4 values, 1 unit, 3 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `average_height` | float | real, value | Average height of the vegetation cover. |
| `average_height_unit` | varchar | real, unit | Unit of measure of `average_height`. |
| `lod1_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 1. |
| `lod2_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 2. |
| `lod3_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 3. |
| `lod4_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 4. |
| `lod1_multi_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-solid at LOD 1. |
| `lod2_multi_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-solid at LOD 2. |
| `lod3_multi_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-solid at LOD 3. |
| `lod4_multi_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-solid at LOD 4. |

#### `solitary_vegetat_object`

A single plant, with species, height, trunk, and crown.

36 columns: 10 administrative (1 key, 9 links, 0 identifiers) and 26 real (7 values, 3 units, 4 code lists, 12 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `species` | varchar | real, value | Species of the plant. |
| `species_codespace` | varchar | real, codespace | Code-list namespace of `species`. Names the vocabulary of that value. |
| `height` | float | real, value | Height of the plant. |
| `height_unit` | varchar | real, unit | Unit of measure of `height`. |
| `trunk_diameter` | float | real, value | Diameter of the trunk. |
| `trunk_diameter_unit` | varchar | real, unit | Unit of measure of `trunk_diameter`. |
| `crown_diameter` | float | real, value | Diameter of the plant crown. |
| `crown_diameter_unit` | varchar | real, unit | Unit of measure of `crown_diameter`. |
| `lod1_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 1. |
| `lod2_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 2. |
| `lod3_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 3. |
| `lod4_brep_id` | bigint | admin, link | Foreign key to surface_geometry.id. Boundary representation at LOD 4. |
| `lod1_other_geom` | geometry | real, geometry | Geometry at LOD 1 that is not a boundary representation. |
| `lod2_other_geom` | geometry | real, geometry | Geometry at LOD 2 that is not a boundary representation. |
| `lod3_other_geom` | geometry | real, geometry | Geometry at LOD 3 that is not a boundary representation. |
| `lod4_other_geom` | geometry | real, geometry | Geometry at LOD 4 that is not a boundary representation. |
| `lod1_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 1. |
| `lod2_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 2. |
| `lod3_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 3. |
| `lod4_implicit_rep_id` | bigint | admin, link | Foreign key to implicit_geometry.id. Prototype placed at LOD 4. |
| `lod1_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 1. |
| `lod2_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 2. |
| `lod3_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 3. |
| `lod4_implicit_ref_point` | geometry | real, geometry | Anchor point of the implicit prototype at LOD 4. |
| `lod1_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 1. |
| `lod2_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 2. |
| `lod3_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 3. |
| `lod4_implicit_transformation` | varchar | real, geometry | Placement matrix of the implicit prototype at LOD 4. |

### WaterBody

#### `waterbody`

River, lake, or other water body.

16 columns: 8 administrative (1 key, 7 links, 0 identifiers) and 8 real (3 values, 0 units, 3 code lists, 2 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `class` | varchar | real, value | Class of the feature, taken from that module's class code list. |
| `class_codespace` | varchar | real, codespace | Code-list namespace of `class`. Names the vocabulary of that value. |
| `function` | varchar | real, value | Function the feature was designed for, from a code list. |
| `function_codespace` | varchar | real, codespace | Code-list namespace of `function`. Names the vocabulary of that value. |
| `usage` | varchar | real, value | How the feature is used, from a code list. |
| `usage_codespace` | varchar | real, codespace | Code-list namespace of `usage`. Names the vocabulary of that value. |
| `lod0_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 0. |
| `lod1_multi_curve` | geometry | real, geometry | Multi-curve geometry at LOD 1. |
| `lod0_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 0. |
| `lod1_multi_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Multi-surface at LOD 1. |
| `lod1_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 1. |
| `lod2_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 2. |
| `lod3_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 3. |
| `lod4_solid_id` | bigint | admin, link | Foreign key to surface_geometry.id. Solid at LOD 4. |

#### `waterboundary_surface`

Semantic surface of a water body, such as the water surface or the water ground.

7 columns: 5 administrative (1 key, 4 links, 0 identifiers) and 2 real (1 value, 0 units, 1 code list, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `id` | bigint | admin, key | Primary key, shared with cityobject.id. |
| `objectclass_id` | integer | admin, link | Foreign key to objectclass.id. Names the concrete class stored in this row. |
| `water_level` | varchar | real, value | Water level this boundary surface stands for. |
| `water_level_codespace` | varchar | real, codespace | Code-list namespace of `water_level`. Names the vocabulary of that value. |
| `lod2_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Surface at LOD 2. |
| `lod3_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Surface at LOD 3. |
| `lod4_surface_id` | bigint | admin, link | Foreign key to surface_geometry.id. Surface at LOD 4. |

#### `waterbod_to_waterbnd_srf`

Links a water body to its boundary surfaces.

2 columns: 2 administrative (0 keys, 2 links, 0 identifiers) and 0 real (0 values, 0 units, 0 code lists, 0 geometry).

| Column | Type | Kind | What it stores |
| --- | --- | --- | --- |
| `waterboundary_surface_id` | bigint | admin, link | Foreign key to waterboundary_surface.id. |
| `waterbody_id` | bigint | admin, link | Foreign key to waterbody.id. |

