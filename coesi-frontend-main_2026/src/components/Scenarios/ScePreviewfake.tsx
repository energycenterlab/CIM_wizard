import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import "./projpreview.css";
import routes from "../../constants/routes.json";
import { clearGraph } from "../../slices/rfGraphSlice";
import { clearComposites } from "../../slices/compositeModelsSlice";
import { hydrateAssignments } from "../../slices/assignmentsSlice";

interface ScePreviewFakeProps {
  name: string;
  id: string;
  description: string;
  longitude: number;
  latitude: number;
  lastEdit: string;
  simulationRunning: boolean;
  initialProgress?: number;
}

const MapPreview: React.FC<{ longitude: number; latitude: number }> = ({
  longitude,
  latitude,
}) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapInstanceRef = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    mapInstanceRef.current = new maplibregl.Map({
      container: mapContainerRef.current!,
      style: "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
      center: [longitude, latitude],
      zoom: 16,
      pitch: 60,
      bearing: -20,
      attributionControl: false,
      interactive: false,
    });

    return () => {
      mapInstanceRef.current?.remove();
    };
  }, [longitude, latitude]);

  return (
    <div
      ref={mapContainerRef}
      style={{
        width: "100%",
        height: "140px",
        borderRadius: "8px",
        overflow: "hidden",
      }}
    />
  );
};

const ScePreviewFake: React.FC<ScePreviewFakeProps> = ({
  name,
  id,
  description,
  longitude,
  latitude,
  lastEdit,
  simulationRunning,
  initialProgress = 0,
}) => {
  const [progress, setProgress] = useState<number>(initialProgress);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (simulationRunning) {
      interval = setInterval(() => {
        setProgress((prev) => (prev < 100 ? prev + 1 : 100));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [simulationRunning]);

  // Function to clear workspace when opening scenario from scenarios page
  const clearWorkspaceAndNavigate = () => {
    // Clear all workspace entities to start with empty workspace
    dispatch(clearGraph()); // Clear ReactFlow nodes and edges
    dispatch(clearComposites()); // Clear composite models
    dispatch(hydrateAssignments([])); // Clear assignments
    try {
      // Also clear any cached workspace in localStorage used by Node editor
      localStorage.removeItem('reactflow-nodes');
      localStorage.removeItem('reactflow-edges');
    } catch {}
    
    // Navigate to input editor
    navigate(`${routes.INPUTEDITORDEMO}`);
  };

  return (
    <div className="project-card">
      <div className="card-header">
        <h2
          onClick={clearWorkspaceAndNavigate}
          style={{ cursor: "pointer" }}
        >
          {name}
        </h2>
        <div>
          <img
            src="/icons/more_horiz.svg"
            alt="menu"
            style={{ cursor: "pointer" }}
          />
        </div>
      </div>

      <p className="description">{description}</p>

      <div className="map-container">
        <MapPreview longitude={longitude} latitude={latitude} />
      </div>

      <div className="footer">
        <div className="meta">
          <span>Last Edit</span>
          <span className="date">
            {lastEdit} by <strong>You</strong>
          </span>
        </div>
      </div>
    </div>
  );
};

export default ScePreviewFake;
