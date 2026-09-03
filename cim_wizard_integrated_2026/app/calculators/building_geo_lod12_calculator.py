"""
Building Geo LoD 1.2 Calculator - Generate 3DCityDB-compatible building surfaces

Methods
-------
by_footprint_height      – basic LOD 1.2 (walls + roof + ground, single zone)
by_footprint_height_floors – per-storey walls + intermediate floor surfaces,
                             one thermal zone per storey
by_mixed_use             – basement + commercial ground + residential floors
                             with per-apartment thermal zones
"""
from typing import Optional, Dict, Any, List
import math
import json

from app.calculators.base_calculator import BaseCalculator
from app.core.geo_metric import (
    polygon_area_3d_m2,
    polygon_area_m2,
    ring_area_m2,
    ring_length_m,
)

BASEMENT_HEIGHT = 3.0

# Surface tilt in degrees from horizontal, per CityGML surface class.
SURFACE_TILT = {
    "WallSurface": 90.0,
    "RoofSurface": 0.0,
    "FloorSurface": 0.0,
    "GroundSurface": 0.0,
    "CeilingSurface": 0.0,
}


def extrude_zone_shell(
    exterior_ring: List[List[float]], z_min: float, z_max: float
) -> Optional[Dict[str, Any]]:
    """Closed shell of one thermal zone as a GeoJSON MultiPolygon of faces.

    Mirrors ``extrude_zone_solid`` in ``logic/stand_alone_CIM.ipynb``:
    bottom slab + top slab + one quad per footprint edge.
    """
    if not exterior_ring or len(exterior_ring) < 4:
        return None

    bottom = [[p[0], p[1], z_min] for p in exterior_ring]
    top = [[p[0], p[1], z_max] for p in exterior_ring]

    faces: List[List[List[List[float]]]] = [[bottom], [top]]
    for i in range(len(exterior_ring) - 1):
        p1, p2 = exterior_ring[i], exterior_ring[i + 1]
        faces.append([[
            [p1[0], p1[1], z_min],
            [p2[0], p2[1], z_min],
            [p2[0], p2[1], z_max],
            [p1[0], p1[1], z_max],
            [p1[0], p1[1], z_min],
        ]])

    return {"type": "MultiPolygon", "coordinates": faces}


