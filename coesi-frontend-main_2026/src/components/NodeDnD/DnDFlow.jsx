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
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import './ControlBar.css';

import axios from 'axios';
import Select from 'react-select';
import { useNavigate } from 'react-router-dom';

import fakedata from '../../constants/final-format-1.json'
import { apiService } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

import SidebarLeft from "./SidebarLeft";
import SidebarRight from "./SidebarRight";

import Legend from "./Legend";
import { useDnD } from './DnDContext';
import { nodeTypes } from "./CustomNodes";
import CustomEdge from "./CustomEdge";
import { getDefaultParams, normalizeModelId } from './modelRegistry';

const DEFAULT_ZOOM = 0.75; // Default zoom level

const DnDFlow = () => {
  const initialNodes = [];
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const { screenToFlowPosition } = useReactFlow();
  const [type] = useDnD();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const onInit = useCallback((instance) => {
    // Force our default zoom on mount (no animation)
    instance.setViewport({ x: 0, y: 0, zoom: DEFAULT_ZOOM }, { duration: 0 });
  }, []);

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
  const [jsonDataSingle, setJsonDataSingle] = useState([]);
  const [jsonDataMulti, setJsonDataMulti] = useState([]);

  //for exporting and POST compositions
  const [selectedTags, setSelectedTags] = useState([]);
  const [activeTool, setActiveTool] = useState(null);


  const compositeTags = ['composite-model','control-system','thermal','feedback','power-system', 'motor-control','sensor', 'signal-processing','sensor-fusion','redundancy', 'control','power-management','multi-motor'];
  const tagOptions = compositeTags.map(tag => ({ value: tag, label: tag }));


  const getSingleModel = () => {
    setJsonDataSingle(fakedata.models)
    setJsonDataMulti(fakedata['composite-models'])
  };
  /*  const getSingleModel = async () => {
    try {
      const resp = await axios.get(`http://192.168.177.23:8080/api/v1/models`);
      console.log("single json fetched",resp.data);
      setJsonDataSingle(resp.data.models);
      setJsonDataMulti(resp.data["composite-models"])
    } catch (error) {
      setJsonDataSingle(fakedata.models)
      setJsonDataMulti(fakedata['composite-models'])
      console.log(error);
    }
  }; */

  useEffect(() => {
    getSingleModel();
  },[])

  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.key === 'Delete' || event.key === 'Backspace')) {
        setNodes((nds) => nds.filter((node) => !node.selected));
        setEdges((eds) => eds.filter((edge) => !edge.selected));
      }
    };
  
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [setNodes, setEdges]);

  const getId = (nodeType) => {
    setNodeCounts((prevCounts) => {
      const newCount = (prevCounts[nodeType] || 0) + 1;
      return { ...prevCounts, [nodeType]: newCount };
    });
    return `${nodeType}_${(nodeCounts[nodeType] || 0) + 1}`;
  };

  const onConnect = useCallback(
    async (params) => {
      console.log('Connection attempt:', params);
      
      // Get source and target nodes
      const sourceNode = nodes.find((n) => n.id === params.source);
      const targetNode = nodes.find((n) => n.id === params.target);
      
      if (!sourceNode || !targetNode) {
        showToast('Error: Could not find source or target node', 'error');
        return;
      }

      // Skip validation for batch→model connections (entity to model)
      const isBatchToModel = !!(sourceNode.data && sourceNode.data.assignmentBatchId);
      
      if (!isBatchToModel) {
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
            
            sourceModel = sourceModelNode.data?.name || sourceModelNode.modelDefId;
            fromPort = portName;
          } else {
            // Regular model nodes - extract from node ID
            sourceModel = params.source.split("_")[0]; // "weather_1" -> "weather"
            fromPort = params.sourceHandle.split("-")[1]; // "weather_1-ghi" -> "ghi"
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
            
            targetModel = targetModelNode.data?.name || targetModelNode.modelDefId;
            toPort = portName;
          } else {
            // Regular model nodes
            targetModel = params.target.split("_")[0]; // "pv_1" -> "pv"
            toPort = params.targetHandle.split("-")[1];   // "pv_1-ghi" -> "ghi"
          }
          
          console.log('Validating connection:', { sourceModel, targetModel, fromPort, toPort });
          
          const validation = await apiService.validateConnection(
            sourceModel,
            targetModel,
            fromPort,
            toPort
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
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            type: "custom",
            markerEnd: {
              type: "arrowclosed",
            },
            style: { stroke: "#555", strokeWidth: 3},
            zIndex: 1500,
          },
          eds,
        )
      );
    },
    [setEdges, nodes, showToast]
  );


  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

