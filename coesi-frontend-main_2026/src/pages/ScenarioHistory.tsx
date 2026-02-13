import React from "react";
import { useNavigate } from "react-router-dom";
import HeaderProjects from "../components/headers/headerProjects";
import routes from "../constants/routes.json";
import "./GeneralPage.css";

const ScenarioHistoryPage = () => {
  const navigate = useNavigate();
  const projectInfo = "projectDemo==id1234"; // should come from useParam
  const [projname] = projectInfo.split("==");

  return (
    <div className="project-container">
      <HeaderProjects useScenarioMenu={true} />
      <div className="project-body">
        <div
          className="project-content"
          style={{
            width: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-start",
            height: "100%",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              overflowY: "auto",
              padding: "24px",
            }}
          >
            <h2
              onClick={() => navigate(`${routes.SCENARIOSDEMO}`)}
              style={{ padding: "0 24px", cursor: "pointer", marginBottom: "24px" }}
            >
              ← Back to Scenarios
            </h2>
            <div
              style={{
                width: "100%",
                padding: "24px",
                backgroundColor: "#fff",
                borderRadius: "8px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              }}
            >
              <h2 style={{ marginBottom: "16px", fontSize: "24px", fontWeight: 600 }}>
                Scenario History
              </h2>
              <p style={{ color: "#666", fontSize: "16px", lineHeight: "1.5" }}>
                This page will display scenario history details.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScenarioHistoryPage;

