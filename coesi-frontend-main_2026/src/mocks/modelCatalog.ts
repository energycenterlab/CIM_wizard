// MOCK: replace with backend fetch later
import type { ModelJson } from '../utils/localModelStore';

export type CatalogModel = ModelJson & { mock: true };

export const modelCatalog: CatalogModel[] = [
  {
    name: 'schedule',
    description: 'Schedule for the internal setpoint temperature for building energy simulation',
    tags: ['schedule','setpoint'],
    simulation_parameters: [
      { name: 'days', data_type: 'datetime', value: '2025-01-01 00:00:00', unit: '-' },
    ],
    input_variables: [],
    output_variables: [
      { name: 'Tset', data_type: 'number', start_value: 16, unit: '°C' },
    ],
    model_parameters: [
      { name: 'schedule', data_type: 'text', default_value: [ '0:16','6:20','22:16' ], unit: '-' },
    ],
    possible_connections: ['building','heat_pump','pv','battery','powernode','weather'],
    simulator_names: ['local-sim'],
    ui_schema: { icon: 'cube', color: '#F4F4F4', portSides: { inputs: 'left', outputs: 'right' } },
    mock: true,
  },
  {
    name: 'weather',
    description: 'Timeseries of weather',
    tags: ['weather','timeseries'],
    simulation_parameters: [
      { name: 'start_date', data_type: 'datetime', value: '2025-01-01 00:00:00' },
      { name: 'stepsize', data_type: 'integer', value: 900, unit: 's' },
    ],
    input_variables: [],
    output_variables: [
      { name: 'T_ext', data_type: 'number', start_value: 20, unit: '°C' },
      { name: 'ghi', data_type: 'number', start_value: 0, unit: 'W/m2' },
    ],
    model_parameters: [],
    possible_connections: ['pv','building','powernode'],
    simulator_names: ['local-sim'],
    ui_schema: { icon: 'cloud', color: '#E6F4FF', portSides: { inputs: 'left', outputs: 'right' } },
    mock: true,
  },
  {
    name: 'powernode',
    description: 'A meter node to calculate the electrical balance',
    tags: ['power','meter'],
    simulation_parameters: [
      { name: 'collect_data', data_type: 'boolean', value: false },
      { name: 'step_size', data_type: 'integer', value: 600, unit: 's' },
    ],
    input_variables: [
      { name: 'NetBatt', data_type: 'number', start_value: 100, unit: 'W' },
      { name: 'Prod', data_type: 'number', start_value: 100, unit: 'W' },
      { name: 'Load', data_type: 'number', start_value: 100, unit: 'W' },
    ],
    output_variables: [
      { name: 'Pnet', data_type: 'number', start_value: 0, unit: 'W' },
      { name: 'Pload', data_type: 'number', start_value: 0, unit: 'W' },
      { name: 'Pnetbatt', data_type: 'number', start_value: 0, unit: 'W' },
      { name: 'Pprod', data_type: 'number', start_value: 0, unit: 'W' },
    ],
    model_parameters: [],
    possible_connections: ['pv','battery','building'],
    simulator_names: ['local-sim'],
    ui_schema: { icon: 'gauge', color: '#FFF7E6', portSides: { inputs: 'left', outputs: 'right' } },
    mock: true,
  },
  {
    name: 'Battery',
    description: 'Battery simulator in FMU from Matlab/Simulink',
    tags: ['battery','storage'],
    simulation_parameters: [
      { name: 'fmu_log', data_type: 'integer', value: 0 },
      { name: 'step_size', data_type: 'integer', value: 600, unit: 's' },
    ],
    input_variables: [
      { name: 'LoadINW', data_type: 'number', start_value: 0, unit: 'Watt' },
      { name: 'GenINW', data_type: 'number', start_value: 0, unit: 'Watt' },
    ],
    output_variables: [
      { name: 'PnetBatt', data_type: 'number', start_value: 0, unit: 'Watt' },
      { name: 'I', data_type: 'number', start_value: 0, unit: 'Amper' },
      { name: 'SOC', data_type: 'number', start_value: 0, unit: '-', min: 0, max: 100 },
      { name: 'V', data_type: 'number', start_value: 0, unit: 'Voltage' },
    ],
    model_parameters: [
      { name: 'SOCinit', data_type: 'number', default_value: 50, unit: '-', min: 0, max: 100 },
      { name: 'fmu_name', data_type: 'text', default_value: 'batterysystem' },
    ],
    possible_connections: ['powernode'],
    simulator_names: ['FMU'],
    ui_schema: { icon: 'battery', color: '#F0FFF4', portSides: { inputs: 'left', outputs: 'right' } },
    mock: true,
  },
  {
    name: 'HeatPump',
    description: 'Heat pump simulator in FMU from Modelica',
    tags: ['heat','pump'],
    simulation_parameters: [
      { name: 'fmu_log', data_type: 'integer', value: 0 },
      { name: 'step_size', data_type: 'integer', value: 300, unit: 's' },
    ],
    input_variables: [
      { name: 'TroomSens', data_type: 'number', start_value: 15, unit: '°C' },
      { name: 'Tset', data_type: 'number', start_value: 20, unit: '°C' },
      { name: 'Tamb', data_type: 'number', start_value: 0, unit: '°C' },
    ],
    output_variables: [
      { name: 'Qsensible', data_type: 'number', start_value: 0, unit: 'Watt' },
      { name: 'Power', data_type: 'number', start_value: 0, unit: 'Watt' },
      { name: 'COP', data_type: 'number', start_value: 0, unit: '-' },
      { name: 'MV', data_type: 'number', start_value: 0, unit: '-' },
    ],
    model_parameters: [
      { name: 'AW', data_type: 'number', default_value: 1.5, min: 1.5, max: 1.5 },
      { name: 'Td', data_type: 'number', default_value: 3000, unit: 'ms', min: 2800, max: 3000 },
      { name: 'Ti', data_type: 'number', default_value: 1500, unit: 'ms', min: 2200, max: 2800 },
      { name: 'contr_type', data_type: 'enum', default_value: 'PID' },
      { name: 'fmu_name', data_type: 'text', default_value: 'HeatPump' },
      { name: 'k', data_type: 'number', default_value: 0.003, min: 0.001, max: 0.008 },
    ],
    possible_connections: ['building','powernode'],
    simulator_names: ['FMU'],
    ui_schema: { icon: 'heat', color: '#FFF0F0', portSides: { inputs: 'left', outputs: 'right' } },
    mock: true,
  },
  {
    name: 'PV',
    description: 'PV model based on pvsim',
    tags: ['pv','solar'],
    simulation_parameters: [
      { name: 'start_date', data_type: 'datetime', value: '2025-01-01 00:00:00' },
      { name: 'step_size', data_type: 'integer', value: 900, unit: 's' },
    ],
    input_variables: [
      { name: 'ghi', data_type: 'number', start_value: 100, unit: 'W/m2' },
      { name: 'T_ext', data_type: 'number', start_value: 25, unit: '°C' },
    ],
    output_variables: [
      { name: 'power_dc', data_type: 'number', start_value: 0, unit: 'W' },
    ],
    model_parameters: [
      { name: 'P_system', data_type: 'number', default_value: 5000, unit: 'W' },
      { name: 'slope', data_type: 'number', default_value: 35, unit: 'degrees' },
    ],
    possible_connections: ['powernode'],
    simulator_names: ['pvsim'],
    ui_schema: { icon: 'sun', color: '#FFFBEA', portSides: { inputs: 'left', outputs: 'right' } },
    mock: true,
  },
  {
    name: 'Building',
    description: 'Building envelope simulator in FMU from EnergyPlus',
    tags: ['building','envelope'],
    simulation_parameters: [
      { name: 'fmu_log', data_type: 'integer', value: 0 },
      { name: 'step_size', data_type: 'integer', value: 600, unit: 's' },
      { name: 'stop_time', data_type: 'integer', value: 31536000, unit: 's' },
    ],
    input_variables: [
      { name: 'Q', data_type: 'number', start_value: 0, unit: 'Watt' },
      { name: 'Peo', data_type: 'number', start_value: 0, unit: '-' },
      { name: 'RH', data_type: 'number', start_value: 50, unit: '%' },
      { name: 'Tbulb', data_type: 'number', start_value: 20, unit: '°C' },
      { name: 'Tdew', data_type: 'number', start_value: 20, unit: '°C' },
    ],
    output_variables: [
      { name: 'TRooMea', data_type: 'number', start_value: 0, unit: '°C' },
      { name: 'Tamb', data_type: 'number', start_value: 0, unit: '°C' },
    ],
    model_parameters: [
      { name: 'fmu_name', data_type: 'text', default_value: 'building_tia' },
    ],
    possible_connections: ['heat_pump','weather','powernode'],
    simulator_names: ['FMU'],
    ui_schema: { icon: 'home', color: '#EFF6FF', portSides: { inputs: 'left', outputs: 'right' } },
    mock: true,
  },
];


