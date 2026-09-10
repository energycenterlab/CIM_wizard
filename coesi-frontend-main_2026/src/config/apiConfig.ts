const env = (import.meta as any)?.env ?? {};

export const COESI_API_BASE = 
  env.VITE_COESI_API_BASE || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost');

export const LEGACY_API_BASE = 
  env.VITE_LEGACY_API_BASE || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost');

export const YAML_BUILDER_URL = 
  env.VITE_YAML_BUILDER_URL || (typeof window !== 'undefined' ? `${window.location.origin}/yaml-builder` : 'http://localhost:8099');

// CIM Wizard Integrated backend (FastAPI)
export const CIM_WIZARD_BASE =
  env.VITE_CIM_WIZARD_BASE || 'http://localhost:8000';

// Centralized CIM Wizard endpoints (kept as functions when params are needed)
export const CIM_WIZARD_URLS = {
  HEALTH: `${CIM_WIZARD_BASE}/api/v1/vector/health`,
  PROJECTS: `${CIM_WIZARD_BASE}/api/v1/vector/projects`,
  SCENARIOS: (projectId: string) => `${CIM_WIZARD_BASE}/api/v1/vector/pscenarios/${projectId}`,
  PROJECT_SCENARIO_DETAILS: (projectId: string, scenarioId: string) =>
    `${CIM_WIZARD_BASE}/api/v1/vector/project_scenario_details/${projectId}/${scenarioId}`,
  BUILDINGS_GEOJSON: (projectId: string, scenarioId: string) =>
    `${CIM_WIZARD_BASE}/api/v1/vector/get_buildings_geojson/${projectId}/${scenarioId}`,
  BUILDING_PROPERTIES: (projectId: string, scenarioId: string) =>
    `${CIM_WIZARD_BASE}/api/v1/vector/buildingproperties/${projectId}/${scenarioId}`,
  BASELINE_SCENARIO: `${CIM_WIZARD_BASE}/api/v1/building/execute_building_analysis`,
  ASSIGN_PV: `${CIM_WIZARD_BASE}/api/v1/building/assign_pv`,
  MAP_TO_CITYDB: `${CIM_WIZARD_BASE}/api/v1/building/map_to_citydb`,
  JOB: (jobId: string) => `${CIM_WIZARD_BASE}/api/v1/jobs/${jobId}`,
  JOBS: `${CIM_WIZARD_BASE}/api/v1/jobs`,
  COMPLETE_CHAIN: `${CIM_WIZARD_BASE}/api/v1/complete/execute_complete_chain`,
};

export const COESI_API_URLS = {
  MODEL_MANAGER: `${COESI_API_BASE}/api/v1/models`,
  VALIDATION_ENGINE: `${COESI_API_BASE}/api/v1/validate`,
  SCENARIO_MANAGER: `${COESI_API_BASE}/api/v1/scenarios`,
  SIMULATIONS: `${COESI_API_BASE}/api/v1/simulations`,
  GRAPHDB: `${COESI_API_BASE}/graphdb`
};

export const API_CONFIG = {
  COESI_API_BASE,
  LEGACY_API_BASE,
  YAML_BUILDER_URL,
  CIM_WIZARD_BASE,
  ...COESI_API_URLS
};

