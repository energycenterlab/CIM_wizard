import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

import HeaderProjects from "../components/headers/headerProjects";
import routes from "../constants/routes.json";

import ScePreviewFake from "../components/Scenarios/ScePreviewfake";
import NewScenarioCard from "../components/Scenarios/NewSce";
import NewScenarioModal from "../components/Scenarios/NewSceForm";

const fakeSceData = [
  {
    name: "baseline",
    description:
      "Small thing that could be important like a brief description of the project we can ask for it during ",
    longitude: 7.681904520961282,
    latitude: 45.06113488000233,
    lastEdit: "19-05-2025",
    simulationRunning: false,
    initialProgress: 0,
  },
];

const SansaFakepage = () => {
  const drawerRef = useRef<HTMLDivElement | null>(null);
  const [isDrawerOpen, setDrawerOpen] = useState(false);

  const projectInfo = "projectDemo==id1234"; //should come from useParam
  const userInfo = "userid"; //also should come from useParam
  const [projname, projectId] = projectInfo.split("==");
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        isDrawerOpen &&
        drawerRef.current &&
        !drawerRef.current.contains(event.target as Node)
      ) {
        setDrawerOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isDrawerOpen]);

  return (
    <div className="pagecontainer">
      <HeaderProjects />
      <div
        className="mainbody"
        style={{ display: "flex", width: "100%", overflow: "hidden" }}
      >
        <div
          className="main-content"
          style={{
            width: isDrawerOpen ? "65%" : "100%",
            transition: "width 0.3s ease",
          }}
        >
          <div
            style={{
              width: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              overflowY: "auto",
            }}
          >
            <h2 style={{ padding: "0 24px" }}>
              <img
                src="/icons/ArrowBack.svg"
                alt="Back"
                style={{ width: 20, height: 20, cursor: "pointer" }}
                onClick={() => navigate(`${routes.PROJECTSDEMO}`)}
              />
              {`   `}SanSalvario
            </h2>
            <div
              style={{
                width: "100%",
                display: "flex",
                flexDirection: "row",
                flexGrow: 1,
                alignContent: "flex-start",
                flexWrap: "wrap",
              }}
            >
              <NewScenarioCard onClick={() => setDrawerOpen(true)} />
              {fakeSceData.map((sce, index) => (
                <ScePreviewFake
                  key={index}
                  name={sce.name}
                  id={sce.name}
                  description={sce.description}
                  longitude={sce.longitude}
                  latitude={sce.latitude}
                  lastEdit={sce.lastEdit}
                  simulationRunning={sce.simulationRunning}
                  initialProgress={sce.initialProgress}
                />
              ))}
            </div>
          </div>
        </div>
        {isDrawerOpen && (
          <div
            className="drawer"
            ref={drawerRef}
            style={{
              width: "35%",
              padding: "20px",
              borderLeft: "1px solid #cccccc",
              transition: "width 0.3s ease",
              overflowY: "auto",
            }}
          >
            <NewScenarioModal projectName={projname} />
          </div>
        )}
      </div>
    </div>
  );
};

export default SansaFakepage;
