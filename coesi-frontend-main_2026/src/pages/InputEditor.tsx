import React, { useEffect, useState, useMemo, useRef, useCallback } from "react";
import HeaderProjects from "../components/headers/headerProjects";
import ControlBar from "../components/InputEditor/ControlBar";
import NodesConfig from "../components/InputEditor/NodesConfig";

import { useDispatch, useSelector } from "react-redux";
import { useLocation, useParams } from "react-router-dom";
import type { RootState } from "../main";
import { store } from "../main";
import "./scenarios.css";

import { showTable, hideTable } from "../slices/visibleTablesSlice";
import { showLayer, hideLayer } from "../slices/visibleLayersSlice";
import { setLayers } from "../slices/scenarioLayersSlice";
import { setGraph, removeNode } from "../slices/rfGraphSlice";
import { deleteCompositeGroup } from "../utils/compositeHelpers";
import { removeAssignment } from "../slices/assignmentsSlice";
import { clearClickedF } from "../slices/clickedFSlice";
import { removeLayer } from "../slices/scenarioLayersSlice";
import { useToast } from "../contexts/ToastContext";
import { exportScenarioToJson, downloadScenarioJson } from "../utils/exportScenarioJson";
import { getProjects, getScenarios, getBuildingsGeoJSON } from "../services/cimWizard";

//import ScenarioMap from "../components/InputEditor/ScenarioMap";
import InputEditorMap from "../components/InputEditor/InputEditorMap";
//@ts-ignore
import Table from "../components/InputEditor/Table";

import tableConfig from "../constants/tableConfigure.json";
import "../components/InputEditor/ControlBar.css";
import AssignmentsView from "../components/InputEditor/AssignmentsView";
import SimulationPreview from "../components/InputEditor/SimulationPreview";

