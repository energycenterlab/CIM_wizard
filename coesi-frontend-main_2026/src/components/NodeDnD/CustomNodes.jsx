import React, { useRef, useEffect, useState, useCallback, useMemo } from "react";
import { Handle, useReactFlow, Position, useUpdateNodeInternals, useNodes, useEdges } from "@xyflow/react";
import ParamEditorModal from './ParamEditorModal';
import { createPortal } from 'react-dom';
import { useBuildingsData } from '../../lib/buildings/useBuildingsData';
import Draggable from 'react-draggable';
import { useSelector, useDispatch } from "react-redux";
import { setClickedNode } from "../../slices/clickNodeSlice";
import { deleteCompositeGroup } from "../../utils/compositeHelpers";
import { logger } from "../../utils/logger";

// Component to auto-adjust font size based on text width
const AutoSizeText = ({ text, maxWidth, baseFontSize = 16, style = {} }) => {
  const textRef = useRef(null);
  const measureRef = useRef(null);
  const [fontSize, setFontSize] = useState(baseFontSize);

  useEffect(() => {
    if (!text || !maxWidth) return;
    
    const measureText = () => {
      if (!measureRef.current) return;
      
      let currentSize = baseFontSize;
      measureRef.current.style.fontSize = `${currentSize}px`;
      let textWidth = measureRef.current.scrollWidth;
      
      // Reduce font size if text doesn't fit
      while (textWidth > maxWidth && currentSize > 8) {
        currentSize -= 0.5;
        measureRef.current.style.fontSize = `${currentSize}px`;
        textWidth = measureRef.current.scrollWidth;
      }
      
      setFontSize(currentSize);
    };
    
    // Use a small delay to ensure DOM is ready
    const timer = setTimeout(measureText, 0);
    return () => clearTimeout(timer);
  }, [text, maxWidth, baseFontSize]);

  return (
    <span style={{ position: 'relative', display: 'inline-block' }}>
      <strong 
        ref={textRef} 
        style={{ fontSize: `${fontSize}px`, ...style }}
      >
        {text}
      </strong>
      <span
        ref={measureRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          visibility: 'hidden',
          whiteSpace: 'nowrap',
          fontSize: `${baseFontSize}px`,
          fontWeight: style.fontWeight || 'bold',
          fontFamily: style.fontFamily || 'sans-serif',
          textTransform: style.textTransform || 'uppercase',
          pointerEvents: 'none'
        }}
      >
        {text}
      </span>
    </span>
  );
};


