import { CIM_WIZARD_URLS, CIM_WIZARD_BASE } from '../config/apiConfig';

export interface ProjectScenario {
  project_id: string;
  scenario_id: string;
  project_name?: string;
  scenario_name?: string;
  project_boundary?: any;
  project_center?: { type: string; coordinates: [number, number] };
  lod?: number;
  project_zoom?: number;
  project_crs?: number;
  created_at?: string;
  updated_at?: string;
}

export interface BuildingFeature {
  type: 'Feature';
  geometry: any;
  properties: {
    building_id: string;
    lod?: number;
    height?: number;
    area?: number;
    volume?: number;
    filter_res?: boolean;
    n_people?: number;
    n_family?: number;
    [key: string]: any;
  };
}

export interface BuildingsGeoJSON {
  type: 'FeatureCollection';
  features: BuildingFeature[];
}

export interface BaselineRequest {
  project_boundary: any; // GeoJSON Feature or FeatureCollection
  project_name?: string;
  scenario_name?: string | null;
  save_to_db?: boolean;
  sync?: boolean;
}

export interface JobStatus {
  job_id: string;
  job_type: string;
  status: 'queued' | 'running' | 'success' | 'failed' | string;
  project_id?: string;
  scenario_id?: string;
  progress?: number;
  current_step?: string | null;
  error?: string | null;
  result?: any;
  poll_url?: string;
}

export type JobProgressCallback = (job: JobStatus) => void;

async function handleResponse<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const json = await resp.json();
      detail = json.detail || json.error || detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }
  return resp.json() as Promise<T>;
}

export async function getProjects(): Promise<ProjectScenario[]> {
  try {
    console.log('🔍 Fetching projects from:', CIM_WIZARD_URLS.PROJECTS);
    const resp = await fetch(CIM_WIZARD_URLS.PROJECTS, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Don't include credentials for CORS to work with wildcard origin
      credentials: 'omit',
    });
    console.log('📡 Response status:', resp.status, resp.statusText);
    console.log('📡 Response headers:', Object.fromEntries(resp.headers.entries()));
    
    if (!resp.ok) {
      const errorText = await resp.text();
      console.error('❌ Error response:', errorText);
      throw new Error(`HTTP ${resp.status}: ${errorText || resp.statusText}`);
    }
    
    const data = await resp.json();
    console.log('✅ Projects fetched successfully:', data.length, 'projects');
    return data;
  } catch (error) {
    console.error('🚨 Failed to fetch projects:', error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error(`Cannot connect to backend at ${CIM_WIZARD_URLS.PROJECTS}. Make sure the backend is running on port 8000.`);
    }
    throw error;
  }
}

export async function getScenarios(projectId: string): Promise<ProjectScenario[]> {
  try {
    const url = CIM_WIZARD_URLS.SCENARIOS(projectId);
    console.log('🔍 Fetching scenarios from:', url);
    const resp = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'omit',
    });
    console.log('📡 Scenarios response status:', resp.status, resp.statusText);
    
    if (!resp.ok) {
      const errorText = await resp.text();
      console.error('❌ Error response:', errorText);
      throw new Error(`HTTP ${resp.status}: ${errorText || resp.statusText}`);
    }
    
    const data = await resp.json();
    console.log('✅ Scenarios fetched successfully:', data.length, 'scenarios');
    return data;
  } catch (error) {
    console.error('🚨 Failed to fetch scenarios:', error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error(`Cannot connect to backend. Make sure the backend is running on port 8000.`);
    }
    throw error;
  }
}

export async function getBuildingsGeoJSON(projectId: string, scenarioId: string): Promise<BuildingsGeoJSON> {
  try {
    const url = CIM_WIZARD_URLS.BUILDINGS_GEOJSON(projectId, scenarioId);
    console.log('🔍 Fetching buildings from:', url);
    const resp = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'omit',
    });
    console.log('📡 Buildings response status:', resp.status, resp.statusText);
    
    if (!resp.ok) {
      const errorText = await resp.text();
      console.error('❌ Error response:', errorText);
      throw new Error(`HTTP ${resp.status}: ${errorText || resp.statusText}`);
    }
    
    const data = await resp.json();
    console.log('✅ Buildings fetched successfully:', data.features?.length || 0, 'buildings');
    return data;
  } catch (error) {
    console.error('🚨 Failed to fetch buildings:', error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error(`Cannot connect to backend. Make sure the backend is running on port 8000.`);
    }
    throw error;
  }
}

export async function getBuildingProperties(projectId: string, scenarioId: string): Promise<any[]> {
  const resp = await fetch(CIM_WIZARD_URLS.BUILDING_PROPERTIES(projectId, scenarioId));
  return handleResponse<any[]>(resp);
}

export async function getJob(jobId: string): Promise<JobStatus> {
  const resp = await fetch(CIM_WIZARD_URLS.JOB(jobId), {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'omit',
  });
  return handleResponse<JobStatus>(resp);
}

async function waitForJob(
  jobId: string,
  onProgress?: JobProgressCallback,
  intervalMs = 2000,
  timeoutMs = 20 * 60 * 1000,
): Promise<JobStatus> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const job = await getJob(jobId);
    onProgress?.(job);
    if (job.status === 'success') return job;
    if (job.status === 'failed') {
      throw new Error(job.error || 'Job failed');
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
  throw new Error('Timed out waiting for the job to finish. Do not retry the create request; check job status instead.');
}

/**
 * POST a heavy pipeline. Default backend response is 202 + job_id.
 * Poll until success. Never retry the POST (each call creates a new project).
 */
export async function postHeavyJob(
  url: string,
  payload: unknown,
  onProgress?: JobProgressCallback,
): Promise<any> {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'omit',
    body: JSON.stringify(payload),
  });

  if (resp.status === 202) {
    const accepted = await resp.json();
    onProgress?.(accepted);
    const jobId = accepted.job_id;
    if (!jobId) {
      throw new Error('Server accepted the job but did not return job_id');
    }
    return waitForJob(jobId, onProgress);
  }

  return handleResponse<any>(resp);
}

export async function createBaselineScenario(
  payload: BaselineRequest,
  onProgress?: JobProgressCallback,
): Promise<any> {
  return postHeavyJob(CIM_WIZARD_URLS.BASELINE_SCENARIO, payload, onProgress);
}

export async function assignPv(
  payload: { project_id: string; scenario_id: string; lod?: number; offset_m?: number },
  onProgress?: JobProgressCallback,
): Promise<any> {
  return postHeavyJob(CIM_WIZARD_URLS.ASSIGN_PV, payload, onProgress);
}

export async function mapToCitydb(
  payload: {
    project_id: string;
    scenario_id: string;
    lod12_method?: string;
    force_lod12?: boolean;
    force_remap?: boolean;
  },
  onProgress?: JobProgressCallback,
): Promise<any> {
  return postHeavyJob(CIM_WIZARD_URLS.MAP_TO_CITYDB, payload, onProgress);
}

export async function healthCheck(): Promise<{ status: string; service?: string }> {
  const resp = await fetch(CIM_WIZARD_URLS.HEALTH);
  return handleResponse<{ status: string; service?: string }>(resp);
}

export const cimWizardConfig = {
  base: CIM_WIZARD_BASE,
  endpoints: CIM_WIZARD_URLS,
};

