import { apiService, COESIModel, COESIModelResponse } from './api';

// Service for managing COESI models
export class COESIModelService {
  private static instance: COESIModelService;
  private cache: { models: COESIModelResponse | null; timestamp: number } = { models: null, timestamp: 0 };
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  static getInstance(): COESIModelService {
    if (!COESIModelService.instance) {
      COESIModelService.instance = new COESIModelService();
    }
    return COESIModelService.instance;
  }

  // Get all models from COESI backend
  async getModels(useCache: boolean = true): Promise<COESIModelResponse> {
    const now = Date.now();
    
    // Return cached data if still valid
    if (useCache && this.cache.models && (now - this.cache.timestamp) < this.CACHE_DURATION) {
      return this.cache.models;
    }

    try {
      const models = await apiService.getCOESIModels(true); // Get detailed models
      this.cache.models = models;
      this.cache.timestamp = now;
      return models;
    } catch (error) {
      console.error('Failed to fetch COESI models:', error);
      // Return empty response if backend is not available
      return { models: [], 'composite-models': [] };
    }
  }

  // Get a specific model by name
  async getModel(modelName: string): Promise<COESIModel | null> {
    try {
      return await apiService.getCOESIModel(modelName);
    } catch (error) {
      console.error(`Failed to fetch model ${modelName}:`, error);
      return null;
    }
  }

  // Add a new model to COESI backend
  async addModel(modelData: any): Promise<{ success: boolean; message: string }> {
    try {
      const result = await apiService.addCOESIModel(modelData);
      // Clear cache to force refresh
      this.cache.models = null;
      this.cache.timestamp = 0;
      return { success: true, message: result.message };
    } catch (error) {
      console.error('Failed to add model:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Unknown error' };
    }
  }

  // Delete a model from COESI backend
  async deleteModel(modelName: string): Promise<{ success: boolean; message: string }> {
    try {
      await apiService.deleteCOESIModel(modelName);
      // Clear cache to force refresh
      this.cache.models = null;
      this.cache.timestamp = 0;
      return { success: true, message: `Model ${modelName} deleted successfully` };
    } catch (error) {
      console.error(`Failed to delete model ${modelName}:`, error);
      return { success: false, message: error instanceof Error ? error.message : 'Unknown error' };
    }
  }

  // Check if COESI services are available
  async checkHealth(): Promise<{ [key: string]: boolean }> {
    return await apiService.checkCOESIServiceHealth();
  }

  // Clear cache
  clearCache(): void {
    this.cache.models = null;
    this.cache.timestamp = 0;
  }

  // Convert COESI model to your frontend's ModelJson format
  convertToModelJson(coesiModel: COESIModel): any {
    return {
      name: coesiModel.name,
      description: coesiModel.description,
      tags: coesiModel.tags || [],
      solver: coesiModel.solver,
      model_execution_cmd: coesiModel.model_execution_cmd,
      simulator_names: coesiModel.simulator_names || [],
      simulation_parameters: this.convertSimulationParameters(coesiModel.simulation_parameters || []),
      input_variables: this.convertVariables(coesiModel.input_variables || []),
      output_variables: this.convertVariables(coesiModel.output_variables || []),
      model_parameters: this.convertModelParameters(coesiModel.model_parameters || []),
      possible_connections: coesiModel.possible_connections || [],
      components: coesiModel.components || [],
      connections: coesiModel.connections || [],
      ui_schema: {
        icon: this.getIconForModel(coesiModel),
        color: this.getColorForModel(coesiModel),
        portSides: { inputs: 'left', outputs: 'right' }
      }
    };
  }

  // Convert simulation parameters from COESI format to frontend format
  private convertSimulationParameters(params: any[]): any[] {
    return params.map(param => ({
      name: param.name,
      data_type: param.data_type,
      value: param.value,
      unit: param.unit || '-',
      description: param.description || '',
      range: param.range || { min: 'none', max: 'none' }
    }));
  }

  // Convert variables (input/output) from COESI format to frontend format
  private convertVariables(variables: any[]): any[] {
    return variables.map(variable => ({
      name: variable.name,
      data_type: variable.data_type,
      start_value: variable.start_value,
      unit: variable.unit || '-',
      description: variable.description || '',
      range: variable.range || { min: 'none', max: 'none' },
      hidden: variable.hidden || false
    }));
  }

  // Convert model parameters from COESI format to frontend format
  private convertModelParameters(params: any[]): any[] {
    return params.map(param => ({
      name: param.name,
      data_type: param.data_type,
      default_value: param.default_value,
      unit: param.unit || '-',
      description: param.description || '',
      range: param.range || { min: 'none', max: 'none' }
    }));
  }

  // Helper method to get appropriate icon for model type
  private getIconForModel(model: COESIModel): string {
    const name = model.name.toLowerCase();
    if (name.includes('building')) return 'home';
    if (name.includes('weather')) return 'cloud';
    if (name.includes('schedule')) return 'cube';
    if (name.includes('battery')) return 'battery';
    if (name.includes('heat') || name.includes('pump')) return 'thermometer';
    if (name.includes('pv') || name.includes('solar')) return 'sun';
    if (name.includes('power')) return 'zap';
    return 'cube';
  }

  // Helper method to get appropriate color for model type
  private getColorForModel(model: COESIModel): string {
    const name = model.name.toLowerCase();
    if (name.includes('building')) return '#EFF6FF';
    if (name.includes('weather')) return '#E6F4FF';
    if (name.includes('schedule')) return '#F4F4F4';
    if (name.includes('battery')) return '#F0FDF4';
    if (name.includes('heat') || name.includes('pump')) return '#FEF2F2';
    if (name.includes('pv') || name.includes('solar')) return '#FFFBEB';
    if (name.includes('power')) return '#F3E8FF';
    return '#F4F4F4';
  }
}

// Export singleton instance
export const coesiModelService = COESIModelService.getInstance();
