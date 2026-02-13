export interface NodeModel {
  name: string;
  inputs: string[];
  outputs: string[];
}

export const NODE_MODELS: NodeModel[] = [
  {
    name: "schedule",
    inputs: ["input1", "input2"],
    outputs: ["Tset"],
  },
  {
    name: "weather",
    inputs: ["input1", "input2"],
    outputs: ["T_ext", "ghi"],
  },
  {
    name: "powernode",
    inputs: ["NetBatt", "Prod", "Load"],
    outputs: ["Pnet", "Pload", "Pnetbatt", "Pprod"],
  },
  {
    name: "PV",
    inputs: ["ghi", "T_ext"],
    outputs: ["power_dc"],
  },
  {
    name: "Building",
    inputs: ["Q", "Peo", "RH", "Tbulb", "Tdew"],
    outputs: ["TRooMea", "Tamb"],
  },
  {
    name: "HeatPump",
    inputs: ["TroomSens", "Tset", "Tamb"],
    outputs: ["Qsensible", "Power", "COP", "MV"],
  },
  {
    name: "Battery",
    inputs: ["LoadINW", "GenINW"],
    outputs: ["PnetBatt", "I", "SOC", "V"],
  },
];















