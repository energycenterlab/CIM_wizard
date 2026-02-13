import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type Assignment = {
  id: string;
  name: string;
  entityType: 'building';
  ids: (string | number)[];
  count: number;
  createdAt: string;
};

export type AssignmentDraft = {
  active: boolean;
  ids: (string | number)[];
  name: string;
  error?: string;
};

interface WorkingState {
  ids: (string | number)[];
  source?: 'map' | 'filter' | 'random' | 'stratified' | 'split';
  rule?: any;
  bindings?: { nodeId: string; nodeLabel: string }[];
}

interface AssignmentsState {
  assignments: Assignment[];
  draft: AssignmentDraft;
  drawerOpen: boolean;
  activeTab: string;
  working: WorkingState;
}

const initialState: AssignmentsState = {
  assignments: [],
  draft: { active: false, ids: [], name: '' },
  drawerOpen: false,
  activeTab: 'Select',
  working: { ids: [] },
};

const assignmentsSlice = createSlice({
  name: 'assignments',
  initialState,
  reducers: {
    hydrateAssignments: (state, action: PayloadAction<Assignment[]>) => {
      state.assignments = action.payload || [];
    },
    setDrawerOpen: (state, action: PayloadAction<boolean>) => {
      state.drawerOpen = action.payload;
    },
    setActiveTab: (state, action: PayloadAction<string>) => {
      state.activeTab = action.payload;
    },
    setDraftActive: (state, action: PayloadAction<boolean>) => {
      state.draft.active = action.payload;
      if (!action.payload) {
        state.draft.error = undefined;
      }
    },
    setDraftIds: (state, action: PayloadAction<(string | number)[]>) => {
      const unique = Array.from(new Set(action.payload));
      state.draft.ids = unique;
      if (!unique.length) {
        state.draft.active = false;
      }
    },
    setDraftName: (state, action: PayloadAction<string>) => {
      state.draft.name = action.payload;
    },
    setDraftError: (state, action: PayloadAction<string | undefined>) => {
      state.draft.error = action.payload;
    },
    addAssignment: (state, action: PayloadAction<Assignment>) => {
      state.assignments.unshift(action.payload);
    },
    removeAssignment: (state, action: PayloadAction<string>) => {
      state.assignments = state.assignments.filter(a => a.id !== action.payload);
    },
    clearDraft: (state) => {
      state.draft = { active: false, ids: [], name: '', error: undefined };
    },
    setWorkingIds: (state, action: PayloadAction<(string | number)[]>) => {
      state.working.ids = Array.from(new Set(action.payload));
    },
    setWorkingSource: (state, action: PayloadAction<WorkingState['source']>) => {
      state.working.source = action.payload;
    },
    setWorkingRule: (state, action: PayloadAction<any>) => {
      state.working.rule = action.payload;
    },
    resetWorking: (state) => {
      state.working = { ids: [] };
    },
  }
});

export const {
  hydrateAssignments,
  setDrawerOpen,
  setActiveTab,
  setDraftActive,
  setDraftIds,
  setDraftName,
  setDraftError,
  addAssignment,
  removeAssignment,
  clearDraft,
  setWorkingIds,
  setWorkingSource,
  setWorkingRule,
  resetWorking,
} = assignmentsSlice.actions;

export default assignmentsSlice.reducer;


