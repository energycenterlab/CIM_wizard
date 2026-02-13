import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface VisibleLayersState {
  visibleLayers: string[];
}

const initialState: VisibleLayersState = {
  visibleLayers: [],
};

const visibleLayersSlice = createSlice({
  name: 'visibleLayersSlice',
  initialState,
  reducers: {
    showLayer: (state, action: PayloadAction<string>) => {
      if (!state.visibleLayers.includes(action.payload)) {
        state.visibleLayers.push(action.payload);
      }
    },
    hideLayer: (state, action: PayloadAction<string>) => {
      state.visibleLayers = state.visibleLayers.filter(
        (id) => id !== action.payload
      );
    },
  },
});

export const { showLayer, hideLayer } = visibleLayersSlice.actions;
export default visibleLayersSlice.reducer;
