// @ts-nocheck
import React, { useRef, useCallback, useState, useEffect, useMemo } from "react";
import {
  ReactFlow,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  useReactFlow,
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  useUpdateNodeInternals,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import './ControlBar.css';

import axios from 'axios';
import Select from 'react-select';

// removed: import fakedata from '../../constants/final-format-1.json'
import { apiService } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

import SidebarLeft from "./SidebarLeft";
//import SidebarRight from "./SidebarRight";

import Legend from "./Legend";
import { useDnD } from './DnDContext';
import { nodeTypes } from "./CustomNodes";
import CustomEdge from "./CustomEdge";
import ConnectionDetailsModal from "./ConnectionDetailsModal";
// REMOVED: Frontend registry imports - now using backend-driven approach
// import { getDefaultParams, normalizeModelId } from './modelRegistry';
import { useDispatch, useSelector } from 'react-redux';
import { setSelectedNodeData } from '../../slices/clickNodeSlice';
import { clearClickedF } from '../../slices/clickedFSlice';
import { setGraph, setLastEdgeId } from '../../slices/rfGraphSlice';
import { cloneNodes, cloneEdges, warnIfFrozen } from '../../utils/cloneUtils';
import ReactFlowErrorBoundary from './ReactFlowErrorBoundary';


const DEFAULT_ZOOM = 0.75; // Default zoom level

const DnDFlowForSce = ({ isLocked = false }) => {
  
const initialNodes = [];
const initialEdges = [];
  //const initialNodes = [];
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const { screenToFlowPosition, fitView } = useReactFlow();
  const updateNodeInternals = useUpdateNodeInternals();
  const [type] = useDnD();
  const dispatch = useDispatch();
  const { showToast } = useToast();
  
  // Connection details modal state
  const [connectionModalVisible, setConnectionModalVisible] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState(null);
  
  // Debug: Monitor type changes (disabled to reduce noise)
  // useEffect(() => {
  //   if (type) {
  //     console.log('🔧 DnD type changed:', type);
  //   }
  // }, [type]);

  // Debounce mechanism to prevent rapid-fire updates
  const nodesChangeTimeoutRef = useRef(null);
  
  // Ultra-fast nodes change handler - minimal processing for position changes
  const handleNodesChange = useCallback((changes) => {
    try {
      // Skip all processing for position-only changes - let ReactFlow handle it directly
      const isPositionOnly = changes.every(change => change.type === 'position');
      
      if (isPositionOnly) {
        // For position changes, just apply directly without any debouncing or cloning
        setNodes((nds) => applyNodeChanges(changes, nds));
        return;
      }
      
      // Only process meaningful changes
      const meaningfulChanges = changes.filter(change => 
        change.type !== 'position' && 
        change.type !== 'select' &&
        change.type !== 'dimensions'
      );
      
      if (meaningfulChanges.length > 0) {
        console.log('🔄 Meaningful nodes change:', meaningfulChanges);
      }
      
      // Clear existing timeout
      if (nodesChangeTimeoutRef.current) {
        clearTimeout(nodesChangeTimeoutRef.current);
      }
      
      // Only debounce non-position changes
      nodesChangeTimeoutRef.current = setTimeout(() => {
        setNodes((nds) => {
          const clonedNodes = cloneNodes(nds);
          const updated = applyNodeChanges(changes, clonedNodes);
          
          if (updated.length !== nds.length) {
            console.log('🔄 Nodes count changed:', { from: nds.length, to: updated.length });
          }
          
          return updated;
        });
      }, 200);
      
    } catch (error) {
      console.error('🚨 Error in handleNodesChange:', error);
      console.error('Changes that caused error:', changes);
      showToast('Error updating nodes', 'error');
    }
  }, [setNodes, showToast]);

  // Locked wrappers to prevent modifications while running

  // Debounce mechanism for edges
  const edgesChangeTimeoutRef = useRef(null);
  
  // Custom edges change handler that ensures mutable objects
  const handleEdgesChange = useCallback((changes) => {
    try {
      // Only log meaningful edge changes
      const meaningfulChanges = changes.filter(change => 
        change.type !== 'select'
      );
      
      if (meaningfulChanges.length > 0) {
        console.log('🔄 Meaningful edges change:', meaningfulChanges);
      }
      
      // Clear existing timeout
      if (edgesChangeTimeoutRef.current) {
        clearTimeout(edgesChangeTimeoutRef.current);
      }
      
      // Debounce the update
      edgesChangeTimeoutRef.current = setTimeout(() => {
        setEdges((eds) => {
          // Clone current edges to ensure they're mutable
          const clonedEdges = cloneEdges(eds);
          const updated = applyEdgeChanges(changes, clonedEdges);
          
          // Only log if there are actual structural changes
          if (updated.length !== eds.length) {
            console.log('🔄 Edges count changed:', { from: eds.length, to: updated.length });
          }
          
          return updated;
        });
      }, 200); // 200ms debounce for better performance
      
    } catch (error) {
      console.error('🚨 Error in handleEdgesChange:', error);
      console.error('Changes that caused error:', changes);
      showToast('Error updating edges', 'error');
    }
  }, [setEdges, showToast]);

  const onNodesChangeSafe = useCallback((changes) => {
    if (isLocked) return;
    handleNodesChange(changes);
  }, [isLocked, handleNodesChange]);

  const onEdgesChangeSafe = useCallback((changes) => {
    if (isLocked) return;
    handleEdgesChange(changes);
  }, [isLocked, handleEdgesChange]);

  // For connect/drop/dragover, bind conditionally in JSX to avoid TDZ on dependencies

  // Redux selectors for syncing with Redux state
  const rfNodes = useSelector((state) => state.rfGraph?.nodes || []);
  const rfEdges = useSelector((state) => state.rfGraph?.edges || []);
  
  // Smart one-way sync: ReactFlow -> Redux (immediate for structural changes)
  const lastSyncedRef = useRef({ nodes: [], edges: [] });
  
  // Expose ReactFlow state to global scope for export access
  useEffect(() => {
    window.reactFlowState = { nodes, edges };
    try {
      window.dispatchEvent(new CustomEvent('reactflow:state-updated'));
    } catch {}
  }, [nodes, edges]);
  
  useEffect(() => {
    // Only sync if there are structural changes (not position changes)
    const hasStructuralChanges = 
      nodes.length !== lastSyncedRef.current.nodes.length ||
      edges.length !== lastSyncedRef.current.edges.length ||
      nodes.some((node, index) => {
        const lastNode = lastSyncedRef.current.nodes[index];
        return !lastNode || node.id !== lastNode.id || node.type !== lastNode.type;
      }) ||
      edges.some((edge, index) => {
        const lastEdge = lastSyncedRef.current.edges[index];
        return !lastEdge || edge.id !== lastEdge.id || edge.source !== lastEdge.source || edge.target !== lastEdge.target;
      });
    
    if (hasStructuralChanges) {
      // IMMEDIATE sync for structural changes (no debounce)
      const clonedNodes = cloneNodes(nodes);
      const clonedEdges = cloneEdges(edges);
      dispatch(setGraph({ nodes: clonedNodes, edges: clonedEdges }));
      
      // Update the reference immediately
      lastSyncedRef.current = {
        nodes: nodes.map(n => ({ id: n.id, type: n.type })),
        edges: edges.map(e => ({ id: e.id, source: e.source, target: e.target }))
      };
    }
  }, [nodes, edges, dispatch]);
  
  // One-way sync: Redux -> ReactFlow (only when a deletion was requested)
  const deletionSyncPendingRef = useRef(false);
  useEffect(() => {
    // Only sync if we know a deletion was requested via workspace event
    if (deletionSyncPendingRef.current && (rfNodes.length < nodes.length || rfEdges.length < edges.length)) {
      console.log('🔄 Syncing Redux deletion to ReactFlow');
      setNodes(rfNodes);
      setEdges(rfEdges);
      deletionSyncPendingRef.current = false;
    }
  }, [rfNodes, rfEdges, nodes.length, edges.length]);
  

  // Development warning for frozen objects
  // Dev warnings for frozen objects (disabled to reduce noise)
  // useEffect(() => {
  //   if (process.env.NODE_ENV === 'development' && nodes.length > 0) {
  //     warnIfFrozen(nodes[0], 'ReactFlow nodes');
  //   }
  // }, [nodes]);

  // useEffect(() => {
  //   if (process.env.NODE_ENV === 'development' && edges.length > 0) {
  //     warnIfFrozen(edges[0], 'ReactFlow edges');
  //   }
  // }, [edges]);

  // State restoration flag to prevent infinite loops
  const hasRestoredState = useRef(false);
  const isSyncingFromRedux = useRef(false);

  // Simple localStorage cache for state persistence
  useEffect(() => {
    // Load from localStorage on mount
    try {
      const cachedNodes = localStorage.getItem('reactflow-nodes');
      const cachedEdges = localStorage.getItem('reactflow-edges');
      
      if (cachedNodes && cachedEdges) {
        const nodes = JSON.parse(cachedNodes);
        const edges = JSON.parse(cachedEdges);
        
        // Only restore if we have valid data and current state is empty
        if (nodes.length > 0 && edges.length >= 0) {
          console.log('🔄 Loading cached state from localStorage:', nodes.length, 'nodes,', edges.length, 'edges');
          setNodes(nodes);
          setEdges(edges);
        }
      }
    } catch (error) {
      console.warn('Failed to load cached state:', error);
    }
  }, []); // Only run once on mount

  // Ultra-minimal caching - only save on major changes, not position changes
  const lastSaveRef = useRef({ nodes: [], edges: [] });
  const saveTimeoutRef = useRef(null);
  
  useEffect(() => {
    // Clear existing timeout
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }
    
    // Only save if there are actual structural changes
    const hasStructuralChanges = 
      nodes.length !== lastSaveRef.current.nodes.length || 
      edges.length !== lastSaveRef.current.edges.length ||
      nodes.some((node, index) => {
        const lastNode = lastSaveRef.current.nodes[index];
        return !lastNode || node.id !== lastNode.id || node.type !== lastNode.type;
      }) ||
      edges.some((edge, index) => {
        const lastEdge = lastSaveRef.current.edges[index];
        return !lastEdge || edge.id !== lastEdge.id || edge.source !== lastEdge.source || edge.target !== lastEdge.target;
      });
    
    if (hasStructuralChanges) {
      // Only save after 5 seconds of no changes
      saveTimeoutRef.current = setTimeout(() => {
        try {
          localStorage.setItem('reactflow-nodes', JSON.stringify(nodes));
          localStorage.setItem('reactflow-edges', JSON.stringify(edges));
          console.log('💾 Cached state to localStorage:', nodes.length, 'nodes,', edges.length, 'edges');
          
          // Update the reference
          lastSaveRef.current = { 
            nodes: nodes.map(n => ({ id: n.id, type: n.type })), 
            edges: edges.map(e => ({ id: e.id, source: e.source, target: e.target }))
          };
        } catch (error) {
          console.warn('Failed to cache state:', error);
        }
      }, 1000); // 1 second delay
    }

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [nodes, edges]);

  // Listen for cleanup workspace event from ControlBar
  useEffect(() => {
    const handleCleanupWorkspace = () => {
      console.log('🧹 Cleanup workspace event received - clearing ReactFlow state');
      setNodes([]);
      setEdges([]);
    };

    window.addEventListener('cleanup-workspace', handleCleanupWorkspace);
    
    return () => {
      window.removeEventListener('cleanup-workspace', handleCleanupWorkspace);
    };
  }, [setNodes, setEdges]);

  // Listen for runtime node updates from timeseries config (adds outputs, refreshes handles)
  useEffect(() => {
    const handleRuntimeNodeUpdate = (e) => {
      const id = e?.detail?.id;
      const outputs = e?.detail?.outputs;
      const output_variables = e?.detail?.output_variables;
      const name = e?.detail?.name;
      const timeseriesConfig = e?.detail?.timeseriesConfig;
      const simulation_parameters = e?.detail?.simulation_parameters;
      if (!id) return;
      console.log('🔄 rf:update-node received', { id, name, outputsLen: Array.isArray(outputs)?outputs.length:undefined });
      setNodes((nds) => nds.map((n) =>
        n.id === id
          ? {
              ...n,
              data: {
                ...n.data,
                name: typeof name === 'string' && name.trim() !== '' ? name : (n.data?.name || n.data?.label),
                outputs: Array.isArray(outputs) ? outputs : (n.data?.outputs || []),
                output_variables: Array.isArray(output_variables) ? output_variables : (n.data?.output_variables || []),
                timeseriesConfig: timeseriesConfig ? timeseriesConfig : (n.data?.timeseriesConfig || undefined),
                simulation_parameters: Array.isArray(simulation_parameters) ? simulation_parameters : (n.data?.simulation_parameters || []),
              },
            }
          : n
      ));
      try { updateNodeInternals(id); } catch {}
    };

    window.addEventListener('rf:update-node', handleRuntimeNodeUpdate);
    return () => window.removeEventListener('rf:update-node', handleRuntimeNodeUpdate);
  }, [setNodes, updateNodeInternals]);

  // Global error handler to catch unhandled errors
  useEffect(() => {
    const handleError = (error) => {
      console.error('🚨 UNHANDLED ERROR:', error);
      console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        filename: error.filename,
        lineno: error.lineno,
        colno: error.colno
      });
      
      // Show user-friendly error message
      showToast('An unexpected error occurred. Please refresh the page.', 'error');
    };

    const handleUnhandledRejection = (event) => {
      console.error('🚨 UNHANDLED PROMISE REJECTION:', event.reason);
      console.error('Promise rejection details:', event.reason);
      showToast('An unexpected error occurred. Please refresh the page.', 'error');
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [showToast]);

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      if (nodesChangeTimeoutRef.current) {
        clearTimeout(nodesChangeTimeoutRef.current);
      }
      if (edgesChangeTimeoutRef.current) {
        clearTimeout(edgesChangeTimeoutRef.current);
      }
    };
  }, []);

  const onInit = useCallback((instance) => {
    console.log('🎯 ReactFlow initialized');
    // Force our default zoom on mount (no animation)
    instance.setViewport({ x: 0, y: 0, zoom: DEFAULT_ZOOM }, { duration: 0 });
  }, []);

  // Listen for fitToView events from the ControlBar
  useEffect(() => {
    const handleFitToView = () => {
      fitView({ 
        padding: 0.1, // 10% padding around the content
        duration: 800, // Smooth animation
        minZoom: 0.1,
        maxZoom: 2
      });
    };

    window.addEventListener('fitToView', handleFitToView);
    return () => window.removeEventListener('fitToView', handleFitToView);
  }, [fitView]);

  const toolItems = [
  { id: 'select', label: 'Select', icon: '/icons/arrow_selector_tool.svg' },
  { id: 'add', label: 'Add', icon: '/icons/add_ad.svg' },
  { id: 'comment', label: 'Comment', icon: '/icons/tooltip_2.svg' },
  { id: 'zoom', label: 'Zoom', icon: '/icons/arrows_output.svg' },
  { id: 'bookmark', label: 'Bookmark', icon: '/icons/bookmark.svg' },
  { id: 'grid', label: 'Grid', icon: '/icons/calendar_view_month.svg' },
  { id: 'structure', label: 'Structure', icon: '/icons/graph_1.svg' },
  { id: 'location', label: 'Location', icon: '/icons/distance_2.svg' },
];

  const [showExportModal, setShowExportModal] = useState(false);
  const [compositeModalName, setCompositeModalName] = useState("");
  const [compositeModalDes, setCompositeModalDes] = useState("");

  // Maintain a counter for each node type
  const [nodeCounts, setNodeCounts] = useState({});
  const nodeCountsRef = useRef({});

  //for exporting and POST compositions
  const [selectedTags, setSelectedTags] = useState([]);
  const [activeTool, setActiveTool] = useState(null);


  const compositeTags = ['composite-model','control-system','thermal','feedback','power-system', 'motor-control','sensor', 'signal-processing','sensor-fusion','redundancy', 'control','power-management','multi-motor'];
  const tagOptions = compositeTags.map(tag => ({ value: tag, label: tag }));

  // removed: getSingleModel() and jsonDataSingle/jsonDataMulti

  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.key === 'Delete' || event.key === 'Backspace')) {
        setNodes((nds) => {
          const filtered = nds.filter((node) => !node.selected);
          // Update Redux with filtered nodes
          // Immediate Redux dispatch for node deletion
          const clonedNodes = cloneNodes(filtered);
          const clonedEdges = cloneEdges(edges);
          dispatch(setGraph({ nodes: clonedNodes, edges: clonedEdges }));
          return filtered;
        });
        setEdges((eds) => {
          const filtered = eds.filter((edge) => !edge.selected);
          // Update Redux with filtered edges
          // Immediate Redux dispatch for edge deletion
          const clonedNodes = cloneNodes(nodes);
          const clonedEdges = cloneEdges(filtered);
          dispatch(setGraph({ nodes: clonedNodes, edges: clonedEdges }));
          return filtered;
        });
      }
    };
  
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [setNodes, setEdges, dispatch, nodes, edges]);

  // Listen for external requests to remove nodes from the workspace (layer tab deletion)
  useEffect(() => {
    const handleRemoveNodes = (e) => {
      const ids = e?.detail?.nodeIds || [];
      if (!Array.isArray(ids) || ids.length === 0) return;

      setNodes((nds) => nds.filter((n) => !ids.includes(n.id)));
      setEdges((eds) => eds.filter((e) => !ids.includes(e.source) && !ids.includes(e.target)));

      // reflect to Redux
      // Immediate Redux dispatch for cleanup
      const clonedNodes = cloneNodes(nodes.filter((n) => !ids.includes(n.id)));
      const clonedEdges = cloneEdges(edges.filter((e) => !ids.includes(e.source) && !ids.includes(e.target)));
      dispatch(setGraph({ nodes: clonedNodes, edges: clonedEdges }));
      // Signal that a deletion sync back to ReactFlow is expected
      deletionSyncPendingRef.current = true;
    };

    window.addEventListener('workspace:remove-nodes', handleRemoveNodes);
    return () => window.removeEventListener('workspace:remove-nodes', handleRemoveNodes);
  }, [dispatch, nodes, edges, setNodes, setEdges]);

  const getId = useCallback((nodeType) => {
    // Build a set of existing IDs to guarantee uniqueness
    const existingIds = new Set((nodes || []).map((n) => n.id));

    // Start from the highest known counter for this type by scanning existing ids
    let counter = nodeCountsRef.current[nodeType] || 0;
    for (const id of existingIds) {
      if (typeof id === 'string' && id.startsWith(`${nodeType}_`)) {
        const suffix = id.slice(nodeType.length + 1);
        const parsed = parseInt(suffix, 10);
        if (!Number.isNaN(parsed) && parsed > counter) counter = parsed;
      }
    }

    // Increment until we find a free id
    let candidate;
    do {
      counter += 1;
      candidate = `${nodeType}_${counter}`;
    } while (existingIds.has(candidate));

    // Persist the counter so subsequent calls continue from here
    nodeCountsRef.current[nodeType] = counter;
    setNodeCounts((prev) => ({ ...prev, [nodeType]: counter }));
    
    return candidate;
  }, [nodes]);

  const onConnect = useCallback(
    async (params) => {
      try {
        // Only log connection attempts that will be validated
        console.log('🔗 Connection attempt:', params);
        
        // Validate params
        if (!params || !params.source || !params.target || !params.sourceHandle || !params.targetHandle) {
          console.error('❌ Invalid connection params:', params);
          showToast('Error: Invalid connection parameters', 'error');
          return;
        }
        
        // Get source and target nodes
        const sourceNode = nodes.find((n) => n.id === params.source);
        const targetNode = nodes.find((n) => n.id === params.target);
        
        if (!sourceNode || !targetNode) {
          console.error('❌ Source or target node not found:', { sourceNode, targetNode });
          showToast('Error: Could not find source or target node', 'error');
          return;
        }
        
        // Validate node data
        if (!sourceNode.data || !targetNode.data) {
          console.error('❌ Missing node data:', { sourceNode: sourceNode.data, targetNode: targetNode.data });
          showToast('Error: Missing node data', 'error');
          return;
        }

      // Skip validation for batch→model connections (entity to model)
      const isBatchToModel = !!(sourceNode.data && sourceNode.data.assignmentBatchId);
      
      // Detect model↔model entity (pink) connections via bottom handles
      const isEntityHandle = (h) => typeof h === 'string' && (
        h.endsWith('-batch') || h.endsWith('-batch-source') || h.endsWith('-batch-target')
      );
      const isModelToModelEntityConnection = !isBatchToModel && isEntityHandle(params.sourceHandle) && isEntityHandle(params.targetHandle);
      
      if (!isBatchToModel && !isModelToModelEntityConnection) {
        // Validate connection for model-to-model connections
        try {
          let sourceModel, targetModel, fromPort, toPort;
          
          // Handle composite block connections
          if (sourceNode.type === 'CompositeBlock') {
            // For composite blocks, we need to find which original model owns the port
            const compositeData = sourceNode.data;
            const portName = params.sourceHandle.split('-').pop(); // Extract port name from handle
            
            // Find which original model in the composite has this output port
            const sourceModelNode = compositeData.nodes?.find(node => 
              node.outputs && node.outputs.includes(portName)
            );
            
            if (!sourceModelNode) {
              showToast(`Port ${portName} not found in composite`, 'error');
              return;
            }
            
            sourceModel = sourceModelNode.data?.modelDefId || sourceModelNode.data?.name || sourceModelNode.modelDefId;
            fromPort = portName;
          } else {
            // Regular model nodes
            sourceModel = sourceNode.data?.modelDefId || sourceNode.data?.name;
            fromPort = params.sourceHandle.includes('-') 
              ? params.sourceHandle.split('-').pop()
              : params.sourceHandle;
          }
          
          // Handle target node (same logic for composite or regular)
          if (targetNode.type === 'CompositeBlock') {
            const compositeData = targetNode.data;
            const portName = params.targetHandle.split('-').pop();
            
            const targetModelNode = compositeData.nodes?.find(node => 
              node.inputs && node.inputs.includes(portName)
            );
            
            if (!targetModelNode) {
              showToast(`Port ${portName} not found in composite`, 'error');
              return;
            }
            
            targetModel = targetModelNode.data?.modelDefId || targetModelNode.data?.name || targetModelNode.modelDefId;
            toPort = portName;
          } else {
            // Regular model nodes
            targetModel = targetNode.data?.modelDefId || targetNode.data?.name;
            toPort = params.targetHandle.includes('-') 
              ? params.targetHandle.split('-').pop()
              : params.targetHandle;
          }
          
          // Try to pass units for timeseries-configured ports if available
          const findOutUnit = (node, port) => {
            const outs = Array.isArray(node.data?.output_variables) ? node.data.output_variables : [];
            const ov = outs.find(v => String(v.name) === String(port));
            return ov?.unit;
          };
          const findInUnit = (node, port) => {
            const ins = Array.isArray(node.data?.input_variables) ? node.data.input_variables : [];
            const iv = ins.find(v => String(v.name) === String(port));
            return iv?.unit;
          };
          const fromUnit = findOutUnit(sourceNode, fromPort);
          const toUnit = findInUnit(targetNode, toPort) || findOutUnit(targetNode, toPort);
          console.log('🔍 Validating connection:', { sourceModel, targetModel, fromPort, toPort, fromUnit, toUnit });
          
          const validation = await apiService.validateConnection(
            sourceModel,
            targetModel,
            fromPort,
            toPort,
            { fromUnit, toUnit }
          );
          
          if (!validation.valid) {
            const reasons = validation.reasons.join(', ');
            showToast(`Connection not allowed: ${reasons}`, 'error');
            return;
          } else {
            showToast('Connection validated successfully', 'success');
          }
        } catch (error) {
          console.error('Validation error:', error);
          const errorMessage = error instanceof Error ? error.message : 'Unknown validation error';
          showToast(`Connection validation failed: ${errorMessage}`, 'error');
          return;
        }
      }

      // Create the edge
      const edgeId = `e_${Date.now()}_${Math.random().toString(36).slice(2,8)}`;
      const baseStyle = { stroke: "#1E3A8A", strokeWidth: 3 };
      let style = baseStyle;
      let data = {};
      if (isBatchToModel) {
        style = { ...baseStyle, strokeDasharray: '8,4', stroke: '#0069FF' };
        data = { isBatchToModel: true };
      } else if (isModelToModelEntityConnection) {
        style = { ...baseStyle, strokeDasharray: '8,4', stroke: '#FF69B4' };
        data = { isModelToModelEntityConnection: true };
      } else {
        // Default connectionType for regular model-to-model connections
        data = { connectionType: 'Same Time' };
      }

      const newEdge = {
        ...params,
        id: edgeId,
        type: "custom",
        markerEnd: {
          type: "arrowclosed",
        },
        style,
        data,
        zIndex: 1500,
      };

      setEdges((eds) => {
        const updated = addEdge(newEdge, eds);
        // Immediate Redux dispatch for connections (structural change)
        const clonedNodes = cloneNodes(nodes);
        const clonedEdges = cloneEdges(updated);
        dispatch(setGraph({ nodes: clonedNodes, edges: clonedEdges }));
        return updated;
      });
      
      } catch (error) {
        console.error('🚨 CRITICAL ERROR in onConnect:', error);
        console.error('Error stack:', error.stack);
        console.error('Connection params that caused error:', params);
        showToast('Connection failed due to an unexpected error', 'error');
        
        // Try to prevent the crash by not proceeding with the connection
        return;
      }
    },
    [setEdges, dispatch, nodes, showToast]
  );



  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

