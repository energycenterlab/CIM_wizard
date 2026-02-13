import React from "react";

const ModelList: React.FC = () => {
  return (
    <div style={{ 
      width: "100%", 
      height: "100%", 
      padding: "20px",
      fontFamily: "monospace",
      fontSize: "14px",
      lineHeight: "1.6",
      backgroundColor: "#f5f5f5"
    }}>
      <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
{`schedule
inputs:
input1, input2
output:
Tset

weather
inputs:
input1
input2
output:
T_ext
ghi

powernode
inputs: 
NetBatt
Prod
Load
outputs:
Pnet
Pload
Pnetbatt
Pprod

PV
inputs:
ghi
T_ext
Outputs:
power_dc

Building
Inputs:
Q
Peo
RH
Tbulb
Tdew
Outputs:
TRooMea
Tamb

HeatPump
inputs:
TroomSens
Tset
Tamb
outputs:
Qsensible
Power
COP
MV

Battery
Inputs
LoadINW
GenINW
Outputs:
PnetBatt
I
SOC
V`}
      </pre>
    </div>
  );
};

export default ModelList;


