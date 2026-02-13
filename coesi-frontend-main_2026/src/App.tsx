import { Routes, Route } from "react-router-dom";

import routes from "./constants/routes.json";

import LandingPage from "./pages/Landing";
import LoginPage from "./pages/Login";
import ProjectsPage from "./pages/Projects";
import ScenariosPage from "./pages/Scenarios";
import ScenarioInspectPage from "./pages/ScenarioInspect";
import ScenarioDeltaPage from "./pages/ScenarioDelta";
import ScenarioHistoryPage from "./pages/ScenarioHistory";
import ModelDetails from "./pages/ModelDetails";
import NodesPage from "./pages/Nodes";

import InputEditor from "./pages/InputEditor";
import SignupPage from "./pages/Signup";

import SansaFakepage from "./pages/SansaFakepage";
import ProfilePage from "./pages/Profile";
import { AuthProvider } from "./contexts/AuthContext";
import { ToastProvider } from "./contexts/ToastContext";
import ProtectedRoute from "./components/ProtectedRoute";
import PublicRoute from "./components/PublicRoute";

import "./App.css";
import "@xyflow/react/dist/style.css";
import "./styles/reactflow-overrides.css";
import "maplibre-gl/dist/maplibre-gl.css";
import ReviewDataModalPortal from "./components/InputEditor/ReviewDataModalPortal";
import TimeseriesConfigPortal from "./components/InputEditor/TimeseriesConfigPortal";

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Routes>
        <Route path={`${routes.LANDING}`} element={<LandingPage />} />
        <Route path={`${routes.LOGIN}`} element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } />
        <Route path={`${routes.SIGNUP}`} element={
          <PublicRoute>
            <SignupPage />
          </PublicRoute>
        } />
        <Route path="/projects/:username" element={
          <ProtectedRoute>
            <ProjectsPage />
          </ProtectedRoute>
        } />
        {/* Dynamic scenarios route with project ID */}
        <Route path="/scenarios/:projectId" element={
          <ProtectedRoute>
            <ScenariosPage />
          </ProtectedRoute>
        } />
        {/* Legacy static route for backwards compatibility */}
        <Route path={`${routes.SCENARIOSDEMO}`} element={
          <ProtectedRoute>
            <ScenariosPage />
          </ProtectedRoute>
        } />
        <Route path={`${routes.SCENARIOSDEMO}/inspect`} element={
          <ProtectedRoute>
            <ScenarioInspectPage />
          </ProtectedRoute>
        } />
        <Route path={`${routes.SCENARIOSDEMO}/delta`} element={
          <ProtectedRoute>
            <ScenarioDeltaPage />
          </ProtectedRoute>
        } />
        <Route path={`${routes.SCENARIOSDEMO}/history`} element={
          <ProtectedRoute>
            <ScenarioHistoryPage />
          </ProtectedRoute>
        } />
        {/* Dynamic input editor route with project and scenario IDs */}
        <Route path="/input-editor/:projectId/:scenarioId" element={
          <ProtectedRoute>
            <InputEditor />
          </ProtectedRoute>
        } />
        <Route path={`${routes.PROFILE}`} element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        } />
        <Route path="projid==1234567" element={
          <ProtectedRoute>
            <SansaFakepage />
          </ProtectedRoute>
        } />
        <Route path={`${routes.NODES}`} element={
          <ProtectedRoute>
            <NodesPage />
          </ProtectedRoute>
        } />
        <Route path={`${routes.INPUTEDITORDEMO}`} element={
          <ProtectedRoute>
            <InputEditor />
          </ProtectedRoute>
        } />
        <Route path={`/projects/:userId/models/:modelName`} element={
          <ProtectedRoute>
            <ModelDetails />
          </ProtectedRoute>
        } />
        </Routes>
        {/* Global modal portal not tied to node re-renders */}
        <ReviewDataModalPortal />
        <TimeseriesConfigPortal />
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
