import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import HeaderProjects from "../components/headers/headerProjects";
import routes from "../constants/routes.json";
import SimulationResults from "../components/InputEditor/SimulationResults";
import { apiService } from "../services/api";
import "./GeneralPage.css";
import "./ScenarioInspect.css";
import refreshIcon from "../assets/refresh.svg";

interface Simulation {
  simulation_id: string;
  status: "pending" | "running" | "completed" | "failed";
  scenario_name: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  execution_time?: number;
  error_message?: string;
}

interface HDF5File {
  name: string;
  path: string;
  size: string;
  modified: number;
  scenario_name: string;
}

const ScenarioInspectPage = () => {
  const navigate = useNavigate();
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [loading, setLoading] = useState(true);
  const [hdf5Files, setHdf5Files] = useState<HDF5File[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>("");
  const [selectedSimulationId, setSelectedSimulationId] = useState<string | null>(null);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [simulationToDelete, setSimulationToDelete] = useState<Simulation | null>(null);

  useEffect(() => {
    fetchSimulations();
  }, []);

  useEffect(() => {
    // When simulations are loaded, use the first one to fetch HDF5 files
    if (simulations.length > 0 && !selectedSimulationId) {
      setSelectedSimulationId(simulations[0].simulation_id);
    }
  }, [simulations]);

  useEffect(() => {
    if (selectedSimulationId) {
      fetchHDF5Files(selectedSimulationId);
    }
  }, [selectedSimulationId]);

  useEffect(() => {
    // Auto-select first file when files are loaded
    if (hdf5Files.length > 0 && !selectedFile) {
      setSelectedFile(hdf5Files[0].name);
    }
  }, [hdf5Files]);

  const fetchSimulations = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAllSimulations();
      const completed = (data || []).filter(
        (sim) => sim.status === "completed"
      ) as Simulation[];
      // Sort by most recent first
      completed.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setSimulations(completed);
    } catch (error) {
      console.error("Error fetching simulations:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHDF5Files = async (simulationId: string) => {
    try {
      setLoadingFiles(true);
      const data = await apiService.getSimulationResults(simulationId);
      const files = (data.hdf5_files || []).map((file: any) => ({
        name: file.name,
        path: file.path,
        size: file.size,
        modified: file.modified,
        scenario_name: file.scenario_name || file.name
      }));
      setHdf5Files(files);
      // Reset selected file when new files are loaded
      if (files.length > 0) {
        setSelectedFile(files[0].name);
      } else {
        setSelectedFile("");
      }
    } catch (error) {
      console.error("Error fetching HDF5 files:", error);
      setHdf5Files([]);
    } finally {
      setLoadingFiles(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return "N/A";
    return `${seconds.toFixed(2)}s`;
  };

  const formatFileSize = (size: string) => {
    // Size is already formatted as "X.X KB" or similar
    return size;
  };

  const getFileDisplayName = (file: HDF5File) => {
    // Show scenario_name if available, otherwise show filename without extension
    if (file.scenario_name && file.scenario_name !== file.name) {
      return `${file.scenario_name} (${file.name})`;
    }
    return file.name.replace('.hdf5', '');
  };

  const handleDeleteSimulation = (simulation: Simulation, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (simulation.status === "running") {
      alert("Cannot delete a running simulation. Please stop it first.");
      return;
    }

    setSimulationToDelete(simulation);
    setShowDeleteDialog(true);
  };

  const confirmDelete = async () => {
    if (!simulationToDelete) return;

    try {
      await apiService.deleteSimulation(simulationToDelete.simulation_id);
      
      // Remove from local state
      setSimulations((prev) => prev.filter((s) => s.simulation_id !== simulationToDelete.simulation_id));
      
      // If the deleted simulation was selected, clear selection
      if (selectedSimulationId === simulationToDelete.simulation_id) {
        setSelectedSimulationId(null);
        setSelectedFile("");
        setHdf5Files([]);
      }
      
      // Refresh the list
      fetchSimulations();
    } catch (error) {
      console.error("Error deleting simulation:", error);
      alert("Failed to delete simulation. Please try again.");
    } finally {
      setShowDeleteDialog(false);
      setSimulationToDelete(null);
    }
  };

  const cancelDelete = () => {
    setShowDeleteDialog(false);
    setSimulationToDelete(null);
  };

  return (
    <div className="project-container">
      <HeaderProjects useScenarioMenu={true} />
      <div className="project-body">
        <div className="scenario-inspect-layout">
          {/* Main Content Area - 70% */}
          <div className="scenario-inspect-main">
            {selectedFile && selectedSimulationId ? (
              <div key={`${selectedSimulationId}-${selectedFile}`} style={{ width: '100%', height: '100%' }}>
                <SimulationResults
                  simulationId={selectedSimulationId}
                  selectedHdf5File={selectedFile}
                />
              </div>
            ) : (
              <div className="scenario-inspect-empty">
                <div className="empty-state">
                  <h3>No HDF5 File Selected</h3>
                  <p>Select an HDF5 file from the sidebar to view simulation results</p>
                </div>
              </div>
            )}
          </div>

          {/* Right Sidebar - 30% Fixed */}
          <div className="scenario-inspect-sidebar">
            {/* Top Section - 20% - HDF5 File Selector */}
            <div className="sidebar-file-selector">
              <div className="file-selector-header">
                <h3 className="file-selector-title">Select HDF5 File</h3>
                <button
                  className="sidebar-refresh-btn"
                  onClick={() => {
                    fetchSimulations();
                    if (selectedSimulationId) {
                      fetchHDF5Files(selectedSimulationId);
                    }
                  }}
                  title="Refresh"
                  disabled={loadingFiles || loading}
                >
                  <img src={refreshIcon} alt="Refresh" width="16" height="16" />
                </button>
              </div>

              <div className="file-selector-content">
                {loadingFiles ? (
                  <div className="file-selector-loading">
                    <div className="spinner-small"></div>
                    <span>Loading files...</span>
                  </div>
                ) : hdf5Files.length === 0 ? (
                  <div className="file-selector-empty">
                    <span>No HDF5 files available</span>
                  </div>
                ) : (
                  <div className="file-select-wrapper">
                    <select
                      className="file-select"
                      value={selectedFile}
                      onChange={(e) => setSelectedFile(e.target.value)}
                    >
                      {hdf5Files.map((file) => (
                        <option key={file.name} value={file.name}>
                          {getFileDisplayName(file)}
                        </option>
                      ))}
                    </select>
                    {selectedFile && (
                      <div className="file-info-preview">
                        {(() => {
                          const file = hdf5Files.find(f => f.name === selectedFile);
                          return file ? (
                            <>
                              <div className="file-info-item">
                                <span className="file-info-label">Size:</span>
                                <span className="file-info-value">{formatFileSize(file.size)}</span>
                              </div>
                              {file.scenario_name && (
                                <div className="file-info-item">
                                  <span className="file-info-label">Scenario:</span>
                                  <span className="file-info-value" title={file.scenario_name}>
                                    {file.scenario_name.length > 20 
                                      ? `${file.scenario_name.substring(0, 20)}...` 
                                      : file.scenario_name}
                                  </span>
                                </div>
                              )}
                            </>
                          ) : null;
                        })()}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Bottom Section - 80% - Simulation List */}
            <div className="sidebar-simulations">
              <div className="simulations-header">
                <h3 className="simulations-title">Simulation History</h3>
                <div className="simulations-counter">
                  <span className="counter-number">{simulations.length}</span>
                  <span className="counter-label">completed</span>
                </div>
              </div>

              <div className="simulations-content">
                {loading ? (
                  <div className="simulations-loading">
                    <div className="spinner"></div>
                    <p>Loading simulations...</p>
                  </div>
                ) : simulations.length === 0 ? (
                  <div className="simulations-empty">
                    <p className="empty-title">No Completed Simulations</p>
                    <p className="empty-hint">Run a simulation to see results here</p>
                  </div>
                ) : (
                  <div className="simulation-list">
                    {simulations.map((sim, index) => (
                      <div
                        key={sim.simulation_id}
                        className="simulation-card-info"
                      >
                        <div className="simulation-card-number">
                          #{simulations.length - index}
                        </div>
                        <div className="simulation-card-content">
                          <div className="simulation-card-header-info">
                            <h4 className="simulation-name-info" title={sim.scenario_name}>
                              {sim.scenario_name}
                            </h4>
                            <button
                              className="simulation-delete-btn"
                              onClick={(e) => handleDeleteSimulation(sim, e)}
                              title="Delete simulation"
                            >
                              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M3.5 3.5L10.5 10.5M10.5 3.5L3.5 10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                              </svg>
                            </button>
                          </div>
                          <div className="simulation-meta-info">
                            <div className="meta-row">
                              <svg className="meta-icon" width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M6 1V6L9 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                                <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.5"/>
                              </svg>
                              <span className="meta-text">{formatDuration(sim.execution_time)}</span>
                            </div>
                            <div className="meta-row">
                              <svg className="meta-icon" width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect x="2" y="3" width="8" height="7" rx="1" stroke="currentColor" strokeWidth="1.5"/>
                                <path d="M4 1V3M8 1V3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                                <path d="M2 5H10" stroke="currentColor" strokeWidth="1.5"/>
                              </svg>
                              <span className="meta-text">{formatDate(sim.created_at)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {showDeleteDialog && simulationToDelete && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000
          }}
        >
          <div
            style={{
              pointerEvents: 'auto',
              backdropFilter: 'saturate(120%) blur(4px)',
              background: 'rgba(255,255,255,0.95)',
              border: '1px solid rgba(0,0,0,0.08)',
              borderRadius: 16,
              boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
              padding: 20,
              maxWidth: '400px',
              width: '90%'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <div style={{ fontWeight: 700, fontSize: 16, color: '#111827' }}>
                Delete Simulation
              </div>
            </div>
            
            <div style={{ fontSize: 13, color: '#374151', marginBottom: 20, lineHeight: '1.5' }}>
              Are you sure you want to delete simulation <strong>"{simulationToDelete.scenario_name}"</strong>?
              <br />
              <strong>This will permanently remove all output files.</strong>
            </div>
            
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
              <button
                onClick={cancelDelete}
                style={{
                  border: '1px solid #E5E7EB',
                  background: 'white',
                  color: '#111827',
                  borderRadius: 8,
                  padding: '6px 12px',
                  fontSize: 13,
                  cursor: 'pointer',
                  transition: 'background-color 0.2s, border-color 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#F9FAFB';
                  e.currentTarget.style.borderColor = '#D1D5DB';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'white';
                  e.currentTarget.style.borderColor = '#E5E7EB';
                }}
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
              style={{
                  border: '1px solid #DC2626',
                  background: '#DC2626',
                  color: 'white',
                  borderRadius: 8,
                  padding: '6px 12px',
                  fontSize: 13,
                  cursor: 'pointer',
                  transition: 'background-color 0.2s, border-color 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#B91C1C';
                  e.currentTarget.style.borderColor = '#B91C1C';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#DC2626';
                  e.currentTarget.style.borderColor = '#DC2626';
                }}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScenarioInspectPage;
