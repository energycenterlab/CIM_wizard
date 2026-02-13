export type SectionKey = 'simulation' | 'inputs' | 'outputs' | 'model';

export type FieldKind = 'number' | 'integer' | 'boolean' | 'datetime' | 'text' | 'enum';

export interface ParamField {
  key: string;
  label: string;
  section: SectionKey;
  kind: FieldKind;
  default: any;
  unit?: string;
  min?: number | 'none';
  max?: number | 'none';
  enum?: string[];
  description?: string;
}

export interface ModelSchema {
  modelDefId: string;
  description: string;
  fields: ParamField[];
}

export const modelRegistry: Record<string, ModelSchema> = {
  schedule: {
    modelDefId: 'schedule',
    description:
      'Schedule for the internal setpoint temperature for building energy simulation',
    fields: [
      { key: 'days', label: 'days', section: 'simulation', kind: 'datetime', default: '2025-01-01 00:00:00', unit: '-' },
      { key: 'Tset', label: 'Tset', section: 'outputs', kind: 'number', default: 16, unit: '°C', min: 0 },
      { key: 'schedule', label: 'schedule', section: 'model', kind: 'text', default: ['0:16','6:20','22:16'], unit: '-' },
    ],
  },
  weather: {
    modelDefId: 'weather',
    description: 'Timeseries of weather',
    fields: [
      { key: 'start_date', label: 'start_date', section: 'simulation', kind: 'datetime', default: '2025-01-01 00:00:00' },
      { key: 'stepsize', label: 'stepsize', section: 'simulation', kind: 'integer', default: 900, unit: 's' },
      { key: 'T_ext', label: 'T_ext', section: 'outputs', kind: 'number', default: 20, unit: '°C', min: 0 },
      { key: 'ghi', label: 'ghi', section: 'outputs', kind: 'number', default: 0, unit: 'W/m2', min: 0 },
    ],
  },
  powernode: {
    modelDefId: 'powernode',
    description: 'A meter node to calculate the electrical balance',
    fields: [
      { key: 'collect_data', label: 'collect_data', section: 'simulation', kind: 'boolean', default: false },
      { key: 'step_size', label: 'step_size', section: 'simulation', kind: 'integer', default: 600, unit: 's' },
      { key: 'NetBatt', label: 'NetBatt', section: 'inputs', kind: 'number', default: 100, unit: 'W', min: 0 },
      { key: 'Prod', label: 'Prod', section: 'inputs', kind: 'number', default: 100, unit: 'W', min: 0 },
      { key: 'Load', label: 'Load', section: 'inputs', kind: 'number', default: 100, unit: 'W', min: 0 },
      { key: 'Pnet', label: 'Pnet', section: 'outputs', kind: 'number', default: 0, unit: 'W' },
      { key: 'Pload', label: 'Pload', section: 'outputs', kind: 'number', default: 0, unit: 'W' },
      { key: 'Pnetbatt', label: 'Pnetbatt', section: 'outputs', kind: 'number', default: 0, unit: 'W' },
      { key: 'Pprod', label: 'Pprod', section: 'outputs', kind: 'number', default: 0, unit: 'W' },
    ],
  },
  battery: {
    modelDefId: 'battery',
    description: 'Battery simulator in FMU from Matlab/Simulink',
    fields: [
      { key: 'fmu_log', label: 'fmu_log', section: 'simulation', kind: 'integer', default: 0, min: 0, max: 7 },
      { key: 'step_size', label: 'step_size', section: 'simulation', kind: 'integer', default: 600, unit: 's', min: 60 },
      { key: 'LoadINW', label: 'LoadINW', section: 'inputs', kind: 'number', default: 0, unit: 'Watt', min: 0 },
      { key: 'GenINW', label: 'GenINW', section: 'inputs', kind: 'number', default: 0, unit: 'Watt', min: 0 },
      { key: 'PnetBatt', label: 'PnetBatt', section: 'outputs', kind: 'number', default: 0, unit: 'Watt' },
      { key: 'I', label: 'I', section: 'outputs', kind: 'number', default: 0, unit: 'Amper', min: 0 },
      { key: 'SOC', label: 'SOC', section: 'outputs', kind: 'number', default: 0, unit: '-', min: 0, max: 100 },
      { key: 'V', label: 'V', section: 'outputs', kind: 'number', default: 0, unit: 'Voltage', min: 0 },
      { key: 'SOCinit', label: 'SOCinit', section: 'model', kind: 'number', default: 50, min: 0, max: 100 },
      { key: 'fmu_name', label: 'fmu_name', section: 'model', kind: 'text', default: 'batterysystem' },
    ],
  },
  heatpump: {
    modelDefId: 'heatpump',
    description: 'Heat pump simulator in FMU from Modelica',
    fields: [
      { key: 'fmu_log', label: 'fmu_log', section: 'simulation', kind: 'integer', default: 0, min: 0, max: 7 },
      { key: 'step_size', label: 'step_size', section: 'simulation', kind: 'integer', default: 300, unit: 's', min: 60 },
      { key: 'TroomSens', label: 'TroomSens', section: 'inputs', kind: 'number', default: 15, unit: '°C' },
      { key: 'Tset', label: 'Tset', section: 'inputs', kind: 'number', default: 20, unit: '°C' },
      { key: 'Tamb', label: 'Tamb', section: 'inputs', kind: 'number', default: 0, unit: '°C' },
      { key: 'Qsensible', label: 'Qsensible', section: 'outputs', kind: 'number', default: 0, unit: 'Watt' },
      { key: 'Power', label: 'Power', section: 'outputs', kind: 'number', default: 0, unit: 'Watt' },
      { key: 'COP', label: 'COP', section: 'outputs', kind: 'number', default: 0, unit: '-' },
      { key: 'MV', label: 'MV', section: 'outputs', kind: 'number', default: 0, unit: '-' },
      { key: 'AW', label: 'AW', section: 'model', kind: 'number', default: 1.5, min: 1.5, max: 1.5 },
      { key: 'Td', label: 'Td', section: 'model', kind: 'number', default: 3000, unit: 'ms', min: 2800, max: 3000 },
      { key: 'Ti', label: 'Ti', section: 'model', kind: 'number', default: 1500, unit: 'ms', min: 2200, max: 2800 },
      { key: 'contr_type', label: 'contr_type', section: 'model', kind: 'enum', default: 'PID', enum: ['PID'] },
      { key: 'fmu_name', label: 'fmu_name', section: 'model', kind: 'text', default: 'HeatPump' },
      { key: 'k', label: 'k', section: 'model', kind: 'number', default: 0.003, min: 0.001, max: 0.008 },
    ],
  },
  pv: {
    modelDefId: 'pv',
    description: 'PV model based on pvsim',
    fields: [
      { key: 'start_date', label: 'start_date', section: 'simulation', kind: 'datetime', default: '2025-01-01 00:00:00' },
      { key: 'step_size', label: 'step_size', section: 'simulation', kind: 'integer', default: 900, unit: 's' },
      { key: 'ghi', label: 'ghi', section: 'inputs', kind: 'number', default: 100, unit: 'W/m2', min: 0 },
      { key: 'T_ext', label: 'T_ext', section: 'inputs', kind: 'number', default: 25, unit: '°C', min: 0 },
      { key: 'power_dc', label: 'power_dc', section: 'outputs', kind: 'number', default: 0, unit: 'W' },
      { key: 'P_system', label: 'P_system', section: 'model', kind: 'number', default: 5000, unit: 'W' },
      { key: 'slope', label: 'slope', section: 'model', kind: 'number', default: 35, unit: 'degrees' },
    ],
  },
  building: {
    modelDefId: 'building',
    description: 'Building envelope simulator in FMU from EnergyPlus',
    fields: [
      { key: 'fmu_log', label: 'fmu_log', section: 'simulation', kind: 'integer', default: 0, min: 0, max: 7 },
      { key: 'step_size', label: 'step_size', section: 'simulation', kind: 'integer', default: 600, unit: 's', min: 60 },
      { key: 'stop_time', label: 'stop_time', section: 'simulation', kind: 'integer', default: 31536000, unit: 's' },
      { key: 'Q', label: 'Q', section: 'inputs', kind: 'number', default: 0, unit: 'Watt' },
      { key: 'Peo', label: 'Peo', section: 'inputs', kind: 'number', default: 0, unit: '-' },
      { key: 'RH', label: 'RH', section: 'inputs', kind: 'number', default: 50, unit: '%' },
      { key: 'Tbulb', label: 'Tbulb', section: 'inputs', kind: 'number', default: 20, unit: '°C' },
      { key: 'Tdew', label: 'Tdew', section: 'inputs', kind: 'number', default: 20, unit: '°C' },
      { key: 'TRooMea', label: 'TRooMea', section: 'outputs', kind: 'number', default: 0, unit: '°C' },
      { key: 'Tamb', label: 'Tamb', section: 'outputs', kind: 'number', default: 0, unit: '°C' },
      { key: 'fmu_name', label: 'fmu_name', section: 'model', kind: 'text', default: 'building_tia' },
    ],
  },
};

const aliasMap: Record<string, string> = {
  PV: 'pv',
  Building: 'building',
  HeatPump: 'heatpump',
  Battery: 'battery',
};

export function normalizeModelId(raw: string): string {
  if (!raw) return '';
  return aliasMap[raw] || raw.toLowerCase();
}

export function getSchema(modelDefId: string): ModelSchema | undefined {
  return modelRegistry[normalizeModelId(modelDefId)];
}

export function getDefaultParams(modelDefId: string): Record<SectionKey, Record<string, any>> {
  const schema = getSchema(modelDefId);
  const result: Record<SectionKey, Record<string, any>> = {
    simulation: {},
    inputs: {},
    outputs: {},
    model: {},
  };
  if (!schema) return result;
  for (const field of schema.fields) {
    // For text arrays (e.g., schedule), default is copied as-is
    (result[field.section] as any)[field.key] = field.default;
  }
  return result;
}

export function listSections(): SectionKey[] {
  return ['simulation', 'inputs', 'outputs', 'model'];
}


