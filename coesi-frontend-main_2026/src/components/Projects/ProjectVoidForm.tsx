import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import routes from "../../constants/routes.json";

import "./DrawerItems.css";

type ProjectFormData = {
  projectName: string;
  projectDescription: string;
  dataOption: "upload" | "default";
  scenarioOption: "create" | "notcreate";
  scenarioName: string;
};

const ProjectVoidForm: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<ProjectFormData>({
    projectName: "",
    projectDescription: "",
    dataOption: "upload",
    scenarioOption: "notcreate",
    scenarioName: "",
  });

  const handleChange = (
    key: keyof ProjectFormData,
    value:
      | string
      | ProjectFormData["dataOption"]
      | ProjectFormData["scenarioOption"]
  ) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSubmit = () => {
    console.log("Submitting:", formData);
    navigate(`${routes.NODES}`);
  };

  return (
    <div
      style={{
        padding: "32px",
        maxWidth: "600px",
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
      }}
    >
      <h2
        style={{
          fontSize: "24px",
          fontWeight: "bold",
          marginBottom: "24px",
          textAlign: "left",
        }}
      >
        Create a new Project
      </h2>

      <input
        type="text"
        placeholder="Project Name"
        value={formData.projectName}
        onChange={(e) => handleChange("projectName", e.target.value)}
        className="inputbox"
      />

      <input
        type="text"
        placeholder="Project Description"
        value={formData.projectDescription}
        onChange={(e) => handleChange("projectDescription", e.target.value)}
        className="inputbox"
      />

      <h3
        style={{
          fontSize: "16px",
          fontWeight: "bold",
          marginBottom: "8px",
          textAlign: "left",
        }}
      >
        Project Data Information
      </h3>

      <label style={{ display: "block", marginBottom: "8px" }}>
        <input
          type="radio"
          checked={formData.dataOption === "upload"}
          onChange={() => handleChange("dataOption", "upload")}
        />{" "}
        Add data
      </label>

      {formData.dataOption === "upload" && (
        <div
          style={{
            width: "100%",
            height: "120px",
            backgroundColor: "#f3f3f3",
            borderRadius: "20px",
            margin: "12px 0 24px 0",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            color: "#555",
            fontSize: "16px",
            textAlign: "center",
            border: "2px dashed #ccc",
            cursor: "pointer",
          }}
          onClick={() => {}}
        ><span>
          Drag a file or {" "} <span style={{ textDecoration: "underline", color: "#777" }}>
             search in your pc
          </span>
        </span>
        </div>
      )}

      <label style={{ display: "block", marginBottom: "24px" }}>
        <input
          type="radio"
          checked={formData.dataOption === "default"}
          onChange={() => handleChange("dataOption", "default")}
        />{" "}
        Create default data
      </label>

      <h3 style={{ fontSize: "16px", fontWeight: "bold", marginBottom: "8px" }}>
        Scenario Information
      </h3>

      <label style={{ display: "block", marginBottom: "8px" }}>
        <input
          type="checkbox"
          checked={formData.scenarioOption === "create"}
          onChange={(e) =>
            handleChange(
              "scenarioOption",
              e.target.checked ? "create" : "notcreate"
            )
          }
        />{" "}
        Create first scenario
      </label>

      {formData.scenarioOption === "create" && (
        <input
          type="text"
          className="inputbox"
          placeholder="Scenario Name"
          value={formData.scenarioName}
          onChange={(e) => handleChange("scenarioName", e.target.value)}
        />
      )}

      <button
        onClick={handleSubmit}
        style={{
          width: "100%",
          backgroundColor: "black",
          color: "white",
          padding: "12px 24px",
          borderRadius: "32px",
          border: "none",
          fontSize: "16px",
          fontWeight: "bold",
          cursor: "pointer",
          marginTop: "50px",
        }}
      >
        Create Project
      </button>
    </div>
  );
};

export default ProjectVoidForm;
