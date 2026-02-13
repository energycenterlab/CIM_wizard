import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface VisibleTablesState {
  visibleTables: string[];
}

const initialState: VisibleTablesState = {
  visibleTables: [],
};

const visibleTablesSlice = createSlice({
  name: 'visibleTablesSlice',
  initialState,
  reducers: {
    showTable: (state, action: PayloadAction<string>) => {
      if (!state.visibleTables.includes(action.payload)) {
        state.visibleTables.push(action.payload);
      }
    },
    hideTable: (state, action: PayloadAction<string>) => {
      state.visibleTables = state.visibleTables.filter(
        (id) => id !== action.payload
      );
    },
  },
});

export const { showTable, hideTable } = visibleTablesSlice.actions;
export default visibleTablesSlice.reducer;
