import React, { useEffect, useRef, useState, useMemo } from "react";
import maplibregl from "maplibre-gl";
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
//@ts-ignore
import Modal from "./Modal";
import { MapboxOverlay as DeckOverlay } from "@deck.gl/mapbox";
import { GeoJsonLayer, ScatterplotLayer } from "@deck.gl/layers";
import type { RootState } from "../../main";
import type { PickingInfo } from "@deck.gl/core";
import type {
  Feature,
  Geometry,
  FeatureCollection,
  GeoJsonProperties,
} from "geojson";
type NamedGeoJson = FeatureCollection<Geometry, GeoJsonProperties> & {
  name: string;
};

import { useDispatch, useSelector } from "react-redux";
import {
  addSelectedFeature,
  removeSelectedFeature,
} from "../../slices/selectedFeaturesSlice";
import { setClickedF } from "../../slices/clickedFSlice";
import { clearSelectedNodeData } from "../../slices/clickNodeSlice";

const MAP_STYLE =
  "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

const InputEditorMap: React.FC<{ 
  onNavigateToAssignments?: () => void; 
  disablePopup?: boolean; 
  filterLayers?: string[]; 
  customVisibleLayers?: string[]; 
  is2D?: boolean;
  isDrawingPolygon?: boolean;
  onStartPolygonDrawing?: () => void;
  onStopPolygonDrawing?: () => void;
  showBuildingDetails?: boolean;
  selectedBuildingDetails?: Feature | null;
  onCloseBuildingDetails?: () => void;
  onBuildingClick?: (building: Feature) => void;
  onFitToView?: () => void;
}> = ({ 
  onNavigateToAssignments, 
  disablePopup = false, 
  filterLayers, 
  customVisibleLayers, 
  is2D = false,
  isDrawingPolygon = false,
  onStartPolygonDrawing,
  onStopPolygonDrawing,
  showBuildingDetails = false,
  selectedBuildingDetails = null,
  onCloseBuildingDetails,
  onBuildingClick,
  onFitToView
}) => {
  const tooltipRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const deckRef = useRef<DeckOverlay | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

  //control feature interaction and layer interaction
  const dispatch = useDispatch();
  const _selectedFeatures = useSelector(
    (state: RootState) => state.selectedFeatures.selectedFeatures
  );
  const selectedFeatures: (string | number)[] = Array.isArray(_selectedFeatures)
    ? _selectedFeatures
    : [];
  const selectedKey = selectedFeatures.join('|');
  const visibleLayers = useSelector(
    (state: RootState) => state.visibleLayers.visibleLayers
  );

  const [hoveredFeature, setHoveredFeature] = useState<Feature | null>(null);
  const [hoveredFeatureId, setHoveredFeatureId] = useState<string | null>(null);
  const [clickedFeature, setClickedFeature] = useState<Feature | null>(null);
  
  // MapboxDraw control state
  const [drawControl, setDrawControl] = useState<any>(null);
  const [polygonPoints, setPolygonPoints] = useState<[number, number][]>([]);

  const [editedValues, setEditedValues] = useState<Record<string, any>>({});
  const [originalValues, setOriginalValues] = useState<Record<string, any>>({});
  const [showConfirmation, setShowConfirmation] = useState(false);

  // GeoJSON layers from store (populated by CIM Wizard fetch)
  const geojsons: NamedGeoJson[] = useSelector(
    (state: RootState) => state.scenarioLayers.layerGeojsonList as any[]
  ) || [];

  const getFeatureId = (feature: any) =>
    feature?.properties?.id ??
    feature?.properties?.building_id ??
    feature?.properties?.buildingid ??
    null;

  const handleHover = (
    info: PickingInfo<Feature<Geometry, GeoJsonProperties>>
  ) => {
    const { object, x, y } = info;

    if (object) {
      setHoveredFeature(object);
      setHoveredFeatureId(getFeatureId(object));

      if (tooltipRef.current && !disablePopup) {
        tooltipRef.current.innerHTML = getTooltipContent(object, "hover") ?? "";
        tooltipRef.current.style.display = "block";
        tooltipRef.current.style.left = `${x + 10}px`;
        tooltipRef.current.style.top = `${y + 10}px`;
      }
    } else {
      setHoveredFeature(null);
      if (tooltipRef.current) {
        tooltipRef.current.style.display = "none";
      }
    }
  };

  const handleClick = (info: PickingInfo) => {
    const { object } = info;

    if (tooltipRef.current) {
      tooltipRef.current.style.display = "none";
    }

    const fid = getFeatureId(object);
    if (object && object.properties && fid) {
      // Handle selection in assignment manager mode (only when not drawing polygon)
      if (disablePopup && !isDrawingPolygon) {
        // Show building details
        onBuildingClick?.(object);
        
        // Also handle selection
        const featureId = String(object.properties.id);
        if (selectedFeatures.includes(featureId)) {
          dispatch(removeSelectedFeature(featureId));
        } else {
          dispatch(addSelectedFeature(featureId));
        }
      }
      
      dispatch(setClickedF(object));
      // Clear any existing node selection when building is clicked
      dispatch(clearSelectedNodeData());
      
      // Only show popup if not disabled
      if (!disablePopup) {
        setClickedFeature(object);
        // setTooltipPosition({ x, y });
      }
    }
  };

  const handleCloseTooltip = () => {
    setClickedFeature(null);
  };

  // Polygon drawing functions
  const startPolygonDrawing = () => {
    if (drawControl) {
      drawControl.changeMode('draw_polygon');
    }
    onStartPolygonDrawing?.();
  };

  const stopPolygonDrawing = () => {
    if (drawControl) {
      drawControl.changeMode('simple_select');
    }
    onStopPolygonDrawing?.();
  };


  // Simple point-in-polygon algorithm
  const isPointInPolygon = (point: number[], polygon: number[][]) => {
    const [x, y] = point;
    let inside = false;
    
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const [xi, yi] = polygon[i];
      const [xj, yj] = polygon[j];
      
      if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
        inside = !inside;
      }
    }
    
    return inside;
  };


  const getTooltipContent = (
    feature: Feature<Geometry, GeoJsonProperties> | null,
    mode: "hover" | "click" = "click"
  ) => {
    if (!feature || !feature.properties) return null;

    // If popup is disabled, only show hover tooltips
    if (disablePopup && mode === "click") return null;

    if (mode === "hover") {
      const id = getFeatureId(feature) ?? feature.properties.name ?? "Unknown";
      return `
    <div style="background-color: white; color: black; padding: 6px 10px; border-radius: 4px;">
      <strong>ID:</strong> ${id}
    </div>`;
    }

    const tooltipStyle =
      "background-color: white; color: black; padding: 10px; border-radius: 4px;";

    const truncatedStyle =
      "white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px;";

    const editableFieldsConfig: Record<string, string> = {
      id: "readonly",
      n_floor: "number",
    };

    // Return input fields for non-baseline scenarios
    const propertiesHtml = Object.entries((feature.properties || {}) as Record<string, any>)
      .map(([key, value]) => {
        const fieldType = editableFieldsConfig[key] || "text";

        if (fieldType === "readonly") {
          return `
              <div style="margin-bottom: 4px; ${truncatedStyle}">
                <strong>${key}:</strong>
                <span>${value}</span>
              </div>`;
        } else {
          return `
              <div style="margin-bottom: 4px; ${truncatedStyle}">
                <strong>${key}:</strong>
                <input 
                  type="${fieldType}" 
                  value="${editedValues[key] || value}" 
                  style="width: 50%; padding: 4px; margin-left: 8px;"
                />
              </div>`;
        }
      })
      .join("");

    return `
          <div style="background-color: white; max-width: 350px; word-wrap: break-word; ${tooltipStyle}">
            ${propertiesHtml}
          </div>`;
  };

  /*  
  ORIGINAL FUNCTION THAT ALLOWS YOU TO SHOW THE WHOLE TOOLTIP DIRECTLY ON THE MAP
  const getTooltipContent = (
    feature: Feature<Geometry, { [key: string]: any }> | null
  ) => {
    if (!feature || !feature.properties) return null;

    const tooltipStyle =
      "background-color: white; color: black; padding: 10px; border-radius: 4px;";

    const truncatedStyle =
      "white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px;";

    const editableFieldsConfig = {
      id: "readonly",
      n_floor: "number",
    };

    if (scenarioName === "baseline") {
      return `
          <div style="max-width: 350px; word-wrap: break-word; text-align: left; ${tooltipStyle}">
            ${Object.entries(feature.properties)
              .map(
                ([key, value]) => `
                <div style="${truncatedStyle}">
                  <strong>${key}:</strong> ${value}
                </div>`
              )
              .join("<br>")}
          </div>`;
    } else {
      // Return input fields for non-baseline scenarios
      const propertiesHtml = Object.entries(feature.properties)
        .map(([key, value]) => {
          const fieldType = editableFieldsConfig[key] || "text";

          if (fieldType === "readonly") {
            return `
              <div style="margin-bottom: 4px; ${truncatedStyle}">
                <strong>${key}:</strong>
                <span>${value}</span>
              </div>`;
          } else {
            return `
              <div style="margin-bottom: 4px; ${truncatedStyle}">
                <strong>${key}:</strong>
                <input 
                  type="${fieldType}" 
                  value="${editedValues[key] || value}" 
                  style="width: 50%; padding: 4px; margin-left: 8px;"
                />
              </div>`;
          }
        })
        .join("");

      return `
          <div style="background-color: white; max-width: 350px; word-wrap: break-word; ${tooltipStyle}">
            ${propertiesHtml}
          </div>`;
    }
  }; */

  // Function to show the confirmation modal
  const handleCloseWithConfirmation = () => {
    // Check if there are any changes
    const changes = Object.keys(editedValues).some(
      (key) => editedValues[key] !== originalValues[key]
    );

    if (changes) {
      setShowConfirmation(true); // Show the confirmation modal
    } else {
      handleCloseTooltip(); // No changes, close the tooltip
    }
  };

  // Handle applying the changes
  const handleApplyChanges = () => {
    // Here you can apply the changes, such as updating the feature
    console.log("Applying changes:", editedValues);

    // Close the confirmation modal and the tooltip
    setShowConfirmation(false);
    handleCloseTooltip();
  };

  // Handle discarding the changes
  const handleDiscardChanges = () => {
    // Reset the edited values to the original values
    setEditedValues({});
    setShowConfirmation(false);
    handleCloseTooltip(); // Close the tooltip
  };

  // Set the initial state when clickedFeature changes (reset when feature changes)
  useEffect(() => {
    if (clickedFeature && clickedFeature.properties) {
      setOriginalValues(clickedFeature.properties);
      setEditedValues({});
    }
  }, [clickedFeature]);

  const layers = useMemo(() => {
    // Use customVisibleLayers if provided (for assignment manager), otherwise use Redux visibleLayers
    const layersToUse = customVisibleLayers || visibleLayers;
    
    // Filter geojsons based on the appropriate layers array
    let filteredGeojsons = geojsons.filter((geojson) =>
      layersToUse.includes(geojson.name)
    );
    
    // If filterLayers prop is provided, remove those layers (for assignment manager)
    if (filterLayers && filterLayers.length > 0) {
      filteredGeojsons = filteredGeojsons.filter((geojson) =>
        !filterLayers.includes(geojson.name)
      );
    }

    const buildingLayers = filteredGeojsons.map((geojson) => {
      return new GeoJsonLayer({
        id: `${geojson.name}`,
        data: geojson,
        stroked: true,
        filled: true,
        extruded: !is2D,
        pointRadiusMinPixels: 10,
        lineWidthMinPixels: is2D ? 1 : 5,
        getFillColor: (feature) => {
          if (disablePopup && selectedFeatures.includes(String(feature.properties.id))) {
            return [255, 165, 0, 255]; // light orange for selected features (only in assignment manager)
          }
          if (hoveredFeature?.properties?.id === feature.properties.id) {
            return [255, 255, 0, 255]; // Yellow for hovered feature
          }
          return [0, 128, 255, 128]; // Default color
        },
        getLineColor: (feature) => {
          if (disablePopup && selectedFeatures.includes(String(feature.properties.id))) {
            return [255, 140, 0, 255]; // Darker orange border for selected features (only in assignment manager)
          }
          if (hoveredFeature?.properties?.name === feature.properties.name) {
            return [255, 255, 0, 255]; // Yellow border for hovered feature
          }
          return [0, 255, 200]; // Default border color
        },
        getPointRadius: () => 10,
        getElevation: (feature) => is2D ? 0 : (feature.properties.altezza_vo || 0),
        pickable: true,
        onHover: handleHover,
        onClick: handleClick,
        updateTriggers: {
          getFillColor: [hoveredFeatureId, selectedKey],
        },
      });
    });

    // Add polygon points layer if there are points
    const polygonPointsLayer = polygonPoints.length > 0 ? new ScatterplotLayer({
      id: 'polygon-points',
      data: polygonPoints.map((point, index) => ({
        position: point,
        id: `point-${index}`,
        index: index,
        isActive: index === polygonPoints.length - 1 // Last point is active
      })),
      pickable: false,
      getRadius: (d) => {
        // Normal size for polygon points
        return d.isActive ? 16 : 8;
      },
      getFillColor: (d) => {
        // White fill for active point, orange for regular points
        return d.isActive ? [255, 255, 255, 255] : [255, 165, 0, 255];
      },
      getLineColor: (d) => {
        // Orange border for active point, darker orange for regular points
        return d.isActive ? [255, 165, 0, 255] : [255, 140, 0, 255];
      },
      getLineWidth: (d) => {
        // Thicker border for active point
        return d.isActive ? 4 : 2;
      },
      updateTriggers: {
        getFillColor: [polygonPoints],
        getLineColor: [polygonPoints],
        getRadius: [polygonPoints],
        getLineWidth: [polygonPoints],
      },
    }) : null;

    // Add polygon line layer to show connecting lines
    const polygonLineLayer = polygonPoints.length > 1 ? new GeoJsonLayer({
      id: 'polygon-lines',
      data: {
        type: 'FeatureCollection',
        features: [{
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: polygonPoints
          },
          properties: {
            id: 'polygon-line'
          }
        }]
      },
      pickable: false,
      getLineColor: [255, 165, 0, 255], // Orange color
      getLineWidth: 3,
      lineWidthMinPixels: 2,
      lineWidthMaxPixels: 4,
      updateTriggers: {
        getLineColor: [polygonPoints],
        getLineWidth: [polygonPoints],
      },
    }) : null;

    // Combine all layers
    const allLayers: any[] = [...buildingLayers];
    if (polygonLineLayer) allLayers.push(polygonLineLayer as any);
    if (polygonPointsLayer) allLayers.push(polygonPointsLayer as any);
    
    
    return allLayers;
  }, [geojsons, hoveredFeature, selectedFeatures, visibleLayers, filterLayers, customVisibleLayers, is2D, polygonPoints]);

  useEffect(() => {
    if (deckRef.current) {
      deckRef.current.setProps({ layers });
    }
  }, [layers]);

  useEffect(() => {
    const map = new maplibregl.Map({
      container: containerRef.current!,
      style: MAP_STYLE,
      center: [7.681654080483028, 45.0599313909609],
      zoom: 16,
      pitch: is2D ? 0 : 45,
      bearing: 0,
    });
    
    mapRef.current = map;

    const deckOverlay = new DeckOverlay({
      layers,
    });
    deckRef.current = deckOverlay;
    map.addControl(deckOverlay);

    // Add MapboxDraw control only in assignment manager mode
    if (disablePopup) {
      const draw = new MapboxDraw({
        displayControlsDefault: false,
        controls: {
          polygon: true,
          trash: true
        },
        defaultMode: 'simple_select',
        styles: [
          {
            id: 'gl-draw-polygon-fill',
            type: 'fill',
            filter: ['all', ['==', '$type', 'Polygon'], ['!=', 'mode', 'static']],
            paint: {
              'fill-color': '#ffa500',
              'fill-opacity': 0.2
            }
          },
          {
            id: 'gl-draw-polygon-stroke-active',
            type: 'line',
            filter: ['all', ['==', '$type', 'Polygon'], ['!=', 'mode', 'static']],
            paint: {
              'line-color': '#ffa500',
              'line-width': 3,
              'line-dasharray': [2, 2]
            }
          },
          {
            id: 'gl-draw-polygon-stroke-inactive',
            type: 'line',
            filter: ['all', ['==', '$type', 'Polygon'], ['==', 'mode', 'static']],
            paint: {
              'line-color': '#ffa500',
              'line-width': 2
            }
          }
        ]
      });
      
      map.addControl(draw, "top-left");
      setDrawControl(draw);

      // Add event listeners for polygon drawing
      const handleDrawCreate = (e: any) => {
        const polygon = e.features[0];
        
        if (polygon && polygon.geometry.type === 'Polygon') {
          // Get all features from visible layers
          const allFeatures: Feature[] = [];
          geojsons.forEach(geojson => {
            if (geojson.features) {
              allFeatures.push(...geojson.features);
            }
          });
          

          // Find features within polygon using point-in-polygon
          const featuresInPolygon = allFeatures.filter(feature => {
            if (feature.geometry.type === 'Polygon' || feature.geometry.type === 'MultiPolygon') {
              // For building polygons, check if centroid is within selection polygon
              const coords = feature.geometry.type === 'Polygon' 
                ? feature.geometry.coordinates[0] 
                : feature.geometry.coordinates[0][0];
              
              if (coords && coords.length > 0) {
                // Calculate centroid
                const centroid = coords.reduce((acc, coord) => {
                  return [acc[0] + coord[0], acc[1] + coord[1]];
                }, [0, 0]).map(sum => sum / coords.length);
                
                const isInside = isPointInPolygon(centroid, polygon.geometry.coordinates[0]);
                return isInside;
              }
            }
            return false;
          });
          

          // Add all features in polygon to selection
          featuresInPolygon.forEach(feature => {
            const featureId = String(feature.properties?.id);
            if (featureId && !selectedFeatures.includes(featureId)) {
              dispatch(addSelectedFeature(featureId));
            }
          });

          // Clear the drawn polygon
          draw.deleteAll();
        }
        
        // Only stop polygon drawing if we actually created a valid polygon
        if (polygon && polygon.geometry.type === 'Polygon' && polygon.geometry.coordinates[0].length >= 3) {
          onStopPolygonDrawing?.();
        }
      };

      const handleDrawDelete = () => {
        setPolygonPoints([]);
        onStopPolygonDrawing?.();
      };

      const handleDrawUpdate = (e: any) => {
        // Track polygon points as they're being drawn
        if (drawControl) {
          const allFeatures = drawControl.getAll();
          
          if (allFeatures.features && allFeatures.features.length > 0) {
            const feature = allFeatures.features[0];
            
            if (feature.geometry && feature.geometry.type === 'Polygon') {
              // Extract the outer ring coordinates (first array)
              const coordinates = feature.geometry.coordinates[0];
              if (coordinates && coordinates.length > 0) {
                // Convert to the format expected by our state
                const points: [number, number][] = coordinates.map((coord: number[]) => [coord[0], coord[1]]);
                setPolygonPoints(points);
              }
            }
          }
        }
      };

      const handleDrawModeChange = (e: any) => {
        // Clear points when switching modes
        if (e.mode !== 'draw_polygon') {
          setPolygonPoints([]);
        }
      };

      map.on("draw.create", handleDrawCreate);
      map.on("draw.delete", handleDrawDelete);
      map.on("draw.update", handleDrawUpdate);
      map.on("draw.modechange", handleDrawModeChange);

      return () => {
        map.off("draw.create", handleDrawCreate);
        map.off("draw.delete", handleDrawDelete);
        map.off("draw.update", handleDrawUpdate);
        map.off("draw.modechange", handleDrawModeChange);
        map.remove();
      };
    }

    return () => {
      map.remove();
    };
  }, [is2D, disablePopup]);

  // Update cursor when drawing mode changes
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.style.cursor = isDrawingPolygon ? "crosshair" : "default";
    }
  }, [isDrawingPolygon]);

  // Control MapboxDraw mode based on drawing state
  useEffect(() => {
    if (drawControl && disablePopup) {
      try {
        if (isDrawingPolygon) {
          drawControl.changeMode('draw_polygon');
        } else {
          drawControl.changeMode('simple_select');
          setPolygonPoints([]); // Clear points when stopping drawing
        }
      } catch (error) {
        console.error('Error changing MapboxDraw mode:', error);
      }
    }
  }, [isDrawingPolygon, drawControl, disablePopup]);

  // Expose fit to view function
  useEffect(() => {
    if (onFitToView && mapRef.current) {
      const fitToView = () => {
        if (mapRef.current) {
          try {
            // Get all features from visible layers to calculate bounds
            const allFeatures: Feature[] = [];
            geojsons.forEach(geojson => {
              if (geojson.features) {
                allFeatures.push(...geojson.features);
              }
            });

            if (allFeatures.length > 0) {
              // Calculate bounds from all features
              let minLng = Infinity, minLat = Infinity, maxLng = -Infinity, maxLat = -Infinity;
              let validCoordsFound = false;
              
              allFeatures.forEach(feature => {
                if (feature.geometry.type === 'Polygon') {
                  feature.geometry.coordinates[0].forEach(coord => {
                    if (Array.isArray(coord) && coord.length >= 2 && 
                        !isNaN(coord[0]) && !isNaN(coord[1]) && 
                        isFinite(coord[0]) && isFinite(coord[1])) {
                      minLng = Math.min(minLng, coord[0]);
                      minLat = Math.min(minLat, coord[1]);
                      maxLng = Math.max(maxLng, coord[0]);
                      maxLat = Math.max(maxLat, coord[1]);
                      validCoordsFound = true;
                    }
                  });
                } else if (feature.geometry.type === 'MultiPolygon') {
                  feature.geometry.coordinates.forEach(polygon => {
                    polygon[0].forEach(coord => {
                      if (Array.isArray(coord) && coord.length >= 2 && 
                          !isNaN(coord[0]) && !isNaN(coord[1]) && 
                          isFinite(coord[0]) && isFinite(coord[1])) {
                        minLng = Math.min(minLng, coord[0]);
                        minLat = Math.min(minLat, coord[1]);
                        maxLng = Math.max(maxLng, coord[0]);
                        maxLat = Math.max(maxLat, coord[1]);
                        validCoordsFound = true;
                      }
                    });
                  });
                }
              });

              if (validCoordsFound && minLng !== Infinity && minLat !== Infinity && 
                  maxLng !== -Infinity && maxLat !== -Infinity) {
                mapRef.current.fitBounds(
                  [[minLng, minLat], [maxLng, maxLat]],
                  { padding: 50, maxZoom: 18 }
                );
              } else {
                // Fallback to default view if no valid coordinates found
                mapRef.current.setCenter([7.681654080483028, 45.0599313909609]);
                mapRef.current.setZoom(16);
              }
            } else {
              // Fallback to default view if no features found
              mapRef.current.setCenter([7.681654080483028, 45.0599313909609]);
              mapRef.current.setZoom(16);
            }
          } catch (error) {
            console.error('Error in fitToView:', error);
            // Fallback to default view on error
            mapRef.current.setCenter([7.681654080483028, 45.0599313909609]);
            mapRef.current.setZoom(16);
          }
        }
      };

      // Store the function reference
      (window as any).fitToView = fitToView;
    }
  }, [onFitToView]);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        overflow: "hidden",
        position: "relative",
      }}
    >
      <div ref={containerRef} style={{ width: "100%", height: "100%" }} />
      <div
        ref={tooltipRef}
        style={{
          position: "absolute",
          pointerEvents: "none",
          zIndex: 999,
          padding: "6px",
          borderRadius: "4px",
          display: "none",
        }}
      />


      <Modal
        isOpen={showConfirmation}
        onRequestClose={() => setShowConfirmation(false)}
        style={{
          overlay: {
            backgroundColor: "rgba(0, 0, 0, 0.5)",
          },
          content: {
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            backgroundColor: "white",
            padding: "20px",
            borderRadius: "4px",
            width: "300px",
            textAlign: "center",
          },
        }}
      >
        <h3>Do you want to save changes?</h3>
        <button onClick={handleApplyChanges} style={{ margin: "8px" }}>
          Save
        </button>
        <button onClick={handleDiscardChanges} style={{ margin: "8px" }}>
          Discard
        </button>
      </Modal>
    </div>
  );
};