const InputEditor = () => {

  interface GeoFeature {
    type: string;
    properties: Record<string, any>;
    geometry: {
      type: string;
      coordinates: any;
    };
  }

  interface GeoJson {
    name: string;
    features: GeoFeature[];
  }

  // All hooks must be called at the top level in consistent order
  const location = useLocation();
  const { projectId: urlProjectId, scenarioId: urlScenarioId } = useParams<{ 
    projectId: string; 
    scenarioId: string; 
  }>();
  
  const [layers, setLayer] = useState<any[]>([]);
  const [tables, setTables] = useState<any[]>([]);

  const [activeToolboxRightTab, setActiveToolboxRightTab] = useState("layers");
  const [sceDisplay, setSceDisplay] = useState<string | null>("map");
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);
  const [isResultsModalOpen, setIsResultsModalOpen] = useState(false);
  const buildAbortRef = useRef<AbortController | null>(null);
  const [isAssignmentManagerOpen, setIsAssignmentManagerOpen] = useState(false);
  const [isDashboardVisible, setDashboardVisible] = useState(false);
  const [isCimLoading, setIsCimLoading] = useState(false);
  const [cimError, setCimError] = useState<string | null>(null);
  
  // Simulation state to persist across navigation
  const [simulationState, setSimulationState] = useState({
    currentStep: 0,
    isComplete: false,
    isModalOpen: false
  });

  const handleRunSimulation = () => {
    // Validate Output Configuration before running:
    // If mode=modified and no port selected -> warn and highlight "Modified" for 1s.
    try {
      const storageKey = `output-config:${location.pathname}`;
      const raw = sessionStorage.getItem(storageKey);
      if (raw) {
        const parsed = JSON.parse(raw);
        const mode = parsed?.portSelectionMode;
        const selected = parsed?.selectedPorts;
        if (mode === 'modified' && (!Array.isArray(selected) || selected.length === 0)) {
          setActiveToolboxRightTab('settings');
          showToast('Select at least one port (Modified output configuration).', 'warning', 2500);
          window.dispatchEvent(new CustomEvent('output-config:highlight-modified'));
          return;
        }
      }
    } catch {
      // ignore parse errors and allow run
    }
    // Reset simulation state and start the flow
      setIsSimulationRunning(true);
    setSimulationState({
      currentStep: 0,
      isComplete: false,
      isModalOpen: false
    });
      buildAbortRef.current = new AbortController();
  };

  // Step callbacks for SimulationPreview
  const handlePreflight = async () => {
    // Preflight validation - can add validation logic here
    // For now, just a placeholder that passes
    return Promise.resolve();
  };

  const handleBuildScenario = async () => {
    // Force Redux sync before export
      console.log('🔄 Forcing Redux sync before export...');
      
      const reactFlowState = window.reactFlowState || { nodes: [], edges: [] };
      console.log('📊 ReactFlow state:', { nodes: reactFlowState.nodes?.length || 0, edges: reactFlowState.edges?.length || 0 });
      
      if (reactFlowState.nodes && reactFlowState.nodes.length > 0) {
        store.dispatch({ type: 'rfGraph/setGraph', payload: { nodes: reactFlowState.nodes, edges: reactFlowState.edges } });
        console.log('✅ Forced Redux sync completed');
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      const state = store.getState();
      console.log('📊 Redux state after sync:', { 
        nodes: state.rfGraph?.nodes?.length || 0, 
        edges: state.rfGraph?.edges?.length || 0 
      });
      
      const scenarioData = exportScenarioToJson(state);
      
    console.log('✅ Scenario JSON generated successfully');
    console.log(scenarioData);

    return { jsonData: scenarioData };
  };

  const handleGenerateConfig = async (jsonData: any) => {
    // Send to YAML builder - use centralized config
    const { YAML_BUILDER_URL } = await import('../config/apiConfig');
    const builderUrls = [`${YAML_BUILDER_URL}/build`];
      let result: any = null;
      let lastErr: any = null;
    
      for (const url of builderUrls) {
        try {
          const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ data: jsonData }),
          signal: buildAbortRef.current?.signal
          });
          if (resp.ok) {
            result = await resp.json();
            break;
          } else {
            lastErr = new Error(await resp.text());
          }
        } catch (e) {
          if ((e as any)?.name === 'AbortError') {
          throw new Error('YAML generation cancelled');
          }
          lastErr = e as any;
        }
      }
    
      if (!result) throw lastErr || new Error('Failed to contact YAML Builder');

    const yamlContent = result?.yaml_v2 || result?.yaml || '';
      if (!yamlContent) throw new Error('Empty YAML from builder');

    const filename = `scenario-${new Date().toISOString().split('T')[0]}-v2.yaml`;
    
    console.log('✅ YAML generated successfully');
    
    return { yamlContent, filename };
  };

  const handleSubmitJob = async (yamlContent: string, filename: string) => {
    // This is handled in SimulationPreview, but we can add additional logic here if needed
    // The actual upload and simulation start happens in SimulationPreview
    return { simulationId: '' }; // Will be set by SimulationPreview
  };

  const handleCancelSimulation = () => {
    try {
      buildAbortRef.current?.abort();
    } finally {
      setIsSimulationRunning(false);
      showToast('Run cancelled', 'info');
    }
  };

  const handleSimulationComplete = () => {
    setIsSimulationRunning(false);
    setSimulationState(prev => ({
      ...prev,
      isComplete: true
    }));
  };

  const handleModalToggle = (isOpen: boolean) => {
    setIsResultsModalOpen(isOpen);
    setSimulationState(prev => ({
      ...prev,
      isModalOpen: isOpen
    }));
  };

  const dispatch = useDispatch();
  const { showToast } = useToast();
  const selectedNode = useSelector((state: RootState) => state.clickedNode.node);

  const visibleTables = useSelector(
    (state: RootState) => state.visibleTables.visibleTables
  );
  const scenarioLayers = useSelector(
    (state: RootState) => state.scenarioLayers.layerGeojsonList
  ) as GeoJson[];

  const loadCimWizardData = useCallback(async () => {
    setIsCimLoading(true);
    setCimError(null);
    try {
      // First try URL params, then query params, then fallback to first project/scenario
      const queryParams = new URLSearchParams(location.search);
      let projectId = urlProjectId || queryParams.get("project_id") || undefined;
      let scenarioId = urlScenarioId || queryParams.get("scenario_id") || undefined;

      console.log('🔍 Loading buildings for project:', projectId, 'scenario:', scenarioId);

      // If we have both IDs from URL, use them directly
      if (projectId && scenarioId) {
        const geojson = await getBuildingsGeoJSON(projectId, scenarioId);
        console.log('📍 Buildings loaded:', geojson.features?.length || 0, 'features');
        
        // Add name property for the map component (required for layer filtering)
        const namedGeojson = {
          ...geojson,
          name: 'buildings'
        };
        
        dispatch(setLayers([namedGeojson as any]));
        dispatch(showLayer('buildings'));  // showLayer expects string layer name, not index
        setCimError(null);
        return;
      }

      // Fallback: fetch projects if not provided
      const projects = await getProjects();
      if (!projects.length) {
        throw new Error("No projects available in CIM Wizard");
      }
      if (!projectId) {
        projectId = projects[0].project_id;
      }

      const scenarios = await getScenarios(projectId);
      if (!scenarios.length) {
        throw new Error("No scenarios available for selected project");
      }
      if (!scenarioId) {
        scenarioId = scenarios[0].scenario_id;
      }

      const geojson = await getBuildingsGeoJSON(projectId, scenarioId);
      console.log('📍 Buildings loaded (fallback):', geojson.features?.length || 0, 'features');
      
      // Add name property for the map component (required for layer filtering)
      const namedGeojson = {
        ...geojson,
        name: 'buildings'
      };
      
      dispatch(setLayers([namedGeojson as any]));
      dispatch(showLayer('buildings'));  // showLayer expects string layer name, not index
      setCimError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load CIM data";
      setCimError(message);
      showToast(`CIM Wizard fetch failed: ${message}`, "error");
    } finally {
      setIsCimLoading(false);
    }
  }, [dispatch, location.search, showToast, urlProjectId, urlScenarioId]);

  // 4. Only run once on mount
  useEffect(() => {
    loadCimWizardData();
  }, [loadCimWizardData]);

  // Auto-switch to Details tab when a node is selected
  useEffect(() => {
    if (selectedNode) {
      setActiveToolboxRightTab('details');
    }
  }, [selectedNode]);

  // Listen for assignment manager open/close events
  useEffect(() => {
    const handleAssignmentManagerOpened = () => {
      setIsAssignmentManagerOpen(true);
    };
    
    const handleAssignmentManagerClosed = () => {
      setIsAssignmentManagerOpen(false);
    };

    window.addEventListener('assignment-manager-opened', handleAssignmentManagerOpened);
    window.addEventListener('assignment-manager-closed', handleAssignmentManagerClosed);

    return () => {
      window.removeEventListener('assignment-manager-opened', handleAssignmentManagerOpened);
      window.removeEventListener('assignment-manager-closed', handleAssignmentManagerClosed);
    };
  }, []);

  useEffect(() => {
    if (!scenarioLayers?.length) return;

    const tabulatorData = scenarioLayers.map((item) => ({ ...item }));

    const generatedTables = tabulatorData.map((geojson) => {
      const tData = geojson.features.map((feature) => ({
        ...feature.properties,
      }));
      const sampleProps = geojson.features[0]?.properties || {};

      const tColumns = Object.keys(sampleProps).map((key) => {
        const value = sampleProps[key];
        let editorType =
          typeof value === "number"
            ? "number"
            : typeof value === "boolean"
            ? "tickCross"
            : "input";

        return { title: key, field: key, editor: editorType };
      });

      return { name: geojson.name, data: tData, columns: tColumns };
    });

    setTables(generatedTables);
  }, [scenarioLayers]);

  useEffect(() => {
    if (!scenarioLayers || scenarioLayers.length === 0) return;

    const namesArray = scenarioLayers.map((layer) => layer.name);
    setLayer(namesArray);
    namesArray.forEach((name) => {
      dispatch(showLayer(name));
      dispatch(showTable(name)); // Show all tables by default
    });
  }, [scenarioLayers]);

  const toggleTableVisible = (layer: string) => {
    if (visibleTables.includes(layer)) {
      dispatch(hideTable(layer));
    } else {
      dispatch(showTable(layer));
    }
  };

  const renderLayerContent = () => {
    switch (sceDisplay) {
      case "map":
        return <InputEditorMap onNavigateToAssignments={() => setSceDisplay("assignments")} />;
      case "table":
        return (
          <div
            style={{
              position: "relative",
              width: "100%",
              height: "100%",
            }}
          >
            {tables.map((table) => (
              <div
                style={{
                  position: "absolute",
                  width: "100%",
                  height: "100%",
                  zIndex: 1000,
                  top: 0,
                  left: 0,
                  backgroundColor: "white",
                  border: "1px solid #ccc",
                  padding: "10px",
                  visibility: visibleTables.includes(table.name)
                    ? "visible"
                    : "hidden",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                

                <div
                  style={{
                    flex: 1,
                    width: "100%",
                    height: "100%",
                    overflow: "hidden",
                  }}
                >
                  <InputTable
                    tableData={table.data}
                    tableConfig={tableConfig}
                    tableColumns={table.columns}
                  />
                </div>
              </div>
            ))}
          </div>
        );
      case "config":
        return <NodesConfig isLocked={isSimulationRunning} />;
      case "assignments":
        return <AssignmentsView />;
      default:
        return null;
    }
  };

  return (
    <div className="pagecontainer">
      <HeaderProjects 
        hideCommunityArchive={true} 
        hideFileEditShow={true}
        showBreadcrumb={true}
        scenarioName="baselineDemo"
        projectId="projid"
        projectName="projname"
      />
      <div
        className="mainbody"
        style={{ display: "flex", flexDirection: "row", ['--rightSidebarWidth' as any]: '430px' }}
      >
        {isDashboardVisible && (
          <div
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              backgroundColor: "rgba(0, 0, 0, 0.5)",
              zIndex: 20000,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <div
              style={{
                backgroundColor: "white",
                margin: "20px",
                padding: "20px",
                borderRadius: "8px",
                minWidth: "300px",
                maxWidth: "80vw",
                maxHeight: "80vh", // limit height
                boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.2)",
                overflowY: "auto", // enable vertical scrolling
              }}
            >
              <h3>Dashboard</h3>
              <img
                src="/images/BadDashboard.png"
                alt="Dashboard"
                style={{
                  width: "100%",
                  height: "auto",
                  display: "block",
                }}
              />
              <button onClick={() => setDashboardVisible(false)}>Close</button>
            </div>
          </div>
        )}

        <div style={{ flex: 1, height: "100%", position: "relative" }}>
          <div
            style={{
              width: "100%",
              height: "100%",
              position: "relative",
              zIndex: 1000,
            }}
          >
            {renderLayerContent()}
          </div>
        </div>
        <div
          className="tabs-container"
          style={{
            width: "370px",
            height: "100%",
            minHeight: 0,
            overflow: "hidden",
            borderLeft: "1px solid #ccc",
          }}
        >
          {isSimulationRunning ? (
            <SimulationPreview 
              onComplete={handleSimulationComplete} 
              onModalToggle={handleModalToggle}
              simulationState={simulationState}
              setSimulationState={setSimulationState}
              onPreflight={handlePreflight}
              onBuildScenario={handleBuildScenario}
              onGenerateConfig={handleGenerateConfig}
              onSubmitJob={handleSubmitJob}
            />
          ) : (
            <>
          <div className="tabs-header">
            <div
              className={`tab ${
                activeToolboxRightTab === "layers" ? "active" : ""
              }`}
              onClick={() => setActiveToolboxRightTab("layers")}
            >
              Layers
            </div>
            <div
              className={`tab ${
                activeToolboxRightTab === "details" ? "active" : ""
              }`}
              onClick={() => setActiveToolboxRightTab("details")}
            >
              Details
            </div>

            <div
              className={`tab ${
                activeToolboxRightTab === "settings" ? "active" : ""
              }`}
              onClick={() => setActiveToolboxRightTab("settings")}
            >
              Simulation setting
            </div>
          </div>

          <div className="tabs-content" style={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
            {activeToolboxRightTab === "layers" && (
              <LayerList layers={layers} currentView={sceDisplay} />
            )}
            {activeToolboxRightTab === "settings" && (
              <ScenarioSettingBoard setShowPopup={setDashboardVisible} />
            )}
            {activeToolboxRightTab === "details" && (
              <FeatureInfoBoard />
            )}
          </div>
            </>
          )}
        </div>
        {/* Floating Toolbar - Centered within available area */}
        {!isAssignmentManagerOpen && !isResultsModalOpen && (
          <div className="floating-toolbar-container">
            <ControlBar onToolSelect={setSceDisplay} activeTool={sceDisplay} onRunSimulation={handleRunSimulation} isSimulationRunning={isSimulationRunning} onCancelSimulation={handleCancelSimulation} />
          </div>
        )}
      </div>
    </div>
  );
};

export default InputEditor;

interface Column {
  title: string;
  field: string;
  editor?: string;
}

interface TableConfig {
  [key: string]: string[];
}

interface InputTableProps {
  tableData: Record<string, any>[];
  tableConfig: TableConfig;
  tableColumns: Column[];
}
const InputTable: React.FC<InputTableProps> = ({
  tableData,
  tableConfig,
  tableColumns,
}) => {
  const tabs = [...Object.keys(tableConfig), "other_attributes"];
  const [tab, setTab] = useState<string>(tabs[0]);

  const getFilteredColumns = (): Column[] => {
    if (tab === "other_attributes") {
      return tableColumns.filter(
        (column) => !Object.values(tableConfig).flat().includes(column.field)
      );
    } else if (tableConfig[tab]) {
      return tableColumns.filter((column) =>
        tableConfig[tab].includes(column.field)
      );
    }
    return [];
  };

  return (
    <div className="table-tabs" style={{ width: "100%", height: "100%" }}>
      <Tabs tabs={tabs} onTabChange={setTab} />

      <div className="table">
        <Table tab={tab} data={tableData} columns={getFilteredColumns()} />
      </div>
    </div>
  );
};

interface TabsProps {
  tabs: string[];
  onTabChange: (tab: string) => void;
}

const Tabs: React.FC<TabsProps> = ({ tabs, onTabChange }) => {
  const [activeToolboxRightTab, setActiveToolboxRightTab] =
    useState("other_attributes");
  const handleTab = (tab: string) => {
    onTabChange(tab);
    setActiveToolboxRightTab(tab);
  };
  return (
    <div className="custom-tabs">
      <div className="tabs-header">
        {tabs.map((key) => (
          <div
            key={key}
            className={`tab ${activeToolboxRightTab === key ? "active" : ""}`}
            onClick={() => handleTab(key)}
          >
            {key.replace("_", " ").toUpperCase()}
          </div>
        ))}
      </div>
    </div>
  );
};

const LayerList: React.FC<{ layers: string[]; currentView: string | null }> = ({ layers, currentView }) => {
  const scenarioInfo = "baselineDemo==id5678";
  const [scenarioName] = scenarioInfo.split("==");

  const dispatch = useDispatch();
  const { showToast } = useToast();
  const visibleLayers = useSelector(
    (state: RootState) => state.visibleLayers.visibleLayers
  );
  const visibleTables = useSelector(
    (state: RootState) => state.visibleTables.visibleTables
  );
  const scenarioLayers = useSelector(
    (state: RootState) => state.scenarioLayers.layerGeojsonList
  );
  
  // Get nodes and edges from the workspace for node editor
  const rfNodes = useSelector((state: RootState) => state.rfGraph.nodes);
  const rfEdges = useSelector((state: RootState) => state.rfGraph.edges);
  // Prefer live ReactFlow state so node.data edits (e.g. composite rename/ports) reflect immediately in this list.
  const liveRfState = (window as any)?.reactFlowState;
  const [liveRfTick, setLiveRfTick] = useState(0);
  useEffect(() => {
    const handler = () => setLiveRfTick((v) => v + 1);
    window.addEventListener('reactflow:state-updated', handler as any);
    return () => window.removeEventListener('reactflow:state-updated', handler as any);
  }, []);
  const nodesForWorkspace = (Array.isArray(liveRfState?.nodes) && liveRfState.nodes.length > 0) ? liveRfState.nodes : rfNodes;
  const edgesForWorkspace = (Array.isArray(liveRfState?.edges) && liveRfState.edges.length > 0) ? liveRfState.edges : rfEdges;
  
  // Get assignments for assignment manager
  const assignments = useSelector((state: RootState) => (state as any).assignments?.assignments || []);

  // State for confirmation dialogs
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [layerToDelete, setLayerToDelete] = useState<string | null>(null);
  const [showItemDeleteDialog, setShowItemDeleteDialog] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<any>(null);

  // UI state for composite expand/collapse
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => ({ ...prev, [groupId]: !prev[groupId] }));
  };

  // Debug: Monitor nodes changes
  // useEffect(() => {
  //   console.log('Nodes changed in LayerList:', rfNodes.length, rfNodes.map(n => n.id));
  // }, [rfNodes]);

  const toggleTableVisible = (layer: string) => {
    if (visibleTables.includes(layer)) {
      dispatch(hideTable(layer));
    } else {
      dispatch(showTable(layer));
    }
  };

  const toggleLayerVisible = (layer: string) => {
    if (visibleLayers.includes(layer)) {
      dispatch(hideLayer(layer));
    } else {
      dispatch(showLayer(layer));
    }
  };

  const handleDeleteLayer = (layerName: string) => {
    setLayerToDelete(layerName);
    setShowDeleteDialog(true);
  };

  const confirmDeleteLayer = () => {
    if (layerToDelete) {
      // Find the layer index in scenarioLayers
      const layerIndex = scenarioLayers.findIndex(layer => layer.name === layerToDelete);
      
      if (layerIndex !== -1) {
        // Remove from scenario layers
        dispatch(removeLayer(layerIndex));
        
        // Also remove from visible layers and tables if present
        if (visibleLayers.includes(layerToDelete)) {
          dispatch(hideLayer(layerToDelete));
        }
        if (visibleTables.includes(layerToDelete)) {
          dispatch(hideTable(layerToDelete));
        }
        
        // Show success toast
        showToast(`Layer "${layerToDelete}" has been deleted successfully`, 'success');
      }
    }
    
    // Close dialog and reset state
    setShowDeleteDialog(false);
    setLayerToDelete(null);
  };

  const cancelDeleteLayer = () => {
    setShowDeleteDialog(false);
    setLayerToDelete(null);
  };

  // Handle delete for workspace items and assignment batches
  const handleDeleteItem = (layer: any) => {
    setItemToDelete(layer);
    setShowItemDeleteDialog(true);
  };

  const confirmDeleteItem = () => {
    if (!itemToDelete) return;
    
    console.log('=== DELETE DEBUG ===');
    console.log('Item to delete:', itemToDelete);
    
    if (itemToDelete.type === 'batch') {
      // Delete assignment batch
      console.log('Deleting assignment batch:', itemToDelete.id);
      dispatch(removeAssignment(itemToDelete.id));
      showToast(`Assignment "${itemToDelete.name}" deleted successfully`, 'success', 2500);
      console.log('Dispatched removeAssignment action');
      try {
        const affectedNodeIds = rfNodes
          .filter((n: any) => String(n.data?.assignmentBatchId) === String(itemToDelete.id))
          .map((n: any) => n.id);
        if (affectedNodeIds.length > 0) {
          window.dispatchEvent(new CustomEvent('workspace:remove-nodes', { detail: { nodeIds: affectedNodeIds } }));
        }
      } catch {}
    } else if (itemToDelete.type === 'composite') {
      // Delete entire composite group
      console.log('Deleting composite group:', itemToDelete.id);
      const { remainingNodes, remainingEdges } = deleteCompositeGroup(
        itemToDelete.id,
        rfNodes,
        rfEdges
      );
      console.log('After composite delete - remaining nodes:', remainingNodes.length);
      dispatch(setGraph({ nodes: remainingNodes, edges: remainingEdges }));
      try {
        const remainingIds = new Set(remainingNodes.map((n: any) => n.id));
        const removedIds = rfNodes.map((n: any) => n.id).filter((id: string) => !remainingIds.has(id));
        if (removedIds.length > 0) {
          window.dispatchEvent(new CustomEvent('workspace:remove-nodes', { detail: { nodeIds: removedIds } }));
        }
      } catch {}
      showToast(`Composite group "${itemToDelete.name}" deleted successfully`, 'success', 2500);
    } else {
      // Delete individual node - use the actual node object if available
      const nodeIdToDelete = itemToDelete.node ? itemToDelete.node.id : itemToDelete.id;
      console.log('Deleting individual node with ID:', nodeIdToDelete);
      console.log('Node to delete details:', itemToDelete.node);
      
      // Check if node exists in current nodes
      const nodeExists = rfNodes.find(n => n.id === nodeIdToDelete);
      console.log('Node exists in current nodes:', !!nodeExists);
      
      if (nodeExists) {
        dispatch(removeNode(nodeIdToDelete));
        console.log('Dispatched removeNode action');
        showToast(`Entity block "${itemToDelete.name || nodeIdToDelete}" deleted successfully`, 'success', 2500);
        try {
          window.dispatchEvent(new CustomEvent('workspace:remove-nodes', { detail: { nodeIds: [nodeIdToDelete] } }));
        } catch {}
      } else {
        console.log('Node not found in current nodes, trying alternative approach');
        // Fallback: manually filter and update
        const updatedNodes = rfNodes.filter(node => node.id !== nodeIdToDelete);
        const updatedEdges = rfEdges.filter(edge => 
          edge.source !== nodeIdToDelete && edge.target !== nodeIdToDelete
        );
        console.log('Manual filter - remaining nodes:', updatedNodes.length);
        dispatch(setGraph({ nodes: updatedNodes, edges: updatedEdges }));
        showToast(`Entity block "${itemToDelete.name || nodeIdToDelete}" deleted successfully`, 'success', 2500);
        try {
          window.dispatchEvent(new CustomEvent('workspace:remove-nodes', { detail: { nodeIds: [nodeIdToDelete] } }));
        } catch {}
      }
    }
    console.log('=== END DELETE DEBUG ===');
    
    setShowItemDeleteDialog(false);
    setItemToDelete(null);
  };

  const cancelDeleteItem = () => {
    setShowItemDeleteDialog(false);
    setItemToDelete(null);
  };


  const [searchTerm, setSearchTerm] = useState("");

  const filteredLayers = useMemo(() => {
    return layers.filter((layer) =>
      layer.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm, layers]);

  // For node editor, create layers from workspace nodes
  const workspaceLayers = useMemo(() => {
    if (currentView !== 'config') return [];
    
    // Group composite models together
    const compositeGroups = new Map();
    const individualNodes: any[] = [];
    
    nodesForWorkspace.forEach((node: any) => {
      if (node.data?.compositeGroupId) {
        // This is part of a composite model
        const groupId = node.data.compositeGroupId;
        if (!compositeGroups.has(groupId)) {
        compositeGroups.set(groupId, {
          id: groupId,
          name: node.data.compositeName || 'Composite Model',
          type: 'composite',
          nodes: []
        });
        }
        compositeGroups.get(groupId).nodes.push(node);
      } else {
        // Individual node (model or entity)
        const isEntity = !!node.data?.assignmentBatchId;
        let displayName = node.data?.name || node.data?.label || node.id;
        if (isEntity) {
          try {
            const assignment = (assignments as any[]).find((a) => String(a.id) === String(node.data?.assignmentBatchId));
            if (assignment && typeof assignment.name === 'string') {
              displayName = assignment.name;
            }
          } catch {}
        }
        individualNodes.push({
          id: node.id,
          name: displayName,
          type: isEntity ? 'entity' : 'model',
          node: node
        });
      }
    });
    
    // Combine composite groups and individual nodes
    return [...Array.from(compositeGroups.values()), ...individualNodes];
  }, [nodesForWorkspace, currentView, assignments, liveRfTick]);

  // For assignment manager, create layers from assignment batches
  const assignmentLayers = useMemo(() => {
    if (currentView !== 'assignments') return [];
    
    return assignments.map((assignment: any) => ({
      id: assignment.id,
      name: assignment.name,
      type: 'batch',
      assignment: assignment,
      count: assignment.count,
      createdAt: assignment.createdAt
    }));
  }, [assignments, currentView]);

  const filteredWorkspaceLayers = useMemo(() => {
    if (currentView !== 'config') return [];
    
    return workspaceLayers.filter((layer) =>
      layer.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [workspaceLayers, searchTerm, currentView]);

  const filteredAssignmentLayers = useMemo(() => {
    if (currentView !== 'assignments') return [];
    
    return assignmentLayers.filter((layer: any) =>
      layer.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [assignmentLayers, searchTerm, currentView]);

  // Get the appropriate title based on current view
  const getTitle = () => {
    switch (currentView) {
      case 'config':
        return 'Node editor';
      case 'assignments':
        return 'Assignment manager';
      case 'map':
        return `${scenarioName} - layers`;
      case 'table':
        return `${scenarioName} - layers`;
      default:
        return `${scenarioName} - layers`;
    }
  };

  // Get the appropriate placeholder text
  const getPlaceholder = () => {
    switch (currentView) {
      case 'config':
        return 'Search models and entities...';
      case 'assignments':
        return 'Search batches...';
      default:
        return 'Search layers...';
    }
  };

  return (
    <div
      style={{
        padding: "10px",
        width: "100%",
        alignItems: "start",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          position: 'sticky',
          top: 0,
          background: '#fff',
          zIndex: 5,
          paddingBottom: 8,
        }}
      >
        <h2 style={{ textAlign: "left", fontSize: "1.6rem", marginTop: 0 }}>{getTitle()}</h2>
        <input
          type="text"
          placeholder={getPlaceholder()}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: "98%",
            padding: "18px",
            marginBottom: "6px",
            border: "1px solid #ccc",
            height: "50px",
            borderRadius: "25px",
            boxSizing: "border-box",
          }}
        />
      </div>

      <ul style={{ listStyle: "none", padding: 0, margin: 0, overflow: 'auto', maxHeight: 'calc(100vh - 260px)' }}>
        {currentView === 'assignments' ? (
          // Assignment manager content
          <>
            {filteredAssignmentLayers.length === 0 ? (
              <li style={{ 
                padding: "20px", 
                textAlign: "center", 
                color: "#666",
                fontStyle: "italic"
              }}>
                {assignmentLayers.length === 0 
                  ? "No batches created yet. Create some batches to see them here."
                  : "No matching batches found."
                }
              </li>
            ) : (
              filteredAssignmentLayers.map((layer: any) => (
                <li
                  key={layer.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "10px 15px",
                    borderBottom: "1px solid #ccc",
                    height: "60px",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      minWidth: "200px",
                    }}
                  >
                    <img
                      src="/icons/assign.svg"
                      alt=""
                      style={{ width: 24, height: 24, marginRight: 12 }}
                    />
                    <div>
                      <div style={{ fontWeight: 600, fontSize: "0.8rem" }}>{layer.name}</div>
                      <div style={{ fontSize: "0.6rem", color: "#666" }}>
                        Batch • {layer.count} items
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <button
                      onClick={() => {
                        console.log('Delete button clicked for batch:', layer.name);
                        handleDeleteItem(layer);
                      }}
                      style={{
                        background: "none",
                        border: "1px solid #ccc",
                        cursor: "pointer",
                        padding: "4px",
                        borderRadius: "4px",
                      }}
                      title="Delete batch"
                    >
                      <img
                        src="/icons/delete.svg"
                        alt="Delete"
                        style={{ width: 20, height: 20 }}
                      />
                    </button>
                  </div>
                </li>
              ))
            )}
          </>
        ) : currentView === 'config' ? (
          // Node editor content
          <>
            {filteredWorkspaceLayers.length === 0 ? (
              <li style={{ 
                padding: "20px", 
                textAlign: "center", 
                color: "#666",
                fontStyle: "italic"
              }}>
                {workspaceLayers.length === 0 
                  ? "No models or entities in workspace. Drop some models to see them here."
                  : "No matching items found."
                }
              </li>
            ) : (
              filteredWorkspaceLayers.flatMap((layer) => {
                let iconSrc = '/icons/graph_1.svg';
                if (layer.type === 'entity') {
                  iconSrc = '/icons/assign.svg';
                } else if (layer.type === 'composite') {
                  iconSrc = '/icons/folder.svg';
                }
                
                // Render composite as collapsible group, else single item
                if (layer.type === 'composite') {
                  const isExpanded = !!expandedGroups[layer.id];
                  // Detect composite block nodes (single RF node representing the whole composite)
                  const isCompositeBlock = Array.isArray(layer.nodes) && layer.nodes.length === 1 && (layer.nodes[0] as any)?.type === 'CompositeBlock';
                  // Child models: if composite block, read inner saved nodes; otherwise use grouped RF nodes
                  const innerNodesRaw = isCompositeBlock
                    ? (((layer.nodes[0] as any)?.data?.nodes)
                        ?? ((layer.nodes[0] as any)?.data?.originalComposite?.nodes)
                        ?? [])
                    : (layer.nodes ?? []);
                  const innerNodesArr = Array.isArray(innerNodesRaw) ? innerNodesRaw : [];
                  const childCount = innerNodesArr.length;
                  const header = (
                    <li
                      key={`group-${layer.id}`}
                      onClick={() => toggleGroup(layer.id)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "10px 15px",
                        borderBottom: "1px solid #ccc",
                        height: "60px",
                        cursor: "pointer",
                        backgroundColor: isExpanded ? "#f8f9fa" : "transparent",
                        transition: "background-color 0.2s ease"
                      }}
                    >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        minWidth: 0,
                      }}
                    >
                        <img
                          src={iconSrc}
                          alt=""
                          style={{ width: 24, height: 24, marginRight: 12 }}
                        />
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontWeight: 600, fontSize: "0.8rem", whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 220 }}>{layer.name}</div>
                          <div style={{ fontSize: "0.6rem", color: "#666" }}>
                            Composite Model • {childCount} {childCount === 1 ? 'item' : 'items'}
                          </div>
                        </div>
                      </div>

                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent triggering the row click
                            console.log('Delete button clicked for:', layer.name);
                            handleDeleteItem(layer);
                          }}
                          style={{
                            background: "none",
                            border: "1px solid #ccc",
                            cursor: "pointer",
                            padding: "4px",
                            borderRadius: "4px",
                          }}
                          title="Delete composite"
                        >
                          <img
                            src="/icons/delete.svg"
                            alt="Delete"
                            style={{ width: 20, height: 20 }}
                          />
                        </button>
                      </div>
                    </li>
                  );

                  if (!isExpanded) return [header];

                  const children = innerNodesArr.map((childNode: any, idx: number) => (
                    <li
                      key={`${layer.id}::${childNode.id || idx}`}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "8px 15px 8px 24px",
                        borderBottom: "1px dashed #e5e7eb",
                        height: "52px",
                        background: '#fafafa'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', minWidth: '200px' }}>
                        <img src={'/icons/graph_2.svg'} alt="" style={{ width: 18, height: 18, marginRight: 10 }} />
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.78rem' }}>{childNode?.data?.name || childNode?.data?.label || childNode?.label || childNode?.modelDefId || childNode?.id}</div>
                          <div style={{ fontSize: '0.6rem', color: '#666' }}>Model</div>
                        </div>
                      </div>
                      {/* Only allow delete if the child is an actual RF node (not inside composite block) */}
                      {!isCompositeBlock && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                          <button
                            onClick={() => handleDeleteItem({ id: childNode.id, name: childNode?.data?.name, type: 'model', node: childNode })}
                            style={{
                              background: 'none',
                              border: '1px solid #ccc',
                              cursor: 'pointer',
                              padding: '4px',
                              borderRadius: '4px'
                            }}
                            title="Delete model"
                          >
                            <img src="/icons/delete.svg" alt="Delete" style={{ width: 18, height: 18 }} />
                          </button>
                        </div>
                      )}
                    </li>
                  ));

                  return [header, ...children];
                }

                return (
                  <li
                    key={`item-${layer.id}`}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "10px 15px",
                      borderBottom: "1px solid #ccc",
                      height: "60px",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        minWidth: 0,
                      }}
                    >
                      <img
                        src={iconSrc}
                        alt=""
                        style={{ width: 24, height: 24, marginRight: 12 }}
                      />
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontWeight: 600, fontSize: "0.8rem", whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 220 }}>{layer.name}</div>
                        <div style={{ fontSize: "0.6rem", color: "#666" }}>
                          {layer.type === 'entity' ? 'Entity' : 'Model'}
                        </div>
                      </div>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      <button
                        onClick={() => {
                          console.log('Delete button clicked for:', layer.name);
                          handleDeleteItem(layer);
                        }}
                        style={{
                          background: "none",
                          border: "1px solid #ccc",
                          cursor: "pointer",
                          padding: "4px",
                          borderRadius: "4px",
                        }}
                        title="Delete"
                      >
                        <img
                          src="/icons/delete.svg"
                          alt="Delete"
                          style={{ width: 20, height: 20 }}
                        />
                      </button>
                    </div>
                  </li>
                );
              })
            )}
          </>
        ) : currentView === 'map' ? (
          // Map view - only layer visibility controls
          <>
            {filteredLayers.map((layer) => {
              const iconSrc = getIconByLayerName(layer); // Function defined below
              return (
                <li
                  key={layer}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "10px 15px",
                    borderBottom: "1px solid #ccc",
                    height: "60px",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      minWidth: 0,
                    }}
                  >
                    <img
                      src={iconSrc}
                      alt=""
                      style={{ width: 24, height: 24, marginRight: 12 }}
                    />
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: "0.8rem", whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 220 }}>{layer}</div>
                      <div style={{ fontSize: "0.6rem", color: "#666" }}>
                        Map layer
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <label 
                      className="custom-checkbox-layer"
                      style={{ 
                        width: '32px', 
                        height: '32px', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        transform: 'translateY(3px)'
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={visibleLayers.includes(layer)}
                        onChange={() => toggleLayerVisible(layer)}
                      />
                      <span 
                        className="checkmark"
                        style={{ 
                          width: '20px', 
                          height: '20px',
                          backgroundSize: 'contain',
                          backgroundRepeat: 'no-repeat'
                        }}
                      ></span>
                    </label>
                    
                    <button
                      onClick={() => handleDeleteLayer(layer)}
                      style={{
                        border: '1px solid #E5E7EB',
                        background: 'white',
                        color: '#111827',
                        borderRadius: 8,
                        padding: '6px',
                        fontSize: 12,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '32px',
                        height: '32px',
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
                      title="Delete layer"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="3,6 5,6 21,6"></polyline>
                        <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                      </svg>
                    </button>
                  </div>
                </li>
              );
            })}
            {filteredLayers.length === 0 && <li>No matching layers</li>}
          </>
        ) : currentView === 'table' ? (
          // Table view - only table visibility controls
          <>
            {filteredLayers.map((layer) => {
              const iconSrc = getIconByLayerName(layer); // Function defined below
              return (
                <li
                  key={layer}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "10px 15px",
                    borderBottom: "1px solid #ccc",
                    height: "60px",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      minWidth: 0,
                    }}
                  >
                    <img
                      src={iconSrc}
                      alt=""
                      style={{ width: 24, height: 24, marginRight: 12 }}
                    />
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: "0.8rem", whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 220 }}>{layer}</div>
                      <div style={{ fontSize: "0.6rem", color: "#666" }}>
                        Table layer
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <label className="custom-checkbox-table">
                      <input
                        type="checkbox"
                        checked={visibleTables.includes(layer)}
                        onChange={() => toggleTableVisible(layer)}
                      />
                      <span className="checkmark"></span>
                    </label>
                  </div>
                </li>
              );
            })}
            {filteredLayers.length === 0 && <li>No matching layers</li>}
          </>
        ) : (
          // Default fallback (should not happen with current views)
          <>
            {filteredLayers.map((layer) => {
              const iconSrc = getIconByLayerName(layer);
              return (
                <li
                  key={layer}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "10px 15px",
                    borderBottom: "1px solid #ccc",
                    height: "60px",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      minWidth: 0,
                    }}
                  >
                    <img
                      src={iconSrc}
                      alt=""
                      style={{ width: 24, height: 24, marginRight: 12 }}
                    />
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: "0.8rem", whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 220 }}>{layer}</div>
                      <div style={{ fontSize: "0.6rem", color: "#666" }}>
                        Single layer
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <label className="custom-checkbox-layer">
                      <input
                        type="checkbox"
                        checked={visibleLayers.includes(layer)}
                        onChange={() => toggleLayerVisible(layer)}
                      />
                      <span className="checkmark"></span>
                    </label>

                    <label className="custom-checkbox-table">
                      <input
                        type="checkbox"
                        checked={visibleTables.includes(layer)}
                        onChange={() => toggleTableVisible(layer)}
                      />
                      <span className="checkmark"></span>
                    </label>
                  </div>
                </li>
              );
            })}
            {filteredLayers.length === 0 && <li>No matching layers</li>}
          </>
        )}
      </ul>
      
      {/* Confirmation Dialog */}
      {showDeleteDialog && (
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
              <div style={{ fontWeight: 700, fontSize: 16, color: '#111827' }}>Delete Layer</div>
            </div>
            
            <div style={{ fontSize: 13, color: '#374151', marginBottom: 20, lineHeight: '1.5' }}>
              Are you sure you want to delete the layer <strong>"{layerToDelete}"</strong>? This action cannot be undone.
            </div>
            
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
              <button
                onClick={cancelDeleteLayer}
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
                onClick={confirmDeleteLayer}
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
      
      {/* Confirmation Dialog for Entity Blocks and Composite Groups */}
      {showItemDeleteDialog && (
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
                Delete {itemToDelete?.type === 'composite' ? 'Composite Group' : itemToDelete?.type === 'batch' ? 'Assignment' : 'Entity Block'}
              </div>
            </div>
            
            <div style={{ fontSize: 13, color: '#374151', marginBottom: 20, lineHeight: '1.5' }}>
              Are you sure you want to delete the {itemToDelete?.type === 'composite' ? 'composite group' : itemToDelete?.type === 'batch' ? 'assignment' : 'entity block'} <strong>"{itemToDelete?.name || itemToDelete?.id}"</strong>? This action cannot be undone.
            </div>
            
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
              <button
                onClick={cancelDeleteItem}
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
                onClick={confirmDeleteItem}
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

const FeatureInfoBoard: React.FC = () => {
  const feature = useSelector((state: RootState) => state.clickedF.feature);
  const nodeInfo = useSelector((state: RootState) => state.clickedNode.node);
  const assignments = useSelector((state: RootState) => (state as any).assignments?.assignments || []);
  const dispatch = useDispatch();

  // Clear feature selection when node is selected to avoid confusion
  useEffect(() => {
    if (feature && nodeInfo) {
      dispatch(clearClickedF());
    }
  }, [feature, nodeInfo, dispatch]);



  // Function to translate technical labels to user-friendly names
  const translateLabel = (key: string): string => {
    const translations: { [key: string]: string } = {
      id: "ID",
      altezza_vo: "Height",
      superficie: "Surface Area",
      categ_uso: "Usage Category",
      epoca_cost: "Construction Period",
      num_piani: "Number of Floors",
      nsez: "Section Number",
      net_leased_area: "Net Leased Area",
      number_of_floors: "Total Floors",
      net_leased_volume: "Net Leased Volume",
      usage: "Usage Type",
      year: "Year",
      n_people: "Number of People",
      n_families: "Number of Families",
      tab_type: "Building Type",
      tabula_year_slot: "Year Slot",
      archetype_code: "Archetype Code"
    };
    return translations[key] || key;
  };

  // Case: Nothing selected
  if (!feature && !nodeInfo) {
    return (
      <div
        style={{
          padding: "16px",
          borderRadius: "8px",
          fontStyle: "italic",
        }}
      >
        No feature selected.
      </div>
    );
  }

  // Case: Only node selected, show node params read-only
  if (!feature && nodeInfo) {
    const batchId = (nodeInfo as any)?.assignmentBatchId;
    const assignment = batchId ? assignments.find((a: any) => String(a.id) === String(batchId)) : undefined;
    const inferMethod = (a: any): string | undefined => {
      if (!a) return undefined;
      const r = a.rule;
      if (r?.kind === 'random') return `Random ${r.percent}% (seed ${r.seed})`;
      if (r?.kind === 'filter') return 'Filter';
      if (r?.kind === 'mapSelection') return 'Map selection';
      if (r?.kind === 'all') return 'All buildings';
      if (typeof a?.name === 'string') {
        const m1 = a.name.match(/^random_(\d+)_p(\d+)/);
        if (m1) return `Random ${m1[1]}% (seed ${m1[2]})`;
        const m2 = a.name.match(/^split_[AB]_(\d+)_p(\d+)/);
        if (m2) return `Random split ${m2[1]}% (seed ${m2[2]})`;
        if (a.name.startsWith('selection_')) return 'Map selection';
      }
      return 'Custom';
    };
    const method = assignment ? inferMethod(assignment) : undefined;

    return (
      <div style={{ padding: "16px" }}>
        <h3 style={{ marginTop: 0, marginBottom: 12 }}>{nodeInfo?.name}</h3>
        {/* Debug: Check what's in nodeInfo */}
        {/* {console.log('nodeInfo:', nodeInfo)} */}
          {nodeInfo?.modelDefId && (
            <div style={{ color: "#666", marginBottom: 12 }}>{nodeInfo.modelDefId}</div>
          )}

          {assignment && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Assignment</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #eee', padding: '2px 0', fontSize: 13 }}>
                <div style={{ color: '#555' }}>Name</div>
                <div style={{ fontWeight: 500 }}>{assignment.name}</div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #eee', padding: '2px 0', fontSize: 13 }}>
                <div style={{ color: '#555' }}>Count</div>
                <div style={{ fontWeight: 500 }}>{assignment.count}</div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #eee', padding: '2px 0', fontSize: 13 }}>
                <div style={{ color: '#555' }}>Method</div>
                <div style={{ fontWeight: 500 }}>{method}</div>
              </div>
            </div>
          )}

          {/* Description */}
          {nodeInfo?.description && (
            <div style={{ marginBottom: 12, color: "#666", fontSize: 13 }}>
              {nodeInfo.description}
            </div>
          )}

          {/* Tags */}
          {nodeInfo?.tags && nodeInfo.tags.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Tags</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {nodeInfo.tags.map((tag: string) => (
                  <span key={tag} style={{ background: '#f1f5f9', color: '#334155', borderRadius: 12, padding: '2px 6px', fontSize: 10 }}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Solver */}
          {nodeInfo?.solver && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Solver</div>
              <div style={{ color: '#444', fontSize: 13 }}>{nodeInfo.solver}</div>
            </div>
          )}

          {/* Execution Command */}
          {nodeInfo?.model_execution_cmd && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Execution Command</div>
              <div style={{ color: '#444', fontFamily: 'monospace', fontSize: 11, background: '#f5f5f5', padding: 4, borderRadius: 4 }}>
                {nodeInfo.model_execution_cmd}
              </div>
            </div>
          )}

          {/* Simulation Parameters */}
          {nodeInfo?.simulation_parameters && nodeInfo.simulation_parameters.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Simulation Parameters</div>
              {nodeInfo.simulation_parameters.map((param: any, index: number) => (
                <div key={index} style={{ marginBottom: 4, padding: 4, background: '#f8fafc', borderRadius: 4, fontSize: 12 }}>
                  <div style={{ fontWeight: 500 }}>{param.name}</div>
                  <div style={{ color: '#666' }}>{param.description}</div>
                  <div style={{ color: '#444' }}>Value: {param.value} {param.unit}</div>
                </div>
              ))}
            </div>
          )}

          {/* Input Variables */}
          {nodeInfo?.input_variables && nodeInfo.input_variables.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Input Variables</div>
              {nodeInfo.input_variables.map((input: any, index: number) => (
                <div key={index} style={{ marginBottom: 4, padding: 4, background: '#f0f9ff', borderRadius: 4, fontSize: 12 }}>
                  <div style={{ fontWeight: 500 }}>{input.name}</div>
                  <div style={{ color: '#666' }}>{input.description}</div>
                  <div style={{ color: '#444' }}>Start: {input.start_value} {input.unit}</div>
                </div>
              ))}
            </div>
          )}

          {/* Output Variables */}
          {nodeInfo?.output_variables && nodeInfo.output_variables.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Output Variables</div>
              {nodeInfo.output_variables.map((output: any, index: number) => (
                <div key={index} style={{ marginBottom: 4, padding: 4, background: '#fef2f2', borderRadius: 4, fontSize: 12 }}>
                  <div style={{ fontWeight: 500 }}>{output.name}</div>
                  <div style={{ color: '#666' }}>{output.description}</div>
                  <div style={{ color: '#444' }}>Start: {output.start_value} {output.unit}</div>
                </div>
              ))}
            </div>
          )}

          {/* Model Parameters */}
          {nodeInfo?.model_parameters && nodeInfo.model_parameters.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Model Parameters</div>
              {nodeInfo.model_parameters.map((param: any, index: number) => (
                <div key={index} style={{ marginBottom: 4, padding: 4, background: '#f0fdf4', borderRadius: 4, fontSize: 12 }}>
                  <div style={{ fontWeight: 500 }}>{param.name}</div>
                  <div style={{ color: '#666' }}>{param.description}</div>
                  <div style={{ color: '#444' }}>Default: {param.default_value} {param.unit}</div>
                </div>
              ))}
            </div>
          )}

          {/* Possible Connections */}
          {nodeInfo?.possible_connections && nodeInfo.possible_connections.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Possible Connections</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {nodeInfo.possible_connections.map((connection: string) => (
                  <span key={connection} style={{ background: '#e0e7ff', color: '#3730a3', borderRadius: 12, padding: '2px 6px', fontSize: 10 }}>
                    {connection}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Components (for composite models) */}
          {nodeInfo?.components && nodeInfo.components.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Components</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {nodeInfo.components.map((component: string) => (
                  <span key={component} style={{ background: '#fef3c7', color: '#92400e', borderRadius: 12, padding: '2px 6px', fontSize: 10 }}>
                    {component}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Connections (for composite models) */}
          {nodeInfo?.connections && nodeInfo.connections.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Connections</div>
              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 4, padding: 8 }}>
                {nodeInfo.connections.map((connection: string, index: number) => (
                  <div key={index} style={{ fontFamily: 'monospace', fontSize: 10, marginBottom: index < nodeInfo.connections.length - 1 ? 4 : 0 }}>
                    {connection}
                  </div>
                ))}
              </div>
            </div>
          )}
      </div>
    );
  }

  // Case: Both feature and node selected - prioritize node details
  if (feature && nodeInfo) {
    // Show node details (same as the node-only case)
    const batchId = (nodeInfo as any)?.assignmentBatchId;
    const assignment = batchId ? assignments.find((a: any) => String(a.id) === String(batchId)) : undefined;
    const inferMethod = (a: any): string | undefined => {
      if (!a) return undefined;
      const r = a.rule;
      if (r?.kind === 'random') return `Random ${r.percent}% (seed ${r.seed})`;
      if (r?.kind === 'filter') return 'Filter';
      if (r?.kind === 'mapSelection') return 'Map selection';
      if (r?.kind === 'all') return 'All buildings';
      if (typeof a?.name === 'string') {
        const m1 = a.name.match(/^random_(\d+)_p(\d+)/);
        if (m1) return `Random ${m1[1]}% (seed ${m1[2]})`;
        const m2 = a.name.match(/^split_[AB]_(\d+)_p(\d+)/);
        if (m2) return `Random split ${m2[1]}% (seed ${m2[2]})`;
        if (a.name.startsWith('selection_')) return 'Map selection';
      }
      return 'Custom';
    };
    const method = assignment ? inferMethod(assignment) : undefined;

    return (
      <div style={{ padding: "16px" }}>
        <h3 style={{ marginTop: 0, marginBottom: 12 }}>{nodeInfo?.name}</h3>
        {nodeInfo?.modelDefId && (
          <div style={{ color: "#666", marginBottom: 12 }}>{nodeInfo.modelDefId}</div>
        )}

        {assignment && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Assignment</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #eee', padding: '2px 0', fontSize: 13 }}>
              <div style={{ color: '#555' }}>Name</div>
              <div style={{ fontWeight: 500 }}>{assignment.name}</div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #eee', padding: '2px 0', fontSize: 13 }}>
              <div style={{ color: '#555' }}>Count</div>
              <div style={{ fontWeight: 500 }}>{assignment.count}</div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #eee', padding: '2px 0', fontSize: 13 }}>
              <div style={{ color: '#555' }}>Method</div>
              <div style={{ fontWeight: 500 }}>{method}</div>
            </div>
          </div>
        )}

        {/* Description */}
        {nodeInfo?.description && (
          <div style={{ marginBottom: 12, color: "#666", fontSize: 13 }}>
            {nodeInfo.description}
          </div>
        )}

        {/* Tags */}
        {nodeInfo?.tags && nodeInfo.tags.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Tags</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {nodeInfo.tags.map((tag: string) => (
                <span key={tag} style={{ background: '#f1f5f9', color: '#334155', borderRadius: 12, padding: '2px 6px', fontSize: 10 }}>
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Solver */}
        {nodeInfo?.solver && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Solver</div>
            <div style={{ color: '#444', fontSize: 13 }}>{nodeInfo.solver}</div>
          </div>
        )}

        {/* Execution Command */}
        {nodeInfo?.model_execution_cmd && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Execution Command</div>
            <div style={{ color: '#444', fontFamily: 'monospace', fontSize: 11, background: '#f5f5f5', padding: 4, borderRadius: 4 }}>
              {nodeInfo.model_execution_cmd}
            </div>
          </div>
        )}

        {/* Simulation Parameters */}
        {nodeInfo?.simulation_parameters && nodeInfo.simulation_parameters.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Simulation Parameters</div>
            {nodeInfo.simulation_parameters.map((param: any, index: number) => (
              <div key={index} style={{ marginBottom: 4, padding: 4, background: '#f8fafc', borderRadius: 4, fontSize: 12 }}>
                <div style={{ fontWeight: 500 }}>{param.name}</div>
                <div style={{ color: '#666' }}>{param.description}</div>
                <div style={{ color: '#444' }}>Value: {param.value} {param.unit}</div>
              </div>
            ))}
          </div>
        )}

        {/* Input Variables */}
        {nodeInfo?.input_variables && nodeInfo.input_variables.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Input Variables</div>
            {nodeInfo.input_variables.map((input: any, index: number) => (
              <div key={index} style={{ marginBottom: 4, padding: 4, background: '#f0f9ff', borderRadius: 4, fontSize: 12 }}>
                <div style={{ fontWeight: 500 }}>{input.name}</div>
                <div style={{ color: '#666' }}>{input.description}</div>
                <div style={{ color: '#444' }}>Start: {input.start_value} {input.unit}</div>
              </div>
            ))}
          </div>
        )}

        {/* Output Variables */}
        {nodeInfo?.output_variables && nodeInfo.output_variables.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Output Variables</div>
            {nodeInfo.output_variables.map((output: any, index: number) => (
              <div key={index} style={{ marginBottom: 4, padding: 4, background: '#fef2f2', borderRadius: 4, fontSize: 12 }}>
                <div style={{ fontWeight: 500 }}>{output.name}</div>
                <div style={{ color: '#666' }}>{output.description}</div>
                <div style={{ color: '#444' }}>Start: {output.start_value} {output.unit}</div>
              </div>
            ))}
          </div>
        )}

        {/* Model Parameters */}
        {nodeInfo?.model_parameters && nodeInfo.model_parameters.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Model Parameters</div>
            {nodeInfo.model_parameters.map((param: any, index: number) => (
              <div key={index} style={{ marginBottom: 4, padding: 4, background: '#f0fdf4', borderRadius: 4, fontSize: 12 }}>
                <div style={{ fontWeight: 500 }}>{param.name}</div>
                <div style={{ color: '#666' }}>{param.description}</div>
                <div style={{ color: '#444' }}>Default: {param.default_value} {param.unit}</div>
              </div>
            ))}
          </div>
        )}

        {/* Possible Connections */}
        {nodeInfo?.possible_connections && nodeInfo.possible_connections.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Possible Connections</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {nodeInfo.possible_connections.map((connection: string) => (
                <span key={connection} style={{ background: '#e0e7ff', color: '#3730a3', borderRadius: 12, padding: '2px 6px', fontSize: 10 }}>
                  {connection}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Components (for composite models) */}
        {nodeInfo?.components && nodeInfo.components.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Components</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {nodeInfo.components.map((component: string) => (
                <span key={component} style={{ background: '#fef3c7', color: '#92400e', borderRadius: 12, padding: '2px 6px', fontSize: 10 }}>
                  {component}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Connections (for composite models) */}
        {nodeInfo?.connections && nodeInfo.connections.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Connections</div>
            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 4, padding: 8 }}>
              {nodeInfo.connections.map((connection: string, index: number) => (
                <div key={index} style={{ fontFamily: 'monospace', fontSize: 10, marginBottom: index < nodeInfo.connections.length - 1 ? 4 : 0 }}>
                  {connection}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Case: Feature selected (without node) - render feature fields
  if (feature && !nodeInfo) {
    return (
    <div
      style={{
        padding: "16px",
        borderRadius: "8px",
        width: "100%",
        wordWrap: "break-word",
        fontSize: "14px",
        textAlign: "left",
        height: "100%",
        overflowY: "auto",
      }}
    >
      <h3 style={{ marginTop: 0, marginBottom: "12px" }}>Feature Info</h3>
      {Object.entries(feature.properties || {}).map(([key, value]) => (
        <div
          key={`${feature.properties?.id}-${key}`}
          style={{
            marginBottom: "6px",
            display: "grid",
            gridTemplateColumns: "140px 1fr",
            alignItems: "center",
            gap: "8px",
            minHeight: "28px",
          }}
        >
          <div
            style={{
              fontWeight: "500",
              fontSize: "13px",
              display: "flex",
              alignItems: "center",
              color: "#333",
            }}
          >
            {translateLabel(key)}:
          </div>

          {key === "id" ? (
            <span 
              style={{ 
                fontSize: "13px",
                display: "flex",
                alignItems: "center",
                height: "28px",
                color: "#666",
              }}
            >
              {String(value)}
            </span>
          ) : (
            <input
              key={`${feature.properties?.id}-${key}-input`}
              type="text"
              defaultValue={String(value)}
              style={{
                padding: "4px 6px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                fontSize: "13px",
                height: "28px",
                boxSizing: "border-box",
                width: "100%",
                maxWidth: "200px",
              }}
            />
          )}
        </div>
      ))}
    </div>
  );
  }

  // If no feature is selected, return null
  return null;
};

const Section: React.FC<{ title: string; obj: Record<string, any> }> = ({ title, obj }) => {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>{title}</div>
      {Object.entries(obj).map(([k, v]) => (
        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #eee', padding: '2px 0', fontSize: 13 }}>
          <div style={{ color: '#555' }}>{k}</div>
          <div style={{ fontWeight: 500 }}>{String(v)}</div>
        </div>
      ))}
    </div>
  );
};

interface ScenarioSettingBoardProps {
  setShowPopup?: (show: boolean) => void;
}

const ScenarioSettingBoard: React.FC<ScenarioSettingBoardProps> = ({
  setShowPopup,
}) => {
  const location = useLocation();
  const rfNodes = useSelector((state: RootState) => state.rfGraph.nodes);
  // Prefer live ReactFlow nodes (includes node.data changes like composite exposed ports),
  // fallback to Redux snapshot when unavailable.
  const liveRfNodes = (window as any)?.reactFlowState?.nodes;
  const [liveRfTick, setLiveRfTick] = useState(0);
  useEffect(() => {
    const handler = () => setLiveRfTick((v) => v + 1);
    window.addEventListener('reactflow:state-updated', handler as any);
    return () => window.removeEventListener('reactflow:state-updated', handler as any);
  }, []);
  const nodesForPorts = (Array.isArray(liveRfNodes) && liveRfNodes.length > 0) ? liveRfNodes : rfNodes;
  type PortSelectionMode = 'all' | 'output' | 'input' | 'modified';
  const [portSelectionMode, setPortSelectionMode] = React.useState<PortSelectionMode>('all');
  const [selectedPorts, setSelectedPorts] = React.useState<Set<string>>(new Set());
  const [highlightModified, setHighlightModified] = React.useState(false);

  // Persist selection state across tab switches (scoped to current route/workspace)
  const storageKey = React.useMemo(() => `output-config:${location.pathname}`, [location.pathname]);

  // Date defaults and state:
  // Requested defaults: 01/01/2015 and 31/01/2015 (HTML date input uses YYYY-MM-DD).
  const DEFAULT_START_DATE = '2015-01-01';
  const DEFAULT_END_DATE = '2015-01-31';
  const todayISO = () => {
    const now = new Date();
    const yyyy = String(now.getFullYear());
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  };
  const [startDate, setStartDate] = React.useState<string>(DEFAULT_START_DATE);
  const [endDate, setEndDate] = React.useState<string>(DEFAULT_END_DATE);

  // Load persisted state on mount
  React.useEffect(() => {
    try {
      const raw = sessionStorage.getItem(storageKey);
      if (raw) {
        const parsed = JSON.parse(raw);
        // Back-compat: previous versions stored { allPortsChecked, selectedPorts }.
        // New behavior uses deterministic mode selection.
        if (parsed?.portSelectionMode === 'all' || parsed?.portSelectionMode === 'output' || parsed?.portSelectionMode === 'input' || parsed?.portSelectionMode === 'modified') {
          setPortSelectionMode(parsed.portSelectionMode);
        } else if (typeof parsed?.allPortsChecked === 'boolean' && parsed.allPortsChecked === true) {
          setPortSelectionMode('all');
        }
        if (Array.isArray(parsed?.selectedPorts)) {
          setSelectedPorts(new Set(parsed.selectedPorts));
        }
        if (typeof parsed?.startDate === 'string') {
          setStartDate(parsed.startDate);
        }
        if (typeof parsed?.endDate === 'string') {
          setEndDate(parsed.endDate);
        }
      }
    } catch {
      // no-op on parse errors
    }
  }, [storageKey]);

  // Listen for highlight requests (e.g., when Run is clicked with invalid config)
  React.useEffect(() => {
    const handler = () => {
      setPortSelectionMode('modified');
      setHighlightModified(true);
      window.setTimeout(() => setHighlightModified(false), 1000);
    };
    window.addEventListener('output-config:highlight-modified', handler as any);
    return () => window.removeEventListener('output-config:highlight-modified', handler as any);
  }, []);

  // Save whenever state changes
  React.useEffect(() => {
    try {
      const payload = {
        portSelectionMode,
        selectedPorts: Array.from(selectedPorts),
        startDate,
        endDate,
      };
      sessionStorage.setItem(storageKey, JSON.stringify(payload));
    } catch {
      // ignore storage errors
    }
  }, [storageKey, portSelectionMode, selectedPorts, startDate, endDate]);

  // Collect all available output ports from all models in workspace
  const availablePorts = React.useMemo(() => {
    const ports: Array<{ modelName: string; portName: string; fullId: string; type: 'input' | 'output' }> = [];
    
    (nodesForPorts || []).forEach((node: any) => {
      const modelName = node.data?.name || node.data?.label || node.id;

      const isCompositeBlock = (node?.type || '') === 'CompositeBlock';
      const compositeInputs = node?.data?.exposedPorts?.inputs ?? node?.data?.unusedInputs ?? node?.data?.allInputs ?? [];
      const compositeOutputs = node?.data?.exposedPorts?.outputs ?? node?.data?.unusedOutputs ?? node?.data?.allOutputs ?? [];

      // Add input ports
      const inputs = isCompositeBlock ? compositeInputs : (node.data?.input_variables || node.data?.inputs || []);
      inputs.forEach((input: any) => {
        const portName = typeof input === 'string' ? input : (input.name || input);
        const fullId = `${node.id}.${portName}`;
        ports.push({ modelName, portName, fullId, type: 'input' });
      });

      // Add output ports
      const outputs = isCompositeBlock ? compositeOutputs : (node.data?.output_variables || node.data?.outputs || []);
      outputs.forEach((output: any) => {
        const portName = typeof output === 'string' ? output : (output.name || output);
        const fullId = `${node.id}.${portName}`;
        ports.push({ modelName, portName, fullId, type: 'output' });
      });
    });
    
    return ports;
  }, [nodesForPorts, liveRfTick]);

  const isPortActive = React.useCallback((portType: 'input' | 'output') => {
    if (portSelectionMode === 'all') return false; // list hidden anyway
    if (portSelectionMode === 'modified') return true;
    if (portSelectionMode === 'output') return portType === 'output';
    if (portSelectionMode === 'input') return portType === 'input';
    return true;
  }, [portSelectionMode]);

  const setModeAndDefaults = React.useCallback((mode: PortSelectionMode) => {
    setPortSelectionMode(mode);
    if (mode === 'all') {
      // "All" exports everything; no need to keep an explicit selection.
      return;
    }
    if (mode === 'modified') {
      // Start with nothing selected; user must pick at least one.
      setSelectedPorts(new Set());
      return;
    }
    if (mode === 'output') {
      setSelectedPorts(new Set(availablePorts.filter(p => p.type === 'output').map(p => p.fullId)));
      return;
    }
    if (mode === 'input') {
      setSelectedPorts(new Set(availablePorts.filter(p => p.type === 'input').map(p => p.fullId)));
      return;
    }
  }, [availablePorts]);

  const togglePort = React.useCallback((fullId: string) => {
    setSelectedPorts(prev => {
      const next = new Set(prev);
      if (next.has(fullId)) {
        // In "modified", enforce at least one selected.
        if (portSelectionMode === 'modified' && next.size <= 1) {
          return prev;
        }
        next.delete(fullId);
      } else {
        next.add(fullId);
      }
      return next;
    });
  }, [portSelectionMode]);

  // Helpers for minimal, stylish date inputs
  const toISODate = (value: string) => {
    // Accept "DD/MM/YYYY" or "YYYY-MM-DD"; fallback to today
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(value)) {
      const [d, m, y] = value.split('/');
      return `${y}-${m}-${d}`;
    }
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
      return value;
    }
    const now = new Date();
    const yyyy = String(now.getFullYear());
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  };

  // Date defaults: end = yesterday; start = end - 30 days
  // (moved above effects)

  const mockData = {
    location: "Torino",
    startDate,
    endDate,
    scenarioName: "demo_1",
    simulationId: "SCN-2025-06",
  };

  // Shared sizing for all right-side form controls (keep columns aligned)
  const FIELD_HEIGHT = 32;

  return (
    <div
      style={{
        padding: "16px",
        borderRadius: "8px",
        fontSize: "14px",
        textAlign: "left",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        boxSizing: "border-box",
      }}
    >
      <div style={{ flexShrink: 0, marginBottom: "16px" }}>
        {Object.entries(mockData).map(([key, value]) => {
          const isDate = key === 'startDate' || key === 'endDate';
          const prettyLabel = key === 'startDate' ? 'Start date' : key === 'endDate' ? 'End date' : key;
          return (
            <div
              key={key}
              style={{
                marginBottom: "12px",
                display: "flex",
                alignItems: "center",
              }}
            >
              <label style={{ width: "120px", fontWeight: "bold" }}>{prettyLabel}:</label>
              {isDate ? (
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    flex: 1,
                    minWidth: 0,
                    width: '100%',
                  }}
                >
                  <input
                    type="date"
                    value={key === 'startDate' ? startDate : endDate}
                    onChange={(e) => {
                      if (key === 'startDate') setStartDate(e.target.value);
                      else setEndDate(e.target.value);
                    }}
                    style={{
                      flex: 1,
                      minWidth: 0,
                      padding: "6px 10px",
                      border: "1px solid #cbd5e1",
                      borderRadius: "6px",
                      backgroundColor: "#f8fafc",
                      color: "#111827",
                      height: `${FIELD_HEIGHT}px`,
                      boxSizing: "border-box",
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => {
                      const t = todayISO();
                      if (key === 'startDate') setStartDate(t);
                      else setEndDate(t);
                    }}
                    style={{
                      height: `${FIELD_HEIGHT}px`,
                      padding: "0 8px",
                      border: "1px solid #cbd5e1",
                      borderRadius: "6px",
                      backgroundColor: "white",
                      color: "#111827",
                      cursor: "pointer",
                      fontSize: 12,
                      fontWeight: 600,
                      whiteSpace: "nowrap",
                      lineHeight: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "#F9FAFB"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "white"; }}
                  >
                    Now
                  </button>
                </div>
              ) : (
                <input
                  type="text"
                  defaultValue={String(value)}
                  style={{
                    flex: 1,
                    minWidth: 0,
                    width: "100%",
                    padding: "6px 10px",
                    border: "1px solid #cbd5e1",
                    borderRadius: "6px",
                    height: `${FIELD_HEIGHT}px`,
                    boxSizing: "border-box",
                  }}
                />
              )}
            </div>
          );
        })}
      </div>
      
      <div style={{ 
        flex: 1, 
        display: "flex", 
        flexDirection: "column", 
        minHeight: 0,
        overflow: "hidden",
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10, flexShrink: 0 }}>
          <div style={{ flex: 1, borderBottom: '1px solid #e5e7eb' }} />
          <div style={{ fontSize: 13, fontWeight: 600, color: '#374151', whiteSpace: 'nowrap' }}>Output Configuration</div>
          <div style={{ flex: 1, borderBottom: '1px solid #e5e7eb' }} />
        </div>
        <div style={{ marginBottom: "10px", flexShrink: 0 }}>
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
            <label style={{ display: "flex", alignItems: "center", gap: 4, cursor: "pointer" }}>
              <input
                type="radio"
                name="portSelectionMode"
                value="all"
                checked={portSelectionMode === 'all'}
                onChange={() => setModeAndDefaults('all')}
                style={{ margin: 1 }}
              />
              <span style={{ fontSize: 13, color: "#111827" }}>All</span>
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: 4, cursor: "pointer" }}>
              <input
                type="radio"
                name="portSelectionMode"
                value="output"
                checked={portSelectionMode === 'output'}
                onChange={() => setModeAndDefaults('output')}
                style={{ margin: 1 }}
              />
              <span style={{ fontSize: 13, color: "#111827" }}>Output</span>
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: 4, cursor: "pointer" }}>
              <input
                type="radio"
                name="portSelectionMode"
                value="input"
                checked={portSelectionMode === 'input'}
                onChange={() => setModeAndDefaults('input')}
                style={{ margin: 1 }}
              />
              <span style={{ fontSize: 13, color: "#111827" }}>Input</span>
            </label>
            <label style={{
              display: "flex",
              alignItems: "center",
              gap: 4,
              cursor: "pointer",
              padding: '2px 6px',
              borderRadius: 6,
              outline: highlightModified ? '2px solid #F59E0B' : 'none',
              boxShadow: highlightModified ? '0 0 0 4px rgba(245,158,11,0.25)' : 'none',
              transition: 'outline 0.15s, box-shadow 0.15s'
            }}>
              <input
                type="radio"
                name="portSelectionMode"
                value="modified"
                checked={portSelectionMode === 'modified'}
                onChange={() => setModeAndDefaults('modified')}
                style={{ margin: 1 }}
              />
              <span style={{ fontSize: 13, color: "#111827" }}>Modified</span>
            </label>
          </div>
        </div>
        
        {portSelectionMode !== 'all' && availablePorts.length > 0 && (
          <div
            className="ports-box-scrollable"
            style={{
              flex: 1,
              overflowY: "auto",
              overflowX: "hidden",
              border: "1px solid #ddd",
              borderRadius: "4px",
              padding: "8px",
              backgroundColor: "#fafafa",
              minHeight: 0,
            }}
          >
            {availablePorts.map((port, index) => (
              <label
                key={port.fullId}
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: index === availablePorts.length - 1 ? "0" : "4px",
                  cursor: isPortActive(port.type) ? "pointer" : "not-allowed",
                  padding: "4px 6px",
                  borderRadius: "3px",
                  opacity: isPortActive(port.type) ? 1 : 0.45,
                  backgroundColor: selectedPorts.has(port.fullId) ? "#f0f0f0" : "transparent",
                  transition: "background-color 0.15s",
                }}
                onMouseEnter={(e) => {
                  if (!selectedPorts.has(port.fullId)) {
                    e.currentTarget.style.backgroundColor = "#f5f5f5";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!selectedPorts.has(port.fullId)) {
                    e.currentTarget.style.backgroundColor = "transparent";
                  }
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedPorts.has(port.fullId)}
                  disabled={!isPortActive(port.type)}
                  onChange={() => togglePort(port.fullId)}
                  style={{ 
                    marginRight: "6px", 
                    cursor: isPortActive(port.type) ? "pointer" : "not-allowed",
                    width: "14px",
                    height: "14px",
                  }}
                />
                <span style={{ fontSize: "12px", color: "#333", lineHeight: "1.4" }}>
                  <strong style={{ fontSize: "12px" }}>{port.modelName}</strong> - {port.portName} <span style={{ color: "#999", fontSize: "10px" }}>({port.type === 'input' ? 'in' : 'out'})</span>
                </span>
              </label>
            ))}
          </div>
        )}
        
        {portSelectionMode !== 'all' && availablePorts.length === 0 && (
          <div style={{ 
            color: "#999", 
            fontSize: "13px", 
            fontStyle: "italic", 
            padding: "16px", 
            flexShrink: 0,
            textAlign: "center",
            backgroundColor: "#fafafa",
            borderRadius: "4px",
            border: "1px dashed #ddd",
          }}>
            No ports available. Add models to the workspace to see available ports.
          </div>
        )}
      </div>
    </div>
  );
};

//temparory, will be replaced
const getIconByLayerName = (layer: string) => {
  const icons: Record<string, string> = {
    Casestudy_Sansalvario: "/icons/apartment.svg",
    line_wgs84: "/icons/grid.svg",
    buses_sansa: "/icons/proj_zone.svg",
  };
  return icons[layer] || "/icons/default.svg";
};
