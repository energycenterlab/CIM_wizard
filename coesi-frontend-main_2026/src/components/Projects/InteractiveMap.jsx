import React, { useState, useCallback, useEffect } from "react";
import maplibregl from "maplibre-gl";
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import { area as calcArea, polygon } from "@turf/turf";
import { centroid } from "@turf/turf";

import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import "./MapStyle.css";


const customStyles = [
  // POINTS
  {
    "id": "gl-draw-point-inactive",
    "type": "circle",
    "filter": ["all", ["==", "$type", "Point"], ["!=", "meta", "midpoint"]],
    "paint": {
      "circle-radius": 5,
      "circle-color": "#3582FF"
    }
  },
  {
    "id": "gl-draw-point-active",
    "type": "circle",
    "filter": ["all", ["==", "$type", "Point"], ["==", "meta", "feature"]],
    "paint": {
      "circle-radius": 7,
      "circle-color": "#3582FF"
    }
  },

  // LINES
  {
    "id": "gl-draw-line-inactive",
    "type": "line",
    "filter": ["all", ["==", "$type", "LineString"], ["!=", "mode", "static"]],
    "layout": {
      "line-cap": "round",
      "line-join": "round"
    },
    "paint": {
      "line-color": "#3582FF",
      "line-width": 2
    }
  },
  {
    "id": "gl-draw-line-active",
    "type": "line",
    "filter": ["all", ["==", "$type", "LineString"], ["!=", "mode", "static"]],
    "layout": {
      "line-cap": "round",
      "line-join": "round"
    },
    "paint": {
      "line-color": "#3582FF",
      "line-width": 2
    }
  },

  // ✅ CUSTOM POLYGONS
  {
    id: 'gl-draw-polygon-fill',
    type: 'fill',
    filter: ['all', ['==', '$type', 'Polygon'], ['!=', 'mode', 'static']],
    paint: {
      'fill-color': '#3582FF',
      'fill-opacity': 0.4
    }
  },
  {
    id: 'gl-draw-polygon-stroke-active',
    type: 'line',
    filter: ['all', ['==', '$type', 'Polygon'], ['!=', 'mode', 'static']],
    paint: {
      'line-color': '#3582FF',
      'line-width': 2
    }
  },
  {
    id: 'gl-draw-polygon-static',
    type: 'fill',
    filter: ['all', ['==', '$type', 'Polygon'], ['==', 'mode', 'static']],
    paint: {
      'fill-color': '#3582FF',
      'fill-opacity': 0.2
    }
  },

  // MIDPOINT HANDLES
  {
    "id": "gl-draw-midpoint",
    "type": "circle",
    "filter": ["all", ["==", "$type", "Point"], ["==", "meta", "midpoint"]],
    "paint": {
      "circle-radius": 4,
      "circle-color": "#fbb03b"
    }
  }
];

function DrawControl(props) {
  const drawControl = new MapboxDraw({
    ...props.options,
    styles:customStyles
   });

  useEffect(() => {
    if (props.map) {
      const { map } = props;
      map.addControl(drawControl);

      map.on("draw.create", props.onCreate);
      map.on("draw.update", props.onUpdate);
      map.on("draw.delete", props.onDelete);

      return () => {
        map.off("draw.create", props.onCreate);
        map.off("draw.update", props.onUpdate);
        map.off("draw.delete", props.onDelete);
        map.removeControl(drawControl);
      };
    }
  }, [props.map, props.onCreate, props.onUpdate, props.onDelete]);

  return null;
}

DrawControl.defaultProps = {
  onCreate: () => {},
  onUpdate: () => {},
  onDelete: () => {},
};

export default function InteractiveMap({
  proj,
  onProjUpdate,
  location,
  polygonArray = {}
}) {
  const [features, setFeatures] = useState({});
  const [draw, setDraw] = useState(null);
  const [zoom, setZoom] = useState(location.zoom);

  const onUpdate = useCallback(
    (e) => {
      const featureID = e.features[0].id;
      setFeatures((currFeatures) => {
        const newFeatures = { ...currFeatures };
        for (const f of e.features) {
          newFeatures[f.id] = f;
        }
        const coordinatesObject = newFeatures[featureID].geometry.coordinates[0];

        const area = updateArea(coordinatesObject); 
        const updatedProj = {
          ...proj,
          coordinates: coordinatesObject,
          polygonCenter: area.center
        };
        onProjUpdate(updatedProj);
        console.log(updatedProj);
        return newFeatures;
      });
    },
    [proj, setFeatures, updateArea]
  );

  const onDelete = useCallback(
    (e) => {
      setFeatures((currFeatures) => {
        const newFeatures = { ...currFeatures };
        for (const f of e.features) {
          delete newFeatures[f.id];
        }
        if (Object.keys(newFeatures).length === 0) {
          const updatedProj = {
            ...proj,
            coordinates: [],
            polygonCenter: null
          };
          onProjUpdate(updatedProj);
        }
        return newFeatures;
      });
    },
  [updateArea, setFeatures]
  );

  useEffect(() => {
    const map = new maplibregl.Map({
      container: "interactivemap",
      style: "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
      center: [location.longitude, location.latitude],
      zoom: zoom + 4,
      attributionControl: false
    });
    
    const newDraw = new MapboxDraw({
      displayControlsDefault: false,
      controls: {
        polygon: true,
        trash: true
      },
      defaultMode: 'draw_polygon',
      styles:customStyles
    });
    map.addControl(newDraw, "top-left");
    setDraw(newDraw);

    setTimeout(() => {
      const toolbox = document.querySelector(".mapboxgl-ctrl-top-left");
      if (toolbox) {
        toolbox.style.top = "20px";
        toolbox.style.left = "50%";
        toolbox.style.transform = "translateX(-50%)";
      }
    }, 0);

    map.on("draw.create", onUpdate);
    map.on("draw.update", onUpdate);
    map.on("draw.delete", onDelete);

    if (polygonArray && polygonArray.length > 0) {
      const geojsonpolygon = {
        type: "Feature",
        geometry: {
          type: "Polygon",
          coordinates: [polygonArray]
        }
      };
      map.on("load", () => {
        map.addSource("polygon_proj", {
          type: "geojson",
          data: geojsonpolygon
        });
        map.addLayer({
          id: "polygon_proj",
          type: "fill",
          source: "polygon_proj",
          layout: {},
          paint: {
            "fill-color": "white",
            "fill-opacity": 0.7,
            "fill-outline-color": "orange"
          }
        });
        console.log("layer added");
      });
    }

    map.on("zoom", () => {
      setZoom(map.getZoom());
    });

    return () => {
      map.remove();
    };
  }, [location, polygonArray.length]);

  function updateArea(coordinates) {
    if (!draw) {
      console.log("updatearea called");
    }
    if (coordinates.length > 0) {
      const poly = polygon([coordinates]);
      const polyCenter = centroid(poly);
      console.log("center found,", polyCenter);
      const area = calcArea(poly);
      const rounded_area = Math.round(area * 100) / 100;
      console.log("area calculated,", rounded_area);
      return {
        area: rounded_area,
        center: {
          latitude: polyCenter.geometry.coordinates[1],
          longitude: polyCenter.geometry.coordinates[0],
          zoom: zoom
        }
      };
    } else {
      console.log("unsuccessful");
    }
  }

    return (
       <div className="map-wrapper">
         <div className="map-wrapper__header">
           Draw a polygon for project creation
         </div>
         <div id="interactivemap" className="map-wrapper__map"></div>
       </div>
    );
}