///////////////
  const onDrop = useCallback(
    async (event) => {
      try {
        event.preventDefault();
    
        if (!type) return;
        
        console.log('🔧 onDrop called with type:', type);
  
      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });
  
      // Accept assignment-batch tiles
      if (typeof type === 'string' && type.startsWith('assignment-batch:')) {
        const batchId = type.split(':')[1];
        const nodeId = getId('assignment');
      const newNode = {
        id: nodeId,
        type: 'parameditor',
        position: position || { x: 0, y: 0 },
        data: {
          name: batchId,
          label: batchId,
          assignmentBatchId: batchId,
          inputs: [],
          outputs: [],
        },
        selected: false,
        style: { backgroundColor: '#dbeafe' },
      };
        setNodes((nds) => {
          const cleared = nds.map((n) => ({ ...n, selected: false }));
          const updatedNodes = cleared.concat(newNode);
          return updatedNodes;
        });
        
        // Immediate Redux dispatch for node creation (outside setNodes)
        const updatedNodes = [...nodes.map((n) => ({ ...n, selected: false })), newNode];
        const clonedNodes = cloneNodes(updatedNodes);
        const clonedEdges = cloneEdges(edges);
        dispatch(setGraph({ nodes: clonedNodes, edges: clonedEdges }));
        if (window.location.pathname.includes('/nodes')) {
          dispatch(clearClickedF());
        }
        return;
      }

      // Support assignment drag types: 'assignment:building'
      if (typeof type === 'string' && type.startsWith('assignment:')) {
        const kind = type.split(':')[1] || 'unknown';
        const nodeId = getId('assignment');
        const newNode = {
          id: nodeId,
          type: 'parameditor',
          position: position || { x: 0, y: 0 },
          data: {
            name: kind,
            label: kind,
            assignmentKind: kind,
            assignmentBatchId: `building-${Date.now()}`, // Add this to get blue color
            inputs: [],
            outputs: [],
          },
          selected: false,
        };
        setNodes((nds) => {
          const cleared = nds.map((n) => ({ ...n, selected: false }));
          const updatedNodes = cleared.concat(newNode);
          return updatedNodes;
        });
        
        // Immediate Redux dispatch for node creation (outside setNodes)
        const updatedNodes = [...nodes.map((n) => ({ ...n, selected: false })), newNode];
        const clonedNodes = cloneNodes(updatedNodes);
        const clonedEdges = cloneEdges(edges);
        dispatch(setGraph({ nodes: clonedNodes, edges: clonedEdges }));
        if (window.location.pathname.includes('/nodes')) {
          dispatch(clearClickedF());
        }
        return;
      }
  
      const nodeId = getId(type);
      // console.log('🔧 Generated nodeId:', nodeId);
      
      // Fetch model details from backend on-demand
      let inputs = [];
      let outputs = [];
      let nodeData = {};
      
      try {
        // Try to fetch model details from COESI backend
        const modelDetails = await apiService.getCOESIModel(type);
        
        if (!modelDetails || !modelDetails.name) {
          throw new Error(`Invalid model response: missing name field`);
        }
        
          nodeData = modelDetails;
          inputs = modelDetails.input_variables?.map(item => item.name) || [];
          outputs = modelDetails.output_variables?.map(item => item.name) || [];
        
        console.log(`✅ Fetched model details for ${type}:`, {
          name: modelDetails.name,
          inputsCount: inputs.length,
          outputsCount: outputs.length
        });
      } catch (error) {
        console.error(`❌ Failed to fetch model details for ${type}:`, error);
        // Fallback: create node with minimal data using the type as name
        const fallbackName = type || 'unknown_model';
        nodeData = { 
          name: fallbackName, 
          description: `Model not found in backend: ${error instanceof Error ? error.message : 'Unknown error'}` 
        };
        inputs = [];
        outputs = [];
        showToast(`Failed to load model "${type}" from backend`, 'error');
      }
  
      // Ensure nodeData has a name
      if (!nodeData.name) {
        nodeData.name = type || 'unknown_model';
      }
  
      const inferredType = Array.isArray(nodeData.connections) && nodeData.connections.length > 0
                   ? "ComplexModel"
                   : (type === "csv_reader" ? "filereader" : "parameditor");
  
      // Use backend model name directly (no frontend normalization)
      const modelDefId = nodeData.name || type;
      const nodeLabel = nodeData.name ? `${nodeData.name} ${(nodeCounts[type] || 0) + 1}` : `${type} ${(nodeCounts[type] || 0) + 1}`;

      const newNode = {
        id: nodeId,
        type: inferredType,
        position: position || { x: 0, y: 0 },
        data: {
          label: nodeLabel,
          ...nodeData,
          inputs: Array.isArray(inputs) ? inputs : [],
          outputs: Array.isArray(outputs) ? outputs : [],
          modelDefId,
          instanceId: `${nodeId}-${Date.now()}`,
          // Ensure name is always present
          name: nodeData.name || type,
        },
        selected: false,
      };
      console.log('🧩 Adding node', { id: newNode.id, type: newNode.type, name: newNode.data?.name, label: newNode.data?.label, instanceId: newNode.data?.instanceId });
      
      // Validate that the node has a proper ID
      if (!newNode.id || newNode.id === 'undefined') {
        console.error('🔧 Invalid node ID generated:', newNode.id);
        return;
      }
 
       // Commit to ReactFlow and Redux using the same updated array
       setNodes((nds) => {
         const cleared = nds.map((n) => ({ ...n, selected: false }));
         const updatedNodes = cleared.concat(newNode);
         console.log('🧩 setNodes after drop', { before: nds.length, after: updatedNodes.length });
         // Reflect the same to Redux immediately
       const clonedNodes = cloneNodes(updatedNodes);
       const clonedEdges = cloneEdges(edges);
       dispatch(setGraph({ nodes: clonedNodes, edges: clonedEdges }));
         console.log('🧩 Redux setGraph nodes', { count: clonedNodes.length });
         return updatedNodes;
       });
       if (window.location.pathname.includes('/nodes')) {
         dispatch(clearClickedF());
       }
       
       } catch (error) {
         console.error('🚨 CRITICAL ERROR in onDrop:', error);
         console.error('Error stack:', error.stack);
         console.error('Drop event that caused error:', event);
         showToast('Failed to create node due to an unexpected error', 'error');
       }
     },
     [screenToFlowPosition, type, dispatch, edges, setNodes]
   );

  // Update selected node details for right panel when selection changes (guarded)
  const lastSelectedIdRef = useRef(null);
  useEffect(() => {
    const selected = nodes.find((n) => n.selected);
    const nextSelectedId = selected?.id || null;

    if (nextSelectedId !== lastSelectedIdRef.current) {
      lastSelectedIdRef.current = nextSelectedId;
      if (selected) {
        dispatch(setSelectedNodeData(selected.data));
        if (window.location.pathname.includes('/nodes')) {
          dispatch(clearClickedF());
        }
      }
    }
  }, [nodes, dispatch]);

  // Memoize to avoid new object identity each render which triggers StoreUpdater effects
  const edgeTypes = useMemo(() => ({ custom: CustomEdge }), []);
  const nodeTypesMemo = useMemo(() => nodeTypes, []);

  // Edge interactions
  const onEdgeClick = useCallback((event, edge) => {
    event.stopPropagation();
    setEdges(es => es.map(e => ({ ...e, selected: e.id === edge.id })));
    
    // Open connection details modal for regular model-to-model connections
    if (!edge.data?.isBatchToModel && !edge.data?.isModelToModelEntityConnection) {
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);
      
      if (sourceNode && targetNode) {
        const sourceModelName = sourceNode.data?.name || sourceNode.data?.label || edge.source;
        const targetModelName = targetNode.data?.name || targetNode.data?.label || edge.target;
        const sourcePort = edge.sourceHandle?.includes('-') ? edge.sourceHandle.split('-').pop() : edge.sourceHandle || '';
        const targetPort = edge.targetHandle?.includes('-') ? edge.targetHandle.split('-').pop() : edge.targetHandle || '';
        const connectionType = edge.data?.connectionType || 'Same Time';
        
        setSelectedConnection({
          edgeId: edge.id,
          sourceModelName,
          sourcePort,
          targetModelName,
          targetPort,
          connectionType,
        });
        setConnectionModalVisible(true);
      }
    }
  }, [nodes, setEdges]);

  const onEdgeMouseEnter = useCallback((event, edge) => {
    setEdges(es => es.map(e => e.id === edge.id ? { ...e, style: { ...e.style, isHovered: true } } : e));
  }, [setEdges]);

  const onEdgeMouseLeave = useCallback((event, edge) => {
    setEdges(es => es.map(e => e.id === edge.id ? { ...e, style: { ...e.style, isHovered: false } } : e));
  }, [setEdges]);

  // removed continuous Redux sync on nodes/edges change to avoid loops
  
  const clearFlow = () => {
    setNodes([]);
    setEdges([]);
    setNodeCounts({});
    // Also clear the localStorage cache
    localStorage.removeItem('reactflow-nodes');
    localStorage.removeItem('reactflow-edges');
    console.log('🗑️ Cleared flow and localStorage cache');
  };

  const handleCancel = () => {
    setSelectedTags([]);
    setShowExportModal(false)
  }

  const handleExport = async () => {
    //these are recoginizing and building input output nodes
    const incomingMap = new Map();
    edges.forEach(({ source, target }) => {
      incomingMap.set(target, (incomingMap.get(target) || 0) + 1);
    });

    //detacting first layer
    const inputOnlyNodes = nodes.filter(node => {
      return !incomingMap.has(node.id); 
    });
    const compositeStart = inputOnlyNodes.map(node => node.data?.id).filter(Boolean);
    const compositeInputs = inputOnlyNodes.flatMap(node => node.data?.input_variables || []);

    //detacting last layer
    const connectedHandles = new Set(
      edges.map(edge => `${edge.source}.${edge.sourceHandle}`)
    );

    const compositeEndSet = new Set(); 
    const compositeOutputs = [];

    nodes.forEach(node => {
      const nodeId = node.id;
      const modelId = node.data?.id;
      const outputs = node.data?.output_variables || [];

      outputs.forEach(output => {
        const handleKey = `${nodeId}.${output.name}`;
        if (!connectedHandles.has(handleKey)) {
          compositeOutputs.push(output.name);
          if (modelId) {
            compositeEndSet.add(modelId);
          }
        }
      });
    });

    const compositeEnd = Array.from(compositeEndSet);

    //filter start and end to get middle nodes
    const compositeStartIds = new Set(compositeStart);
    const compositeEndIds = new Set(compositeEnd);

    const middleNodes = nodes.filter(node => {
      const nodeId = node.data?.id;
      return nodeId && !compositeStartIds.has(nodeId) && !compositeEndIds.has(nodeId);
    });

    const compositeMiddle = middleNodes.map(node => node.data?.id).filter(Boolean);

    
    

    const exportComponents = {
      first_layer: compositeStart,
      last_layer: compositeEnd,
      other_layers: compositeMiddle
    }
   //these are recoginizing and building input output nodes

    const selectedTagsExport = selectedTags.map(tag => tag.value || []) ;

    const exportedData = {
      name: compositeModalName, 
      id: null,
      description: compositeModalDes,
     // last_modification: new Date().toISOString(),////
      tags:[],
      components: exportComponents,
      connections: edges.map(({ source, sourceHandle, target, targetHandle }) => ({
        from: `${source}.${sourceHandle}`,
        to: `${target}.${targetHandle}`
      })),
      input_variables: compositeInputs, 
      model_execution_cmd: null,
      model_parameters: [],
      output_variables: compositeOutputs,
      simulation_parameters:[],
      simulator_names:[],
      solver:null,
      tags:selectedTagsExport,
    };

    console.log("export object, \n", exportedData)
    setShowExportModal(false); 
    setCompositeModalName("");
    setCompositeModalDes("");
    setSelectedTags([]);

    try {
      const resp = await axios.post(`http://192.168.177.23:8080/api/v1/models`, exportedData);
      console.log("modal post response",resp.data);
    } catch (error) {
      console.log(error);
    }
  };

  
  return (
    <div
      className="dndflow"
      style={{
      display: 'flex',
      height: '100%',  
      width: '100%',    
      overflow: 'hidden' 
    }}
    > 
    
    <SidebarLeft 
      setNodes={setNodes}
      setEdges={setEdges}
    />
  
    <div
      className="reactflow-wrapper"
      ref={reactFlowWrapper}
      style={{
        flex: 1,
        position: 'relative',
        height: '100%',
      }}
    >  
      <ReactFlowErrorBoundary>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChangeSafe}
          onEdgesChange={onEdgesChangeSafe}
          onConnect={isLocked ? undefined : onConnect}
          onDrop={isLocked ? undefined : onDrop}
          onDragOver={isLocked ? undefined : onDragOver}
          onInit={onInit}
          onEdgeClick={onEdgeClick}
          onEdgeMouseEnter={onEdgeMouseEnter}
          onEdgeMouseLeave={onEdgeMouseLeave}
          nodeTypes={nodeTypesMemo}
          edgeTypes={edgeTypes}
          fitView={false}
          defaultViewport={{ x: 0, y: 0, zoom: DEFAULT_ZOOM }}
          minZoom={0.2}
          maxZoom={2}
          panOnScroll
          panOnDrag={!isLocked}
          selectionOnDrag={!isLocked}
          nodesDraggable={!isLocked}
          nodesConnectable={!isLocked}
          connectionRadius={20}
          style={{ backgroundColor: "#F7F9FB" }}
        >
     
      <Background />
        {showExportModal && (
        <div
          style={{
            position: "absolute",
            top: "30%",
            left: "50%",
            transform: "translate(-50%, -30%)",
            backgroundColor: "#fff",
            padding: "20px",
            borderRadius: "8px",
            boxShadow: "0 0 10px rgba(0,0,0,0.2)",
            zIndex: 3000,
            minWidth: "300px",
            minHeight: "300px",
            overflowY: "auto"
          }}
        >
          <h3 style={{ marginBottom: "10px" }}>Export Flow</h3>
          <label style={{ fontSize: "14px" }}>Composite Modal name:</label>
          <input
            type="text"
            value={compositeModalName}
            onChange={(e) => setCompositeModalName(e.target.value)}
            placeholder="Enter a name..."
            style={{
              width: "90%",
              padding: "12px",
              marginBottom: "12px",
              marginTop: "4px",
              borderRadius: "4px",
              border: "1px solid #ccc",
            }}
          />

          <label style={{ fontSize: "14px" }}>Description:</label>
          <input
            type="text"
            value={compositeModalDes}
            onChange={(e) => setCompositeModalDes(e.target.value)}
            placeholder="Enter a description..."
            style={{
              width: "90%",
              padding: "12px",
              marginBottom: "12px",
              marginTop: "4px",
              borderRadius: "4px",
              border: "1px solid #ccc",
            }}
          />
          <br/>

          <label style={{ fontSize: "14px" }}>Select Tags:</label>
          <Select
            isMulti
            options={tagOptions}
            value={selectedTags}
            onChange={setSelectedTags}
            placeholder="Choose tags..."
            styles={{
              control: (base) => ({
                ...base,
                borderRadius: "4px",
                borderColor: "#ccc",
                minHeight: "40px",
              }),
            }}
          />

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "14px" }}>
            <button
              onClick={handleCancel}
              style={{
                padding: "6px 12px",
                backgroundColor: "#ccc",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleExport}
              style={{
                padding: "6px 12px",
                backgroundColor: "#007bff",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Confirm
            </button>
          </div>
        </div>
      )}
        </ReactFlow>
      </ReactFlowErrorBoundary>
      {selectedConnection && connectionModalVisible && (
        <ConnectionDetailsModal
          visible={connectionModalVisible}
          onClose={() => {
            setConnectionModalVisible(false);
            setSelectedConnection(null);
          }}
          onDeleteConnection={() => {
            if (!selectedConnection?.edgeId) return;
            const edgeId = selectedConnection.edgeId;
            setEdges((es) => es.filter((e) => e.id !== edgeId));
            setConnectionModalVisible(false);
            setSelectedConnection(null);
          }}
          sourceModelName={selectedConnection.sourceModelName || ''}
          sourcePort={selectedConnection.sourcePort || ''}
          targetModelName={selectedConnection.targetModelName || ''}
          targetPort={selectedConnection.targetPort || ''}
          connectionType={selectedConnection.connectionType || 'Same Time'}
          onConnectionTypeChange={(type) => {
            if (selectedConnection) {
              setEdges(es => es.map(e => 
                e.id === selectedConnection.edgeId 
                  ? { ...e, data: { ...e.data, connectionType: type } }
                  : e
              ));
              setSelectedConnection({ ...selectedConnection, connectionType: type });
            }
          }}
        />
      )}
      {isLocked && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'rgba(255,255,255,0.4)',
            zIndex: 4000,
            cursor: 'not-allowed'
          }}
        />
      )}
      </div>
    </div>
  );
};

export default DnDFlowForSce;