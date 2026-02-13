import React, { useState, useEffect, useMemo, useRef } from "react";
import { createPortal } from 'react-dom';
import { useSelector, useDispatch } from 'react-redux';
import type { RootState } from '../../main';
import { addComposite } from '../../slices/compositeModelsSlice';
import { clearGraph } from '../../slices/rfGraphSlice';
// REMOVED: clearComposites, hydrateAssignments - not needed for cleanup
import { useToast } from '../../contexts/ToastContext';
// REMOVED: setDrawerOpen - not used in this component

interface ToolItem {
  id: string;
  label: string;
  icon: string;
  special?: boolean;
}

interface ControlBarProps {
  onToolSelect: (toolId: string) => void;
  activeTool?: string | null;
  onFitToView?: () => void;
  onRunSimulation?: () => void;
  isSimulationRunning?: boolean;
  onCancelSimulation?: () => void;
}

const ControlBar: React.FC<ControlBarProps> = ({ onToolSelect, activeTool: propActiveTool, onFitToView, onRunSimulation, isSimulationRunning = false, onCancelSimulation }) => {
  const [activeTool, setActiveTool] = useState<string | null>(propActiveTool || "map");

  // Sync internal state with prop changes
  useEffect(() => {
    if (propActiveTool !== undefined) {
      setActiveTool(propActiveTool);
    }
  }, [propActiveTool]);

  const toolItems2: ToolItem[] = [
    { id: "map", label: "Map", icon: "/icons/distance_2.svg" },
    { id: "table", label: "Table", icon: "/icons/calendar_view_month.svg" },
    { id: "config", label: "Node", icon: "/icons/graph_1.svg" },
  ];

  const viewMode = (propActiveTool || activeTool);

  const handleClick = (toolId: string) => {
    setActiveTool(toolId);
    onToolSelect(toolId);
  };

  // Save button: eligibility and handler
  const { showToast } = useToast();
  const rfNodes = useSelector((s: RootState) => s.rfGraph.nodes);
  const rfEdges = useSelector((s: RootState) => s.rfGraph.edges);
  const lastEdgeId = useSelector((s: RootState) => s.rfGraph.lastEdgeId);
  const composites = useSelector((s: RootState) => s.compositeModels.composites);
  const dispatch = useDispatch();

  const isNodeView = (propActiveTool || activeTool) === 'config';

  const namingNameFor = (n: any) => {
    const d = n?.data || {};
    return (d.instanceName || d.title || d.modelName || d.name || n?.label || n?.id || '')
      .toString()
      .trim()
      .replace(/\s+/g, ' ');
  };

  type ComponentInfo = {
    nodeIds: string[];
    nodes: any[];
    edges: any[];
    autoNameFull: string;
    autoNamePreview: string;
  };

  const component: ComponentInfo = useMemo(() => {
    // Build adjacency from edges (ignore self-loops)
    const adjacency = new Map<string, Set<string>>();
    rfEdges.forEach((e: any) => {
      if (!e?.source || !e?.target || e.source === e.target) return;
      if (!adjacency.has(e.source)) adjacency.set(e.source, new Set());
      if (!adjacency.has(e.target)) adjacency.set(e.target, new Set());
      adjacency.get(e.source)!.add(e.target);
      adjacency.get(e.target)!.add(e.source);
    });

    // Seeds: selected nodes, else selected edge endpoints, else last edge endpoints
    const selectedNodeIds = rfNodes.filter((n: any) => n.selected).map((n: any) => n.id);
    const selectedEdge = rfEdges.find((e: any) => e.selected);
    const last = lastEdgeId ? rfEdges.find((e: any) => e.id === lastEdgeId) : rfEdges[rfEdges.length - 1];

    let seeds: string[] = [];
    if (selectedNodeIds.length >= 1) {
      seeds = [...selectedNodeIds];
    } else if (selectedEdge && selectedEdge.source && selectedEdge.target) {
      seeds = [selectedEdge.source, selectedEdge.target];
    } else if (last && last.source && last.target) {
      seeds = [last.source, last.target];
    }

    if (seeds.length === 0) {
      return { nodeIds: [], nodes: [], edges: [], autoNameFull: '', autoNamePreview: '' };
    }

    // BFS from seeds to find full connected component
    const visited = new Set<string>();
    const queue: string[] = [];
    seeds.forEach((id) => { if (id && !visited.has(id)) { visited.add(id); queue.push(id); } });
    while (queue.length) {
      const cur = queue.shift() as string;
      const neighbors = adjacency.get(cur);
      if (!neighbors) continue;
      neighbors.forEach((nb) => {
        if (!visited.has(nb)) {
          visited.add(nb);
          queue.push(nb);
        }
      });
    }

    const idSet = visited;
    // Filter out entity blocks (assignmentBatchId) from composite model selection
    const compNodes = rfNodes.filter((n: any) => idSet.has(n.id) && !n.data?.assignmentBatchId);
    const compEdges = rfEdges.filter((e: any) => e.source && e.target && e.source !== e.target && idSet.has(e.source) && idSet.has(e.target));

    // Stable order by x then y
    const orderedNodes = [...compNodes].sort((a: any, b: any) => {
      const ax = a.position?.x || 0;
      const ay = a.position?.y || 0;
      const bx = b.position?.x || 0;
      const by = b.position?.y || 0;
      return ax - bx || ay - by;
    });

    const tokens = orderedNodes.map((n) => namingNameFor(n)).filter(Boolean);
    let baseFull = tokens.join('+') || 'Composite';

    // Ensure unique among existing composites
    const existing = new Set(composites.map((c: any) => c.name));
    let uniqueName = baseFull;
    if (existing.has(uniqueName)) {
      let idx = 2;
      while (existing.has(`${baseFull} (${idx})`)) idx++;
      uniqueName = `${baseFull} (${idx})`;
    }

    const preview = tokens.length > 3
      ? `${tokens.slice(0, 3).join('+')} +${tokens.length - 3} more`
      : tokens.join('+');

    return {
      nodeIds: Array.from(idSet),
      nodes: compNodes,
      edges: compEdges,
      autoNameFull: uniqueName,
      autoNamePreview: preview || uniqueName,
    };
  }, [rfNodes, rfEdges, lastEdgeId, composites]);

  const canSave = isNodeView && component.nodes.length >= 2 && component.edges.length >= 1;
  
  // Check if workspace is empty (no nodes or edges)
  const isWorkspaceEmpty = rfNodes.length === 0 && rfEdges.length === 0;

  const saveTitleText = canSave
    ? (component.autoNamePreview ? `Will save as: ${component.autoNamePreview}` : 'Ready to save')
    : ((propActiveTool || activeTool) !== 'config'
      ? 'Available in Node Editor'
      : 'Drop ≥2 nodes and connect a port pair');

  // Portal tooltip for Save button
  const saveBtnRef = useRef<HTMLButtonElement>(null);
  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipPos, setTooltipPos] = useState<{ left: number; top: number }>({ left: 0, top: 0 });

  // Clean up workspace state
  const [showCleanupDialog, setShowCleanupDialog] = useState(false);
  const cleanupBtnRef = useRef<HTMLButtonElement>(null);
  const [showCleanupTooltip, setShowCleanupTooltip] = useState(false);
  const [cleanupTooltipPos, setCleanupTooltipPos] = useState<{ left: number; top: number }>({ left: 0, top: 0 });

  const handleSaveMouseEnter = () => {
    const rect = saveBtnRef.current?.getBoundingClientRect();
    if (rect) {
      setTooltipPos({ left: rect.left + rect.width / 2, top: rect.top - 8 });
      setShowTooltip(true);
    }
  };
  const handleSaveMouseLeave = () => setShowTooltip(false);

  const onSave = () => {
    if (!canSave) return;
    const selNodes = component.nodes;
    const selEdges = component.edges;
    if (selNodes.length < 2) return;
    const minX = Math.min(...selNodes.map((n: any) => n.position?.x || 0));
    const minY = Math.min(...selNodes.map((n: any) => n.position?.y || 0));
    const nodesPayload = selNodes.map((n: any) => ({
      id: n.id,
      modelDefId: n.data?.modelDefId || n.data?.name || n.type,
      type: n.type,
      label: n.data?.label || n.data?.name || n.id,
      params: n.data?.params,
      width: n.width,
      height: n.height,
      relativeX: (n.position?.x || 0) - minX,
      relativeY: (n.position?.y || 0) - minY,
      inputs: n.data?.inputs,
      outputs: n.data?.outputs,
      data: n.data,
      style: n.style,
      className: n.className,
    }));
    const edgesPayload = selEdges.map((e: any) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      sourceHandle: e.sourceHandle,
      targetHandle: e.targetHandle,
      type: e.type,
      style: e.style,
      markerEnd: e.markerEnd,
    }));
    dispatch(addComposite({ id: `${Date.now()}`, name: component.autoNameFull || 'Composite', createdAt: new Date().toISOString(), nodes: nodesPayload, edges: edgesPayload } as any));
    showToast && showToast(`Saved configuration: ${component.autoNameFull || 'Composite'}`, 'success', 2500);
  };

  const onSaveKey = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    if (!canSave) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSave();
    }
  };

  // Fit to view functionality
  const handleFitToView = () => {
    if (!isNodeView) return;
    // For now, we'll use a simple approach - dispatch a custom event
    // that the ReactFlow component can listen to
    window.dispatchEvent(new CustomEvent('fitToView'));
  };

  // Clean up workspace functionality
  const handleCleanupMouseEnter = () => {
    const rect = cleanupBtnRef.current?.getBoundingClientRect();
    if (rect) {
      setCleanupTooltipPos({ left: rect.left + rect.width / 2, top: rect.top - 8 });
      setShowCleanupTooltip(true);
    }
  };
  const handleCleanupMouseLeave = () => setShowCleanupTooltip(false);

  const handleCleanupClick = () => {
    if (isWorkspaceEmpty) return;
    setShowCleanupDialog(true);
  };

  const handleCleanupConfirm = () => {
    // Clear dropped models and layers, NOT user-created batches and composites
    try {
      // Clear the ReactFlow workspace (dropped models and connections)
      localStorage.removeItem('reactflow-nodes');
      localStorage.removeItem('reactflow-edges');
    } catch {}
    
    // Clear Redux state for layers tab (rfGraph contains dropped models)
    dispatch(clearGraph()); // This clears rfNodes and rfEdges for layers tab
    
    // Dispatch a custom event to notify ReactFlow component to clear its state
    window.dispatchEvent(new CustomEvent('cleanup-workspace'));
    
    showToast && showToast('Workspace cleaned up successfully - dropped models and connections removed', 'success', 2500);
    setShowCleanupDialog(false);
  };

  const handleCleanupCancel = () => {
    setShowCleanupDialog(false);
  };

  return (
    <div className="control-bar">
      {/* Save icon button - only visible in node editor */}
      {isNodeView && (
        <>
          <button
            ref={saveBtnRef}
            onClick={onSave}
            onKeyDown={onSaveKey}
            onMouseEnter={handleSaveMouseEnter}
            onMouseLeave={handleSaveMouseLeave}
            className="control-button"
            title={saveTitleText}
            aria-label="Save composite configuration"
            disabled={!canSave}
          >
            <img src="/icons/save.svg" alt="Save" />
          </button>
          {showTooltip && createPortal(
            <div
              style={{
                position: 'fixed',
                left: tooltipPos.left,
                top: tooltipPos.top,
                transform: 'translate(-50%, -100%)',
                background: 'rgba(0,0,0,0.85)',
                color: '#fff',
                padding: '6px 8px',
                borderRadius: 6,
                fontSize: 12,
                zIndex: 20000,
                pointerEvents: 'none',
                maxWidth: 360,
                whiteSpace: 'nowrap',
              }}
            >
              {canSave ? `Will save as: ${component.autoNameFull}` : saveTitleText}
            </div>,
            document.body
          )}
        </>
      )}

      {/* Clean up workspace button - only visible in node editor */}
      {isNodeView && (
        <>
          <button
            ref={cleanupBtnRef}
            onClick={handleCleanupClick}
            onMouseEnter={handleCleanupMouseEnter}
            onMouseLeave={handleCleanupMouseLeave}
            className="control-button"
            title={isWorkspaceEmpty ? "Workspace is already empty" : "Clean up workspace - remove dropped models and connections (preserves user-created batches and composites)"}
            aria-label="Clean up workspace"
            disabled={isWorkspaceEmpty}
          >
            <img src="/icon/cleaner.svg" alt="Clean up workspace" />
          </button>
          {showCleanupTooltip && createPortal(
            <div
              style={{
                position: 'fixed',
                left: cleanupTooltipPos.left,
                top: cleanupTooltipPos.top,
                transform: 'translate(-50%, -100%)',
                background: 'rgba(0,0,0,0.85)',
                color: '#fff',
                padding: '6px 8px',
                borderRadius: 6,
                fontSize: 12,
                zIndex: 20000,
                pointerEvents: 'none',
                maxWidth: 360,
                whiteSpace: 'nowrap',
              }}
            >
              {isWorkspaceEmpty ? "Workspace is already empty" : "Clean up workspace - remove dropped models and connections (preserves user-created batches and composites)"}
            </div>,
            document.body
          )}
        </>
      )}

      {/* Fit to view button - only visible in node editor */}
      {isNodeView && (
        <button
          onClick={handleFitToView}
          className="control-button"
          title="Fit all elements to workspace view"
          aria-label="Fit to view"
        >
          <img src="/icons/proj_zone.svg" alt="Fit to view" />
        </button>
      )}

      {/* Select icon button - safe zone mode */}
      <button
        onClick={() => {}}
        className="control-button"
        title="Select mode - safe zone for navigation without activating other tools"
        aria-label="Select mode"
      >
        <img src="/icons/arrow_selector_tool.svg" alt="Select" />
      </button>

      <div className="vertical-divider">
        <img src="/icons/vertical_divider.svg" alt="divider" />
      </div>

      {toolItems2.map((tool) => (
        <button
          key={tool.id}
          onClick={() => handleClick(tool.id)}
          className={`control-button ${tool.special ? "run" : ""} ${
            activeTool === tool.id ? "active" : ""
          }`}
          title={tool.label}
        >
          <img src={tool.icon} alt={tool.label} />
          {tool.special && <span style={{ marginLeft: 8 }}>{tool.label}</span>}
        </button>
      ))}


      <div className="vertical-divider">
        <img src="/icons/vertical_divider.svg" alt="divider" />
      </div>

      {isSimulationRunning ? (
        <button
          onClick={onCancelSimulation}
          className="control-button"
          style={{ background: '#eee' }}
        >
          Cancel
        </button>
      ) : (
        <button
          onClick={onRunSimulation}
          disabled={isSimulationRunning}
          className="control-button run"
          style={{
            opacity: isSimulationRunning ? 0.5 : 1,
            cursor: isSimulationRunning ? 'not-allowed' : 'pointer'
          }}
        >
          Run <img src="/icons/fast_forward.svg" alt="run" />
        </button>
      )}

      {/* Clean up workspace confirmation dialog */}
      {showCleanupDialog && (
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
                Clean Up Workspace
              </div>
            </div>
            
            <div style={{ fontSize: 13, color: '#374151', marginBottom: 20, lineHeight: '1.5' }}>
              Are you sure you want to clean the workspace? This will remove all dropped models and connections, but preserve your user-created batches and composite models.
            </div>
            
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
              <button
                onClick={handleCleanupCancel}
                style={{
                  border: '1px solid #e5e7eb',
                  background: '#fff',
                  color: '#374151',
                  borderRadius: 8,
                  padding: '8px 16px',
                  fontSize: 14,
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'background-color 0.2s, border-color 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f9fafb';
                  e.currentTarget.style.borderColor = '#d1d5db';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#fff';
                  e.currentTarget.style.borderColor = '#e5e7eb';
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleCleanupConfirm}
                style={{
                  border: '1px solid #dc2626',
                  background: '#dc2626',
                  color: 'white',
                  borderRadius: 8,
                  padding: '8px 16px',
                  fontSize: 14,
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'background-color 0.2s, border-color 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#b91c1c';
                  e.currentTarget.style.borderColor = '#b91c1c';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#dc2626';
                  e.currentTarget.style.borderColor = '#dc2626';
                }}
              >
                Clean Up
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ControlBar;
