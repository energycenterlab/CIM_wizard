import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface CompositeNode {
  id: string;
  modelDefId: string;
  type: string;
  label: string;
  params: any;
  width?: number;
  height?: number;
  relativeX: number;
  relativeY: number;
  inputs?: string[];
  outputs?: string[];
  data: { [key: string]: any }; // Complete data object for full restoration
  style?: { [key: string]: any }; // Node styling
  className?: string; // Node CSS class
}

export interface CompositeEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle: string;
  targetHandle: string;
  type?: string; // Edge type (e.g., 'custom', 'default')
  style?: { [key: string]: any }; // Edge styling
  markerEnd?: any; // Arrow markers
  data?: { [key: string]: any }; // Preserve edge data (binding flags)
}

export interface CompositeModel {
  id: string;
  name: string;
  createdAt: string;
  nodes: CompositeNode[];
  edges: CompositeEdge[];
}

interface CompositeModelsState {
  composites: CompositeModel[];
}

const initialState: CompositeModelsState = {
  composites: [],
};

// Load from localStorage on initialization
const loadComposites = (): CompositeModel[] => {
  try {
    if (typeof window === 'undefined') {
      return []; // Server-side rendering
    }
    const stored = localStorage.getItem('coesi.composites');
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Failed to load composites from localStorage:', error);
    return [];
  }
};

// Save to localStorage
const saveComposites = (composites: CompositeModel[]) => {
  try {
    if (typeof window === 'undefined') {
      return; // Server-side rendering
    }
    localStorage.setItem('coesi.composites', JSON.stringify(composites));
  } catch (error) {
    console.error('Failed to save composites to localStorage:', error);
  }
};

const compositeModelsSlice = createSlice({
  name: 'compositeModels',
  initialState: {
    ...initialState,
    composites: loadComposites(),
  },
  reducers: {
    addComposite: (state, action: PayloadAction<CompositeModel>) => {
      state.composites.push(action.payload);
      saveComposites(state.composites);
    },
    deleteComposite: (state, action: PayloadAction<string>) => {
      state.composites = state.composites.filter(composite => composite.id !== action.payload);
      saveComposites(state.composites);
    },
    clearComposites: (state) => {
      state.composites = [];
      saveComposites(state.composites);
    },
  },
});

export const { addComposite, deleteComposite, clearComposites } = compositeModelsSlice.actions;
export default compositeModelsSlice.reducer;
