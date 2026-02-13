import React, { useState, useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import { useNavigate } from "react-router-dom";
import "maplibre-gl/dist/maplibre-gl.css";

import "./projpreview.css";
import routes from "../../constants/routes.json";

interface ProjectPreviewProps {
  name: string;
  description: string;
  longitude: number;
  latitude: number;
  lastEdit: string;
  simulationRunning: boolean;
  initialProgress?: number;
  projectId?: string;
  scenarioId?: string;
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

const ProjectPreview: React.FC<ProjectPreviewProps> = ({
  name,
  description,
  longitude,
  latitude,
  lastEdit,
  simulationRunning,
  initialProgress = 0,
  projectId,
  scenarioId,
}) => {
  const [progress, setProgress] = useState<number>(initialProgress);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  
  // Navigate to scenarios page with project ID
  const handleProjectClick = () => {
    if (projectId) {
      navigate(`/scenarios/${projectId}`);
    } else {
      // Fallback to legacy route if no projectId
      navigate(`${routes.SCENARIOSDEMO}`);
    }
  };

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (simulationRunning) {
      interval = setInterval(() => {
        setProgress((prev) => (prev < 100 ? prev + 1 : 100));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [simulationRunning]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleArchiveProject = () => {
    // TODO: Implement archive functionality with backend
    console.log(`Archiving project: ${name}`);
    setShowDropdown(false);
    // Here you would typically make an API call to archive the project
  };

  return (
    <div className="project-card">
      <div className="card-header">
        <h2
          onClick={handleProjectClick}
          style={{ cursor: "pointer" }}
        >
          {name}
        </h2>
        <div style={{ position: "relative" }}>
          <img
            src="/icons/more_horiz.svg"
            alt="menu"
            style={{ cursor: "pointer" }}
            onClick={(e) => {
              e.stopPropagation();
              setShowDropdown(!showDropdown);
            }}
          />
          
          {/* Dropdown Menu */}
          {showDropdown && (
            <div
              ref={dropdownRef}
              style={{
                position: "absolute",
                top: "100%",
                right: "0",
                backgroundColor: "white",
                border: "1px solid #e0e0e0",
                borderRadius: "8px",
                boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                zIndex: 1000,
                minWidth: "100px",
                padding: "4px 0",
              }}
            >
              <div
                style={{
                  padding: "6px 12px",
                  cursor: "pointer",
                  fontSize: "13px",
                  color: "#333",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  whiteSpace: "nowrap",
                }}
                onClick={handleArchiveProject}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = "#f5f5f5";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = "transparent";
                }}
              >
                <img 
                  src="/icons/folder.svg" 
                  alt="archive" 
                  style={{ width: "14px", height: "14px", flexShrink: 0 }}
                />
                Archive
              </div>
            </div>
          )}
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

        {simulationRunning ? (
          <>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="simulation-info">
              <span>Running</span>
              <span>{(1200 - progress) * 36}s remaining</span>
            </div>
          </>
        ) : (
          <p className="no-sim">No Simulation Run</p>
        )}
      </div>
    </div>
  );
};

export default ProjectPreview;
