import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Fields that ReactFlow manages internally and should not be stored in Redux
const LAYOUT_FIELDS = [
  'width', 'height', 'positionAbsolute', 'dragging', 'selected', 
  'dragging', 'selected', 'type', 'zIndex', 'extent', 'expandParent',
  'position', 'data', 'style', 'className', 'sourcePosition', 'targetPosition',
  'hidden', 'parentNode', 'dragHandle', 'selectable', 'connectable',
  'deletable', 'focusable', 'resizing', 'initialWidth', 'initialHeight'
];

const EDGE_LAYOUT_FIELDS = [
  'sourceX', 'sourceY', 'targetX', 'targetY', 'sourcePosition', 'targetPosition',
  'pathOptions', 'interactionWidth', 'labelStyle', 'labelShowBg', 'labelBgStyle',
  'labelBgPadding', 'labelBgBorderRadius', 'animated', 'hidden', 'deletable',
  'selectable', 'focusable', 'data', 'style', 'className', 'markerStart', 'markerEnd'
];

/**
 * Strip layout fields from a node to create a serializable version for Redux
 */
function sanitizeNodeForRedux(node: any): any {
  if (!node || typeof node !== 'object') return node;
  
  const sanitized: any = {};
  
  // Keep essential fields including position for ReactFlow
  const keepFields = ['id', 'type', 'data', 'position'];
  
  for (const field of keepFields) {
    if (node.hasOwnProperty(field)) {
      if (field === 'data') {
        sanitized[field] = sanitizeNodeData(node.data);
      } else if (field === 'position') {
        // Ensure position is properly structured
        sanitized[field] = {
          x: node.position?.x || 0,
          y: node.position?.y || 0
        };
      } else {
        sanitized[field] = node[field];
      }
    }
  }
  
  return sanitized;
}

/**
 * Strip layout fields from an edge to create a serializable version for Redux
 */
function sanitizeEdgeForRedux(edge: any): any {
  if (!edge || typeof edge !== 'object') return edge;
  
  const sanitized: any = {};
  
  // Keep only essential fields
  const keepFields = ['id', 'source', 'target', 'sourceHandle', 'targetHandle', 'type', 'data'];
  
  for (const field of keepFields) {
    if (edge.hasOwnProperty(field)) {
      sanitized[field] = field === 'data' ? sanitizeNodeData(edge.data) : edge[field];
    }
  }
  
  return sanitized;
}

/**
 * Sanitize node data to remove any non-serializable content
 */
function sanitizeNodeData(data: any): any {
  if (!data || typeof data !== 'object') return data;
  // Preserve arrays by sanitizing items recursively
  if (Array.isArray(data)) {
    return data.map((item) => sanitizeNodeData(item));
  }
  
  // Create a clean copy with only serializable data
  const sanitized: any = {};
  
  for (const [key, value] of Object.entries(data)) {
    // Skip functions, DOM elements, and other non-serializable content
    if (typeof value === 'function' || 
        (typeof value === 'object' && value !== null && 
         (value instanceof HTMLElement || value instanceof Event))) {
      continue;
    }
    
    // Ensure inputs and outputs are arrays
    if (key === 'inputs' || key === 'outputs') {
      sanitized[key] = Array.isArray(value) ? value : [];
    }
    // Recursively sanitize nested objects
    else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeNodeData(value);
    } else {
      sanitized[key] = value;
    }
  }
  
  return sanitized;
}

export interface RfGraphState {
  nodes: any[];
  edges: any[];
  lastEdgeId?: string;
}

const initialState: RfGraphState = {
  nodes: [],
  edges: [],
  lastEdgeId: undefined,
};

const rfGraphSlice = createSlice({
  name: 'rfGraph',
  initialState,
  reducers: {
    setGraph: (state, action: PayloadAction<{ nodes: any[]; edges: any[] }>) => {
      // Sanitize nodes and edges before storing in Redux
      state.nodes = action.payload.nodes.map(sanitizeNodeForRedux);
      state.edges = action.payload.edges.map(sanitizeEdgeForRedux);
    },
    setNodes: (state, action: PayloadAction<any[]>) => {
      // Sanitize nodes before storing in Redux
      state.nodes = action.payload.map(sanitizeNodeForRedux);
    },
    setEdges: (state, action: PayloadAction<any[]>) => {
      // Sanitize edges before storing in Redux
      state.edges = action.payload.map(sanitizeEdgeForRedux);
    },
    addNode: (state, action: PayloadAction<any>) => {
      // Sanitize node before adding to Redux
      state.nodes.push(sanitizeNodeForRedux(action.payload));
    },
    updateNode: (state, action: PayloadAction<{ id: string; updates: any }>) => {
      const index = state.nodes.findIndex(node => node.id === action.payload.id);
      if (index !== -1) {
        // Sanitize updates before applying
        const sanitizedUpdates = sanitizeNodeForRedux(action.payload.updates);
        state.nodes[index] = { ...state.nodes[index], ...sanitizedUpdates };
      }
    },
    removeNode: (state, action: PayloadAction<string>) => {
      state.nodes = state.nodes.filter(node => node.id !== action.payload);
      // Also remove edges connected to this node
      state.edges = state.edges.filter(edge => 
        edge.source !== action.payload && edge.target !== action.payload
      );
    },
    addEdge: (state, action: PayloadAction<any>) => {
      // Sanitize edge before adding to Redux
      state.edges.push(sanitizeEdgeForRedux(action.payload));
    },
    updateEdge: (state, action: PayloadAction<{ id: string; updates: any }>) => {
      const index = state.edges.findIndex(edge => edge.id === action.payload.id);
      if (index !== -1) {
        // Sanitize updates before applying
        const sanitizedUpdates = sanitizeEdgeForRedux(action.payload.updates);
        state.edges[index] = { ...state.edges[index], ...sanitizedUpdates };
      }
    },
    removeEdge: (state, action: PayloadAction<string>) => {
      state.edges = state.edges.filter(edge => edge.id !== action.payload);
    },
    setLastEdgeId: (state, action: PayloadAction<string>) => {
      state.lastEdgeId = action.payload;
    },
    clearGraph: (state) => {
      state.nodes = [];
      state.edges = [];
      state.lastEdgeId = undefined;
    },
  },
});

export const {
  setGraph,
  setNodes,
  setEdges,
  addNode,
  updateNode,
  removeNode,
  addEdge,
  updateEdge,
  removeEdge,
  setLastEdgeId,
  clearGraph,
} = rfGraphSlice.actions;

export default rfGraphSlice.reducer;








