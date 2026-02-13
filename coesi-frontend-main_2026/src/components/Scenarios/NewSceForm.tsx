import { useState, FormEvent } from "react";
import { useParams } from "react-router-dom";
import { useSelector } from "react-redux";

import axios from "axios";
import ClipLoader from "react-spinners/ClipLoader";

import routes from "../../constants/routes.json";
//@ts-ignore
import ScenarioConfigData from "./ScenarioConfigData";

interface NewScenarioModalProps {
  projectName: string;
}

interface RootState {
  projectPolygonInfo: {
    polygonArray: [number, number][];
    mapCenter: {
      latitude: number;
      longitude: number;
      zoom: number;
    };
  };
}

interface FileConfig {
  [key: string]: any; // Define specific structure if known
}

const NewScenarioModal: React.FC<NewScenarioModalProps> = ({ projectName }) => {
  //const history = createBrowserHistory();

  const [confirmLoading, setConfirmLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [scenarioName, setScenarioName] = useState("");
  const [selectedTool, setSelectedTool] = useState<string[]>([]);
  const [fileList, setFileList] = useState<any[]>([]);
  const [fileConfig, setFileConfig] = useState<FileConfig>({});
  const [uploading, setUploading] = useState(false); // Currently unused

  //const { projectInfo } = useParams<{ projectInfo: string }>();
  const projectInfo = "projectDemo==id1234";
  const [projname, projectId] = projectInfo.split("==");

  const polygonArray = useSelector(
    (state: RootState) => state.projectPolygonInfo.polygonArray
  );
  const mapCenter = useSelector(
    (state: RootState) => state.projectPolygonInfo.mapCenter
  );

  const Loader = ({
    isSpinning,
    isVisible,
  }: {
    isSpinning: boolean;
    isVisible: boolean;
  }) => {
    if (!isVisible) return null;

    return (
      <div className="sweet-loading">
        <ClipLoader
          color="green"
          loading={isSpinning}
          size={150}
          aria-label="Loading Spinner"
          data-testid="loader"
        />
      </div>
    );
  };

  const handleCancel = () => {
    setScenarioName("");
    setErrorMessage("");
    setFileList([]);
    setSelectedTool([]);
    setFileConfig({});
  };

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();

    if (!scenarioName) {
      setErrorMessage("Scenario name is mandatory");
      return;
    }

    const values = {
      projectName,
      scenario_name: scenarioName,
      scenarioList: selectedTool,
      fileConfig,
      project_id: projectId,
      scenario_id: "",
      buildingGeometry: fileList[0],
      polygonArray,
      mapCenter,
    };

    setConfirmLoading(true);

    try {
      const resp = await axios.post(`${routes.SHELPER}/polygonArray`, values);

      if (resp.data === "Name invalid") {
        setErrorMessage("Scenario name already taken :(");
      } else {
        setScenarioName("");
        setErrorMessage("");
        setFileList([]);
        setSelectedTool([]);
        setFileConfig({});
        //  history.push(
        //   `${routes.PROJECTS}/${projectName}==${projectId}/${scenarioName}==${resp.data.scenario_id}`
        // );
        // window.location.reload();
      }
    } catch (err) {
      console.error("Validation failed:", err);
      setErrorMessage("Failed to create scenario.");
    } finally {
      setConfirmLoading(false);
    }
  };

    return (
        <form onSubmit={handleCreate} autoComplete="off">
          <h2 className="scenario-form-title">{projectName} - Create new Scenario</h2>

          <div className="scenario-form-row">
            <label className="scenario-form-label" htmlFor="scenario-name-input">
              Name of the scenario:
            </label>
            <div className="scenario-form-content">
              <input
                  id="scenario-name-input"
                  type="text"
                  value={scenarioName}
                  onChange={(e) => setScenarioName(e.target.value)}
                  placeholder="Enter scenario name"
                  required
                  className="scenario-name-input"
              />
            </div>
          </div>


          <ScenarioConfigData
              fileList={fileList}
              setFileList={setFileList}
              setFilesConfig={setFileConfig}
              selectedTool={selectedTool}
              setSelectedTool={setSelectedTool}
          />

          {errorMessage && <p style={{color: "red"}}>{errorMessage}</p>}
          <Loader isSpinning={confirmLoading} isVisible={confirmLoading}/>

          <div className="scenario-form-actions">
            <button type="button" className="cancel-button" onClick={handleCancel}>
              Cancel
            </button>
            <button type="submit" className="create-button" disabled={confirmLoading}>
              {confirmLoading ? "Creating..." : "Create Scenario"}
            </button>
          </div>
        </form>
    );
};

export default NewScenarioModal;
