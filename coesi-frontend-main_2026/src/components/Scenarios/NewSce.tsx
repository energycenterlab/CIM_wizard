import React from "react";
import "./projpreview.css"; // assuming ScePreview styles are here

interface NewScenarioCardProps {
  onClick: () => void;
}

const NewScenarioCard: React.FC<NewScenarioCardProps> = ({ onClick }) => {
  return (
    <div
      className="project-card"
      onClick={onClick}
      style={{
        backgroundColor: "#f5f5f5",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        cursor: "pointer",
        color: "#888",
        fontWeight: "bold",
        fontSize: "16px",
      }}
    >
      New Scenario&nbsp;+
    </div>
  );
};

export default NewScenarioCard;
