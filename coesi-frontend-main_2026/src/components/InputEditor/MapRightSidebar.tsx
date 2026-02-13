import React from 'react';
import type { Feature } from 'geojson';

interface MapRightSidebarProps {
  isDrawingPolygon: boolean;
  onStartPolygonDrawing: () => void;
  onStopPolygonDrawing: () => void;
  showBuildingDetails: boolean;
  selectedBuildingDetails: Feature | null;
  onCloseBuildingDetails: () => void;
  onFitToView?: () => void;
}

const MapRightSidebar: React.FC<MapRightSidebarProps> = ({
  isDrawingPolygon,
  onStartPolygonDrawing,
  onStopPolygonDrawing,
  showBuildingDetails,
  selectedBuildingDetails,
  onCloseBuildingDetails,
  onFitToView
}) => {
  return (
    <div style={{
      background: '#fff',
      borderLeft: '1px solid #eee',
      padding: '12px',
      borderRadius: 8,
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      minWidth: '150px',
      maxWidth: '200px'
    }}>
      {/* Map Tools */}
      <div style={{
        background: "white",
        border: "1px solid #e5e7eb",
        borderRadius: "6px",
        padding: "8px",
        boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
        marginBottom: "12px"
      }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "8px"
        }}>
          {/* Fit to View Button */}
          <button
            onClick={() => {
              onFitToView?.();
            }}
            style={{
              background: "transparent",
              border: "1px solid #d1d5db",
              borderRadius: "4px",
              padding: "6px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flex: 1
            }}
            title="Fit to view"
          >
            <img 
              src="/icons/proj_zone.svg" 
              alt="Fit to view" 
              style={{ width: "16px", height: "16px" }}
            />
          </button>

          {/* Polygon Drawing Button */}
          <button
            onClick={() => {
              if (isDrawingPolygon) {
                onStopPolygonDrawing();
              } else {
                onStartPolygonDrawing();
              }
            }}
            style={{
              background: isDrawingPolygon ? "#3b82f6" : "transparent",
              border: isDrawingPolygon ? "1px solid #3b82f6" : "1px solid #d1d5db",
              borderRadius: "4px",
              padding: "6px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flex: 1,
              position: "relative"
            }}
            title={isDrawingPolygon ? "Stop drawing polygon" : "Click to draw polygon on map"}
          >
            <img 
              src="/icons/polygon.svg" 
              alt="Draw polygon" 
              style={{ 
                width: "16px", 
                height: "16px",
                filter: isDrawingPolygon ? "brightness(0) invert(1)" : "none"
              }}
            />
          </button>
        </div>
        
      </div>

      {/* Building Details Panel */}
      {showBuildingDetails && selectedBuildingDetails && (
        <div style={{
          background: "white",
          border: "1px solid #e5e7eb",
          borderRadius: "6px",
          padding: "8px",
          boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
          flex: 1,
          overflow: "auto"
        }}>
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "8px"
          }}>
            <h4 style={{
              margin: 0,
              fontSize: "14px",
              fontWeight: "600",
              color: "#111827"
            }}>
              Building Details
            </h4>
            <button
              onClick={onCloseBuildingDetails}
              style={{
                background: "none",
                border: "none",
                fontSize: "16px",
                cursor: "pointer",
                color: "#6b7280",
                padding: "0",
                width: "20px",
                height: "20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center"
              }}
            >
              ×
            </button>
          </div>
          
          <div style={{ fontSize: "12px", color: "#374151" }}>
            {selectedBuildingDetails.properties && Object.entries(selectedBuildingDetails.properties).map(([key, value]) => {
              // Show only relevant building properties
              const relevantKeys = ['id', 'altezza_vo', 'num_piani', 'superficie', 'categ_uso', 'epoca_cost', 'usage_category', 'building_type', 'year'];
              if (!relevantKeys.includes(key)) return null;
              
              const displayKey = key === 'altezza_vo' ? 'Height' :
                                key === 'num_piani' ? 'Floors' :
                                key === 'superficie' ? 'Surface' :
                                key === 'categ_uso' ? 'Usage' :
                                key === 'epoca_cost' ? 'Year Built' :
                                key === 'usage_category' ? 'Usage Category' :
                                key === 'building_type' ? 'Building Type' :
                                key === 'year' ? 'Year' :
                                key;
              
              return (
                <div key={key} style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: "4px",
                  paddingBottom: "4px",
                  borderBottom: "1px solid #f3f4f6",
                  minHeight: "20px",
                  alignItems: "center"
                }}>
                  <span style={{ 
                    fontWeight: "500",
                    flexShrink: 0,
                    marginRight: "8px"
                  }}>
                    {displayKey}:
                  </span>
                  <span style={{
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                    maxWidth: "120px",
                    textAlign: "right"
                  }}>
                    {String(value)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default MapRightSidebar;