///////////////
  const onDrop = useCallback(
    async (event) => {
      event.preventDefault();
  
      if (!type) return;
  
      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });
  
      const nodeId = getId(type);
      
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
  
      const modelDefId = normalizeModelId(nodeData.name || type);
      const nodeLabel = nodeData.name ? `${nodeData.name} ${(nodeCounts[type] || 0) + 1}` : `${type} ${(nodeCounts[type] || 0) + 1}`;

      const newNode = {
        id: nodeId,
        type: inferredType,
        position,
        data: {
          label: nodeLabel,
          ...nodeData,
          inputs: Array.isArray(inputs) ? inputs : [],
          outputs: Array.isArray(outputs) ? outputs : [],
          modelDefId,
          // Ensure name is always present
          name: nodeData.name || type,
        },
      };
  
      setNodes((nds) => nds.concat(newNode));
    },
    [screenToFlowPosition, type, nodeCounts]
  );

  const edgeTypes = {
    custom: CustomEdge,
  };
  
  const clearFlow = () => {
    setNodes([]);
    setEdges([]);
    setNodeCounts({});
  };

  const handleCancel = () => {
    setSelectedTags([]);
    setShowExportModal(false)
  }

  const handleExport = async () => {
       console.log("All Nodes:", nodes);
  console.log("All Edges:", edges);
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
      height: '89vh',  
      width: '99vw',    
      overflow: 'hidden',
      position: 'relative'
    }}
    > 
    {/* Baseline Back Button in its own separate container */}
    <div
      style={{
        position: 'fixed',
        top: '102px',
        left: '24px',
        zIndex: 15000,
        backgroundColor: 'white',
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '8px 12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        cursor: 'pointer',
        color: '#222',
        fontWeight: 600,
        fontSize: '18px',
        lineHeight: '1',
        gap: '6px',
        minWidth: '120px',
        justifyContent: 'center'
      }}
      onClick={() => navigate("/scenarios/projid==projname")}
    >
      <img
        src="/icons/ArrowBack.svg"
        alt="Back"
        style={{ width: 18, height: 18, marginRight: 4 }}
      />
      <span style={{ fontSize: '18px', fontWeight: 600, verticalAlign: 'middle' }}>
        baseline
      </span>
    </div>

  <SidebarLeft jsonDataSingle={jsonDataSingle} jsonDataMulti={jsonDataMulti} />
    <div
      className="reactflow-wrapper"
      ref={reactFlowWrapper}
      style={{
        flex: 1,
        position: 'relative',
        height: '100%',
      }}
    > 
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onInit={onInit}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView={false}
        defaultViewport={{ x: 0, y: 0, zoom: DEFAULT_ZOOM }}
        minZoom={0.2}
        maxZoom={2}
        panOnScroll
        panOnDrag
        selectionOnDrag
        style={{ backgroundColor: "#F7F9FB" }}
      >

       {/* Control bar at bottom */}
      <div className="control-bar">
        {toolItems.map((tool) => (
          <button
            key={tool.id}
            onClick={() => setActiveTool(tool.id)}
            className={`control-button ${tool.special ? 'run' : ''} ${
              activeTool === tool.id ? 'active' : ''
            }`}
            title={tool.label}
          >
            <img src={tool.icon} alt={tool.label} />
            {tool.special && <span style={{ marginLeft: 8 }}>{tool.label}</span>}
          </button>
        ))}
        <div className="vertical-divider"> <img src="/icons/vertical_divider.svg" alt="divider" /></div>
{/* Export Button (opens modal) */}
            <button
              onClick={() => setShowExportModal(true)}
              style={{
                height:"35px",
                borderRadius: "20px",
                backgroundColor: "#28a745",
                color: "#fff",
                border: "none",
                cursor: "pointer",
                whiteSpace: "nowrap",
              }}
            >
              Save Cofiguration
            </button>

            {/* Clear Button */}
            <button
              onClick={clearFlow}
              style={{
                height:"35px",
                borderRadius: "20px",
                backgroundColor: "#dc3545",
                color: "#fff",
                border: "none",
                cursor: "pointer",
                whiteSpace: "nowrap",
              }}
            >
              Clear All
            </button>

            <button
              onClick={()=>{}}
              style={{
                height:"35px",
                borderRadius: "20px",
                backgroundColor: "#eeff00",
                color: "black",
                border: "none",
                cursor: "pointer",
                whiteSpace: "nowrap",
              }}
            >
              Run {" "}
              <img src="/icons/fast_forward.svg" alt="run" />
            </button>

      </div>
      
          
          
          <Legend/>
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
      </div>
  <SidebarRight selectedNode={nodes.find((n) => n.selected)} />
    </div>
  );
};

export default DnDFlow;