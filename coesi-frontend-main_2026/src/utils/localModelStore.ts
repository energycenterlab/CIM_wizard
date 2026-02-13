export type ParamItem = {
  name: string;
  data_type: string;
  unit?: string;
  min?: number | 'none' | string;
  max?: number | 'none' | string;
  value?: any; // simulation
  default_value?: any; // model
  start_value?: any; // inputs/outputs
};

export type ModelJson = {
  name: string;
  description: string;
  tags: string[];
  simulation_parameters: ParamItem[];
  input_variables: ParamItem[];
  output_variables: ParamItem[];
  model_parameters: ParamItem[];
  possible_connections?: string[];
  simulator_names?: string[];
  ui_schema?: {
    icon?: string;
    color?: string;
    portSides?: { inputs: 'left' | 'right'; outputs: 'left' | 'right' };
  };
};

const keyFor = (projectId: string) => `coesi.models.${projectId}`;

export function loadModels(projectId: string): ModelJson[] {
  try {
    const raw = localStorage.getItem(keyFor(projectId));
    if (!raw) return [];
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

export function saveModels(projectId: string, models: ModelJson[]): void {
  localStorage.setItem(keyFor(projectId), JSON.stringify(models));
}

export function upsertModel(projectId: string, model: ModelJson): { replaced: boolean } {
  const list = loadModels(projectId);
  const idx = list.findIndex((m) => m.name === model.name);
  if (idx >= 0) {
    list[idx] = withUiDefaults(model);
    saveModels(projectId, list);
    return { replaced: true };
  }
  list.push(withUiDefaults(model));
  saveModels(projectId, list);
  return { replaced: false };
}

export function removeModel(projectId: string, name: string): boolean {
  const list = loadModels(projectId);
  const idx = list.findIndex((m) => m.name === name);
  if (idx === -1) return false;
  list.splice(idx, 1);
  saveModels(projectId, list);
  return true;
}

export function modelExists(projectId: string, name: string): boolean {
  return loadModels(projectId).some((m) => m.name === name);
}

export function getCustomModelByName(projectId: string, name: string): ModelJson | undefined {
  return loadModels(projectId).find((m) => m.name === name);
}

export function withUiDefaults(model: ModelJson): ModelJson {
  return {
    ...model,
    ui_schema: {
      icon: model.ui_schema?.icon ?? 'cube',
      color: model.ui_schema?.color ?? '#F4F4F4',
      portSides: model.ui_schema?.portSides ?? { inputs: 'left', outputs: 'right' },
    },
  };
}

export type ValidationResult = { valid: true; parsed: ModelJson } | { valid: false; message: string };

export function validateModelJson(obj: any): ValidationResult {
  try {
    if (!obj || typeof obj !== 'object') return { valid: false, message: 'Root must be an object' };
    const required = [
      'name',
      'description',
      'tags',
      'simulation_parameters',
      'input_variables',
      'output_variables',
      'model_parameters',
    ];
    for (const f of required) {
      if (!(f in obj)) return { valid: false, message: `Missing required field: ${f}` };
    }
    if (typeof obj.name !== 'string' || obj.name.trim() === '') return { valid: false, message: 'name must be a non-empty string' };
    if (typeof obj.description !== 'string') return { valid: false, message: 'description must be a string' };
    if (!Array.isArray(obj.tags)) return { valid: false, message: 'tags must be an array' };
    const arrays = ['simulation_parameters', 'input_variables', 'output_variables', 'model_parameters'];
    for (const k of arrays) {
      if (!Array.isArray(obj[k])) return { valid: false, message: `${k} must be an array` };
      for (const item of obj[k]) {
        if (typeof item?.name !== 'string') return { valid: false, message: `${k} items require name:string` };
        if (typeof item?.data_type !== 'string') return { valid: false, message: `${k} items require data_type:string` };
        if (!('value' in item || 'default_value' in item || 'start_value' in item)) {
          return { valid: false, message: `${k}.${item.name} requires value/default_value/start_value` };
        }
      }
    }
    return { valid: true, parsed: withUiDefaults(obj as ModelJson) };
  } catch (e: any) {
    return { valid: false, message: e?.message || 'Unknown error' };
  }
}

export function buildPreview(model: ModelJson) {
  return {
    name: model.name,
    description: model.description,
    simulationCount: model.simulation_parameters.length,
    inputCount: model.input_variables.length,
    outputCount: model.output_variables.length,
    modelParamCount: model.model_parameters.length,
    possible: model.possible_connections,
  };
}

// Helpers to convert JSON model into editor schema/defaults
import { ModelSchema, ParamField, SectionKey } from '../components/NodeDnD/modelRegistry';

const mapType = (t: string): ParamField['kind'] => {
  const k = String(t || '').toLowerCase();
  if (k === 'int' || k === 'integer') return 'integer';
  if (k === 'number' || k === 'float' || k === 'double') return 'number';
  if (k === 'bool' || k === 'boolean') return 'boolean';
  if (k === 'datetime' || k === 'date' || k === 'timestamp') return 'datetime';
  if (k === 'enum') return 'enum';
  return 'text';
};

export function convertModelJsonToSchema(model: ModelJson): ModelSchema {
  const fields: ParamField[] = [];
  const push = (section: SectionKey, arr: ParamItem[], valueKey: 'value' | 'default_value' | 'start_value') => {
    for (const it of arr) {
      fields.push({
        key: it.name,
        label: it.name,
        section,
        kind: mapType(it.data_type),
        default: (it as any)[valueKey],
        unit: it.unit,
        min: normalizeBound(it.min),
        max: normalizeBound(it.max),
      });
    }
  };
  push('simulation', model.simulation_parameters || [], 'value');
  push('inputs', model.input_variables || [], 'start_value');
  push('outputs', model.output_variables || [], 'start_value');
  push('model', model.model_parameters || [], 'default_value');
  return { modelDefId: model.name.toLowerCase(), description: model.description, fields };
}

export function defaultsFromModelJson(model: ModelJson) {
  const sections: Record<SectionKey, Record<string, any>> = {
    simulation: {},
    inputs: {},
    outputs: {},
    model: {},
  };
  for (const it of model.simulation_parameters || []) sections.simulation[it.name] = it.value;
  for (const it of model.input_variables || []) sections.inputs[it.name] = it.start_value;
  for (const it of model.output_variables || []) sections.outputs[it.name] = it.start_value;
  for (const it of model.model_parameters || []) sections.model[it.name] = it.default_value;
  return sections;
}

function normalizeBound(b?: number | 'none' | string) {
  if (b === undefined) return undefined;
  if (b === 'none') return 'none';
  if (typeof b === 'string' && b.toLowerCase() === 'none') return 'none';
  const n = Number(String(b).replace(',', '.'));
  return isNaN(n) ? undefined : n;
}


