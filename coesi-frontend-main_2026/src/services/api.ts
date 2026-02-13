import { COESI_API_BASE, COESI_API_URLS, LEGACY_API_BASE } from '../config/apiConfig';

const API_BASE_URL = LEGACY_API_BASE;
export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  profile_photo?: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  longitude: number;
  latitude: number;
  user_id: number;
  simulation_running: boolean;
  initial_progress: number;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  role: string;
}

export interface ProjectCreateRequest {
  name: string;
  description: string;
  longitude: number;
  latitude: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface COESIModel {
  name: string;
  description: string;
  uri?: string;
  tags?: string[];
  solver?: string;
  model_execution_cmd?: string;
  simulator_names?: string[];
  model_type?: string; 
  type?: string; 
  simulation_parameters?: Array<{
    name: string;
    unit: string;
    value: any;
    description: string;
    tags: string[];
    data_type: string;
    range: {
      min: string;
      max: string;
    };
  }>;
  input_variables?: Array<{
    name: string;
    description: string;
    unit: string;
    start_value: any;
    data_type: string;
    hidden: boolean;
    range: {
      min: string;
      max: string;
    };
    tags: string[];
  }>;
  output_variables?: Array<{
    name: string;
    description: string;
    unit: string;
    start_value: any;
    data_type: string;
    hidden: boolean;
    range: {
      min: string;
      max: string;
    };
    tags: string[];
  }>;
  model_parameters?: Array<{
    name: string;
    description: string;
    unit: string;
    default_value: any;
    data_type: string;
    range: {
      min: string;
      max: string;
    };
    tags: string[];
  }>;
  possible_connections?: string[];
  components?: string[];
  connections?: string[];
}

export interface COESIModelResponse {
  models: COESIModel[];
  'composite-models': COESIModel[];
}

// Connection Validation Types
export interface ConnectionValidationRequest {
  source: string;
  target: string;
  from_port: string;
  to_port: string;
}

export interface ConnectionValidationResponse {
  valid: boolean;
  reasons: string[];
}

// API service class
class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    // Load token from localStorage on initialization
    this.token = localStorage.getItem('auth_token');
  }

  // Set authentication token
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  // Clear authentication token
  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  // Get headers for API requests
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Generic request method
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: this.getHeaders(),
    };

    try {
      if (!endpoint.includes('/api/auth/me')) {
        console.log('🌐 API Request:', { url, method: options.method || 'GET', endpoint });
      }
      
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('🌐 API Error Response:', { status: response.status, errorData, url });
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (!endpoint.includes('/api/auth/me')) {
        console.log('🌐 API Success:', { endpoint, resultType: typeof result });
      }
      
      return result;
    } catch (error) {
      console.error('🚨 API request failed:', {
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        url,
        endpoint,
        method: options.method || 'GET'
      });
      
      if (endpoint === '/api/auth/me' && (!options.method || options.method === 'GET')) {
        throw new Error('AUTH_ME_UNAVAILABLE');
      }
      throw error;
    }
  }

  // Authentication methods
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async register(userData: RegisterRequest): Promise<User> {
    try {
      return await this.request<User>('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      });
    } catch (error) {
      // Re-throw the error with the detail message
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Registration failed');
    }
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/auth/me');
  }

  async getProjects(): Promise<Project[]> {
    return this.request<Project[]>('/api/projects/');
  }

  async getProject(id: number): Promise<Project> {
    return this.request<Project>(`/api/projects/${id}`);
  }

  async createProject(projectData: ProjectCreateRequest): Promise<Project> {
    return this.request<Project>('/api/projects/', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
  }

  async updateProject(id: number, projectData: Partial<ProjectCreateRequest>): Promise<Project> {
    return this.request<Project>(`/api/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(projectData),
    });
  }

  async deleteProject(id: number): Promise<void> {
    return this.request<void>(`/api/projects/${id}`, {
      method: 'DELETE',
    });
  }

  async uploadProfilePhoto(file: File): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/users/me/photo`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to upload profile photo');
    }

    return response.json();
  }

  async deleteProfilePhoto(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/users/me/photo', {
      method: 'DELETE',
    });
  }

  async updateProfile(profileData: Partial<User>): Promise<User> {
    return this.request<User>('/api/users/me', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/users/me/change-password', {
      method: 'POST',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.token;
  }

  // Logout
  logout() {
    this.clearToken();
  }

  // COESI Model Manager API methods
  async getCOESIModels(details: boolean = false): Promise<COESIModelResponse> {
    const url = `${COESI_API_URLS.MODEL_MANAGER}?details=${details}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch COESI models: ${response.statusText}`);
    }
    
    return response.json();
  }

  async getCOESIModel(modelName: string): Promise<COESIModel> {
    // Use path-based endpoint: /api/v1/models/{modelName}
    const url = `${COESI_API_URLS.MODEL_MANAGER}/${encodeURIComponent(modelName)}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch COESI model: ${response.statusText}`);
    }
    
    const model = await response.json();
    
    if (model.models && Array.isArray(model.models) && model.models.length > 0) {
      return model.models[0];
    }
    
    return model;
  }

  async addCOESIModel(modelData: any): Promise<{ status: string; message: string; model_name: string }> {
    const url = `${COESI_API_URLS.MODEL_MANAGER}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(modelData),
    });

    let json: any = null;
    try { json = await response.json(); } catch {}

    if (!response.ok) {
      const detail = json?.detail || response.statusText;
      throw new Error(detail);
    }

    return json as { status: string; message: string; model_name: string };
  }

  async deleteCOESIModel(modelName: string): Promise<void> {
    const url = `${COESI_API_URLS.MODEL_MANAGER}/${modelName}`;
    const response = await fetch(url, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete COESI model: ${response.statusText}`);
    }
  }

  // Health check for COESI services
  async checkCOESIServiceHealth(): Promise<{ [key: string]: boolean }> {
    const services = {
      modelManager: false,
      validationEngine: false,
      scenarioManager: false,
      graphDB: false,
      gateway: false
    };

    //gateway health
    try {
      const gatewayResponse = await fetch(`${COESI_API_BASE}/health`);
      services.gateway = gatewayResponse.ok;
    } catch (e) {
      services.gateway = false;
    }

    try {
      const modelManagerResponse = await fetch(`${COESI_API_URLS.MODEL_MANAGER}`);
      services.modelManager = modelManagerResponse.ok;
    } catch (e) {
      services.modelManager = false;
    }

    try {
      const validationResponse = await fetch(`${COESI_API_URLS.VALIDATION_ENGINE}`);
      services.validationEngine = validationResponse.ok;
    } catch (e) {
      services.validationEngine = false;
    }

    try {
      const scenarioResponse = await fetch(`${COESI_API_URLS.SCENARIO_MANAGER}`);
      services.scenarioManager = scenarioResponse.ok;
    } catch (e) {
      services.scenarioManager = false;
    }

    try {
      const graphDBResponse = await fetch(`${COESI_API_URLS.GRAPHDB}`);
      services.graphDB = graphDBResponse.ok;
    } catch (e) {
      services.graphDB = false;
    }

    return services;
  }

  // Connection Validation
  async validateConnection(
    source: string,
    target: string,
    fromPort: string,
    toPort: string,
    opts?: { fromUnit?: string; toUnit?: string }
  ): Promise<ConnectionValidationResponse> {
    // Build query parameters
    const qp = new URLSearchParams({
      source,
      target,
      from_port: fromPort,
      to_port: toPort,
    });
    if (opts?.fromUnit) qp.append('from_unit', opts.fromUnit);
    if (opts?.toUnit) qp.append('to_unit', opts.toUnit);
    
    //port-connections with POST method
    const url = `${COESI_API_URLS.VALIDATION_ENGINE}/port-connections?${qp.toString()}`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorDetail = errorText;
        try {
          const errorJson = JSON.parse(errorText);
          errorDetail = errorJson.detail || errorJson.message || errorText;
        } catch {
        }
        throw new Error(`Validation failed: ${errorDetail} (${response.status})`);
      }
      
      const result = await response.json();
      
      // Ensure response has valid structure
      if (typeof result.valid !== 'boolean') {
        throw new Error('Invalid validation response: missing valid field');
      }
      
      return result;
    } catch (error) {
      console.error('Connection validation error:', error);
      throw error;
    }
  }

  // Scenario Manager API methods
  async uploadScenarioYAML(yamlContent: string, filename: string): Promise<{ success: boolean; filename: string; message: string }> {
    const formData = new FormData();
    const blob = new Blob([yamlContent], { type: 'text/yaml;charset=utf-8' });
    formData.append('file', blob, filename);

    const response = await fetch(`${COESI_API_URLS.SCENARIO_MANAGER}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to upload scenario: ${response.statusText}`);
    }

    return response.json();
  }

  async getScenario(scenarioName: string): Promise<any> {
    const response = await fetch(`${COESI_API_URLS.SCENARIO_MANAGER}/${scenarioName}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch scenario: ${response.statusText}`);
    }
    
    return response.json();
  }

  // Simulation Core API methods
  async startSimulation(scenarioName: string, options?: {
    log_level?: string;
    lazy_stepping?: boolean;
    webdash?: boolean;
    realtime?: boolean;
  }): Promise<{ simulation_id: string; status: string; message: string; created_at: string; scenario_name: string }> {
    const response = await fetch(COESI_API_URLS.SIMULATIONS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        scenario_name: scenarioName,
        log_level: options?.log_level || 'INFO',
        lazy_stepping: options?.lazy_stepping || false,
        webdash: options?.webdash || false,
        realtime: options?.realtime || false,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to start simulation: ${response.statusText}`);
    }

    return response.json();
  }

  async getSimulationStatus(simulationId: string): Promise<{
    simulation_id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    created_at: string;
    started_at?: string;
    completed_at?: string;
    execution_time?: number;
    error_message?: string;
  }> {
    const response = await fetch(`${COESI_API_URLS.SIMULATIONS}/${simulationId}/status`);

    if (!response.ok) {
      throw new Error(`Failed to get simulation status: ${response.statusText}`);
    }

    return response.json();
  }

  async getSimulationResults(simulationId: string): Promise<{
    hdf5_files: Array<{
      name: string;
      path: string;
      size: string;
      modified: number;
      scenario_name: string;
    }>;
    total_files: number;
    outputs_folder: string;
  }> {
    const response = await fetch(`${COESI_API_URLS.SIMULATIONS}/${simulationId}/results/files`);

    if (!response.ok) {
      throw new Error(`Failed to get simulation results: ${response.statusText}`);
    }

    return response.json();
  }

  async stopSimulation(simulationId: string): Promise<{ message: string; simulation_id: string; status: string }> {
    const response = await fetch(`${COESI_API_URLS.SIMULATIONS}/${simulationId}/stop`, {
      method: 'POST',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to stop simulation: ${response.statusText}`);
    }

    return response.json();
  }

  // Get all simulations
  async getAllSimulations(): Promise<Array<{
    simulation_id: string;
    status: "pending" | "running" | "completed" | "failed";
    scenario_name: string;
    created_at: string;
    started_at?: string;
    completed_at?: string;
    execution_time?: number;
    duration?: number;
    error_message?: string;
  }>> {
    const response = await fetch(COESI_API_URLS.SIMULATIONS);

    if (!response.ok) {
      throw new Error(`Failed to get simulations: ${response.statusText}`);
    }

    return response.json();
  }

  // Get HDF5 file info
  async getSimulationFileInfo(simulationId: string, filename: string): Promise<{
    groups: { [key: string]: any };
    attributes: { [key: string]: any };
  }> {
    const response = await fetch(`${COESI_API_URLS.SIMULATIONS}/${simulationId}/results/files/${filename}/info`);

    if (!response.ok) {
      throw new Error(`Failed to get file info: ${response.statusText}`);
    }

    return response.json();
  }

  // Get HDF5 file data
  async getSimulationFileData(simulationId: string, filename: string, datasets: string): Promise<any> {
    const url = `${COESI_API_URLS.SIMULATIONS}/${simulationId}/results/files/${filename}?datasets=${encodeURIComponent(datasets)}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to get file data: ${response.statusText}`);
    }

    return response.json();
  }

  // Delete simulation
  async deleteSimulation(simulationId: string): Promise<void> {
    const response = await fetch(`${COESI_API_URLS.SIMULATIONS}/${simulationId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to delete simulation: ${response.statusText}`);
    }
  }
}

export const apiService = new ApiService(API_BASE_URL);

// Export COESI_API_BASE for use in components
export { COESI_API_BASE as getCoesiApiBase };