// Common Node Component
const NodeWrapper = ({ id, data, children }) => {
  const nodeRef = useRef(null);
  const [nodeHeight, setNodeHeight] = useState(80);
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      ref={nodeRef}
      style={{
        position: "relative",
        borderRadius: 5,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {typeof children === "function" ? children(nodeHeight - 30, isHovered) : children}
    </div>
  );
};

// FileReaderNode Component
export const FileReaderNode = ({ data }) => {
  const { setNodes } = useReactFlow();
  return (
    <NodeWrapper id={data.id} data={data}>
      <div style={{ 
        background: "white", 
        border: "2.5px solid #9F283E", 
        borderRadius: 12, 
        padding: 10,
        boxShadow: "0 4px 8px rgba(0,0,0,0.1)"
      }}>
        <AutoSizeText 
          text={data.label} 
          maxWidth={200 - 20} 
          baseFontSize={16}
          style={{ color: "#000000", fontFamily: "sans-serif", fontWeight: "bold", textTransform: "uppercase" }}
        />
        <br />
        <input type="file" onChange={(e) => logger.debug("File selected:", e.target.files[0])} />
        {createHandles(data.inputs, "target", "left", 100)}
        {createHandles(data.outputs, "source", "right", 100)}
      </div>
    </NodeWrapper>
  );
};
// ParamEditorNode Component
const ParamEditorNode = ({ id, data }) => {
  const { getNodes, getEdges, setNodes, setEdges } = useReactFlow();
  
  // Use reactive hooks - this ensures the component re-renders when graph topology changes
  // These are used for the totalEntities calculation to react to connection changes
  const nodes = useNodes();
  const edges = useEdges();
  
  const [isOpen, setIsOpen] = useState(false);
  
  // Get assignments to find the entity name
  const assignments = useSelector((state) => state.assignments?.assignments || []);
  const assignment = data.assignmentBatchId ? 
    assignments.find((a) => String(a.id) === String(data.assignmentBatchId)) : 
    null;

  // Calculate total entities by traversing pink connections and batch-to-model connections to find assignment batches
  // Models connected via pink ports share the same entity batch
  const totalEntities = useMemo(() => {
    logger.debug(`[totalEntities] Calculating for node ${id}`, {
      nodeData: data,
      totalNodes: nodes.length,
      totalEdges: edges.length,
      totalAssignments: assignments.length,
      assignments: assignments.map(a => ({ id: a.id, name: a.name, count: a.count, idsLength: Array.isArray(a.ids) ? a.ids.length : 0 }))
    });
    
    // Helper to check if an edge is a pink entity connection
    const isEntityEdge = (edge) => {
      if (edge?.data?.isModelToModelEntityConnection) return true;
      const sh = edge?.sourceHandle || '';
      const th = edge?.targetHandle || '';
      const looksEntity = (h) => typeof h === 'string' && (
        h.endsWith('-batch') || h.endsWith('-batch-source') || h.endsWith('-batch-target')
      );
      return looksEntity(sh) && looksEntity(th);
    };

    // Helper to find assignment batch for a node
    const findAssignmentForNode = (nodeId) => {
      logger.debug(`[findAssignmentForNode] Checking node ${nodeId}`);
      const node = nodes.find((n) => n.id === nodeId);
      if (!node) {
        logger.debug(`[findAssignmentForNode] Node ${nodeId} not found`);
        return null;
      }

      logger.debug(`[findAssignmentForNode] Node ${nodeId} data:`, {
        assignmentBatchId: node.data?.assignmentBatchId,
        name: node.data?.name || node.data?.label
      });

      // Check if node has assignmentBatchId directly
      if (node.data?.assignmentBatchId) {
        const foundAssignment = assignments.find((a) => 
          String(a.id) === String(node.data.assignmentBatchId)
        );
        logger.debug(`[findAssignmentForNode] Node ${nodeId} has direct assignmentBatchId:`, {
          assignmentBatchId: node.data.assignmentBatchId,
          foundAssignment: foundAssignment ? { id: foundAssignment.id, count: foundAssignment.count, idsLength: Array.isArray(foundAssignment.ids) ? foundAssignment.ids.length : 0 } : null
        });
        if (foundAssignment) {
          const count = foundAssignment.count || (Array.isArray(foundAssignment.ids) ? foundAssignment.ids.length : 0);
          logger.debug(`[findAssignmentForNode] Returning count ${count} from direct assignmentBatchId`);
          return count;
        }
      }

      // Check for incoming batch-to-model connections (blue dotted lines)
      // When a batch connects TO this model, the source node is the batch
      const incomingBatchEdges = edges.filter((e) => 
        e.target === nodeId && e.data?.isBatchToModel && e.source
      );
      logger.debug(`[findAssignmentForNode] Node ${nodeId} incoming batch edges:`, incomingBatchEdges.map(e => ({
        id: e.id,
        source: e.source,
        target: e.target,
        isBatchToModel: e.data?.isBatchToModel
      })));
      
      for (const edge of incomingBatchEdges) {
        const sourceNode = nodes.find((n) => n.id === edge.source);
        logger.debug(`[findAssignmentForNode] Checking incoming batch edge from ${edge.source}:`, {
          sourceNode: sourceNode ? { id: sourceNode.id, assignmentBatchId: sourceNode.data?.assignmentBatchId, name: sourceNode.data?.name } : null
        });
        if (sourceNode?.data?.assignmentBatchId) {
          const foundAssignment = assignments.find((a) => 
            String(a.id) === String(sourceNode.data.assignmentBatchId)
          );
          logger.debug(`[findAssignmentForNode] Found assignment from incoming batch edge:`, {
            assignmentBatchId: sourceNode.data.assignmentBatchId,
            foundAssignment: foundAssignment ? { id: foundAssignment.id, count: foundAssignment.count, idsLength: Array.isArray(foundAssignment.ids) ? foundAssignment.ids.length : 0 } : null
          });
          if (foundAssignment) {
            const count = foundAssignment.count || (Array.isArray(foundAssignment.ids) ? foundAssignment.ids.length : 0);
            logger.debug(`[findAssignmentForNode] Returning count ${count} from incoming batch edge`);
            return count;
          }
        }
      }

      // Check for outgoing batch-to-model connections (this node is batch connecting to a model)
      // This shouldn't happen for regular models, but check just in case
      const outgoingBatchEdges = edges.filter((e) => 
        e.source === nodeId && e.data?.isBatchToModel && e.target
      );
      logger.debug(`[findAssignmentForNode] Node ${nodeId} outgoing batch edges:`, outgoingBatchEdges.length);
      
      for (const edge of outgoingBatchEdges) {
        // If this node is the batch, it should have assignmentBatchId (already checked above)
        // But also check the target node in case it has assignmentBatchId
        const targetNode = nodes.find((n) => n.id === edge.target);
        if (targetNode?.data?.assignmentBatchId) {
          const foundAssignment = assignments.find((a) => 
            String(a.id) === String(targetNode.data.assignmentBatchId)
          );
          if (foundAssignment) {
            const count = foundAssignment.count || (Array.isArray(foundAssignment.ids) ? foundAssignment.ids.length : 0);
            logger.debug(`[findAssignmentForNode] Returning count ${count} from outgoing batch edge`);
            return count;
          }
        }
      }

      logger.debug(`[findAssignmentForNode] No assignment found for node ${nodeId}`);
      return null;
    };

    // First, check this node directly
    logger.debug(`[totalEntities] Step 1: Checking node ${id} directly`);
    const directResult = findAssignmentForNode(id);
    if (directResult !== null) {
      logger.debug(`[totalEntities] Found direct result: ${directResult}`);
      return directResult;
    }

    // Traverse all pink-connected nodes to find shared batch
    // Models connected via pink ports share the same entity batch
    logger.debug(`[totalEntities] Step 2: Traversing pink connections from node ${id}`);
    const visited = new Set();
    const queue = [id];
    visited.add(id);

    while (queue.length > 0) {
      const currentNodeId = queue.shift();
      logger.debug(`[totalEntities] Processing node ${currentNodeId} from queue`);
      
      // Check if this connected node has a batch (direct or via batch-to-model edge)
      const result = findAssignmentForNode(currentNodeId);
      if (result !== null) {
        logger.debug(`[totalEntities] Found result ${result} from pink-connected node ${currentNodeId}`);
        return result;
      }

      // Also check for batch connections on nodes connected to this node via batch-to-model edges
      // This handles the case where a batch connects to a model in the pink-connected group
      const allConnectedEdges = edges.filter((e) => 
        (e.source === currentNodeId || e.target === currentNodeId)
      );
      logger.debug(`[totalEntities] Node ${currentNodeId} has ${allConnectedEdges.length} connected edges`);
      
      for (const edge of allConnectedEdges) {
        const connectedNodeId = edge.source === currentNodeId ? edge.target : edge.source;
        
        // If it's a batch-to-model edge, check the batch node (source)
        if (edge.data?.isBatchToModel) {
          logger.debug(`[totalEntities] Found batch-to-model edge:`, {
            edgeId: edge.id,
            source: edge.source,
            target: edge.target,
            currentNodeId
          });
          const batchNodeId = edge.source; // Source is always the batch
          const batchResult = findAssignmentForNode(batchNodeId);
          if (batchResult !== null) {
            logger.debug(`[totalEntities] Found batch result ${batchResult} from batch node ${batchNodeId}`);
            return batchResult;
          }
        }
      }

      // Find all nodes connected via pink edges (shared batch group)
      const entityEdges = edges.filter((e) => 
        isEntityEdge(e) && (e.source === currentNodeId || e.target === currentNodeId)
      );
      logger.debug(`[totalEntities] Node ${currentNodeId} has ${entityEdges.length} pink entity edges`);

      for (const edge of entityEdges) {
        const connectedNodeId = edge.source === currentNodeId ? edge.target : edge.source;
        if (!visited.has(connectedNodeId)) {
          logger.debug(`[totalEntities] Adding pink-connected node ${connectedNodeId} to queue`);
          visited.add(connectedNodeId);
          queue.push(connectedNodeId);
        }
      }
    }

    logger.debug(`[totalEntities] No assignment found, returning 0`);
    return 0;
  }, [id, data.assignmentBatchId, assignments, nodes, edges]);

  const ReviewDataModal = ({ assignment, onClose }) => {
    const { features, isLoading } = useBuildingsData();
    const [allowBackgroundClose, setAllowBackgroundClose] = React.useState(false);
    const [mounted, setMounted] = React.useState(false);
    React.useEffect(() => {
      logger.debug('[ReviewDataModal] mount', { assignmentId: assignment?.id, name: assignment?.name });
      const t2 = setTimeout(() => setAllowBackgroundClose(true), 250);
      // trigger a lightweight entrance animation
      const raf = requestAnimationFrame(() => setMounted(true));
      return () => { clearTimeout(t2); logger.debug('[ReviewDataModal] unmount'); };
    }, []);
    const idSet = new Set((assignment?.ids || []).map(String));
    const rows = React.useMemo(() => (
      Array.isArray(features)
        ? features
            .filter(f => idSet.has(String(f.id)))
            .map(f => ({
              ID: String(f.id),
              Height: typeof f.height === 'number' ? f.height : undefined,
              Year: typeof f.year === 'number' ? f.year : undefined,
              Usage: (f.usage_category || f.usage_type || '') + '',
              Type: (f.building_type || '') + '',
              Surface: typeof f.surface_area === 'number' ? f.surface_area : undefined,
            }))
        : []
    ), [features, assignment]);

    React.useEffect(() => {
      logger.debug('[ReviewDataModal] data state', { isLoading, featuresCount: Array.isArray(features) ? features.length : 'n/a', rows: rows.length, allowBackgroundClose });
    }, [isLoading, features, rows.length, allowBackgroundClose]);

    const mean = (arr) => {
      const nums = arr.filter(v => typeof v === 'number' && !Number.isNaN(v));
      if (!nums.length) return null;
      return nums.reduce((a,b)=>a+b,0) / nums.length;
    };

    const analytics = {
      meanHeight: mean(rows.map(r=>r.Height)),
      avgYear: mean(rows.map(r=>r.Year)),
      meanSurface: mean(rows.map(r=>r.Surface)),
      usageDist: (()=>{
        const total = rows.length || 1;
        const counts = rows.reduce((acc,r)=>{ const k=r.Usage||'unknown'; acc[k]=(acc[k]||0)+1; return acc; },{});
        return Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([k,c])=>({k, pct: Math.round((c*10000)/total)/100}));
      })()
    };
    if (!assignment) return null;
    return createPortal(
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 99999 }} onClick={() => { logger.debug('[ReviewDataModal] backdrop click', { allowBackgroundClose }); if (allowBackgroundClose) onClose(); }}>
        <div style={{ background: 'white', width: 900, maxWidth: '92vw', maxHeight: '85vh', minHeight: 480, borderRadius: 12, overflow: 'hidden', display: 'flex', flexDirection: 'column', boxShadow: '0 10px 30px rgba(0,0,0,0.25)', opacity: mounted ? 1 : 0, transform: mounted ? 'translateY(0)' : 'translateY(6px)', transition: 'opacity 150ms ease, transform 150ms ease' }} onClick={(e) => e.stopPropagation()} onMouseDown={(e)=> e.stopPropagation()}>
          <div style={{ padding: 16, borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontWeight: 700 }}>Review Data — {assignment.name}</div>
            <button onClick={onClose} style={{ background: 'transparent', border: 'none', fontSize: 20, cursor: 'pointer' }}>×</button>
          </div>
          {/* Top: Analytics summary */}
          <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}>
            <div style={{ fontWeight: 600, marginBottom: 8 }}>Analytics Summary</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12 }}>
              <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 12 }}>
                <div style={{ color: '#6b7280', fontSize: 12 }}>Entities</div>
                <div style={{ fontWeight: 700, fontSize: 18 }}>{rows.length || assignment.count || 0}</div>
              </div>
              <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 12 }}>
                <div style={{ color: '#6b7280', fontSize: 12 }}>Mean Height</div>
                <div style={{ fontWeight: 700 }}>{analytics.meanHeight ? analytics.meanHeight.toFixed(1)+' m' : '-'}</div>
              </div>
              <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 12 }}>
                <div style={{ color: '#6b7280', fontSize: 12 }}>Avg Year</div>
                <div style={{ fontWeight: 700 }}>{analytics.avgYear ? Math.round(analytics.avgYear) : '-'}</div>
              </div>
              <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 12 }}>
                <div style={{ color: '#6b7280', fontSize: 12 }}>Mean Surface</div>
                <div style={{ fontWeight: 700 }}>{analytics.meanSurface ? analytics.meanSurface.toFixed(1)+' m²' : '-'}</div>
              </div>
            </div>
            <div style={{ marginTop: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Usage Distribution</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {analytics.usageDist.map(u => (
                  <span key={u.k} style={{ background: '#eef2ff', color: '#1f2937', borderRadius: 999, padding: '4px 10px', fontSize: 12 }}>{u.k}: {u.pct}%</span>
                ))}
              </div>
            </div>
          </div>
          {/* Bottom: Data preview */}
          <div style={{ padding: 16, overflow: 'auto', minHeight: 240 }}>
            <div style={{ fontWeight: 600, marginBottom: 8 }}>Data Preview</div>
            {isLoading ? (
              <div style={{ color: '#6b7280', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, height: 180 }}>
                <span>Loading</span>
                <div style={{ display: 'flex', gap: 4 }}>
                  {[0,1,2].map(i => (
                    <div key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: '#2563EB', animation: 'loadingDots 1.2s infinite ease-in-out both', animationDelay: `${i*0.15}s` }} />
                  ))}
                </div>
              </div>
            ) : rows.length > 0 ? (
              <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: '#f9fafb' }}>
                      {["ID","Height","Year","Usage","Type"].map((k) => (
                        <th key={k} style={{ textAlign: 'left', padding: '8px 10px', borderBottom: '1px solid #e5e7eb', fontSize: 12, color: '#374151' }}>{k}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.slice(0, 200).map((row, idx) => (
                      <tr key={idx}>
                        <td style={{ padding: '8px 10px', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>{row.ID}</td>
                        <td style={{ padding: '8px 10px', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>{row.Height ?? ''}</td>
                        <td style={{ padding: '8px 10px', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>{row.Year ?? ''}</td>
                        <td style={{ padding: '8px 10px', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>{row.Usage}</td>
                        <td style={{ padding: '8px 10px', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>{row.Type}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ color: '#6b7280' }}>No detailed rows available. This batch has {assignment.count ?? 0} entities.</div>
            )}
          </div>
          <div style={{ padding: 16, borderTop: '1px solid #eee', display: 'flex', justifyContent: 'flex-end' }}>
            <button onClick={onClose} style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 8, padding: '8px 14px' }}>Close</button>
          </div>
        </div>
      </div>,
      document.body
    );
  };

  const handleParamChange = (paramType, name, value) => {
    setNodes((nodes) =>
      nodes.map((node) =>
        node.id === id
          ? {
              ...node,
              data: {
                ...node.data,
                [paramType]: node.data[paramType].map((param) => {
                  if (param.name !== name) return param;
                  return { ...param, value };
                }),
              },
            }
          : node
      )
    );
  };

  const handleRightClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    // If this node is part of a composite group, delete the entire group
    if (data.compositeGroupId) {
      const allNodes = getNodes();
      const allEdges = getEdges();
      
      const { remainingNodes, remainingEdges } = deleteCompositeGroup(
        data.compositeGroupId,
        allNodes,
        allEdges
      );
      
      setNodes(remainingNodes);
      setEdges(remainingEdges);
      
      logger.debug(`Deleted composite group: ${data.compositeName}`);
    }
  };

  const renderParams = (paramList,  paramTypeKey) => (
    <>
      {paramList.map((param) => {
        const currentValue = param.value;

        return (
          <div key={param.name} style={{ marginBottom: 10, textAlign:"left" }}>
            <label>
              {param.name}:{" "}({param.unit})
              <input
                type="text"
                value={currentValue}
                onChange={(e) =>
                  handleParamChange(paramTypeKey, param.name, e.target.value)
                }
              />{" "}
              
            </label>
            <div style={{ fontSize: "0.85em", color: "#555" }}>
              {param.description}
            </div>
          </div>
        );
      })}
    </>
  );

  useEffect(() => {
    const handleKeyDown = (e) => {
      const isEditingInput =
        e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA";
  
      if (isOpen && isEditingInput && (e.key === "Backspace" || e.key === "Delete")) {
        e.stopPropagation(); 
      }
    };
  
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown, true);
    }
  
    return () => {
      window.removeEventListener("keydown", handleKeyDown, true);
    };
  }, [isOpen]);

  useEffect(() => {
    const allReady = getNodes().every((n) => n.data?.calculatedHeight);
    if (allReady) {
      setNodes((nodes) => [...nodes]);
    }
  }, [getNodes, setNodes]);

  // Default height stays the same; expand when there are many ports so they don't overlap.
  const inCount = Array.isArray(data.inputs) ? data.inputs.length : 0;
  const outCount = Array.isArray(data.outputs) ? data.outputs.length : 0;
  const maxPorts = Math.max(inCount, outCount);
  const baseMinHeight = data.assignmentBatchId ? 80 : 120;
  const dynMinHeight = data.assignmentBatchId ? baseMinHeight : computeExpandedHeight(baseMinHeight, maxPorts);
  const TOP_PADDING = 5;
  const BOTTOM_PADDING = -3;
  const PORT_AREA_HEIGHT = dynMinHeight - TOP_PADDING - BOTTOM_PADDING;

  return (
    <>
      <NodeWrapper id={data.id} data={data}>
        {(nodeHeight, isHovered) => (
          <div style={{ position: "relative" }}>
            {/* Main stylish yellow box */}
            <div
              onContextMenu={handleRightClick}
              style={{
                background: "white",
                padding: 10,
                width: data.assignmentBatchId ? 220 : 200,
                minHeight: dynMinHeight,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                borderRadius: 12,
                border: data.assignmentBatchId ? "2.5px solid #0069FF" : "2.5px solid #9F283E",
                boxShadow: isHovered 
                  ? "0 8px 16px rgba(255, 105, 180, 0.3), 0 4px 8px rgba(0,0,0,0.15)" 
                  : "0 4px 8px rgba(0,0,0,0.1)",
                position: "relative",
                transition: "all 0.2s ease-in-out",
                transform: isHovered ? "translateY(-2px)" : "translateY(0)",
              }}
            >
              {(() => {
                const modelName = data.assignmentBatchId ? (assignment?.name || data.name || data.label) : (data.name || data.label);
                const containerWidth = (data.assignmentBatchId ? 220 : 200) - 20; // width - padding
                return (
                  <AutoSizeText 
                    text={modelName} 
                    maxWidth={containerWidth} 
                    baseFontSize={16}
                    style={{ marginBottom: 8, color: "#000000", fontFamily: "sans-serif", fontWeight: "bold", textTransform: "uppercase" }}
                  />
                );
              })()}
              <button
                onClick={() => {
                  const isTimeseries = Array.isArray(data.tags) && data.tags.includes('timeseries');
                  const hasOutputs = (Array.isArray(data.outputs) && data.outputs.length > 0) || (Array.isArray(data.output_variables) && data.output_variables.length > 0);
                  const hasTsConfig = !!data.timeseriesConfig;
                  if (data.assignmentBatchId && assignment) {
                    window.dispatchEvent(new CustomEvent('review-data:open', { detail: { assignmentId: assignment.id } }));
                  } else if (isTimeseries && (!hasOutputs || hasTsConfig)) {
                    window.dispatchEvent(new CustomEvent('timeseries-config:open', { detail: { nodeId: id } }));
                  } else {
                    setIsOpen(true);
                  }
                }}
                style={{
                  backgroundColor: "#000000",
                  color: "#FFFFFF",
                  border: "none",
                  borderRadius: 6,
                  padding: "8px 16px",
                  fontSize: 12,
                  cursor: "pointer",
                  fontWeight: "500",
                  transition: "all 0.2s ease-in-out",
                  boxShadow: "0 2px 4px rgba(0, 0, 0, 0.3)",
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = "#333333";
                  e.target.style.transform = "translateY(-1px)";
                  e.target.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.4)";
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = "#000000";
                  e.target.style.transform = "translateY(0)";
                  e.target.style.boxShadow = "0 2px 4px rgba(0, 0, 0, 0.3)";
                }}
              >
                {data.assignmentBatchId ? 'Review Data' : 'Configuration'}
              </button>
            </div>

            {/* Top-center handle for assignment batch nodes */}
            {data.assignmentBatchId && (
              <Handle
                id={`${id}-assignment-top`}
                type="source"
                position={Position.Top}
                isConnectable={true}
                style={{
                  backgroundColor: "#FF69B4",
                  width: "14px",
                  height: "14px",
                  borderRadius: "50%",
                  border: "2px solid white",
                  zIndex: 20,
                  cursor: "crosshair",
                  pointerEvents: 'auto',
                }}
              />
            )}

            {/* Input handles with labels */}
            {data.inputs && Array.isArray(data.inputs) && data.inputs.map((input, index) => {
              const spacing = PORT_AREA_HEIGHT / (data.inputs.length + 1);
              const handleCenterY = TOP_PADDING + spacing * (index + 1);
              return (
                <Handle
                  key={input}
                  id={`${id}-${input}`}
                  type="target"
                  position={Position.Left}
                  className="port port--left"
                  data-label={input}
                  style={{
                    position: "absolute",
                    top: `${handleCenterY - 5}px`,
                    left: "-5px",
                    backgroundColor: "green",
                    width: "14px",
                    height: "14px",
                    borderRadius: "50%",
                    border: "2px solid white",
                    zIndex: 10,
                    cursor: "crosshair",
                  }}
                />
              );
            })}

            {/* Bottom entity handles (hidden for timeseries/scheduler): target + source to allow model↔model linking */}
            {!data.assignmentBatchId && !data?.tags?.includes('timeseries') && !data?.tags?.includes('scheduler') && (
              <>
              <Handle
                id={`${id}-batch-target`}
                type="target"
                position={Position.Bottom}
                isConnectable={true}
                  isValidConnection={() => true}
                style={{
                  backgroundColor: "#FF69B4",
                  width: "14px",
                  height: "14px",
                  borderRadius: "50%",
                  border: "2px solid white",
                  zIndex: 20,
                  cursor: "crosshair",
                  pointerEvents: 'auto',
                    position: 'absolute',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    bottom: '-6px',
                }}
              />
                {/* Invisible overlay source handle shares same position; enables dragging from the same spot without showing a second dot */}
                <Handle
                  id={`${id}-batch-source`}
                  type="source"
                  position={Position.Bottom}
                  isConnectable={true}
                  isValidConnection={() => true}
                  style={{
                    backgroundColor: "transparent",
                    width: "14px",
                    height: "14px",
                    borderRadius: "50%",
                    border: "none",
                    zIndex: 21,
                    cursor: "crosshair",
                    pointerEvents: 'auto',
                    position: 'absolute',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    bottom: '-6px',
                  }}
                />
              </>
            )}

            {/* Output handles with labels */}
            {data.outputs && Array.isArray(data.outputs) && data.outputs.map((output, index) => {
              const spacing = PORT_AREA_HEIGHT / (data.outputs.length + 1);
              const handleCenterY = TOP_PADDING + spacing * (index + 1);
              return (
                <Handle
                  key={output}
                  id={`${id}-${output}`}
                  type="source"
                  position={Position.Right}
                  className="port port--right"
                  data-label={output}
                  style={{
                    position: "absolute",
                    top: `${handleCenterY - 5}px`,
                    right: "-5px",
                    backgroundColor: "red",
                    width: "14px",
                    height: "14px",
                    borderRadius: "50%",
                    border: "2px solid white",
                    zIndex: 10,
                    cursor: "crosshair",
                  }}
                />
              );
            })}
          </div>
        )}
      </NodeWrapper>

      {isOpen && !data.assignmentBatchId && (
        <ParamEditorModal nodeId={id} totalEntities={totalEntities} onClose={() => setIsOpen(false)} />
      )}
    </>
  );
};

const ComplexModelNode = ({ data }) => {
  const [showDetails, setShowDetails] = useState(false);
  const { label, inputs = [], outputs = [] } = data;


  // Optional: prevent node deletion while modal is open
  useEffect(() => {
    const handleKeyDown = (e) => {
      const isInput = e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA";
      if (showDetails && isInput && (e.key === "Backspace" || e.key === "Delete")) {
        e.stopPropagation();
      }
    };

    if (showDetails) {
      window.addEventListener("keydown", handleKeyDown, true);
    }

    return () => {
      window.removeEventListener("keydown", handleKeyDown, true);
    };
  }, [showDetails]);

  return (
    <>
      <NodeWrapper id={data.id} data={data}>
        {() => (
          <div
            style={{
              background: "white",
              padding: 10,
              width: 200,
              height: 80,
              borderRadius: 12,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              alignItems: "center",
              border: "2.5px solid #9F283E",
              boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
            }}
          >
            <AutoSizeText 
              text={data.name || label} 
              maxWidth={200 - 20} 
              baseFontSize={16}
              style={{ color: "#000000", fontFamily: "sans-serif", fontWeight: "bold", textTransform: "uppercase" }}
            />
            <button
              onClick={() => setShowDetails(true)}
              style={{
                backgroundColor: "#000000",
                color: "#FFFFFF",
                border: "none",
                borderRadius: 6,
                padding: "6px 12px",
                fontSize: 12,
                cursor: "pointer",
                fontWeight: "500",
                transition: "all 0.2s ease-in-out",
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = "#333333";
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = "#000000";
              }}
            >
              Show Detail
            </button>

            {createHandles(inputs, "target", "left", 120)}
            {createHandles(outputs, "source", "right", 120)}
            
            {/* Bottom entity handles (hidden for timeseries/scheduler unless predefined outputs exist): target + source to allow model↔model linking */}
            {(!data?.tags?.includes('timeseries') && !data?.tags?.includes('scheduler')) || ((Array.isArray(data.outputs) && data.outputs.length>0) || (Array.isArray(data.output_variables) && data.output_variables.length>0)) ? (
              <>
            <Handle
              id={`${data.id}-batch-target`}
              type="target"
              position={Position.Bottom}
              isConnectable={true}
                  isValidConnection={() => true}
              style={{
                backgroundColor: "#FF69B4",
                width: "14px",
                height: "14px",
                borderRadius: "50%",
                border: "2px solid white",
                zIndex: 20,
                cursor: "crosshair",
                pointerEvents: 'auto',
                    position: 'absolute',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    bottom: '-6px',
              }}
            />
                {/* Invisible overlay source handle shares same position; enables dragging from the same spot without showing a second dot */}
                <Handle
                  id={`${data.id}-batch-source`}
                  type="source"
                  position={Position.Bottom}
                  isConnectable={true}
                  isValidConnection={() => true}
                  style={{
                    backgroundColor: "transparent",
                    width: "14px",
                    height: "14px",
                    borderRadius: "50%",
                    border: "none",
                    zIndex: 21,
                    cursor: "crosshair",
                    pointerEvents: 'auto',
                    position: 'absolute',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    bottom: '-6px',
                  }}
                />
              </>
            ) : null}
          </div>
        )}
      </NodeWrapper>

      {showDetails && (
        <div
          style={{
            position: "fixed",
            top: "0",
            left: "200%",
            transform: "translateX(-50%)",
            background: "white",
            padding: 20,
            borderRadius: 10,
            boxShadow: "0 5px 15px rgba(0,0,0,0.3)",
            maxHeight: "80vh",
            overflowY: "auto",
            width: 400,
            zIndex: 9999,
          }}
        >

        <div style={{ textAlign: "right"}}>
          <button
            onClick={() => setShowDetails(false)}
            style={{
              borderRadius: 200,
              backgroundColor: "red",
              color: "white",
              border: "none",
              width: 20,
              height: 20,
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            x
          </button>
        </div>


          <h3>Details for: {label}</h3>

          <div className="mb-4">
  <strong>Components:</strong>
      {Object.entries(data.components).map(([layerName, components]) => (
        <div key={layerName} style={{ marginBottom: 8, textAlign:'left' }}>
          <div style={{ marginBottom: 4 }}>{layerName}:</div>
          <ul style={{ paddingLeft: 20 }}>
            {components.map((id, idx) => (
              <li key={idx}>{id}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>

      <div className="mb-4">
        <strong>Connections:</strong>
        <ul style={{ paddingLeft: 20, marginTop: 5 }}>
          {data.connections.map((conn, i) => (
            <li key={i}>
              {conn.from} ({conn.output_from}) → {conn.to} ({conn.input_to})
            </li>
          ))}
        </ul>
      </div>
    </div>
    )}
    </>
  );
};

const createCornerHandles = (data, height, width) => {
  return (
    <>
      {createHandles(data.inputsTop, "target", "top", height)}
      {createHandles(data.inputsLeft, "target", "left", height)}
      {createHandles(data.outputsRight, "source", "right", height)}
      {createHandles(data.outputsBottom, "source", "bottom", height)}
    </>
  );
};

export const SimulatorNode = ({ id, data }) => {
  const dispatch = useDispatch()
  const [isSelected, setIsSelected] = useState(false);

  const handleClick = (e) => {
    if (e.button === 0) { // left-click only
      setIsSelected(!isSelected);
      logger.debug(`Node clicked: ${id}`);
      dispatch(setClickedNode(id))
    }
  };

  return (
    <NodeWrapper id={id} data={data}>
      {() => (
        <div
          onClick={handleClick}
          style={{
            background: "white", 
            padding: 10,
            width: 160,
            height: 60,
            borderRadius: 12,
            border: "2.5px solid #9F283E",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontWeight: "bold",
            cursor: "pointer",
            boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
          }}
        >
          <AutoSizeText 
            text={data.label} 
            maxWidth={160 - 20} 
            baseFontSize={16}
            style={{ color: "#000000", fontFamily: "sans-serif", fontWeight: "bold", textTransform: "uppercase" }}
          />
          {createCornerHandles(data, 60, 160)}
        </div>
      )}
    </NodeWrapper>
  );
};


export const FeatureNode = ({ id, data }) => {
  const [isSelected, setIsSelected] = useState(false);
  const dispatch = useDispatch()

  const handleClick = (e) => {
    if (e.button === 0) { // left-click only
      setIsSelected(!isSelected);
      logger.debug(`Node clicked: ${id}`);
      dispatch(setClickedNode(id))
    }
  };

   return (
    <NodeWrapper id={id} data={data}>
      {() => (
        <div
          onClick={handleClick}
          style={{
            background: "white",
            padding: 10,
            width: 160,
            height: 40,
            borderRadius: 12,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontWeight: "bold",
            cursor: "pointer",
            border: "4px solid #9F283E",
            boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
          }}
        >
          <AutoSizeText 
            text={data.name} 
            maxWidth={160 - 20} 
            baseFontSize={16}
            style={{ color: "#000000", fontFamily: "sans-serif", fontWeight: "bold", textTransform: "uppercase" }}
          />
          {createCornerHandles(data, -40, 160)}
        </div>
      )}
    </NodeWrapper>
  );
};

// Create handles for inputs and outputs
const createHandles = (ports, type, position, height) => {
  if (!ports || !Array.isArray(ports) || ports.length === 0) return null;
  
  return ports.map((port, index) => (
    <Handle
      key={`${type}-${port}-${index}`}
      id={port} // This is the port name that will be used in validation
      type={type}
      position={position}
      className={`port port--${position}`}
      data-label={port}
      style={{
        background: "#FF69B4",
        width: 14,
        height: 14,
        border: "2px solid white",
        top: position === "left" || position === "right" ? 
          `${20 + (index * (height / Math.max(ports.length, 1)))}px` : 
          position === "top" ? `${10 + (index * 30)}px` : 
          `${height - 10 - (index * 30)}px`,
        left: position === "left" ? "-6px" : 
              position === "right" ? "auto" : 
              `${10 + (index * 30)}px`,
        right: position === "right" ? "-6px" : "auto",
      }}
    />
  ));
};

// Keep default node height, but expand when many ports exist so handles don't overlap
const computeExpandedHeight = (baseHeight, portCount, threshold = 7, stepPx = 18) => {
  const n = typeof portCount === 'number' ? portCount : 0;
  if (n <= threshold) return baseHeight;
  return baseHeight + (n - threshold) * stepPx;
};

// Composite Block Node Component
const CompositeBlockNode = ({ id, data }) => {
  const { setNodes } = useReactFlow();
  const updateNodeInternals = useUpdateNodeInternals();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('ports'); // 'schema' | 'ports' | 'json'
  const [exposedPorts, setExposedPorts] = useState(data.exposedPorts || {
    inputs: data.unusedInputs || [],
    outputs: data.unusedOutputs || []
  });
  const [bindingModels, setBindingModels] = useState(Array.isArray(data.bindingModels) ? data.bindingModels : []);
  const initialName = (data?.compositeName || data?.name || data?.label || '').toString();
  const [draftName, setDraftName] = useState(initialName);
  const originalNameRef = useRef(initialName);
  const originalPortsRef = useRef(exposedPorts);
  const originalBindingRef = useRef(bindingModels);
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false);

  // Keep draft name in sync when not editing (e.g. external updates)
  useEffect(() => {
    if (isModalOpen) return;
    const next = (data?.compositeName || data?.name || data?.label || '').toString();
    setDraftName(next);
    originalNameRef.current = next;
  }, [data?.compositeName, data?.name, data?.label, isModalOpen]);

  // Helper: detect binding groups (models connected via pink entity edges)
  const findBindingGroups = useCallback((nodes, edges) => {
    const isEntityEdge = (edge) => {
      if (edge?.data?.isModelToModelEntityConnection) return true;
      const sh = edge?.sourceHandle || '';
      const th = edge?.targetHandle || '';
      const looksEntity = (h) => typeof h === 'string' && (
        h.endsWith('-batch') || h.endsWith('-batch-source') || h.endsWith('-batch-target')
      );
      return looksEntity(sh) && looksEntity(th);
    };

    const bindable = nodes.filter(n => {
      const tags = n?.data?.tags || [];
      return !tags.includes('timeseries') && !tags.includes('scheduler');
    });

    const visited = new Set();
    const groups = [];
    const byId = new Map(bindable.map(n => [n.id, n]));

    bindable.forEach(n => {
      if (visited.has(n.id)) return;
      const stack = [n.id];
      const group = [];
      while (stack.length) {
        const cur = stack.pop();
        if (visited.has(cur)) continue;
        if (!byId.has(cur)) continue;
        visited.add(cur);
        group.push(cur);
        edges.forEach(e => {
          if (!isEntityEdge(e)) return;
          if (e.source === cur && !visited.has(e.target)) stack.push(e.target);
          if (e.target === cur && !visited.has(e.source)) stack.push(e.source);
        });
      }
      if (group.length > 0) groups.push(group);
    });
    return groups;
  }, []);

  // Generate composite JSON
  const generateCompositeJSON = () => {
    const nodes = data.nodes || data.originalComposite?.nodes || [];
    const edges = data.edges || data.originalComposite?.edges || [];
    
    // Extract component names
    const components = nodes.map(n => n.data?.name || n.data?.label || n.data?.modelDefId || n.id).filter(Boolean);
    
    // Extract connections from edges
    const connections = edges.map(edge => {
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);
      if (sourceNode && targetNode) {
        const sourceName = sourceNode.data?.name || sourceNode.data?.label || sourceNode.data?.modelDefId || sourceNode.id;
        const targetName = targetNode.data?.name || targetNode.data?.label || targetNode.data?.modelDefId || targetNode.id;
        return `${sourceName}.${edge.sourceHandle}:${targetName}.${edge.targetHandle}`;
      }
      return null;
    }).filter(Boolean);

    // Get exposed ports for possible connections
    const possibleConnections = [
      ...(exposedPorts.inputs || []),
      ...(exposedPorts.outputs || []),
      ...bindingModels
    ].filter(Boolean);

    // Generate input/output variables from exposed ports
    const inputVariables = (exposedPorts.inputs || []).map(port => ({
      name: port,
      description: `Input port: ${port}`,
      unit: "",
      start_value: "0",
      data_type: "float",
      hidden: false,
      range: { min: "0", max: "none" },
      tags: []
    }));

    const outputVariables = (exposedPorts.outputs || []).map(port => ({
      name: port,
      description: `Output port: ${port}`,
      unit: "",
      start_value: "0",
      data_type: "float",
      hidden: false,
      range: { min: "0", max: "none" },
      tags: []
    }));

    const compositeName = data.name || components.join('+');
    const tags = components.map(c => c.toLowerCase()).concat(['composite-model']);

    return {
      name: compositeName,
      description: `composite model of ${components.join('+')}`,
      tags: tags,
      solver: null,
      model_execution_cmd: null,
      simulator_names: [],
      simulation_parameters: [],
      input_variables: inputVariables,
      output_variables: outputVariables,
      model_parameters: [],
      components: components,
      connections: connections,
      possible_connections: possibleConnections
    };
  };

  const handleConfigClick = (e) => {
    e.stopPropagation();
    setActiveTab('ports');
    // Snapshot originals for unsaved-changes detection
    originalNameRef.current = (data?.compositeName || data?.name || data?.label || '').toString();
    originalPortsRef.current = data.exposedPorts || {
      inputs: data.unusedInputs || [],
      outputs: data.unusedOutputs || []
    };
    originalBindingRef.current = Array.isArray(data.bindingModels) ? data.bindingModels : [];
    setDraftName(originalNameRef.current);
    setShowUnsavedDialog(false);
    setIsModalOpen(true);
  };

  const handlePortToggle = (portType, portName) => {
    setExposedPorts(prev => ({
      ...prev,
      [portType]: prev[portType].includes(portName) 
        ? prev[portType].filter(p => p !== portName)
        : [...prev[portType], portName]
    }));
  };

  const handleBindingToggle = (modelName) => {
    setBindingModels((prev) => prev.includes(modelName)
      ? prev.filter((m) => m !== modelName)
      : [...prev, modelName]
    );
  };

  const handleSaveAll = () => {
    const sanitizedName = String(draftName || '').replace(/\s+/g, '');
    const finalName = sanitizedName !== '' ? sanitizedName : (originalNameRef.current || 'composite');
    // Persist exposed ports and binding models into node.data
    // Persist also bindingGroupsNodeIds for stability if needed
    const nodesArr = (data.nodes && Array.isArray(data.nodes)) ? data.nodes : (data.originalComposite?.nodes || []);
    const edgesArr = (data.edges && Array.isArray(data.edges)) ? data.edges : (data.originalComposite?.edges || []);
    const bindingGroupsNodeIds = findBindingGroups(nodesArr, edgesArr);
    setNodes((nodes) => nodes.map((n) => (
      n.id === id
        ? { ...n, data: { ...n.data, exposedPorts, bindingModels, bindingGroupsNodeIds, compositeName: finalName, label: finalName, name: finalName } }
        : n
    )));
    // Ensure React Flow recalculates handle bounds for this node
    setTimeout(() => updateNodeInternals(id), 0);
    setShowUnsavedDialog(false);
    setIsModalOpen(false);
  };

  const handleDiscardAndClose = () => {
    // Reset to original state
    const origPorts = originalPortsRef.current || {
      inputs: data.unusedInputs || [],
      outputs: data.unusedOutputs || []
    };
    const origBindings = Array.isArray(originalBindingRef.current) ? originalBindingRef.current : [];
    setExposedPorts(origPorts);
    setBindingModels(origBindings);
    // Revert any live-preview changes written into node.data while modal was open
    setNodes((nodes) => nodes.map((n) => (
      n.id === id
        ? { ...n, data: { ...n.data, exposedPorts: origPorts, bindingModels: origBindings } }
        : n
    )));
    setDraftName((originalNameRef.current || '').toString());
    setShowUnsavedDialog(false);
    setIsModalOpen(false);
  };

  const hasUnsavedChanges = useMemo(() => {
    const normArr = (a) => (Array.isArray(a) ? [...a].map(String).sort() : []);
    const portsNow = { inputs: normArr(exposedPorts?.inputs), outputs: normArr(exposedPorts?.outputs) };
    const portsOrig = { inputs: normArr(originalPortsRef.current?.inputs), outputs: normArr(originalPortsRef.current?.outputs) };
    const bindsNow = normArr(bindingModels);
    const bindsOrig = normArr(originalBindingRef.current);
    const nameNow = String(draftName || '').replace(/\s+/g, '');
    const nameOrig = String(originalNameRef.current || '').replace(/\s+/g, '');
    return (
      JSON.stringify(portsNow) !== JSON.stringify(portsOrig) ||
      JSON.stringify(bindsNow) !== JSON.stringify(bindsOrig) ||
      nameNow !== nameOrig
    );
  }, [exposedPorts, bindingModels, draftName]);

  const attemptCloseModal = useCallback(() => {
    if (hasUnsavedChanges) {
      setShowUnsavedDialog(true);
      return;
    }
    setIsModalOpen(false);
  }, [hasUnsavedChanges]);

  const handleDownload = () => {
    const jsonData = generateCompositeJSON();
    const jsonString = JSON.stringify(jsonData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${jsonData.name || 'composite'}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Keep handle bounds in sync while editing
  useEffect(() => {
    updateNodeInternals(id);
  }, [id, exposedPorts, bindingModels, updateNodeInternals]);

  const openModal = useCallback((tab) => {
    setActiveTab(tab);
    originalNameRef.current = (data?.compositeName || data?.name || data?.label || '').toString();
    originalPortsRef.current = data.exposedPorts || {
      inputs: data.unusedInputs || [],
      outputs: data.unusedOutputs || []
    };
    originalBindingRef.current = Array.isArray(data.bindingModels) ? data.bindingModels : [];
    setDraftName(originalNameRef.current);
    setShowUnsavedDialog(false);
    setIsModalOpen(true);
  }, [data?.compositeName, data?.name, data?.label, data?.exposedPorts, data?.unusedInputs, data?.unusedOutputs, data?.bindingModels]);

  // While the modal is open, live-preview port selections into node.data so other panels (e.g. Simulation settings)
  // can see updated exposed ports immediately. Name remains unsaved until Save.
  useEffect(() => {
    if (!isModalOpen) return;
    setNodes((nodes) => nodes.map((n) => (
      n.id === id
        ? { ...n, data: { ...n.data, exposedPorts, bindingModels } }
        : n
    )));
  }, [isModalOpen, id, exposedPorts, bindingModels, setNodes]);

  return (
    <NodeWrapper id={id} data={data}>
      {(() => {
        const inCount = Array.isArray(exposedPorts?.inputs) ? exposedPorts.inputs.length : 0;
        const outCount = Array.isArray(exposedPorts?.outputs) ? exposedPorts.outputs.length : 0;
        const dynMinHeight = computeExpandedHeight(160, Math.max(inCount, outCount));
        const TOP_PADDING = 5;
        const BOTTOM_PADDING = -3;
        const PORT_AREA_HEIGHT = dynMinHeight - TOP_PADDING - BOTTOM_PADDING;
        return (
      <div style={{ 
        background: "white", 
        border: "2.5px solid #9F283E", 
        borderRadius: 12, 
        padding: 12,
        boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
        minWidth: 350,
        minHeight: dynMinHeight,
        position: "relative",
        overflow: 'visible',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ marginBottom: 12, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <AutoSizeText 
            text={data.compositeName || data.label} 
            maxWidth={350 - 24} 
            baseFontSize={16}
            style={{ 
              fontWeight: "bold", 
              color: "#000000", 
              marginBottom: 8,
              textAlign: "center",
              width: '100%'
            }}
          />
          
          <div style={{ display: 'flex', gap: 6, justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            onClick={() => {
              openModal('schema');
            }}
              style={{
                background: "#f8f9fa",
                border: "1px solid #dee2e6",
                borderRadius: 6,
                color: "#495057",
                padding: "8px 16px",
                fontSize: 12,
                cursor: "pointer",
                fontWeight: "500",
                transition: "all 0.2s ease-in-out"
              }}
              title="Show composite schema"
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#e9ecef';
                e.currentTarget.style.border = '1px solid #cbd5e1';
                e.currentTarget.style.boxShadow = '0 2px 6px rgba(0,0,0,0.15)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#f8f9fa';
                e.currentTarget.style.border = '1px solid #dee2e6';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              Schema
            </button>
            
            <button
              onClick={handleConfigClick}
              style={{
                background: "#000000",
                border: "none",
                borderRadius: 6,
                color: "white",
                padding: "8px 16px",
                fontSize: 12,
                cursor: "pointer",
                fontWeight: "500",
                transition: "all 0.2s ease-in-out"
              }}
              title="Configure composite ports"
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#333333';
                e.currentTarget.style.boxShadow = '0 2px 6px rgba(0,0,0,0.25)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#000000';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              Config
            </button>

            <button
              onClick={() => {
                openModal('json');
              }}
              style={{
                background: "#6c757d",
                border: "none",
                borderRadius: 6,
                color: "white",
                padding: "8px 16px",
                fontSize: 12,
                cursor: "pointer",
                fontWeight: "500",
                transition: "all 0.2s ease-in-out"
              }}
              title="Show composite JSON"
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#5a6268';
                e.currentTarget.style.boxShadow = '0 2px 6px rgba(0,0,0,0.25)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#6c757d';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              JSON
            </button>
          </div>
        </div>

        {/* Input handles - only show exposed inputs */}
        {exposedPorts.inputs && Array.isArray(exposedPorts.inputs) && exposedPorts.inputs.length > 0 && exposedPorts.inputs.map((input, index) => {
          const spacing = PORT_AREA_HEIGHT / (exposedPorts.inputs.length + 1);
          const handleCenterY = TOP_PADDING + spacing * (index + 1);
          return (
            <Handle
              key={input}
              id={`${id}-${input}`}
              type="target"
              position={Position.Left}
              className="port port--left"
              data-label={input}
              isConnectable={true}
              style={{
                position: "absolute",
                top: `${handleCenterY - 5}px`,
                left: "-5px",
                backgroundColor: "green",
                width: "14px",
                height: "14px",
                borderRadius: "50%",
                border: "2px solid white",
                zIndex: 20,
                cursor: "crosshair",
                pointerEvents: 'auto',
              }}
            />
          );
        })}

        {/* Output handles - only show exposed outputs */}
        {exposedPorts.outputs && Array.isArray(exposedPorts.outputs) && exposedPorts.outputs.length > 0 && exposedPorts.outputs.map((output, index) => {
          const spacing = PORT_AREA_HEIGHT / (exposedPorts.outputs.length + 1);
          const handleCenterY = TOP_PADDING + spacing * (index + 1);
          return (
            <Handle
              key={output}
              id={`${id}-${output}`}
              type="source"
              position={Position.Right}
              className="port port--right"
              data-label={output}
              isConnectable={true}
              style={{
                position: "absolute",
                top: `${handleCenterY - 5}px`,
                right: "-5px",
                backgroundColor: "red",
                width: "14px",
                height: "14px",
                borderRadius: "50%",
                border: "2px solid white",
                zIndex: 20,
                cursor: "crosshair",
                pointerEvents: 'auto',
              }}
            />
          );
        })}

        {/* Bottom binding handles - ONE per selected binding group (e.g., "pv/building") */}
        {(() => {
          if (data.tags?.includes('timeseries') || data.tags?.includes('scheduler')) return null;
          if (!Array.isArray(bindingModels) || bindingModels.length === 0) return null;

          const nodesArr = (data.nodes && Array.isArray(data.nodes)) ? data.nodes : (data.originalComposite?.nodes || []);
          const edgesArr = (data.edges && Array.isArray(data.edges)) ? data.edges : (data.originalComposite?.edges || []);
          const persistedGroups = data.bindingGroupsNodeIds || data.originalComposite?.bindingGroupsNodeIds;
          const groups = Array.isArray(persistedGroups) && persistedGroups.length > 0
            ? persistedGroups
            : findBindingGroups(nodesArr, edgesArr);

          const selectedGroups = groups
            .map((group) => {
              const names = group.map(nodeId => {
                const node = nodesArr.find(n => n.id === nodeId);
                return node?.data?.name || node?.data?.label || node?.label || node?.modelDefId || node?.id;
              }).filter(Boolean);
              const isSelected = names.some(nm => bindingModels.includes(nm));
              return { names, isSelected };
            })
            .filter(g => g.isSelected);

          if (selectedGroups.length === 0) return null;

          return selectedGroups.map((group, index) => {
            const count = selectedGroups.length;
          const pct = ((index + 1) / (count + 1)) * 100;
          const left = `calc(${pct}% - 7px)`;
            const displayName = group.names.length > 1 ? group.names.join('/') : group.names[0];
            const safeKey = displayName.replace(/\s+/g, '_');
          return (
            <Handle
                key={`bind-group-${safeKey}`}
                id={`${id}-bind-group-${safeKey}`}
              type="target"
              position={Position.Bottom}
              className="port port--bottom"
                data-label={displayName}
              isConnectable={true}
              isConnectableEnd={true}
              isValidConnection={() => true}
              style={{
                position: 'absolute',
                left,
                bottom: '-6px',
                backgroundColor: '#FF69B4',
                width: '14px',
                height: '14px',
                borderRadius: '50%',
                border: '2px solid white',
                zIndex: 20,
                cursor: 'crosshair',
                pointerEvents: 'auto',
              }}
            />
          );
          });
        })()}
      </div>
        );
      })()}

      {/* Configuration Modal */}
      {isModalOpen && createPortal(
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 99999 }} onClick={attemptCloseModal}>
          <div style={{ background: 'white', borderRadius: 12, width: 800, maxWidth: '92vw', minHeight: 420, maxHeight: '80vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '0 10px 30px rgba(0,0,0,0.25)' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ padding: 16, borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
                <div style={{ fontWeight: 600, whiteSpace: 'nowrap' }}>Composite model</div>
                <input
                  value={draftName}
                  onChange={(e) => setDraftName(String(e.target.value || '').replace(/\s+/g, ''))}
                  onFocus={() => setDraftName('')}
                  onBlur={() => {
                    if (String(draftName || '').trim() === '') {
                      setDraftName(originalNameRef.current || '');
                    }
                  }}
                  style={{
                    flex: 1,
                    minWidth: 160,
                    maxWidth: 420,
                    padding: '6px 10px',
                    border: '1px solid #d1d5db',
                    borderRadius: 8,
                    fontSize: 13,
                    outline: 'none',
                  }}
                />
              </div>
              <button onClick={attemptCloseModal} style={{ background: 'transparent', border: 'none', fontSize: 18, cursor: 'pointer' }}>×</button>
            </div>
            <div style={{ padding: 0, display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
              {/* Tabs */}
              <div style={{ display: 'flex', gap: 0, borderBottom: '1px solid #eee' }}>
                <button onClick={() => setActiveTab('schema')} style={{ padding: '10px 14px', border: 'none', background: activeTab === 'schema' ? '#fff' : '#f7f7f7', borderBottom: activeTab === 'schema' ? '2px solid #2563eb' : '2px solid transparent', cursor: 'pointer', fontWeight: 500 }}>Schema</button>
                <button onClick={() => setActiveTab('ports')} style={{ padding: '10px 14px', border: 'none', background: activeTab === 'ports' ? '#fff' : '#f7f7f7', borderBottom: activeTab === 'ports' ? '2px solid #2563eb' : '2px solid transparent', cursor: 'pointer', fontWeight: 500 }}>Port Config</button>
                <button onClick={() => setActiveTab('json')} style={{ padding: '10px 14px', border: 'none', background: activeTab === 'json' ? '#fff' : '#f7f7f7', borderBottom: activeTab === 'json' ? '2px solid #2563eb' : '2px solid transparent', cursor: 'pointer', fontWeight: 500 }}>JSON</button>
              </div>

              {/* Body */}
              {activeTab === 'schema' && (
                <div style={{ padding: 16, flex: 1, minHeight: 0, overflow: 'auto' }}>
                  <div style={{ display: 'flex', gap: 16 }}>
                    <div style={{ flex: 1 }}>
                      <h4 style={{ margin: '8px 0' }}>Components</h4>
                      <div style={{ maxHeight: 320, overflowY: 'auto', border: '1px solid #e5e7eb', borderRadius: 6, padding: 8 }}>
                        {(data.nodes || []).map((n) => (
                          <div key={n.id} style={{ padding: '6px 8px', borderBottom: '1px dashed #eee' }}>
                            <div style={{ fontWeight: 600 }}>{n.data?.name || n.data?.label || n.id}</div>
                            <div style={{ color: '#666', fontSize: 12 }}>{n.type}</div>
                          </div>
                        ))}
                        {(!data.nodes || data.nodes.length === 0) && <div style={{ color: '#666' }}>No components</div>}
                      </div>
                    </div>
                    <div style={{ flex: 1 }}>
                      <h4 style={{ margin: '8px 0' }}>Connections</h4>
                      <div style={{ maxHeight: 320, overflowY: 'auto', border: '1px solid #e5e7eb', borderRadius: 6, padding: 8, fontFamily: 'monospace', fontSize: 12 }}>
                        {(data.edges || []).map((e) => (
                          <div key={e.id} style={{ padding: '6px 8px', borderBottom: '1px dashed #eee' }}>
                            {`${e.source}.${e.sourceHandle} -> ${e.target}.${e.targetHandle}`}
                          </div>
                        ))}
                        {(!data.edges || data.edges.length === 0) && <div style={{ color: '#666' }}>No connections</div>}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {activeTab === 'ports' && (
                <div style={{ padding: 16, flex: 1, minHeight: 0, overflow: 'hidden' }}>
                  <p style={{ color: '#666', fontSize: 14, marginTop: 0 }}>Select which ports should be exposed on the composite block:</p>
                  <div style={{ display: 'flex', gap: 16 }}>
                    <div style={{ flex: 1 }}>
                      <h4 style={{ margin: '8px 0' }}>Input Ports</h4>
                      <div style={{ height: '100%', maxHeight: 300, overflowY: 'auto', border: '1px solid #e5e7eb', borderRadius: 6, padding: 8 }}>
                        {data.allInputs?.map(input => (
                          <label key={input} style={{ display: 'block', marginBottom: 8, padding: '4px 8px', borderRadius: 4, backgroundColor: exposedPorts.inputs.includes(input) ? '#f0f9ff' : 'transparent' }}>
                            <input type="checkbox" checked={exposedPorts.inputs.includes(input)} onChange={() => handlePortToggle('inputs', input)} style={{ marginRight: 8 }} />
                            {input}
                          </label>
                        ))}
                      </div>
                    </div>
                    <div style={{ flex: 1 }}>
                      <h4 style={{ margin: '8px 0' }}>Output Ports</h4>
                      <div style={{ height: '100%', maxHeight: 300, overflowY: 'auto', border: '1px solid #e5e7eb', borderRadius: 6, padding: 8 }}>
                        {data.allOutputs?.map(output => (
                          <label key={output} style={{ display: 'block', marginBottom: 8, padding: '4px 8px', borderRadius: 4, backgroundColor: exposedPorts.outputs.includes(output) ? '#fef2f2' : 'transparent' }}>
                            <input type="checkbox" checked={exposedPorts.outputs.includes(output)} onChange={() => handlePortToggle('outputs', output)} style={{ marginRight: 8 }} />
                            {output}
                          </label>
                        ))}
                      </div>
                    </div>
                    {/* Binding Ports Column */}
                    <div style={{ flex: 1 }}>
                      <h4 style={{ margin: '8px 0' }}>Binding Port</h4>
                      <div style={{ height: '100%', maxHeight: 300, overflowY: 'auto', border: '1px solid #e5e7eb', borderRadius: 6, padding: 8 }}>
                        {(() => {
                          const nodesArr = (data.nodes && Array.isArray(data.nodes)) ? data.nodes : (data.originalComposite?.nodes || []);
                          const edgesArr = (data.edges && Array.isArray(data.edges)) ? data.edges : (data.originalComposite?.edges || []);
                          const persistedGroups = data.bindingGroupsNodeIds || data.originalComposite?.bindingGroupsNodeIds;
                          const bindingGroups = Array.isArray(persistedGroups) && persistedGroups.length > 0
                            ? persistedGroups
                            : findBindingGroups(nodesArr, edgesArr);

                          return bindingGroups.map((group, groupIndex) => {
                            const groupModelNames = group.map(nodeId => {
                              const node = nodesArr.find(n => n.id === nodeId);
                              return node?.data?.name || node?.data?.label || node?.label || node?.modelDefId || node?.id;
                            }).filter(Boolean);
                            const isGroupSelected = groupModelNames.some(name => bindingModels.includes(name));
                            const displayName = groupModelNames.length > 1 ? groupModelNames.join('/') : groupModelNames[0];
                          return (
                              <label 
                                key={`bind-group-${groupIndex}`} 
                                style={{ 
                                  display: 'block', 
                                  marginBottom: 8, 
                                  padding: '4px 8px', 
                                  borderRadius: 4, 
                                  backgroundColor: isGroupSelected ? '#fde4f2' : 'transparent',
                                  border: groupModelNames.length > 1 ? '1px solid #e0e0e0' : 'none'
                                }}
                              >
                                <input 
                                  type="checkbox" 
                                  checked={isGroupSelected} 
                                  onChange={() => {
                                    // Toggle whole group at once
                                    setBindingModels((prev) => {
                                      const hasAny = groupModelNames.some(nm => prev.includes(nm));
                                      return hasAny 
                                        ? prev.filter(nm => !groupModelNames.includes(nm))
                                        : [...prev, ...groupModelNames];
                                    });
                                  }} 
                                  style={{ marginRight: 8 }} 
                                />
                                {displayName}
                                {groupModelNames.length > 1 && (
                                  <span style={{ fontSize: '10px', color: '#666', marginLeft: 4 }}>
                                    ({groupModelNames.length} models)
                                  </span>
                                )}
                            </label>
                          );
                          });
                        })()}
                        {(!data.nodes || data.nodes.length === 0) && !(data.originalComposite?.nodes?.length) && (
                          <div style={{ color: '#666' }}>No models in composite</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {activeTab === 'json' && (
                <div style={{ padding: 16, flex: 1, minHeight: 0, overflow: 'auto' }}>
                  <div style={{ 
                    background: '#f8f9fa', 
                    border: '1px solid #e9ecef', 
                    borderRadius: 8, 
                    padding: 16, 
                    fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                    fontSize: '12px',
                    lineHeight: '1.4',
                    overflow: 'auto',
                    maxHeight: '400px'
                  }}>
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                      {JSON.stringify(generateCompositeJSON(), null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
            <div style={{ padding: 16, borderTop: '1px solid #eee', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', minHeight: 56 }}>
              {activeTab === 'ports' && (
                <div style={{ display: 'flex', gap: 8 }}>
                  <button onClick={handleDiscardAndClose} style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 8, padding: '8px 14px' }}>Cancel</button>
                  <button onClick={handleSaveAll} style={{ background: '#4A90E2', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 14px' }}>Save</button>
                </div>
              )}
              {activeTab === 'json' && (
                <button onClick={handleDownload} style={{ background: '#28a745', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 14px' }}>
                  Download model
                </button>
              )}
              {activeTab !== 'ports' && activeTab !== 'json' && hasUnsavedChanges && (
                <div style={{ display: 'flex', gap: 8 }}>
                  <button onClick={handleDiscardAndClose} style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 8, padding: '8px 14px' }}>Cancel</button>
                  <button onClick={handleSaveAll} style={{ background: '#4A90E2', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 14px' }}>Save</button>
                </div>
              )}
              {/* Schema tab: no footer buttons; bar keeps consistent height via minHeight */}
            </div>

            {showUnsavedDialog && (
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'rgba(0,0,0,0.25)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: 16,
                }}
                onClick={() => setShowUnsavedDialog(false)}
              >
                <div
                  style={{
                    background: 'white',
                    borderRadius: 12,
                    width: 420,
                    maxWidth: '92vw',
                    padding: 16,
                    boxShadow: '0 10px 30px rgba(0,0,0,0.25)',
                  }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <div style={{ fontWeight: 700, marginBottom: 8 }}>Unsaved changes</div>
                  <div style={{ color: '#4b5563', fontSize: 13, marginBottom: 14 }}>
                    You have unsaved changes. Save to keep them, or discard to close.
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                    <button
                      onClick={() => { setShowUnsavedDialog(false); }}
                      style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 8, padding: '8px 14px' }}
                    >
                      Continue editing
                    </button>
                    <button
                      onClick={() => { setShowUnsavedDialog(false); handleDiscardAndClose(); }}
                      style={{ background: 'white', border: '1px solid #d1d5db', borderRadius: 8, padding: '8px 14px' }}
                    >
                      Discard
                    </button>
                    <button
                      onClick={() => { setShowUnsavedDialog(false); handleSaveAll(); }}
                      style={{ background: '#4A90E2', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 14px' }}
                    >
                      Save
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>,
        document.body
      )}
    </NodeWrapper>
  );
};

// Export node types
export const nodeTypes = {
  filereader: FileReaderNode,
  parameditor: ParamEditorNode,
  ComplexModel: ComplexModelNode,
  simulator: SimulatorNode,
  feature: FeatureNode,
  CompositeBlock: CompositeBlockNode,
};