import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

import HeaderProjects from "../components/headers/headerProjects";
import routes from "../constants/routes.json";

import NewProjectButtonColourful from "../components/buttons/newProjectButtonColourful";

import ProjectVoidForm from "../components/Projects/ProjectVoidForm";
// @ts-ignore
import ProjectGeoForm from "../components/Projects/ProjectGeoForm";

import ProjectPreview from "../components/Projects/ProjPreview";
import OpenProjects from "../components/Projects/OpenProjects";
import AddModelJsonDrawer from "../components/Projects/AddModelJsonDrawer";
import { useToast } from "../contexts/ToastContext";
import { getProjects, ProjectScenario } from "../services/cimWizard";

import "./GeneralPage.css";

const fakeProjData = [
  {
    name: "Cenisia",
    description:
      "Small thing that could be important like a brief description of the project we can ask for it during ",
    longitude: 7.650107994458712,
    latitude: 45.068994108650934,
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
    name: "ComoLake",
    description:
      "Small thing that could be important like a brief description of the project we can ask for it during ",
    longitude: 9.073688960776073,
    latitude: 45.81570174149794,
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
    name: "River",
    description:
      "Small thing that could be important like a brief description of the project we can ask for it during ",
    longitude: 12.480372406877159,
    latitude: 41.88753725723592,
    lastEdit: "18-05-2025",
    simulationRunning: false,
    initialProgress: 0,
  },
];

interface ProjectDisplayData {
  name: string;
  description: string;
  longitude: number;
  latitude: number;
  lastEdit: string;
  simulationRunning: boolean;
  initialProgress: number;
  projectId?: string;
  scenarioId?: string;
}

const ProjectsPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast?.() || { showToast: (m: string) => console.log(m) };
  const drawerRef = useRef<HTMLDivElement | null>(null);
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [drawerOption, setDrawerOption] = useState("");
  const [activeTab, setActiveTab] = useState("create"); // Add state for active tab
  const [showAddModel, setShowAddModel] = useState(false);
  const [projects, setProjects] = useState<ProjectDisplayData[]>([]);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [projectsError, setProjectsError] = useState<string | null>(null);

  // Update URL to include user's name
  useEffect(() => {
    if (user) {
      const newPath = `/projects/${user.username}`;
      if (window.location.pathname !== newPath) {
        navigate(newPath, { replace: true });
      }
    }
  }, [user, navigate]);

  // Fetch projects from CIM Wizard API
  useEffect(() => {
    const fetchProjects = async () => {
      setIsLoadingProjects(true);
      setProjectsError(null);
      try {
        const apiProjects = await getProjects();
        
        // Transform API response to match ProjectPreview component format
        const transformedProjects: ProjectDisplayData[] = apiProjects.map((proj: ProjectScenario) => {
          // Extract coordinates from project_center GeoJSON Point
          const longitude = proj.project_center?.coordinates?.[0] || 0;
          const latitude = proj.project_center?.coordinates?.[1] || 0;
          
          // Format date from ISO string to DD-MM-YYYY
          const formatDate = (dateString: string) => {
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

          return {
            name: proj.project_name || 'Unnamed Project',
            description: `Project: ${proj.project_name || 'N/A'}, Scenario: ${proj.scenario_name || 'N/A'}`,
            longitude,
            latitude,
            lastEdit: formatDate(proj.updated_at || proj.created_at || new Date().toISOString()),
            simulationRunning: false, // Default value, can be updated if API provides this
            initialProgress: 0, // Default value
            projectId: proj.project_id,
            scenarioId: proj.scenario_id,
          };
        });
        
        setProjects(transformedProjects);
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Failed to load projects';
        setProjectsError(message);
        console.error('Failed to fetch projects:', error);
        if (showToast) {
          showToast(`Failed to load projects: ${message}`, 'error');
        }
        // Fallback to empty array on error
        setProjects([]);
      } finally {
        setIsLoadingProjects(false);
      }
    };

    fetchProjects();
  }, [showToast]);

  const handleCreateConfiguration = () => {
    setDrawerOption("config");
    setDrawerOpen(true);
    setShowAddModel(true);
  };
  const handleCreateGEO = () => {
    setDrawerOption("geo");
    setDrawerOpen(true);
  };
  const handleCreateVoid = () => {
    setDrawerOption("void");
    setDrawerOpen(true);
  };
  const handleOpenProject = () => {
    setDrawerOption("open");
    setDrawerOpen(true);
  };
  const handleProjectClick = () => {
    setActiveTab("create");
    setDrawerOption("geo");
    setDrawerOpen(true);
  };

  const handleCreateProjectFromMenu = () => {
    setActiveTab("create");
    setDrawerOption("geo");
    setDrawerOpen(true);
  };

  const handleOpenProjectFromMenu = () => {
    setActiveTab("open");
    setDrawerOption("geo");
    setDrawerOpen(true);
  };

  const renderDrawerContent = () => {
    switch (drawerOption) {
      case "void":
        return <ProjectVoidForm />;
      case "open":
        return <OpenProjects />;
      case "geo":
        return (
          <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
            {/* Tab Navigation */}
            <div style={{ 
              display: "flex", 
              borderBottom: "1px solid #e0e0e0", 
              marginBottom: "20px" 
            }}>
              <button
                onClick={() => {
                  setActiveTab("create");
                }}
                style={{
                  padding: "12px 24px",
                  border: "none",
                  background: activeTab === "create" ? "#4CAF50" : "#f5f5f5",
                  color: activeTab === "create" ? "white" : "#333",
                  cursor: "pointer",
                  borderBottom: activeTab === "create" ? "3px solid #4CAF50" : "3px solid transparent",
                  fontWeight: activeTab === "create" ? "600" : "400",
                  transition: "all 0.2s ease",
                  borderRadius: "4px 4px 0 0"
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== "create") {
                    e.currentTarget.style.background = "#e8f5e8";
                    e.currentTarget.style.color = "#2e7d32";
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== "create") {
                    e.currentTarget.style.background = "#f5f5f5";
                    e.currentTarget.style.color = "#333";
                  }
                }}
              >
                Create a Project
              </button>
              <button
                onClick={() => {
                  setActiveTab("open");
                }}
                style={{
                  padding: "12px 24px",
                  border: "none",
                  background: activeTab === "open" ? "#2196F3" : "#f5f5f5",
                  color: activeTab === "open" ? "white" : "#333",
                  cursor: "pointer",
                  borderBottom: activeTab === "open" ? "3px solid #2196F3" : "3px solid transparent",
                  fontWeight: activeTab === "open" ? "600" : "400",
                  transition: "all 0.2s ease",
                  borderRadius: "4px 4px 0 0"
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== "open") {
                    e.currentTarget.style.background = "#e3f2fd";
                    e.currentTarget.style.color = "#1976d2";
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== "open") {
                    e.currentTarget.style.background = "#f5f5f5";
                    e.currentTarget.style.color = "#333";
                  }
                }}
              >
                Open Project
              </button>
            </div>
            
            {/* Tab Content */}
            <div style={{ flex: 1 }}>
              {activeTab === "create" ? <ProjectGeoForm /> : <OpenProjects />}
            </div>
          </div>
        );
      case "config":
        return (
          user ? (
            <AddModelJsonDrawer
              projectId={user.username}
              onAdded={(m, replaced) => {
                showToast && showToast(`Model "${m.name}" added${replaced ? ' (replaced)' : ''}.`, 'success', 2500);
              }}
            />
          ) : null
        );
      default:
        return null;
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        isDrawerOpen &&
        drawerRef.current &&
        !drawerRef.current.contains(event.target as Node)
      ) {
        setDrawerOpen(false);
        setDrawerOption("");
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
        onCreateProject={handleCreateProjectFromMenu}
        onOpenProject={handleOpenProjectFromMenu}
      />
      <div className="project-body">
        <div
            className="project-content"
            style={{
              width: isDrawerOpen ? "65%" : "100%",
              transition: "width 0.3s ease",
              minWidth: 0, // ensures flex child can shrink
              display: "flex",
              flexDirection: "column",
              height: "100%",
              overflow: "hidden", // do NOT scroll the whole column
            }}
        >
          {/* Top: Buttons - Not scrollable */}
          <div
              style={{
                width: "100%",
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
                paddingBottom: "12px"
              }}
          >
            <h2 style={{padding: "0 24px"}}>Create a Project</h2>
            <div
                style={{
                  width: "100%",
                  display: "flex",
                  flexDirection: "row",
                  flexWrap: "wrap",
                }}
            >
              <NewProjectButtonColourful
                  label="Project"
                  icon="/icons/distance.svg"
                  onClick={handleProjectClick}
                  color="#E97132"
              />
              <NewProjectButtonColourful
                  label="Model"
                  icon="/icons/graph_2.svg"
                  onClick={handleCreateConfiguration}
                  color="#3582FF"
              />
            </div>
          </div>

          {/* Bottom: Recent Projects - This is the only scrollable section */}
          <div
              style={{
                flex: 1, // fills the rest of the column
                width: "100%",
                overflowY: "auto",
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
              }}
          >
            <h2 style={{padding: "0 24px"}}>Recent Projects</h2>
            {isLoadingProjects ? (
              <div style={{padding: "24px", textAlign: "center"}}>Loading projects...</div>
            ) : projectsError ? (
              <div style={{padding: "24px", color: "#d32f2f"}}>
                Error loading projects: {projectsError}
              </div>
            ) : projects.length === 0 ? (
              <div style={{padding: "24px", textAlign: "center", color: "#666"}}>
                No projects found. Create a new project to get started.
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
                    gap: "0px",
                  }}
              >
                {projects.map((proj, index) => (
                    <ProjectPreview
                        key={proj.projectId || index}
                        name={proj.name}
                        description={proj.description}
                        longitude={proj.longitude}
                        latitude={proj.latitude}
                        lastEdit={proj.lastEdit}
                        simulationRunning={proj.simulationRunning}
                        initialProgress={proj.initialProgress}
                        projectId={proj.projectId}
                        scenarioId={proj.scenarioId}
                    />
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="project-drawer"
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
             }}>
          {/* Only render content when drawer is open */}
          {isDrawerOpen ? renderDrawerContent() : null}
        </div>

      </div>
    </div>
  );
};

export default ProjectsPage;
