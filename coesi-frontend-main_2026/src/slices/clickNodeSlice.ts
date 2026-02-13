
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { Feature, Geometry, GeoJsonProperties } from "geojson";

interface ClickedNodeState {
  feature: Feature<Geometry, GeoJsonProperties> | null;
  node: any | null;
}

const initialState: ClickedNodeState = {
  feature: null,
  node: null,
};

const clickedNodeSlice = createSlice({
  name: "clickedNode",
  initialState,
  reducers: {
    setClickedNode(
      state,
      action: PayloadAction<Feature<Geometry, GeoJsonProperties>>
    ) {
      state.feature = action.payload;
      console.log(state.feature)
    },
    setSelectedNodeData(state, action: PayloadAction<any>) {
      state.node = action.payload;
    },
    clearClickedNode(state) {
      state.feature = null;
    },
    clearSelectedNodeData(state) {
      state.node = null;
    },
  },
});

export const { setClickedNode, clearClickedNode, setSelectedNodeData, clearSelectedNodeData } =
  clickedNodeSlice.actions;

export default clickedNodeSlice.reducer;