export default InputEditorMap;

/* 
ORIGINAL RETURN WITH TOOLTIPS
return (
    <div
      style={{
        width: "100%",
        height: "100%",
        overflow: "hidden",
        position: "relative",
      }}
    >
      <div ref={containerRef} style={{ width: "100%", height: "100%" }} />
      <div
        ref={tooltipRef}
        style={{
          position: "absolute",
          pointerEvents: "none",
          zIndex: 999,
          padding: "6px",
          borderRadius: "4px",
          display: "none",
        }}
      />
      {clickedFeature && tooltipPosition && !disablePopup && (
        <Draggable>
          <div
            style={{
              position: "absolute",
              left: tooltipPosition.x,
              top: tooltipPosition.y,
              padding: "8px",
              borderRadius: "4px",
              zIndex: 1000,
              maxHeight: "300px",
              overflowY: "auto",
              cursor: "move",
            }}
          >
            <div
              style={{
                marginBottom: "4px",
                background: "white",
                padding: "10px",
                display: "flex",
                flexDirection: "column",
                overflowY: "scroll",
                scrollbarWidth: "none",
                msOverflowStyle: "none",
              }}
            >
              <button
                onClick={handleCloseWithConfirmation}
                style={{
                  marginBottom: "8px",
                  padding: "4px 8px",
                  backgroundColor: "red",
                  color: "white",
                  border: "none",
                  borderRadius: "15px",
                  cursor: "pointer",
                  width: "30px",
                }}
              >
                x
              </button>

              <div
                dangerouslySetInnerHTML={{
                  __html: getTooltipContent(clickedFeature),
                }}
              />
            </div>
          </div>
        </Draggable>
      )}
      <Modal
        isOpen={showConfirmation}
        onRequestClose={() => setShowConfirmation(false)}
        style={{
          overlay: {
            backgroundColor: "rgba(0, 0, 0, 0.5)",
          },
          content: {
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            backgroundColor: "white",
            padding: "20px",
            borderRadius: "4px",
            width: "300px",
            textAlign: "center",
          },
        }}
      >
        <h3>Do you want to save changes?</h3>
        <button onClick={handleApplyChanges} style={{ margin: "8px" }}>
          Save
        </button>
        <button onClick={handleDiscardChanges} style={{ margin: "8px" }}>
          Discard
        </button>
      </Modal>
    </div>
  );
 */
