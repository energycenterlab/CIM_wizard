import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import routes from "../../constants/routes.json";

import ProjectPreview from "./ProjPreview";

const fakeProjData = [
  {
    name: "San Salvario",
    description:
      "Small thing that could be important like a brief description of the project we can ask for it during ",
    longitude: 7.681904520961282,
    latitude: 45.06113488000233,
    lastEdit: "20-05-2025",
    simulationRunning: true,
    initialProgress: 20,
  },
  {
    name: "Crocetta",
    description:
      "Small thing that could be important like a brief description of the project we can ask for it during ",
    longitude: 7.663589407221153,
    latitude: 45.05872290656662,
    lastEdit: "19-05-2025",
    simulationRunning: false,
    initialProgress: 0,
  },
  {
    name: "Vanchiglia",
    description:
      "Small thing that could be important like a brief description of the project we can ask for it during ",
    longitude: 7.699284274460377,
    latitude: 45.06731733747307,
    lastEdit: "18-05-2025",
    simulationRunning: false,
    initialProgress: 0,
  },
  {
    name: "Vanchiglia",
    description:
      "Small thing that could be important like a brief description of the project we can ask for it during ",
    longitude: 7.763589467221253,
    latitude: 45.06872291656762,
    lastEdit: "18-05-2025",
    simulationRunning: false,
    initialProgress: 0,
  },
  {
    name: "Vanchiglia",
    description:
      "Small thing that could be important like a brief description of the project we can ask for it during ",
    longitude: 7.699284274460377,
    latitude: 45.06731733747307,
    lastEdit: "18-05-2025",
    simulationRunning: false,
    initialProgress: 0,
  },
];

const OpenProjects: React.FC = () => {
  return (
    <div
      style={{
        width: "100%",
        display: "flex",
        flexDirection: "row",
        flexWrap: "wrap",
      }}
    >
      {fakeProjData.map((proj, index) => (
        <ProjectPreview
          key={index}
          name={proj.name}
          description={proj.description}
          longitude={proj.longitude}
          latitude={proj.latitude}
          lastEdit={proj.lastEdit}
          simulationRunning={proj.simulationRunning}
          initialProgress={proj.initialProgress}
        />
      ))}
    </div>
  );
};

export default OpenProjects;
