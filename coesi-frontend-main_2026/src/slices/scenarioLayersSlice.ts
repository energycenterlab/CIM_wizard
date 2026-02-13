import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Define the type of a single layer — adjust `any` to a more specific type if known
type Layer = any;

interface ScenarioLayersState {
  layerGeojsonList: Layer[];
}

const initialState: ScenarioLayersState = {
  layerGeojsonList: [],
};

const scenarioLayersSlice = createSlice({
  name: 'scenarioLayers',
  initialState,
  reducers: {
    setLayers: (state, action: PayloadAction<Layer[]>) => {
      state.layerGeojsonList = action.payload;
    },
    addLayer: (state, action: PayloadAction<Layer>) => {
      state.layerGeojsonList.push(action.payload);
      console.log('layer added');
    },
    removeLayer: (state, action: PayloadAction<number>) => {
      state.layerGeojsonList.splice(action.payload, 1); // correct way to remove by index
    },
    emptyLayer: (state) => {
      state.layerGeojsonList = [];
    },
  },
});

export const { setLayers, addLayer, removeLayer, emptyLayer } = scenarioLayersSlice.actions;
export default scenarioLayersSlice.reducer;
