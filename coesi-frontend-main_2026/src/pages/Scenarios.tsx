import React, { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate, useSearchParams, useParams } from "react-router-dom";

import HeaderProjects from "../components/headers/headerProjects";
import routes from "../constants/routes.json";

import ScePreview from "../components/Scenarios/ScePreview";
import NewScenarioCard from "../components/Scenarios/NewSce";
import NewScenarioModal from "../components/Scenarios/NewSceForm";
import { getScenarios, ProjectScenario } from "../services/cimWizard";

interface ScenarioDisplayData {
  name: string;
  id: string;
  description: string;
  longitude: number;
  latitude: number;
  lastEdit: string;
  simulationRunning: boolean;
  initialProgress: number;
  isConfigured: boolean;
  projectId: string;
  scenarioId: string;
}

const ScenariosPage = () => {
  const drawerRef = useRef<HTMLDivElement | null>(null);
  const [searchParams] = useSearchParams();
  const { projectId: urlProjectId } = useParams<{ projectId: string }>();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [isModalVisible, setModalVisible] = useState(false);
  
  // State for scenarios from API
  const [scenarios, setScenarios] = useState<ScenarioDisplayData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [projectName, setProjectName] = useState<string>("");
  
  const projectId = urlProjectId || "";
  const navigate = useNavigate();

  // Fetch scenarios from the API
  const loadScenarios = useCallback(async () => {
    if (!projectId) {
      setError("No project ID provided");
      setIsLoading(false);
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('🔍 Fetching scenarios for project:', projectId);
      const apiScenarios = await getScenarios(projectId);
      console.log('📡 Scenarios returned:', apiScenarios);
      
      // Transform API response to display format
      const transformedScenarios: ScenarioDisplayData[] = apiScenarios.map((s: ProjectScenario) => {
        // Extract coordinates from project_center GeoJSON Point
        const longitude = s.project_center?.coordinates?.[0] || 0;
        const latitude = s.project_center?.coordinates?.[1] || 0;
        
        // Format date
        const formatDate = (dateString: string | undefined) => {
          if (!dateString) return new Date().toLocaleDateString('en-GB');
          try {
            const date = new Date(dateString);
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}-${month}-${year}`;
          } catch {
            return new Date().toLocaleDateString('en-GB');
          }
        };
        
        // Set project name from first scenario
        if (!projectName && s.project_name) {
          setProjectName(s.project_name);
        }
        
        return {
          name: s.scenario_name || 'Unnamed Scenario',
          id: s.scenario_id,
          description: `Scenario for project: ${s.project_name || 'N/A'}`,
          longitude,
          latitude,
          lastEdit: formatDate(s.updated_at || s.created_at),
          simulationRunning: false,
          initialProgress: 0,
          isConfigured: true,
          projectId: s.project_id,
          scenarioId: s.scenario_id,
        };
      });
      
      setScenarios(transformedScenarios);
      console.log('✅ Scenarios loaded:', transformedScenarios.length);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load scenarios';
      setError(message);
      console.error('❌ Failed to fetch scenarios:', err);
    } finally {
      setIsLoading(false);
    }
  }, [projectId, projectName]);

  // Load scenarios on mount
  useEffect(() => {
    loadScenarios();
  }, [loadScenarios]);

  // Check if we should open the drawer automatically
  useEffect(() => {
    const shouldOpenDrawer = searchParams.get('new');
    if (shouldOpenDrawer === 'true') {
      setDrawerOpen(true);
      // Clean up the URL parameter
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.delete('new');
      const newUrl = `${window.location.pathname}${newSearchParams.toString() ? '?' + newSearchParams.toString() : ''}`;
      window.history.replaceState({}, '', newUrl);
    }
  }, [searchParams]);

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
    <div className="project-container">
      <HeaderProjects 
        useScenarioMenu={true}
        onAddScenario={() => setDrawerOpen(true)}
      />
      <div
        className="project-body"
        style={{ display: "flex", width: "100%", overflow: "hidden" }}
      >
        <div
          className="project-content"
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
            <h2
              onClick={() => navigate(`${routes.PROJECTSDEMO}`)}
              style={{ padding: "0 24px", cursor: "pointer" }}
            >
              ← Back to Projects
            </h2>
            <h3 style={{ padding: "0 24px", color: "#666", fontWeight: "normal" }}>
              {projectName ? `Project: ${projectName}` : `Project ID: ${projectId}`}
            </h3>
            
            {isLoading ? (
              <div style={{ padding: "24px", textAlign: "center" }}>Loading scenarios...</div>
            ) : error ? (
              <div style={{ padding: "24px", color: "#d32f2f" }}>
                Error loading scenarios: {error}
              </div>
            ) : (
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
                {scenarios.map((sce, index) => (
                  <ScePreview
                    key={sce.scenarioId || index}
                    name={sce.name}
                    id={sce.scenarioId}
                    description={sce.description}
                    longitude={sce.longitude}
                    latitude={sce.latitude}
                    lastEdit={sce.lastEdit}
                    simulationRunning={sce.simulationRunning}
                    initialProgress={sce.initialProgress}
                    isConfigured={sce.isConfigured}
                    projectId={sce.projectId}
                    scenarioId={sce.scenarioId}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
          <div
            className="project-drawer"
            ref={drawerRef}
            style={{
               width: isDrawerOpen ? "35%" : "0%",
               minWidth: isDrawerOpen ? "360px" : "0px",
               padding: isDrawerOpen ? "20px" : "0px",
               borderLeft: isDrawerOpen ? "1px solid #cccccc" : "none",
               transition: "width 0.3s, min-width 0.3s, padding 0.3s, border 0.3s",
               height: "100%",
               overflowY: "auto",
               background: "#fff",
               boxSizing: "border-box"
            }}
          >
            <NewScenarioModal projectName={projectName || projectId} />
          </div>
      </div>
    </div>
  );
};

export default ScenariosPage;
