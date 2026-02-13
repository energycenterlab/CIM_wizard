import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { configureStore } from "@reduxjs/toolkit";
import { Provider } from "react-redux";

import authReducer from "./slices/autoSlice.ts";
import selectedFeaturesReducer from "./slices/selectedFeaturesSlice.ts";
import visibleLayerReducer from "./slices/visibleLayersSlice.ts";
import visibleTableReducer from "./slices/visibleTablesSlice.ts";
import projectPolygonInfoReducer from "./slices/projectPolygonInfoSlice.ts";
import sceanrioLayersReducer from "./slices/scenarioLayersSlice.ts";
import clickedFReducer from "./slices/clickedFSlice.ts";
import clickedNodeReducer from "./slices/clickNodeSlice.ts";
import compositeModelsReducer from "./slices/compositeModelsSlice.ts";
import rfGraphReducer from "./slices/rfGraphSlice.ts";
import assignmentsReducer from "./slices/assignmentsSlice.ts";

import "./index.css";
import App from "./App.tsx";
import { ApiProvider } from "./contexts/ApiContext";

const store = configureStore({
  reducer: {
    auth: authReducer,
    selectedFeatures: selectedFeaturesReducer,
    visibleLayers: visibleLayerReducer,
    visibleTables: visibleTableReducer,
    projectPolygonInfo: projectPolygonInfoReducer,
    scenarioLayers: sceanrioLayersReducer,
    clickedF: clickedFReducer,
    clickedNode: clickedNodeReducer,
    compositeModels: compositeModelsReducer,
    rfGraph: rfGraphReducer,
    assignments: assignmentsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      // Completely disable immutableCheck and serializableCheck for performance
      // and to prevent freezing of large graph objects in development
      immutableCheck: false,
      serializableCheck: false,
    }),
});

// Optional types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Export store for direct access
export { store };

createRoot(document.getElementById("root")!).render(
  // NOTE: StrictMode double-invokes mount/unmount in development which can
  // cause visible flicker for modals. We render without StrictMode here.
  <Provider store={store}>
    <ApiProvider>
      <BrowserRouter basename="/urbansim">
        <App />
      </BrowserRouter>
    </ApiProvider>
  </Provider>
);
