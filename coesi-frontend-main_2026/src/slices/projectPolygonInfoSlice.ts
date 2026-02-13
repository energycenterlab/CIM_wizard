import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { FeatureCollection, Geometry, GeoJsonProperties } from 'geojson';

type PolygonArray = FeatureCollection<Geometry, GeoJsonProperties> | null;

interface MapCenter {
  latitude: number;
  longitude: number;
  zoom: number;
  pitch?: number;
  bearing?: number;
}

interface ProjectPolygonInfoState {
  polygonArray: PolygonArray;
  mapCenter: MapCenter | null;
}

const initialState: ProjectPolygonInfoState = {
  polygonArray: null,
  mapCenter: null,
};

const projectPolygonInfoSlice = createSlice({
  name: 'projectPolygonInfo',
  initialState,
  reducers: {
    setPolygon: (state, action: PayloadAction<PolygonArray>) => {
      state.polygonArray = action.payload;
    },
    setMapCenter: (state, action: PayloadAction<MapCenter>) => {
      state.mapCenter = action.payload;
    },
    emptyPolygon: (state) => {
      state.polygonArray = null;
      state.mapCenter = null;
    },
  },
});

export const { setPolygon, setMapCenter, emptyPolygon } = projectPolygonInfoSlice.actions;
export default projectPolygonInfoSlice.reducer;
