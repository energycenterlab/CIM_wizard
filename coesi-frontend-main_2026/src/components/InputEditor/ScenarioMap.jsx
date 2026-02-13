
import { useState, useMemo, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import DeckGL from "@deck.gl/react";
import  StaticMap  from 'react-map-gl';
import { Map } from "react-map-gl/maplibre";
import maplibregl from "maplibre-gl";
import Draggable from "react-draggable";
import { PolygonLayer, GeoJsonLayer } from "@deck.gl/layers";
import './MapStyle.css';
import Modal from "./Modal";

import { useSelector } from "react-redux";

import { clearSelectedNodeData } from "../../slices/clickNodeSlice";

/*
light: https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json
dark: https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json
*/

const ScenarioMap = () => {

  //const initialVState = useSelector((state) => state.projectPolygonInfo.mapCenter)
  //const geojsons = useSelector((state)=>state.scenarioLayers.layerGeojsonList)
const initialVState = {
    latitude: 45.067848797120725,
    longitude: 7.651635756298525,
    zoom: 8,
    pitch: 45,
    bearing: 0,
  };
const geojsons = useSelector((state) => state.scenarioLayers.layerGeojsonList) || [];

  const dispatch = useDispatch();
  const visibleLayers = useSelector((state) => state.visibleLayers.visibleLayers);
  const [hoveredFeature, setHoveredFeature] = useState(null);
  const [clickedFeature, setClickedFeature] = useState(null); 
  const [tooltipPosition, setTooltipPosition] = useState(null);  
  //const { scenarioInfo } = useParams();
  const scenarioInfo = "baselineDemo==id5678"
  const [scenarioName, ] = scenarioInfo.split("==")

  const [editedValues, setEditedValues] = useState({});
  const [originalValues, setOriginalValues] = useState({});
  const [showConfirmation, setShowConfirmation] = useState(false);
  
  const mapStyle = "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json";/////

  const initialViewState = {
    latitude: initialVState.latitude,
    longitude: initialVState.longitude,
    zoom: initialVState.zoom+8,
    pitch: 45,
    bearing: 0,
  };

  const handleHover = (info) => {
    const { object } = info;
    if (object) {
      setHoveredFeature(object); 
    } else {
      setHoveredFeature(null); 
    }
  };

  const handleClick = (info) => {
    const { object, x, y } = info;
    if (object && object.properties && object.properties.id) {
      setClickedFeature(object);
      // Clear any existing node selection when building is clicked
      dispatch(clearSelectedNodeData());
      setTooltipPosition({ x, y });
    }
  };

  const handleCloseTooltip = () => {
    setClickedFeature(null); // Remove persistent tooltip
    setTooltipPosition(null); // Reset tooltip position
  };

 const getTooltipContent = (feature) => {
  if (!feature || !feature.properties) return null;

  const editableFieldsConfig = {
    id: 'readonly',
    n_floor: 'number',
  };

  const renderField = (key, value) => {
    const fieldType = editableFieldsConfig[key] || 'text';

    if (fieldType === 'readonly') {
      return `
        <div style="margin-bottom: 10px;">
          <label style="font-weight: bold; display: block; margin-bottom: 2px;">${key}:</label>
          <span>${value}</span>
        </div>`;
    } else {
      return `
        <div style="margin-bottom: 10px;">
          <label style="font-weight: bold; display: block; margin-bottom: 2px;">${key}:</label>
          <input 
            type="${fieldType}" 
            value="${editedValues[key] || value}" 
            style="width: 100%; padding: 6px 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px;"
          />
        </div>`;
    }
  };

  const allFields = Object.entries(feature.properties)
    .map(([key, value]) => renderField(key, value))
    .join("");

  return `
    <div style="
      width: 100%;
      padding: 8px 0;
      text-align: left;
      font-family: sans-serif;
      font-size: 14px;
      color: #000;
    ">
      ${allFields}
    </div>
  `;
}; 

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
  
  const getColorForIndex = (index) => {
  const baseColors = [
    [0, 128, 255],
    [0, 200, 100],
    [255, 128, 0],
    [128, 0, 255],
    [255, 0, 128],
    [0, 255, 200],
  ];
  const color = baseColors[index % baseColors.length];
  return [...color, 128]; 
};

const layerColors = useMemo(() => {
  return geojsons.map((_, index) => getColorForIndex(index));
}, [geojsons.length]);

  const layers = useMemo(() => {
    const filtered = geojsons.filter((_, idx) => visibleLayers.includes(idx));
    return filtered.map((geojson, idx) => {
      const originalIndex = visibleLayers[idx];
      const color = layerColors[originalIndex] || [0, 128, 255, 128];
      return new GeoJsonLayer({
        id: `geojson-layer-${originalIndex}`,
        data: geojson,
        stroked: true,
        filled: true,
        extruded: true,
        pointRadiusMinPixels: 5,
        lineWidthMinPixels: 2,
        getFillColor: (feature) => {
          if (hoveredFeature && hoveredFeature.properties.id === feature.properties.id) {
            return [255, 255, 0, 255];
          }
          return color;
        },
        getLineColor: (feature) => {
          if (hoveredFeature && hoveredFeature.properties.id === feature.properties.id) {
            return [255, 255, 0, 255];
          }
          return [0, 255, 200];
        },
        getPointRadius: () => 10,
        getElevation: (feature) => feature.properties.altezza_vo || 0,
        pickable: true,
        onHover: handleHover,
        onClick: handleClick,
        updateTriggers: {
          getFillColor: [hoveredFeature],
        },
      });
    });
  }, [geojsons, hoveredFeature, visibleLayers, layerColors]);
  

  return (
    <>
    <div style={{ width: "100%", height: "100%" }}>
      <DeckGL
      initialViewState={initialViewState}
        controller={true}
        layers={layers}
        getTooltip={({ object }) => 
          clickedFeature && object?.properties.id === clickedFeature.properties.id
            ? null
            : object
            ? { html: getTooltipContent(object) }
            : null
        }
      ><Map mapLib={maplibregl} mapStyle={mapStyle} />
        </DeckGL>

      {clickedFeature && tooltipPosition && (
       <Draggable>
        <div
          style={{
            position: "absolute",
            left: tooltipPosition.x,
            top: tooltipPosition.y,
            backgroundColor: "rgba(255, 255, 255, 0.9)",
            padding: "8px",
            borderRadius: "4px",
            boxShadow: "0 2px 4px rgba(0, 0, 0, 0.2)",
            zIndex: 1000,
            maxHeight: "300px", 
            overflowY: "auto",  
            cursor: "move",    
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
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            x
          </button>
          
          <div dangerouslySetInnerHTML={{ __html: getTooltipContent(clickedFeature) }} />
        </div>
      </Draggable>

      )}
    </div>
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
      </>
    
  );
};

export default ScenarioMap;

