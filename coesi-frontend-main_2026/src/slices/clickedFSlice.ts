
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { Feature, Geometry, GeoJsonProperties } from "geojson";

interface ClickedFState {
  feature: Feature<Geometry, GeoJsonProperties> | null;
}

const initialState: ClickedFState = {
  feature: null,
};

const clickedFSlice = createSlice({
  name: "clickedF",
  initialState,
  reducers: {
    setClickedF(
      state,
      action: PayloadAction<Feature<Geometry, GeoJsonProperties>>
    ) {
      state.feature = action.payload;
      console.log(state.feature)
    },
    clearClickedF(state) {
      state.feature = null;
    },
  },
});

export const { setClickedF, clearClickedF } =
  clickedFSlice.actions;

export default clickedFSlice.reducer;