class BuildingGeoLod12Calculator(BaseCalculator):
    """Calculate LoD 1.2 building surfaces from footprint and height for 3DCityDB compatibility"""
    
    def __init__(self, pipeline_executor):
        super().__init__(pipeline_executor)
    
    def by_footprint_height(self) -> Optional[Dict[str, Any]]:
        """Generate LoD 1.2 semantic surfaces from footprint geometry and height."""
        try:
            building_geo = self.pipeline.get_feature_safely('building_geo', calculator_name=self.calculator_name)
            building_heights = self.pipeline.get_feature_safely('building_height', calculator_name=self.calculator_name)

            if not building_geo:
                self.pipeline.log_error(self.calculator_name, "No building_geo data available")
                return None

            buildings = building_geo.get('buildings', [])
            if not buildings:
                self.pipeline.log_error(self.calculator_name, "No buildings found in building_geo")
                return None

            self.pipeline.log_info(
                self.calculator_name,
                f"Generating LoD 1.2 surfaces for {len(buildings)} buildings"
            )

            building_lod12_data = []
            skipped = 0

            for i, building in enumerate(buildings):
                building_id = building.get('building_id')
                geometry = building.get('geometry', {})

                height = (
                    building_heights[i]
                    if building_heights and i < len(building_heights)
                    else 12.0
                )

                surfaces = self._generate_lod12_surfaces(geometry, height)
                if surfaces is None:
                    skipped += 1
                    continue

                wall_count = len(surfaces.get('wall_surfaces', []))
                total_surfaces = wall_count + (1 if surfaces.get('roof_surface') else 0) \
                                            + (1 if surfaces.get('ground_surface') else 0)

                lod12_data = {
                    'building_id': building_id,
                    'surfaces': surfaces,
                    'metadata': {
                        'total_surfaces': total_surfaces,
                        'wall_count': wall_count,
                        'building_height': height,
                        'surface_types': ['WallSurface', 'RoofSurface', 'GroundSurface'],
                        'coordinate_system': 'EPSG:4326',
                        'lod_specification': '1.2',
                        'citydb_compatible': True,
                        'generated_from': 'footprint_height',
                    },
                }
                building_lod12_data.append(lod12_data)

            result = {
                'project_id': building_geo.get('project_id'),
                'scenario_id': building_geo.get('scenario_id'),
                'building_lod12_data': building_lod12_data,
                'total_buildings': len(building_lod12_data),
                'skipped_buildings': skipped,
                'lod': 1.2,
                'generation_method': 'footprint_height',
            }

            self.data_manager.set_feature('building_geo_lod12', result)

            self.pipeline.log_calculation_success(
                self.calculator_name,
                'by_footprint_height',
                result,
                f"Generated LoD 1.2 surfaces for {len(building_lod12_data)} buildings "
                f"({skipped} skipped due to invalid geometry)"
            )

            return result

        except Exception as e:
            self.pipeline.log_calculation_failure(self.calculator_name, 'by_footprint_height', str(e))
            return None

    # ------------------------------------------------------------------
    # Pipeline method: per-storey LOD 1.2 with floor surfaces
    # ------------------------------------------------------------------

    def by_footprint_height_floors(self) -> Optional[Dict[str, Any]]:
        """Generate LOD 1.2 surfaces decomposed by storey, one thermal zone per floor."""
        try:
            building_geo = self.get_feature('building_geo')
            building_heights = self.get_feature('building_height')
            n_floors_result = self.get_feature('building_n_floors')

            if not building_geo:
                self.log_error("No building_geo data available")
                return None

            buildings = building_geo.get('buildings', [])
            n_floors_list = (
                n_floors_result.get('building_floors', [])
                if isinstance(n_floors_result, dict) else []
            )

            building_lod12_data: List[dict] = []
            skipped = 0

            for i, building in enumerate(buildings):
                height = (
                    building_heights[i]
                    if building_heights and i < len(building_heights)
                    else 12.0
                )
                n_floors = (
                    int(n_floors_list[i])
                    if n_floors_list and i < len(n_floors_list) and n_floors_list[i]
                    else max(1, round(height / 3.0))
                )
                geometry = building.get('geometry', {})
                lod12 = self.generate_lod12_with_floors(geometry, height, n_floors)
                if lod12 is None:
                    skipped += 1
                    continue
                lod12['building_id'] = building.get('building_id')
                building_lod12_data.append(lod12)

            result = {
                'project_id': building_geo.get('project_id'),
                'scenario_id': building_geo.get('scenario_id'),
                'building_lod12_data': building_lod12_data,
                'total_buildings': len(building_lod12_data),
                'skipped_buildings': skipped,
                'lod': 1.2,
                'generation_method': 'footprint_height_floors',
            }
            self.data_manager.set_feature('building_geo_lod12', result)
            self.log_success(
                'by_footprint_height_floors', result,
                f"Generated per-storey LoD 1.2 for {len(building_lod12_data)} buildings",
            )
            return result
        except Exception as e:
            self.log_failure('by_footprint_height_floors', str(e))
            return None

    # ------------------------------------------------------------------
    # Pipeline method: mixed-use (basement + commercial + residential)
    # ------------------------------------------------------------------

    def by_mixed_use(self) -> Optional[Dict[str, Any]]:
        """Generate LOD 1.2 with mixed-use decomposition.

        Layout per building:
            -  basement (non-residential, BASEMENT_HEIGHT below ground)
            -  commercial ground floor
            -  N residential floors with apartments distributed by n_families
        """
        try:
            building_geo = self.get_feature('building_geo')
            building_heights = self.get_feature('building_height')
            n_floors_result = self.get_feature('building_n_floors')
            n_families_result = self.get_feature('building_n_families')

            if not building_geo:
                self.log_error("No building_geo data available")
                return None

            buildings = building_geo.get('buildings', [])
            n_floors_list = (
                n_floors_result.get('building_floors', [])
                if isinstance(n_floors_result, dict) else []
            )
            n_families_list = (
                n_families_result.get('building_families', [])
                if isinstance(n_families_result, dict) else []
            )

            building_lod12_data: List[dict] = []
            skipped = 0

            for i, building in enumerate(buildings):
                height = (
                    building_heights[i]
                    if building_heights and i < len(building_heights)
                    else 12.0
                )
                n_floors = (
                    int(n_floors_list[i])
                    if n_floors_list and i < len(n_floors_list) and n_floors_list[i]
                    else max(1, round(height / 3.0))
                )
                n_families = (
                    int(n_families_list[i])
                    if n_families_list and i < len(n_families_list) and n_families_list[i]
                    else max(1, n_floors - 1) * 2
                )
                geometry = building.get('geometry', {})
                lod12 = self.generate_lod12_mixed_use(
                    geometry, height, n_floors, n_families,
                )
                if lod12 is None:
                    skipped += 1
                    continue
                lod12['building_id'] = building.get('building_id')
                building_lod12_data.append(lod12)

            result = {
                'project_id': building_geo.get('project_id'),
                'scenario_id': building_geo.get('scenario_id'),
                'building_lod12_data': building_lod12_data,
                'total_buildings': len(building_lod12_data),
                'skipped_buildings': skipped,
                'lod': 1.2,
                'generation_method': 'mixed_use',
            }
            self.data_manager.set_feature('building_geo_lod12', result)
            self.log_success(
                'by_mixed_use', result,
                f"Generated mixed-use LoD 1.2 for {len(building_lod12_data)} buildings",
            )
            return result
        except Exception as e:
            self.log_failure('by_mixed_use', str(e))
            return None

    # ==================================================================
    # Direct-call methods (called by CityDB mapper or pipeline methods)
    # ==================================================================

    def generate_lod12_with_floors(
        self, geometry: dict, height: float, n_floors: int,
    ) -> Optional[Dict[str, Any]]:
        """Generate LOD 1.2 surfaces with per-storey walls and floor slabs.

        Returns a dict with ``surfaces``, ``storeys``, ``thermal_zones``,
        and ``metadata``, or ``None`` on invalid input.
        """
        ring = self._validated_ring(geometry)
        if ring is None:
            return None

        n_floors = max(1, n_floors)
        storey_h = height / n_floors
        footprint_area = self._calculate_polygon_area(geometry)

        all_walls: List[dict] = []
        floor_surfaces: List[dict] = []
        storeys: List[dict] = []
        thermal_zones: List[dict] = []

        for f in range(n_floors):
            z_min = f * storey_h
            z_max = (f + 1) * storey_h
            label = f"F{f}"
            zone_id = f"tz-{label}"

            walls = self._generate_wall_surfaces_for_range(
                ring, z_min, z_max, label, zone_id=zone_id,
            )
            all_walls.extend(walls)

            if f < n_floors - 1:
                floor_surfaces.append(
                    self._generate_horizontal_surface(
                        ring, z_max, f"floor_{f + 1}", "FloorSurface",
                        zone_id=zone_id,
                    )
                )

            storeys.append({
                "storey_index": f,
                "label": label,
                "usage": "residential",
                "z_min": round(z_min, 3),
                "z_max": round(z_max, 3),
                "storey_height": round(storey_h, 3),
            })
            thermal_zones.append({
                "zone_id": zone_id,
                "storey_index": f,
                "usage": "residential",
                "volume_m3": round(footprint_area * storey_h, 2),
                "floor_area_m2": round(footprint_area, 2),
                "z_min": round(z_min, 3),
                "z_max": round(z_max, 3),
                "is_heated": True,
                "is_cooled": False,
            })

        surfaces = {
            "wall_surfaces": all_walls,
            "roof_surface": self._generate_roof_surface(ring, height),
            "ground_surface": self._generate_ground_surface(ring),
            "floor_surfaces": floor_surfaces,
        }

        wall_count = len(all_walls)
        total_surfaces = (
            wall_count
            + len(floor_surfaces)
            + (1 if surfaces["roof_surface"] else 0)
            + (1 if surfaces["ground_surface"] else 0)
        )

        return {
            "surfaces": surfaces,
            "storeys": storeys,
            "thermal_zones": thermal_zones,
            "metadata": {
                "total_surfaces": total_surfaces,
                "wall_count": wall_count,
                "floor_count": len(floor_surfaces),
                "building_height": height,
                "n_floors": n_floors,
                "storey_height": round(storey_h, 3),
                "footprint_area_m2": round(footprint_area, 2),
                "surface_types": [
                    "WallSurface", "RoofSurface", "GroundSurface", "FloorSurface",
                ],
                "coordinate_system": "EPSG:4326",
                "lod_specification": "1.2",
                "generation_method": "footprint_height_floors",
            },
        }

    def generate_lod12_mixed_use(
        self,
        geometry: dict,
        height: float,
        n_floors: int,
        n_families: int,
        basement_height: float = BASEMENT_HEIGHT,
    ) -> Optional[Dict[str, Any]]:
        """Generate LOD 1.2 for a mixed-use building.

        Layout (bottom-to-top)::

            basement        z ∈ [-basement_height, 0]       1 TZ  (storage)
            ground floor    z ∈ [0, storey_h]               1 TZ  (commercial)
            floors 1..R     z ∈ [storey_h, height]          per-apartment TZs

        ``n_families`` apartments are distributed across R = n_floors - 1
        residential floors.
        """
        ring = self._validated_ring(geometry)
        if ring is None:
            return None

        n_floors = max(2, n_floors)
        n_families = max(1, n_families)
        storey_h = height / n_floors
        footprint_area = self._calculate_polygon_area(geometry)

        residential_floors = n_floors - 1
        base_apt = n_families // residential_floors
        extra = n_families % residential_floors

        all_walls: List[dict] = []
        floor_surfaces: List[dict] = []
        storeys: List[dict] = []
        thermal_zones: List[dict] = []

        # ── basement ─────────────────────────────────────────────
        bz_min = -basement_height
        bz_max = 0.0
        all_walls.extend(
            self._generate_wall_surfaces_for_range(
                ring, bz_min, bz_max, "B", zone_id="tz-basement",
            )
        )
        floor_surfaces.append(
            self._generate_horizontal_surface(
                ring, bz_min, "basement_floor", "FloorSurface",
                zone_id="tz-basement",
            )
        )
        storeys.append({
            "storey_index": -1,
            "label": "basement",
            "usage": "non_residential_storage",
            "z_min": round(bz_min, 3),
            "z_max": round(bz_max, 3),
            "storey_height": round(basement_height, 3),
        })
        thermal_zones.append({
            "zone_id": "tz-basement",
            "storey_index": -1,
            "usage": "non_residential_storage",
            "volume_m3": round(footprint_area * basement_height, 2),
            "floor_area_m2": round(footprint_area, 2),
            "z_min": round(bz_min, 3),
            "z_max": round(bz_max, 3),
            "is_heated": False,
            "is_cooled": False,
        })

        # ── ground floor (commercial) ────────────────────────────
        gz_min = 0.0
        gz_max = storey_h
        all_walls.extend(
            self._generate_wall_surfaces_for_range(
                ring, gz_min, gz_max, "G", zone_id="tz-commercial",
            )
        )
        floor_surfaces.append(
            self._generate_horizontal_surface(
                ring, gz_max, "floor_1", "FloorSurface",
                zone_id="tz-commercial",
            )
        )
        storeys.append({
            "storey_index": 0,
            "label": "ground_floor",
            "usage": "commercial",
            "z_min": round(gz_min, 3),
            "z_max": round(gz_max, 3),
            "storey_height": round(storey_h, 3),
        })
        thermal_zones.append({
            "zone_id": "tz-commercial",
            "storey_index": 0,
            "usage": "commercial",
            "volume_m3": round(footprint_area * storey_h, 2),
            "floor_area_m2": round(footprint_area, 2),
            "z_min": round(gz_min, 3),
            "z_max": round(gz_max, 3),
            "is_heated": True,
            "is_cooled": True,
        })

        # ── residential floors ───────────────────────────────────
        for r in range(residential_floors):
            f_idx = r + 1
            z_min = f_idx * storey_h
            z_max = (f_idx + 1) * storey_h
            label = f"F{f_idx}"
            # Storey walls and slabs are shared by every apartment on the floor;
            # attribute them to the first zone, as the stand-alone notebook does.
            storey_zone_id = f"tz-{label}-A1"

            all_walls.extend(
                self._generate_wall_surfaces_for_range(
                    ring, z_min, z_max, label, zone_id=storey_zone_id,
                )
            )
            if f_idx < n_floors - 1:
                floor_surfaces.append(
                    self._generate_horizontal_surface(
                        ring, z_max, f"floor_{f_idx + 1}", "FloorSurface",
                        zone_id=storey_zone_id,
                    )
                )

            apts_this_floor = base_apt + (1 if r < extra else 0)
            storey_volume = footprint_area * storey_h
            storey_area = footprint_area

            storeys.append({
                "storey_index": f_idx,
                "label": label,
                "usage": "residential",
                "z_min": round(z_min, 3),
                "z_max": round(z_max, 3),
                "storey_height": round(storey_h, 3),
                "apartments": apts_this_floor,
            })

            for a in range(apts_this_floor):
                thermal_zones.append({
                    "zone_id": f"tz-{label}-A{a + 1}",
                    "storey_index": f_idx,
                    "apartment_index": a + 1,
                    "usage": "residential",
                    "volume_m3": round(storey_volume / apts_this_floor, 2),
                    "floor_area_m2": round(storey_area / apts_this_floor, 2),
                    "z_min": round(z_min, 3),
                    "z_max": round(z_max, 3),
                    "is_heated": True,
                    "is_cooled": False,
                })

        surfaces = {
            "wall_surfaces": all_walls,
            "roof_surface": self._generate_roof_surface(ring, height),
            "ground_surface": self._generate_ground_surface(ring),
            "floor_surfaces": floor_surfaces,
        }

        wall_count = len(all_walls)
        total_surfaces = (
            wall_count
            + len(floor_surfaces)
            + (1 if surfaces["roof_surface"] else 0)
            + (1 if surfaces["ground_surface"] else 0)
        )

        return {
            "surfaces": surfaces,
            "storeys": storeys,
            "thermal_zones": thermal_zones,
            "metadata": {
                "total_surfaces": total_surfaces,
                "wall_count": wall_count,
                "floor_count": len(floor_surfaces),
                "building_height": height,
                "basement_height": basement_height,
                "n_floors": n_floors,
                "n_families": n_families,
                "residential_floors": residential_floors,
                "storey_height": round(storey_h, 3),
                "footprint_area_m2": round(footprint_area, 2),
                "total_thermal_zones": len(thermal_zones),
                "surface_types": [
                    "WallSurface", "RoofSurface", "GroundSurface", "FloorSurface",
                ],
                "coordinate_system": "EPSG:4326",
                "lod_specification": "1.2",
                "generation_method": "mixed_use",
            },
        }

    # ==================================================================
    # Geometry helpers (shared by all methods)
    # ==================================================================

    def _validated_ring(self, geometry: dict) -> Optional[List[List[float]]]:
        """Extract and validate the exterior ring from a Polygon geometry."""
        if geometry.get('type') != 'Polygon':
            return None
        coordinates = geometry.get('coordinates', [])
        if not coordinates:
            return None
        ring = list(coordinates[0])
        if len(ring) < 4:
            return None
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        return ring

    def _generate_wall_surfaces_for_range(
        self,
        exterior_ring: List[List[float]],
        z_min: float,
        z_max: float,
        storey_label: str,
        zone_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generate wall surfaces for a single storey (z_min → z_max)."""
        walls: List[Dict[str, Any]] = []
        wall_height = z_max - z_min
        for i in range(len(exterior_ring) - 1):
            p1 = exterior_ring[i]
            p2 = exterior_ring[i + 1]
            wall_coordinates = [
                [p1[0], p1[1], z_min],
                [p2[0], p2[1], z_min],
                [p2[0], p2[1], z_max],
                [p1[0], p1[1], z_max],
                [p1[0], p1[1], z_min],
            ]
            wall_length = ring_length_m(p1, p2)
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            azimuth = math.degrees(math.atan2(dx, dy))
            if azimuth < 0:
                azimuth += 360

            walls.append({
                'surface_id': f"wall_{storey_label}_{i + 1}",
                'surface_type': 'WallSurface',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [wall_coordinates],
                },
                'properties': {
                    'wall_index': i + 1,
                    'storey_label': storey_label,
                    'zone_id': zone_id,
                    'area_m2': wall_length * wall_height,
                    'height_m': wall_height,
                    'length_m': wall_length,
                    'z_min': z_min,
                    'z_max': z_max,
                    'azimuth_degrees': azimuth,
                    'tilt_degrees': SURFACE_TILT['WallSurface'],
                    'orientation': self._get_cardinal_direction(azimuth),
                    'lod': 1.2,
                },
            })
        return walls

    def _generate_horizontal_surface(
        self,
        exterior_ring: List[List[float]],
        z: float,
        surface_id: str,
        surface_type: str = "FloorSurface",
        zone_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a horizontal slab (floor or ceiling) at height *z*."""
        coords = [[p[0], p[1], z] for p in exterior_ring]
        area = self._calculate_polygon_area_3d(coords)
        return {
            'surface_id': surface_id,
            'surface_type': surface_type,
            'zone_id': zone_id,
            'geometry': {
                'type': 'Polygon',
                'coordinates': [coords],
            },
            'properties': {
                'area_m2': area,
                'height_m': z,
                'tilt_degrees': SURFACE_TILT.get(surface_type, 0.0),
                'lod': 1.2,
            },
        }

    def _get_building_geometry_from_database(self, building_id: str, lod: int) -> Optional[Dict[str, Any]]:
        """Get building geometry from database"""
        try:
            from cim_wizard.models import Building
            from django.contrib.gis.geos import GEOSGeometry
            import json
            
            try:
                building = Building.objects.get(building_id=building_id, lod=lod)
                
                # Convert GEOSGeometry to GeoJSON
                geom_geojson = json.loads(building.building_geometry.geojson)
                
                self.pipeline.log_info(
                    self.calculator_name, 
                    f"Retrieved building geometry from database for building {building_id}"
                )
                return geom_geojson
                
            except Building.DoesNotExist:
                self.pipeline.log_error(
                    self.calculator_name, 
                    f"Building with building_id={building_id} and lod={lod} not found in database"
                )
                return None
                
        except Exception as e:
            self.pipeline.log_error(
                self.calculator_name, 
                f"Failed to get building geometry from database: {str(e)}"
            )
            return None
    
    def _get_building_height_from_database(self, building_id: str, project_id: str, scenario_id: str, lod: int) -> Optional[float]:
        """Get building height from database"""
        try:
            from cim_wizard.models import BuildingProperties
            
            try:
                building_props = BuildingProperties.objects.get(
                    building_id=building_id,
                    project_id=project_id,
                    scenario_id=scenario_id,
                    lod=lod
                )
                
                if building_props.height is None or building_props.height <= 0:
                    self.pipeline.log_error(
                        self.calculator_name, 
                        f"Building {building_id} has invalid height: {building_props.height}"
                    )
                    return None
                
                self.pipeline.log_info(
                    self.calculator_name, 
                    f"Retrieved building height {building_props.height}m from database for building {building_id}"
                )
                return building_props.height
                
            except BuildingProperties.DoesNotExist:
                self.pipeline.log_error(
                    self.calculator_name, 
                    f"BuildingProperties for building_id={building_id}, project_id={project_id}, scenario_id={scenario_id}, lod={lod} not found in database"
                )
                return None
                
        except Exception as e:
            self.pipeline.log_error(
                self.calculator_name, 
                f"Failed to get building height from database: {str(e)}"
            )
            return None
    
    def _extract_footprint_from_context(self, building_geo: Dict[str, Any], building_id: str) -> Optional[Dict[str, Any]]:
        """Extract building footprint geometry from building_geo context"""
        try:
            buildings = building_geo.get('buildings', [])
            
            for building in buildings:
                if building.get('building_id') == building_id:
                    footprint_geometry = building.get('geometry')
                    if footprint_geometry:
                        self.pipeline.log_info(
                            self.calculator_name, 
                            f"Retrieved building footprint from context for building {building_id}"
                        )
                        return footprint_geometry
            
            self.pipeline.log_error(
                self.calculator_name, 
                f"Building footprint not found in context for building_id: {building_id}"
            )
            return None
            
        except Exception as e:
            self.pipeline.log_error(
                self.calculator_name, 
                f"Failed to extract footprint from context: {str(e)}"
            )
            return None
    
    def _extract_height_from_context(self, building_height: Dict[str, Any], building_id: str) -> Optional[float]:
        """Extract building height from building_height context"""
        try:
            # Handle different building_height formats
            if isinstance(building_height, (int, float)):
                return building_height
            
            if isinstance(building_height, dict):
                building_props = building_height.get('building_properties', [])
                for prop in building_props:
                    if prop.get('building_id') == building_id:
                        height_value = prop.get('height')
                        if height_value and height_value > 0:
                            self.pipeline.log_info(
                                self.calculator_name, 
                                f"Retrieved building height {height_value}m from context for building {building_id}"
                            )
                            return height_value
            
            self.pipeline.log_error(
                self.calculator_name, 
                f"Valid height not found in context for building_id: {building_id}"
            )
            return None
            
        except Exception as e:
            self.pipeline.log_error(
                self.calculator_name, 
                f"Failed to extract height from context: {str(e)}"
            )
            return None
    
    def _generate_lod12_surfaces(self, footprint_geometry: Dict[str, Any], height: float) -> Dict[str, Any]:
        """Generate LoD 1.2 semantic surfaces from footprint and height"""
        try:
            if footprint_geometry.get('type') != 'Polygon':
                self.pipeline.log_error(self.calculator_name, f"Unsupported geometry type: {footprint_geometry.get('type')}")
                return None
            
            coordinates = footprint_geometry.get('coordinates', [])
            if not coordinates or len(coordinates) == 0:
                self.pipeline.log_error(self.calculator_name, "Invalid footprint coordinates")
                return None
            
            # Get exterior ring coordinates
            exterior_ring = coordinates[0]
            if len(exterior_ring) < 4:  # Need at least 4 points for a closed polygon
                self.pipeline.log_error(self.calculator_name, "Insufficient coordinates for polygon")
                return None
            
            # Ensure polygon is closed
            if exterior_ring[0] != exterior_ring[-1]:
                exterior_ring.append(exterior_ring[0])
            
            # Generate surfaces
            surfaces = {
                'wall_surfaces': [],
                'roof_surface': None,
                'ground_surface': None,
                'building_volume': None
            }
            
            # 1. Generate Wall Surfaces
            wall_surfaces = self._generate_wall_surfaces(exterior_ring, height)
            surfaces['wall_surfaces'] = wall_surfaces
            
            # 2. Generate Roof Surface (top surface at height)
            roof_surface = self._generate_roof_surface(exterior_ring, height)
            surfaces['roof_surface'] = roof_surface
            
            # 3. Generate Ground Surface (bottom surface at ground level)
            ground_surface = self._generate_ground_surface(exterior_ring)
            surfaces['ground_surface'] = ground_surface
            
            # 4. Calculate building volume for validation
            area = self._calculate_polygon_area(footprint_geometry)
            volume = area * height
            surfaces['building_volume'] = {
                'volume_m3': volume,
                'base_area_m2': area,
                'height_m': height
            }
            
            self.pipeline.log_info(
                self.calculator_name, 
                f"Generated {len(wall_surfaces)} wall surfaces, 1 roof surface, 1 ground surface"
            )
            
            return surfaces
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to generate LoD 1.2 surfaces: {str(e)}")
            return None
    
    def _generate_wall_surfaces(self, exterior_ring: List[List[float]], height: float) -> List[Dict[str, Any]]:
        """Generate wall surfaces for each edge of the building footprint"""
        wall_surfaces = []
        
        try:
            # Process each edge of the polygon
            for i in range(len(exterior_ring) - 1):  # -1 because last point equals first point
                p1 = exterior_ring[i]
                p2 = exterior_ring[i + 1]
                
                # Create wall surface as a vertical rectangle
                wall_coordinates = [
                    [p1[0], p1[1], 0.0],        # bottom-left
                    [p2[0], p2[1], 0.0],        # bottom-right
                    [p2[0], p2[1], height],     # top-right
                    [p1[0], p1[1], height],     # top-left
                    [p1[0], p1[1], 0.0]         # close polygon
                ]
                
                # Calculate wall properties
                wall_length = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                wall_area = wall_length * height
                
                # Calculate orientation (azimuth from north)
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                azimuth = math.degrees(math.atan2(dx, dy))
                if azimuth < 0:
                    azimuth += 360
                
                wall_surface = {
                    'surface_id': f"wall_{i+1}",
                    'surface_type': 'WallSurface',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [wall_coordinates]
                    },
                    'properties': {
                        'wall_index': i + 1,
                        'area_m2': wall_area,
                        'height_m': height,
                        'length_m': wall_length,
                        'azimuth_degrees': azimuth,
                        'orientation': self._get_cardinal_direction(azimuth),
                        'lod': 1.2,
                        'surface_material': 'unknown',  # For TABULA typology assignment
                        'construction_type': 'unknown'   # For TABULA typology assignment
                    },
                    'semantic': {
                        'surface_class': 'WallSurface',
                        'building_element': 'exterior_wall',
                        'thermal_properties': {
                            'u_value': None,  # To be filled by TABULA calculator
                            'thermal_resistance': None,
                            'thermal_capacity': None
                        }
                    }
                }
                
                wall_surfaces.append(wall_surface)
            
            return wall_surfaces
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to generate wall surfaces: {str(e)}")
            return []
    
    def _generate_roof_surface(self, exterior_ring: List[List[float]], height: float) -> Dict[str, Any]:
        """Generate roof surface (top surface at building height)"""
        try:
            # Create roof coordinates at the specified height
            roof_coordinates = []
            for point in exterior_ring:
                roof_coordinates.append([point[0], point[1], height])
            
            # Calculate roof area
            roof_area = self._calculate_polygon_area_3d(roof_coordinates)
            
            roof_surface = {
                'surface_id': 'roof_1',
                'surface_type': 'RoofSurface',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [roof_coordinates]
                },
                'properties': {
                    'area_m2': roof_area,
                    'height_m': height,
                    'roof_type': 'flat',  # LoD 1.2 typically has flat roofs
                    'slope_degrees': 0.0,
                    'tilt_degrees': SURFACE_TILT['RoofSurface'],
                    'lod': 1.2,
                    'surface_material': 'unknown',  # For TABULA typology assignment
                    'construction_type': 'unknown'   # For TABULA typology assignment
                },
                'semantic': {
                    'surface_class': 'RoofSurface',
                    'building_element': 'roof',
                    'thermal_properties': {
                        'u_value': None,  # To be filled by TABULA calculator
                        'thermal_resistance': None,
                        'thermal_capacity': None
                    }
                }
            }
            
            return roof_surface
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to generate roof surface: {str(e)}")
            return None
    
    def _generate_ground_surface(self, exterior_ring: List[List[float]]) -> Dict[str, Any]:
        """Generate ground surface (bottom surface at ground level)"""
        try:
            # Create ground coordinates at height 0
            ground_coordinates = []
            for point in exterior_ring:
                ground_coordinates.append([point[0], point[1], 0.0])
            
            # Reverse order for proper normal direction (pointing up)
            ground_coordinates.reverse()
            
            # Calculate ground area
            ground_area = self._calculate_polygon_area_3d(ground_coordinates)
            
            ground_surface = {
                'surface_id': 'ground_1',
                'surface_type': 'GroundSurface',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [ground_coordinates]
                },
                'properties': {
                    'area_m2': ground_area,
                    'height_m': 0.0,
                    'tilt_degrees': SURFACE_TILT['GroundSurface'],
                    'lod': 1.2,
                    'surface_material': 'unknown',  # For foundation/ground interface
                    'construction_type': 'slab_on_ground'
                },
                'semantic': {
                    'surface_class': 'GroundSurface',
                    'building_element': 'ground_slab',
                    'thermal_properties': {
                        'u_value': None,  # To be filled by TABULA calculator
                        'thermal_resistance': None,
                        'thermal_capacity': None
                    }
                }
            }
            
            return ground_surface
            
        except Exception as e:
            self.pipeline.log_error(self.calculator_name, f"Failed to generate ground surface: {str(e)}")
            return None
    
    def _get_cardinal_direction(self, azimuth: float) -> str:
        """Convert azimuth angle to cardinal direction"""
        if azimuth >= 337.5 or azimuth < 22.5:
            return 'North'
        elif 22.5 <= azimuth < 67.5:
            return 'Northeast'
        elif 67.5 <= azimuth < 112.5:
            return 'East'
        elif 112.5 <= azimuth < 157.5:
            return 'Southeast'
        elif 157.5 <= azimuth < 202.5:
            return 'South'
        elif 202.5 <= azimuth < 247.5:
            return 'Southwest'
        elif 247.5 <= azimuth < 292.5:
            return 'West'
        elif 292.5 <= azimuth < 337.5:
            return 'Northwest'
        else:
            return 'Unknown'
    
    def _calculate_polygon_area(self, geometry: Dict[str, Any]) -> float:
        """Footprint area in m2 (coordinates are EPSG:4326, so reproject)."""
        return polygon_area_m2(geometry)

    def _calculate_polygon_area_3d(self, coordinates: List[List[float]]) -> float:
        """True 3D area in m2 of a planar ring given in EPSG:4326 + metre Z."""
        return polygon_area_3d_m2(coordinates)
    
    def _save_surfaces_to_database(self, building_id: str, surfaces: Dict[str, Any]) -> bool:
        """Save LoD 1.2 surfaces to database"""
        try:
            from cim_wizard.models import Building
            from django.db import transaction
            
            with transaction.atomic():
                try:
                    # Get the building record
                    building = Building.objects.get(building_id=building_id, lod=0)  # Start with LoD 0
                    
                    # Update with LoD 1.2 surfaces
                    building.building_surfaces_lod12 = surfaces
                    building.save()
                    
                    self.pipeline.log_info(
                        self.calculator_name, 
                        f"Successfully saved LoD 1.2 surfaces to database for building {building_id}"
                    )
                    return True
                    
                except Building.DoesNotExist:
                    self.pipeline.log_error(
                        self.calculator_name, 
                        f"Building not found in database: {building_id}"
                    )
                    return False
                    
        except Exception as e:
            self.pipeline.log_error(
                self.calculator_name, 
                f"Failed to save LoD 1.2 surfaces to database: {str(e)}"
            )
            return False 