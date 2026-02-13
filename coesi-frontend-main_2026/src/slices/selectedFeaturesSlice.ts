import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface SelectedFeaturesState {
  selectedFeatures: (string | number | any)[];
}

const initialState: SelectedFeaturesState = {
  selectedFeatures: [],
};

const selectedFeaturesSlice = createSlice({
  name: 'selectedFeatures',
  initialState,
  reducers: {
    addSelectedFeature: (state, action: PayloadAction<string>) => {
      const id = String(action.payload);
      // Check if the ID is already in the array (handling both string/number IDs and objects)
      const exists = state.selectedFeatures.some(item => {
        if (typeof item === 'string' || typeof item === 'number') {
          return String(item) === id;
        } else if (item && typeof item === 'object' && item.properties && item.properties.id) {
          return String(item.properties.id) === id;
        }
        return false;
      });
      
      if (!exists) {
        state.selectedFeatures.push(id);
      }
    },
    removeSelectedFeature: (state, action: PayloadAction<string>) => {
      state.selectedFeatures = state.selectedFeatures.filter(
        (item) => {
          // Handle both cases: when item is a string/number ID or when it's an object with properties.id
          if (typeof item === 'string' || typeof item === 'number') {
            return String(item) !== String(action.payload);
          } else if (item && typeof item === 'object' && item.properties && item.properties.id) {
            return String(item.properties.id) !== String(action.payload);
          }
          return true; // Keep items that don't match either pattern
        }
      );
    },
    deleteSelectedFeature: (state) => {
      state.selectedFeatures = [];
      console.log('called and deleted');
    },
    normalizeSelectedFeatures: (state) => {
      // Convert any objects in the array to their ID strings
      state.selectedFeatures = state.selectedFeatures.map(item => {
        if (typeof item === 'string' || typeof item === 'number') {
          return String(item);
        } else if (item && typeof item === 'object' && item.properties && item.properties.id) {
          return String(item.properties.id);
        }
        return String(item); // Fallback
      }).filter((id, index, arr) => arr.indexOf(id) === index); // Remove duplicates
    },
  },
});

export const {
  addSelectedFeature,
  removeSelectedFeature,
  deleteSelectedFeature,
  normalizeSelectedFeatures,
} = selectedFeaturesSlice.actions;

export default selectedFeaturesSlice.reducer;
