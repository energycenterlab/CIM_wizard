"""
CIM Wizard Data Manager - Integrated Version

Single data-access boundary for the entire application.  Every database
read, write, and delete goes through this class so that routes and
calculators contain only request/response or domain logic.

Responsibilities:
  - Context management  (project/scenario/building identifiers)
  - Configuration loading (configuration.json)
  - Feature proxy generation (FeatureProxy / FeatureMethodSelector)
  - CRUD operations on ProjectScenario, Building, BuildingProperties
  - Raster queries (DSM/DTM)
  - Census-boundary persistence
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, text
from sqlalchemy.orm import Session

from app.services.census_service import CensusService
from app.services.raster_service import RasterService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Chaining helpers
# ---------------------------------------------------------------------------

class FeatureMethodSelector:
    """Represents a specific feature.method combination for chaining"""

    def __init__(self, feature_name: str, method_name: str):
        self.feature_name = feature_name
        self.method_name = method_name
        self.next_selector = None

    def __or__(self, other):
        if isinstance(other, FeatureMethodSelector):
            current = self
            while current.next_selector is not None:
                current = current.next_selector
            current.next_selector = other
            return self
        raise TypeError("Can only chain FeatureMethodSelector objects")

    def to_execution_plan(self):
        plan = []
        current = self
        while current:
            plan.append({
                'feature_name': current.feature_name,
                'method_name': current.method_name,
            })
            current = current.next_selector
        return plan


class FeatureProxy:
    """Proxy object that creates FeatureMethodSelector when accessing methods"""

    def __init__(self, feature_name: str):
        self.feature_name = feature_name

    def __getattr__(self, method_name: str):
        return FeatureMethodSelector(self.feature_name, method_name)


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class CimWizardDataManager:
    """
    Central data-access boundary.

    All database operations (read / write / delete) are performed through
    this class.  Routes call data-manager methods instead of ``db.query``
    directly; calculators call data-manager methods instead of holding
    their own ``_save_to_database`` helpers.
    """

    def __init__(self, config_path: str = None, db_session: Session = None):
        # Core data storage
        self.calculated_features: Dict[str, Any] = {}

        # Database session
        self.db_session = db_session

        # Service instances (lazy)
        self.census_service: Optional[CensusService] = None
        self.raster_service: Optional[RasterService] = None

        # Identifiers
        self.scenario_id: Optional[str] = None
        self.building_id: Optional[str] = None
        self.project_id: Optional[str] = None

        # Service URLs (kept for compatibility)
        self.raster_service_url = "internal://raster_service"
        self.census_service_url = "internal://census_service"

        # Additional context
        self.project_boundary = None

        # Configuration
        self.configuration: Dict[str, Any] = {}
        self.load_configuration(config_path)

        # Runtime method priority overrides
        self.method_priority_overrides: Dict[str, Dict[str, int]] = {}

        # Dynamic feature proxies and _data attributes from configuration
        for feature_name in self.configuration.get('features', {}):
            data_attr = f"{feature_name}_data"
            if not hasattr(self, data_attr):
                setattr(self, data_attr, None)
            if not hasattr(self, feature_name):
                setattr(self, feature_name, FeatureProxy(feature_name))

    # ==================================================================
    # Configuration
    # ==================================================================

    def load_configuration(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "configuration.json"
        try:
            with open(config_path, 'r') as f:
                self.configuration = json.load(f)
            if 'services' in self.configuration:
                self.configuration['services']['raster_gateway']['url'] = "internal://raster_service"
                self.configuration['services']['census_gateway']['url'] = "internal://census_service"
        except FileNotFoundError:
            logger.warning("Configuration file not found at %s", config_path)
            self.configuration = {}
        except json.JSONDecodeError as e:
            logger.error("Error parsing configuration file: %s", e)
            self.configuration = {}

    # ==================================================================
    # Service access
    # ==================================================================

    def get_census_service(self) -> CensusService:
        if not self.census_service:
            self.census_service = CensusService(db_session=self.db_session)
        return self.census_service

    def get_raster_service(self) -> RasterService:
        if not self.raster_service:
            self.raster_service = RasterService(db_session=self.db_session)
        return self.raster_service

    # ==================================================================
    # Context management
    # ==================================================================

    def set_context(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'db_session':
                self.db_session = value
                self.census_service = None
                self.raster_service = None
            elif hasattr(self, key):
                setattr(self, key, value)
            elif hasattr(self, f"{key}_data"):
                setattr(self, f"{key}_data", value)

    def get_context(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        if hasattr(self, f"{key}_data"):
            return getattr(self, f"{key}_data")
        return None

    def clear_context(self):
        self.calculated_features = {}
        self.scenario_id = None
        self.building_id = None
        self.project_id = None
        for attr in dir(self):
            if attr.endswith('_data'):
                setattr(self, attr, None)
        self.census_service = None
        self.raster_service = None

    # ==================================================================
    # Feature management
    # ==================================================================

    def set_feature(self, feature_name: str, value: Any):
        self.calculated_features[feature_name] = value
        data_attr = f"{feature_name}_data"
        if hasattr(self, data_attr):
            setattr(self, data_attr, value)

    def get_feature(self, feature_name: str) -> Any:
        if feature_name in self.calculated_features:
            return self.calculated_features[feature_name]
        data_attr = f"{feature_name}_data"
        if hasattr(self, data_attr):
            return getattr(self, data_attr)
        return None

    def has_feature(self, feature_name: str) -> bool:
        return (feature_name in self.calculated_features
                or getattr(self, f"{feature_name}_data", None) is not None)

    def set_inputs_from_request(self, inputs: Dict[str, Any]):
        if not inputs:
            return
        for key in ('project_id', 'scenario_id', 'building_id'):
            if key in inputs:
                setattr(self, key, inputs[key])
        feature_keys = list(self.configuration.get('features', {}).keys())
        for key, value in inputs.items():
            if key in feature_keys:
                self.set_feature(key, value)
            elif key not in ('project_id', 'scenario_id', 'building_id'):
                self.set_context(**{key: value})

    def set_method_priority(self, feature: str, priorities: Dict[str, int]):
        self.method_priority_overrides[feature] = priorities

    def get_method_priority_override(self, feature: str) -> Optional[Dict[str, int]]:
        return self.method_priority_overrides.get(feature)

    def get_available_pipelines(self) -> List[str]:
        if self.configuration and 'predefined_pipelines' in self.configuration:
            return list(self.configuration['predefined_pipelines'].keys())
        return []

    def get_configured_features(self) -> List[str]:
        if self.configuration and 'features' in self.configuration:
            return list(self.configuration['features'].keys())
        return []

    def get_available_features(self) -> List[str]:
        features = list(self.calculated_features.keys())
        for attr in dir(self):
            if attr.endswith('_data') and getattr(self, attr) is not None:
                feature_name = attr[:-5]
                if feature_name not in features:
                    features.append(feature_name)
        return features

    # ==================================================================
    # Configuration access
    # ==================================================================

    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        if self.configuration and 'features' in self.configuration:
            return self.configuration['features'].get(feature_name, {})
        return {}

    def get_pipeline_config(self, pipeline_name: str) -> Dict[str, Any]:
        if self.configuration and 'predefined_pipelines' in self.configuration:
            return self.configuration['predefined_pipelines'].get(pipeline_name, {})
        return {}

    def get_global_settings(self) -> Dict[str, Any]:
        if self.configuration:
            return self.configuration.get('global_settings', {})
        return {}

    # ==================================================================
    # SCENARIO  CRUD
    # ==================================================================

    def _require_session(self) -> Session:
        if not self.db_session:
            raise RuntimeError("No database session available")
        return self.db_session

    def _serialize_scenario(self, s) -> Dict[str, Any]:
        from geoalchemy2.shape import to_shape
        from shapely.geometry import mapping
        item: Dict[str, Any] = {
            "project_id": s.project_id,
            "scenario_id": s.scenario_id,
            "project_name": s.project_name,
            "scenario_name": s.scenario_name,
            "project_zoom": s.project_zoom,
            "project_crs": s.project_crs,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        try:
            if s.project_boundary is not None:
                item["project_boundary"] = mapping(to_shape(s.project_boundary))
        except Exception:
            item["project_boundary"] = None
        try:
            if s.project_center is not None:
                item["project_center"] = mapping(to_shape(s.project_center))
        except Exception:
            item["project_center"] = None
        return item

    def list_projects(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        from app.models.vector import ProjectScenario
        session = self._require_session()
        rows = session.query(ProjectScenario).offset(offset).limit(limit).all()
        return [self._serialize_scenario(r) for r in rows]

    def count_projects(self) -> int:
        from app.models.vector import ProjectScenario
        return self._require_session().query(ProjectScenario).count()

    def get_dashboard(self, limit: int = 10) -> Dict[str, Any]:
        return {
            "total_projects": self.count_projects(),
            "projects": self.list_projects(offset=0, limit=limit),
        }

    def get_scenario(self, project_id: str, scenario_id: str) -> Optional[Dict[str, Any]]:
        from app.models.vector import ProjectScenario
        session = self._require_session()
        row = session.query(ProjectScenario).filter_by(
            project_id=project_id, scenario_id=scenario_id
        ).first()
        return self._serialize_scenario(row) if row else None

    def get_scenario_orm(self, project_id: str, scenario_id: str):
        from app.models.vector import ProjectScenario
        return self._require_session().query(ProjectScenario).filter_by(
            project_id=project_id, scenario_id=scenario_id
        ).first()

    def get_scenarios_for_project(self, project_id: str) -> List[Dict[str, Any]]:
        from app.models.vector import ProjectScenario
        session = self._require_session()
        rows = session.query(ProjectScenario).filter(
            ProjectScenario.project_id == project_id
        ).all()
        return [self._serialize_scenario(r) for r in rows]

    def get_baseline_scenario_id(self, project_id: str) -> Optional[str]:
        from app.models.vector import ProjectScenario
        session = self._require_session()
        row = session.query(ProjectScenario).filter(
            and_(ProjectScenario.project_id == project_id,
                 ProjectScenario.scenario_id == project_id)
        ).first()
        if row:
            return row.scenario_id
        row = session.query(ProjectScenario).filter(
            and_(ProjectScenario.project_id == project_id,
                 ProjectScenario.scenario_name.ilike("baseline"))
        ).first()
        return row.scenario_id if row else None

    def save_scenario(
        self,
        project_id: str,
        scenario_id: str,
        project_name: str,
        scenario_name: str,
        scenario_geo: Dict[str, Any],
    ) -> bool:
        """Upsert a ProjectScenario from GeoJSON geometry."""
        try:
            from shapely.geometry import shape, Polygon
            from geoalchemy2.shape import from_shape
            from app.models.vector import ProjectScenario

            session = self._require_session()
            geometry = scenario_geo.get('geometry')
            if not geometry:
                return False

            geom_shape = shape(geometry)
            if geometry['type'] == 'MultiPolygon':
                polygon_coords = geometry['coordinates'][0]
                boundary_shape = Polygon(
                    polygon_coords[0],
                    polygon_coords[1:] if len(polygon_coords) > 1 else [],
                )
            else:
                boundary_shape = geom_shape

            center_shape = boundary_shape.centroid

            scenario = session.query(ProjectScenario).filter_by(
                project_id=project_id, scenario_id=scenario_id
            ).first()

            if not scenario:
                scenario = ProjectScenario(
                    project_id=project_id,
                    scenario_id=scenario_id,
                    project_name=project_name,
                    scenario_name=scenario_name,
                    project_boundary=from_shape(boundary_shape, srid=4326),
                    project_center=from_shape(center_shape, srid=4326),
                    project_zoom=15,
                    project_crs=4326,
                    created_at=datetime.utcnow(),
                )
                session.add(scenario)
            else:
                scenario.project_name = project_name
                scenario.scenario_name = scenario_name
                scenario.project_boundary = from_shape(boundary_shape, srid=4326)
                scenario.project_center = from_shape(center_shape, srid=4326)
                scenario.updated_at = datetime.utcnow()

            session.commit()
            return True
        except Exception as e:
            self.db_session.rollback()
            logger.error("save_scenario failed: %s", e, exc_info=True)
            return False

    def create_scenario_from_baseline(
        self, project_id: str, scenario_name: str
    ) -> Optional[Dict[str, Any]]:
        """Create a new scenario by copying metadata from the baseline."""
        import uuid as _uuid
        from app.models.vector import ProjectScenario

        session = self._require_session()
        baseline = self.get_scenario_orm(project_id, project_id)
        if not baseline:
            from app.models.vector import ProjectScenario as PS
            baseline = session.query(PS).filter(
                and_(PS.project_id == project_id,
                     PS.scenario_name.ilike("baseline"))
            ).first()
        if not baseline:
            return None

        scenario_id = str(_uuid.uuid4())
        new_scenario = ProjectScenario(
            project_id=project_id,
            scenario_id=scenario_id,
            project_name=baseline.project_name,
            scenario_name=scenario_name.strip(),
            project_boundary=baseline.project_boundary,
            project_center=baseline.project_center,
            project_zoom=baseline.project_zoom,
            project_crs=baseline.project_crs,
            census_boundary=baseline.census_boundary,
        )
        session.add(new_scenario)
        session.commit()
        session.refresh(new_scenario)
        return self._serialize_scenario(new_scenario)

    def update_census_boundary(
        self, project_id: str, scenario_id: str, census_boundary: Dict[str, Any]
    ) -> bool:
        """Persist a census boundary GeoJSON onto the ProjectScenario row."""
        try:
            from shapely.geometry import shape, MultiPolygon, Polygon
            from geoalchemy2.shape import from_shape

            session = self._require_session()
            scenario = self.get_scenario_orm(project_id, scenario_id)
            if not scenario:
                logger.warning("Scenario %s/%s not found", project_id, scenario_id)
                return False
            geometry = census_boundary.get('geometry')
            if not geometry:
                return False
            census_shape = shape(geometry)
            if isinstance(census_shape, Polygon):
                census_shape = MultiPolygon([census_shape])
            scenario.census_boundary = from_shape(census_shape, srid=4326)
            session.commit()
            return True
        except Exception as e:
            self.db_session.rollback()
            logger.error("update_census_boundary failed: %s", e)
            return False

    def delete_project_data(
        self,
        project_id: str,
        scenario_id: Optional[str] = None,
        building_id: Optional[str] = None,
    ) -> Dict[str, int]:
        """Cascading delete.  Returns counts of deleted rows."""
        from app.models.vector import ProjectScenario, Building, BuildingProperties

        session = self._require_session()
        deleted = {
            "building_properties_deleted": 0,
            "buildings_deleted": 0,
            "project_scenarios_deleted": 0,
        }

        if project_id and scenario_id and building_id:
            # Single building
            deleted["building_properties_deleted"] = session.query(BuildingProperties).filter(
                and_(BuildingProperties.project_id == project_id,
                     BuildingProperties.scenario_id == scenario_id,
                     BuildingProperties.building_id == building_id)
            ).delete(synchronize_session=False)
            if session.query(BuildingProperties).filter(
                BuildingProperties.building_id == building_id
            ).count() == 0:
                deleted["buildings_deleted"] = session.query(Building).filter(
                    Building.building_id == building_id
                ).delete(synchronize_session=False)
            session.commit()

        elif project_id and scenario_id:
            # Whole scenario
            bp_bids = [r.building_id for r in session.query(
                BuildingProperties.building_id
            ).filter(and_(
                BuildingProperties.project_id == project_id,
                BuildingProperties.scenario_id == scenario_id,
            )).all()]

            deleted["building_properties_deleted"] = session.query(BuildingProperties).filter(
                and_(BuildingProperties.project_id == project_id,
                     BuildingProperties.scenario_id == scenario_id)
            ).delete(synchronize_session=False)

            b_count = 0
            for bid in bp_bids:
                if session.query(BuildingProperties).filter(
                    BuildingProperties.building_id == bid
                ).count() == 0:
                    b_count += session.query(Building).filter(
                        Building.building_id == bid
                    ).delete(synchronize_session=False)
            deleted["buildings_deleted"] = b_count

            deleted["project_scenarios_deleted"] = session.query(ProjectScenario).filter(
                and_(ProjectScenario.project_id == project_id,
                     ProjectScenario.scenario_id == scenario_id)
            ).delete(synchronize_session=False)
            session.commit()

        else:
            # Whole project
            bp_bids = [r.building_id for r in session.query(
                BuildingProperties.building_id
            ).filter(BuildingProperties.project_id == project_id).distinct().all()]

            deleted["building_properties_deleted"] = session.query(BuildingProperties).filter(
                BuildingProperties.project_id == project_id
            ).delete(synchronize_session=False)

            b_count = 0
            for bid in bp_bids:
                if session.query(BuildingProperties).filter(
                    BuildingProperties.building_id == bid
                ).count() == 0:
                    b_count += session.query(Building).filter(
                        Building.building_id == bid
                    ).delete(synchronize_session=False)
            deleted["buildings_deleted"] = b_count

            deleted["project_scenarios_deleted"] = session.query(ProjectScenario).filter(
                ProjectScenario.project_id == project_id
            ).delete(synchronize_session=False)
            session.commit()

        return deleted

    # ==================================================================
    # BUILDING  CRUD
    # ==================================================================

    def save_building(self, building_data: Dict[str, Any], lod: int = 0) -> bool:
        """Upsert a Building row from a dict that may be a GeoJSON Feature."""
        try:
            from shapely.geometry import shape
            from geoalchemy2.shape import from_shape
            from app.models.vector import Building

            session = self._require_session()
            building_id = building_data.get('building_id')
            if not building_id and 'properties' in building_data:
                building_id = building_data['properties'].get('building_id')
            if not building_id:
                return False

            existing = session.query(Building).filter_by(
                building_id=building_id, lod=lod
            ).first()

            geom_dict = building_data.get('geometry', {})
            if not existing:
                kwargs: Dict[str, Any] = dict(
                    building_id=building_id, lod=lod,
                    building_geometry_source='integrated_database',
                    created_at=datetime.utcnow(),
                )
                if geom_dict:
                    kwargs['building_geometry'] = from_shape(shape(geom_dict), srid=4326)
                session.add(Building(**kwargs))
            else:
                if geom_dict:
                    existing.building_geometry = from_shape(shape(geom_dict), srid=4326)
                existing.updated_at = datetime.utcnow()

            session.commit()
            return True
        except Exception as e:
            self.db_session.rollback()
            logger.error("save_building failed: %s", e, exc_info=True)
            return False

    def get_building(self, building_id: str, lod: int = 0) -> Optional[Dict[str, Any]]:
        from geoalchemy2.shape import to_shape
        from shapely.geometry import mapping
        from app.models.vector import Building

        session = self._require_session()
        b = session.query(Building).filter(
            and_(Building.building_id == building_id, Building.lod == lod)
        ).first()
        if not b:
            return None
        geom = mapping(to_shape(b.building_geometry)) if b.building_geometry else None
        return {
            "building_id": b.building_id,
            "lod": b.lod,
            "geometry": geom,
            "geometry_source": b.building_geometry_source,
            "census_id": b.census_id,
        }

    def get_buildings_geojson(
        self, project_id: str, scenario_id: str, lod: int = 0
    ) -> Dict[str, Any]:
        """
        Return a GeoJSON FeatureCollection with building geometries merged
        with their properties.  Handles baseline / delta merging.
        Includes building-level columns (z_value, building_name, pv_ids),
        grid data (if grid_id assigned), and PV data (if pv_ids present).
        """
        from geoalchemy2.shape import to_shape
        from shapely.geometry import mapping
        from sqlalchemy import text
        from app.models.vector import Building, BuildingProperties

        session = self._require_session()
        baseline_sid = self.get_baseline_scenario_id(project_id)
        is_baseline = scenario_id == project_id or scenario_id == baseline_sid
        query_sid = baseline_sid or scenario_id

        def _props_dict(p):
            return {
                "height": p.height, "area": p.area, "volume": p.volume,
                "type": p.type, "n_people": p.n_people, "n_family": p.n_family,
                "number_of_floors": p.number_of_floors,
                "const_year": p.const_year, "const_period_census": p.const_period_census,
                "const_tabula": p.const_tabula,
                "envelope_efficiency": p.envelope_efficiency,
                "fmu_file": p.fmu_file,
            }

        def _merge(base_dict, delta_row):
            out = dict(base_dict)
            if delta_row:
                for k, v in _props_dict(delta_row).items():
                    if v is not None:
                        out[k] = v
            return out

        # Pre-load PV data keyed by building_id for buildings that have PVs
        pv_map = {}
        try:
            pv_rows = session.execute(text("""
                SELECT pv_id, building_id, fid, slope, num, area_reale, number, s,
                       index_righ, id_pod, ST_AsGeoJSON(pv_geometry)::text AS geojson
                FROM cim_vector.pv
            """)).mappings().all()
            import json as _json
            for r in pv_rows:
                bid = str(r["building_id"])
                entry = {k: r[k] for k in ("pv_id", "fid", "slope", "num", "area_reale",
                                            "number", "s", "index_righ", "id_pod")}
                entry["pv_id"] = str(entry["pv_id"])
                try:
                    entry["geometry"] = _json.loads(r["geojson"])
                except Exception:
                    entry["geometry"] = None
                pv_map.setdefault(bid, []).append(entry)
        except Exception:
            pass

        def _build_features(query_rows, delta_map=None):
            features = []
            for props, building in query_rows:
                try:
                    geom = mapping(to_shape(building.building_geometry))
                except Exception:
                    continue
                base = _props_dict(props)
                merged = _merge(base, delta_map.get((building.building_id, lod))) if delta_map else base

                bid_str = str(building.building_id)
                merged["z_value"] = building.z_value
                merged["building_name"] = building.building_name
                merged["pv_ids"] = [str(p) for p in building.pv_ids] if building.pv_ids else []

                if bid_str in pv_map:
                    merged["pv_data"] = pv_map[bid_str]

                features.append({
                    "type": "Feature",
                    "geometry": geom,
                    "properties": {
                        "building_id": bid_str,
                        "lod": building.lod,
                        **merged,
                    },
                })
            return features

        base_query = session.query(BuildingProperties, Building).join(
            Building, Building.building_id == BuildingProperties.building_id
        ).filter(and_(
            BuildingProperties.project_id == project_id,
            BuildingProperties.scenario_id == query_sid,
            BuildingProperties.lod == lod,
        ))

        if is_baseline:
            features = _build_features(base_query)
        else:
            delta_rows = session.query(BuildingProperties).filter(and_(
                BuildingProperties.project_id == project_id,
                BuildingProperties.scenario_id == scenario_id,
                BuildingProperties.lod == lod,
            )).all()
            delta_map = {(r.building_id, r.lod): r for r in delta_rows}
            features = _build_features(base_query, delta_map)

        # Include grid data if grid_id is assigned to this scenario
        grid_info = None
        try:
            grid_row = session.execute(text("""
                SELECT grid_id FROM cim_vector.cim_wizard_project_scenario
                WHERE project_id = :pid AND scenario_id = :sid AND grid_id IS NOT NULL
            """), {"pid": project_id, "sid": scenario_id}).fetchone()
            if grid_row:
                grid_info = {"grid_id": str(grid_row[0])}
        except Exception:
            pass

        result = {"type": "FeatureCollection", "features": features}
        if grid_info:
            result["grid"] = grid_info
        return result

    def get_buildings_at_point(self, lng: float, lat: float) -> List[Dict[str, Any]]:
        from geoalchemy2 import func
        from app.models.vector import Building
        session = self._require_session()
        point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
        rows = session.query(Building).filter(
            func.ST_Contains(Building.building_geometry, point)
        ).all()
        return [{"building_id": b.building_id, "lod": b.lod, "census_id": b.census_id} for b in rows]

    def get_buildings_in_buffer(self, lng: float, lat: float, buffer_m: float = 10) -> List[Dict[str, Any]]:
        from geoalchemy2 import func
        from app.models.vector import Building
        session = self._require_session()
        point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
        buffer_deg = buffer_m / 111320.0
        rows = session.query(Building).filter(
            func.ST_DWithin(Building.building_geometry, point, buffer_deg)
        ).all()
        return [{"building_id": b.building_id, "lod": b.lod, "census_id": b.census_id} for b in rows]

    # ==================================================================
    # BUILDING PROPERTIES  CRUD
    # ==================================================================

    def upsert_building_properties_batch(
        self,
        buildings: List[Dict[str, Any]],
        project_id: str,
        scenario_id: str,
        property_name: str,
        values: List[Any],
    ) -> int:
        """
        Bulk upsert a single property column across many buildings.

        ``buildings`` is a list of dicts each containing at least
        ``building_id`` (and optionally ``lod``).  ``values`` is a
        parallel list of the same length.
        """
        from app.models.vector import BuildingProperties
        session = self._require_session()

        _CAST = {
            "height": lambda v: float(v),
            "area": lambda v: float(v),
            "volume": lambda v: float(v),
            "number_of_floors": lambda v: float(v),
            "type": lambda v: str(v),
            "n_people": lambda v: int(round(float(v))),
            "n_family": lambda v: int(round(float(v))),
            "const_year": lambda v: int(v),
            "const_period_census": lambda v: str(v),
            "const_tabula": lambda v: str(v),
            "filter_res": lambda v: bool(v),
            "envelope_efficiency": lambda v: str(v),
            "fmu_file": lambda v: str(v),
        }

        cast_fn = _CAST.get(property_name)
        updated = 0

        try:
            for i, building in enumerate(buildings):
                if i >= len(values):
                    break
                raw_value = values[i]
                if raw_value is None:
                    continue

                building_id = building.get('building_id')
                if not building_id and 'properties' in building:
                    building_id = building['properties'].get('building_id')
                if not building_id:
                    continue

                lod = building.get('lod', 0)
                try:
                    typed_value = cast_fn(raw_value) if cast_fn else raw_value
                except (ValueError, TypeError):
                    continue

                props = session.query(BuildingProperties).filter(and_(
                    BuildingProperties.building_id == building_id,
                    BuildingProperties.project_id == project_id,
                    BuildingProperties.scenario_id == scenario_id,
                    BuildingProperties.lod == lod,
                )).first()

                if not props:
                    props = BuildingProperties(
                        building_id=building_id,
                        project_id=project_id,
                        scenario_id=scenario_id,
                        lod=lod,
                        created_at=datetime.utcnow(),
                    )
                    session.add(props)

                setattr(props, property_name, typed_value)
                props.updated_at = datetime.utcnow()
                updated += 1

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("upsert_building_properties_batch failed: %s", e)
            raise

        return updated

    def upsert_building_property_fields(
        self,
        project_id: str,
        scenario_id: str,
        building_id: str,
        lod: int = 0,
        **fields,
    ) -> bool:
        """Upsert arbitrary fields on a single BuildingProperties row."""
        from app.models.vector import BuildingProperties
        session = self._require_session()

        props = session.query(BuildingProperties).filter(and_(
            BuildingProperties.building_id == building_id,
            BuildingProperties.project_id == project_id,
            BuildingProperties.scenario_id == scenario_id,
            BuildingProperties.lod == lod,
        )).first()

        if not props:
            props = BuildingProperties(
                building_id=building_id,
                project_id=project_id,
                scenario_id=scenario_id,
                lod=lod,
                **fields,
            )
            session.add(props)
        else:
            for k, v in fields.items():
                setattr(props, k, v)

        session.commit()
        return True

    def get_building_properties(
        self,
        project_id: str,
        scenario_id: str,
        building_id: Optional[str] = None,
        lod: int = 0,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query building properties with baseline/delta merge logic.
        """
        from app.models.vector import BuildingProperties
        session = self._require_session()
        baseline_sid = self.get_baseline_scenario_id(project_id)
        is_baseline = scenario_id == project_id or scenario_id == baseline_sid
        query_sid = baseline_sid or scenario_id

        def _serialize(p):
            return {
                "building_id": str(p.building_id),
                "scenario_id": str(p.scenario_id),
                "project_id": p.project_id,
                "lod": p.lod,
                "height": p.height, "area": p.area, "volume": p.volume,
                "number_of_floors": p.number_of_floors, "type": p.type,
                "const_period_census": p.const_period_census,
                "const_year": p.const_year, "const_tabula": p.const_tabula,
                "n_people": p.n_people, "n_family": p.n_family,
                "envelope_efficiency": p.envelope_efficiency,
                "fmu_file": p.fmu_file,
                "created_at": p.created_at, "updated_at": p.updated_at,
            }

        if is_baseline:
            q = session.query(BuildingProperties).filter(and_(
                BuildingProperties.project_id == project_id,
                BuildingProperties.scenario_id == query_sid,
                BuildingProperties.lod == lod,
            ))
            if building_id:
                q = q.filter(BuildingProperties.building_id == building_id)
            return [_serialize(p) for p in q.offset(offset).limit(limit).all()]

        # Delta merge
        q = session.query(BuildingProperties).filter(and_(
            BuildingProperties.project_id == project_id,
            BuildingProperties.scenario_id == baseline_sid,
            BuildingProperties.lod == lod,
        ))
        if building_id:
            q = q.filter(BuildingProperties.building_id == building_id)
        baseline_rows = q.offset(offset).limit(limit).all()

        delta_rows = session.query(BuildingProperties).filter(and_(
            BuildingProperties.project_id == project_id,
            BuildingProperties.scenario_id == scenario_id,
            BuildingProperties.lod == lod,
        )).all()
        delta_map = {(r.building_id, r.lod): r for r in delta_rows}

        result = []
        for p in baseline_rows:
            base = _serialize(p)
            base["scenario_id"] = scenario_id
            delta = delta_map.get((p.building_id, p.lod))
            if delta:
                d = _serialize(delta)
                for k, v in d.items():
                    if v is not None and k not in ("building_id", "scenario_id", "project_id", "lod", "created_at"):
                        base[k] = v
            result.append(base)
        return result

    # ==================================================================
    # RASTER  helpers
    # ==================================================================

    def check_raster_table(self, table_name: str) -> bool:
        session = self._require_session()
        try:
            result = session.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).fetchone()
            return (result[0] if result else 0) > 0
        except Exception:
            session.rollback()
            return False

    def query_raster_value(self, table_name: str, lon: float, lat: float) -> Optional[float]:
        session = self._require_session()
        try:
            query = text(f"""
                SELECT ST_Value(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                FROM {table_name}
                WHERE ST_Intersects(rast, ST_SetSRID(ST_Point(:lon, :lat), 4326))
                LIMIT 1
            """)
            result = session.execute(query, {'lon': lon, 'lat': lat}).fetchone()
            if result and result[0] is not None:
                return float(result[0])
            return None
        except Exception:
            session.rollback()
            return None

    # ==================================================================
    # Utility
    # ==================================================================

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            'project_id': self.project_id,
            'scenario_id': self.scenario_id,
            'building_id': self.building_id,
            'calculated_features': self.calculated_features.copy(),
            'services': {'census': 'integrated', 'raster': 'integrated'},
        }
        for attr in dir(self):
            if attr.endswith('_data'):
                value = getattr(self, attr)
                if value is not None:
                    result[attr[:-5]] = value
        return result

    def __repr__(self):
        svc = "integrated" if (self.census_service or self.raster_service) else "not initialized"
        return (
            f"CimWizardDataManager(project={self.project_id}, "
            f"scenario={self.scenario_id}, features={len(self.calculated_features)}, "
            f"services={svc})"
        )
