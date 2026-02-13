import React, { useState, useRef } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';

import ClipLoader from "react-spinners/ClipLoader";

//import { createBrowserHistory } from 'history';

import InteractiveMap from './InteractiveMap';
import routes from '../../constants/routes.json';
import { createBaselineScenario } from '../../services/cimWizard';
import "./DrawerItems.css";

const ProjectGeoForm = () => {
 // const history = createBrowserHistory();

  const [formData, setFormData] = useState({});
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [projvalue, setProjValue] = useState({});
  const [fileUploaded, setFileUploaded]= useState(false);
  const [selectedOption, setSelectedOption] = useState('mapPolygon');
  const [buildingGeometry, setBuildingGeometry] = useState();

  const navigate = useNavigate();

  const handleCancel = () => {
    setFormData({});
    setErrorMessage("");
    setProjValue({});
    setFileUploaded(false);
    setConfirmLoading(false);
  };

  const handleCreate = async () => {
    console.log('Creating project with data:', projvalue);
    
    if (!formData.proj_name) {
      setErrorMessage('Project name is mandatory!');
      return;
    }
    
    if (fileUploaded && projvalue.coordinates && projvalue.coordinates.length > 0) {
      setErrorMessage('Please provide either a file or draw a polygon, not both.');
      return;
    }
    
    if (!fileUploaded && (!projvalue.coordinates || projvalue.coordinates.length === 0)) {
      setErrorMessage('Please upload a file or draw a polygon to create the project.');
      return;
    }

    setConfirmLoading(true);
    setErrorMessage('');

    try {
      // Convert coordinates to GeoJSON Feature format
      let projectBoundary;
      
      if (fileUploaded && buildingGeometry) {
        // If building geometry file was uploaded, use it as project boundary
        if (buildingGeometry.type === 'FeatureCollection' && buildingGeometry.features && buildingGeometry.features.length > 0) {
          // Use the first feature as the project boundary
          projectBoundary = buildingGeometry.features[0];
        } else if (buildingGeometry.type === 'Feature') {
          projectBoundary = buildingGeometry;
        } else {
          throw new Error('Invalid GeoJSON format in uploaded file. Expected Feature or FeatureCollection.');
        }
      } else {
        // Convert polygon coordinates to GeoJSON Feature
        // projvalue.coordinates is an array of [lng, lat] pairs
        if (!projvalue.coordinates || projvalue.coordinates.length < 3) {
          throw new Error('Polygon must have at least 3 coordinates.');
        }
        
        // Ensure polygon is closed (first and last coordinates should be the same)
        const coordinates = [...projvalue.coordinates];
        const firstCoord = coordinates[0];
        const lastCoord = coordinates[coordinates.length - 1];
        if (firstCoord[0] !== lastCoord[0] || firstCoord[1] !== lastCoord[1]) {
          coordinates.push([firstCoord[0], firstCoord[1]]);
        }
        
        projectBoundary = {
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: [coordinates] // Polygon coordinates need to be wrapped in an array
          },
          properties: {}
        };
      }

      console.log('Sending project boundary to backend:', projectBoundary);

      // Call the backend API to create the project
      const response = await createBaselineScenario({
        project_boundary: projectBoundary,
        project_name: formData.proj_name,
        scenario_name: 'baseline',
        save_to_db: true
      });

      console.log('Backend response:', response);

      if (response && response.project_id) {
        // Success! Navigate to the scenarios page for this project
        const projectId = response.project_id;
        navigate(routes.SCENARIOS.replace(':projectId', projectId));
        
        // Reset form
        setFormData({});
        setProjValue({});
        setFileUploaded(false);
        setBuildingGeometry(undefined);
      } else {
        throw new Error('Invalid response from server: missing project_id');
      }
    } catch (err) {
      console.error('Failed to create project:', err);
      const errorMessage = err?.message || err?.toString() || 'Failed to create project. Please try again.';
      setErrorMessage(errorMessage);
    } finally {
      setConfirmLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleMapUpdate = (updatedproj) => {
    console.log('NewProjModal');
    console.log(updatedproj);
    setProjValue(updatedproj);
  };

  const Loader = ({ isSpinning, isVisible }) => {
    // Only render the loader if it's visible
    if (!isVisible) {
      return null;
    }

    return (
      <div className="sweet-loading">
        <ClipLoader
          color="green" // Default color
          loading={isSpinning} // Controlled by parent
          size={150}
          aria-label="Loading Spinner"
          data-testid="loader"
        />
      </div>
    );
  };

  return (

    <form onSubmit={(e) => {
      e.preventDefault();  // prevent default form submission
        handleCreate();
          }}>
      <div style={{width:"100%",overflow:'hidden'}}>
        <h2
        style={{
          fontSize: "24px",
          fontWeight: "bold",
          textAlign: "left",
          marginTop: "0px"
        }}
        >Create a Project</h2>
        <input
          type="text"
          className="inputbox"
          name="proj_name"
          value={formData.proj_name}
          onChange={handleInputChange}
          placeholder="Enter project name"
          style={{ width: '100%', marginBottom: "20px" }}
        />
      </div>

      <div style={{ width:"100%" }}>
      <h3
        style={{
          fontSize: "24px",
          textAlign: "left",
        }}
        >Define project geometry:</h3>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start'}}>


      <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: '10px' }}>
        <input
          type="radio"
          id="mapPolygon"
          name="geometryOption"
          value="mapPolygon"
          checked={selectedOption === 'mapPolygon'}
          onChange={(e) => setSelectedOption(e.target.value)}
          style={{ width: '20px', height: '20px', margin: 0}}
        />
        <label htmlFor="mapPolygon" style={{
      marginLeft: '10px',
      fontSize: '16px',
      lineHeight: '1.2',
    }}>Use Map Polygon</label>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: '10px' }}>
          <input
          type="radio"
          id="geometryUpload"
          name="geometryOption"
          value="geometryUpload"
          checked={selectedOption === 'geometryUpload'}
          onChange={(e) => setSelectedOption(e.target.value)}
          style={{ width: '20px', height: '20px', margin: 0}}
        />
        <label htmlFor="geometryUpload"
         style={{
      marginLeft: '10px',
      fontSize: '16px',
      lineHeight: '1.2',
    }}>Upload Geometry File</label>
      </div>
        </div>

        {selectedOption === 'geometryUpload' && (
          <div style={{ marginTop: '5px', textAlign:"left"}}>
            <label style={{ marginBottom: '15px'}} >Upload geometry file for project:</label>
            <BuildingGeometryUpload fileUploaded={fileUploaded} setFileUploaded={setFileUploaded} setBuildingGeometry={setBuildingGeometry} />
          </div>
        )}

        {selectedOption === 'mapPolygon' && (
          <div style={{ marginTop: '20px' }}>
            <MapPolygonSearchLocation
              proj={{ ...projvalue }}
              onMapUpdate={handleMapUpdate}
            />
          </div>
        )}
        </div>
    <RasterUpload />
      {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
      <div className={"button-row"}>
      <button type="submit" disabled={confirmLoading}>
        {confirmLoading ? "Creating..." : "Create Project"}
      </button>
      <button type="button" className="cancel-button" onClick={handleCancel} style={{ marginLeft: '10px' }}>
        Cancel
      </button>
    </div>
  </form>
  );
};
export default ProjectGeoForm;


const MAX_AREA_SIZE = 100;

const MapPolygonSearchLocation = ({ proj, onMapUpdate }) => {
  const [location, setLocation] = useState({
    longitude:12.4829321, //roma
    latitude:41.8933203,
    zoom: 8,
    pitch: 0,
    bearing: 0
  });

  const [latlong, setLatlong] = useState({ lat: 0, long: 0 });
  const [address, setAddress] = useState('');

  const getLatLong = async () => {
    try {
      const resp = await axios.get(
        `https://nominatim.openstreetmap.org/?format=json&q=${address}&limit=1`
      );
      if (resp.data && resp.data.length > 0) {
        const lat = resp.data[0].lat;
        const long = resp.data[0].lon;
        setLatlong({ lat, long });
        goToLocation(lat, long);
      }
    } catch (err) {
      console.log('Error during location retrieval:', err);
    }
  };

  const goToLocation = (lat, long) => {
    console.log('Going to location:', lat, long);
    const regex = /^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$/;
    if (!regex.test(`${lat},${long}`)) {
      console.log('Invalid latitude/longitude coordinates');
      return;
    }

    setLocation({
      latitude: parseFloat(lat),
      longitude: parseFloat(long),
      zoom: 12,
    });
  };

  const handleProjUpdate = (updatedProj) => {
    onMapUpdate(updatedProj);};

  return (
  <>
    <div style={{textAlign: "left"}}>
      <label>Select a project area:</label>
      <br/>
      <small style={{color: '#888', fontSize: '0.8em'}}>Select project location by name: </small>

      <div className={"flex-row"}>
        <input
          id="address"
          className="inputbox"
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="Input location name"
        />
        <button className={"mapsearchbutton"} type="button" onClick={getLatLong}>
          Search
        </button>
      </div>

      <div className={"flex-row"}>
        <input
          id="latitude"
          className="inputbox"
          type="number"
          value={latlong.lat}
          onChange={(e) => setLatlong({...latlong, lat: e.target.value})}
          placeholder="Latitude"
        />
        <input
          id="longitude"
          className="inputbox"
          type="number"
          value={latlong.long}
          onChange={(e) => setLatlong({...latlong, long: e.target.value})}
          placeholder="Longitude"
        />
        <button className="mapsearchbutton" type="button" onClick={() => goToLocation(latlong.lat, latlong.long)}>
          Go
        </button>
      </div>
    </div>

    <div>
      <InteractiveMap
        proj={{...proj}}
        onProjUpdate={handleProjUpdate}
        location={location}
      />
    </div>
  </>
)

}

//may be used later
const checkArea = (rule, value, callback) => {
  if (!rule.required) callback();
  else if (!value)
    callback('Create a polygon by selecting an area in the map.');
  else if (calcPolyArea(value) > MAX_AREA_SIZE) {
    callback(
        `Area selected is above ${MAX_AREA_SIZE} km2. CEA would not be able to extract information from that size due to the bandwidth limitation of Open Street Maps API. Try selecting a smaller area.`
    );
  } else {
    callback();
  }
};

// BuildingGeometryUpload.jsx

const BuildingGeometryUpload = ({ fileUploaded, setFileUploaded, setBuildingGeometry }) => {
  const fileInputRef = useRef(null);

  // Handle normal file select and drag-drop
  const handleFileChange = (event) => {
    let file;
    // Handles both normal and drag events
    if (event.dataTransfer && event.dataTransfer.files.length > 0) {
      file = event.dataTransfer.files[0];
    } else {
      file = event.target.files[0];
    }
    if (!file) {
      console.log('No file selected.');
      return;
    }
    if (
      file.type === 'application/json' ||
      file.name.endsWith('.json') ||
      file.name.endsWith('.geojson')
    ) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const jsonData = JSON.parse(e.target.result);
          setBuildingGeometry(jsonData);
          setFileUploaded(true);
        } catch (error) {
          alert('Invalid JSON file format.');
        }
      };
      reader.readAsText(file);
    } else {
      alert('Please upload a valid JSON or GeoJSON file.');
      setFileUploaded(false);
    }
  };

  // Remove uploaded file and reset input
  const handleFileRemove = () => {
    setFileUploaded(false);
    setBuildingGeometry(undefined);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div key="buildingFile" style={{ marginBottom: '20px' }}>
      <div
        className="project-upload-dropbox"
        tabIndex={0}
        onClick={() => fileInputRef.current && fileInputRef.current.click()}
        onDragOver={e => e.preventDefault()}
          onDrop={e => {
            e.preventDefault();        // <--- THIS LINE IS KEY!
            handleFileChange(e);
          }}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '110px',
          background: '#f3f3f3',
          marginTop: "8px",
          borderRadius: '16px',
          border: '2px dashed #bbb',
          cursor: 'pointer',
          position: 'relative',
        }}
        title="Drag a JSON/GeoJSON file here or click to search in your PC"
      >
        <input
          type="file"
          accept=".json,.geojson,application/json"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="project-upload-file"
          style={{ display: "none" }}
        />
        {!fileUploaded ? (
          <span>
            <b>Drag a file</b> or{' '}
            <span style={{ textDecoration: "underline", color: "#777", cursor: "pointer" }}>
              search in your PC
            </span>
            <br />
            <small>(Accepted: .json or .geojson)</small>
          </span>
        ) : (
          <span style={{ color: "#29582A" }}>
            File uploaded!{' '}
            <button type="button" className="cancel-button" style={{ marginLeft: 12 }} onClick={handleFileRemove}>
              Remove
            </button>
          </span>
        )}
      </div>
    </div>
  );
};


const RasterUpload = () => {
  const [isDTMUpload, setDTMUpload] = useState(false);
  const [isDSMUpload, setDSMUpload] = useState(false);

  const dtmInputRef = useRef(null);
  const dsmInputRef = useRef(null);


  const handleDTMChange = () => {
    setDTMUpload(true);

  }
  const handleDTMRemove = () => {
    setDTMUpload(false)
    if (dtmInputRef.current) {
      dtmInputRef.current.value = '';
    }
  };

  const handleDSMChange = () => {
    setDSMUpload(true)
  }
  const handleDSMRemove = () => {
    setDSMUpload(false)
    if (dsmInputRef.current) {
      dsmInputRef.current.value = '';
    }
  }

  return (
    <>
     <label style={{ marginTop: '12px' }}><strong>*Optional: You can upload terrain data here</strong></label>
    <div key="DTMUpload">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent:'space-between' }}>
      <span>DTM</span>
          <input
            type="file"
            accept="json" //should dbe .json
            ref={dtmInputRef}
            onChange={handleDTMChange}
            style={{ width: '300px' , marginBottom: '10px', marginLeft:'20px' }}
          />
        {isDTMUpload && (<button type="button" onClick={handleDTMRemove} style={{ marginLeft: '10px' }}>
        Remove
        </button>  )}
      </div>
  </div>
  <div key="DSMUpload">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent:    'space-between' }}>
      <span>DSM</span>
          <input
            type="file"
            accept="json"
            onChange={handleDSMChange}
            ref={dsmInputRef}
            style={{ width: '300px',marginLeft:'20px' }}
          />
        {isDSMUpload && (<button type="button" onClick={handleDSMRemove} style={{ marginLeft: '10px' }}>
        Remove
        </button> )}
      </div>
  </div>
  </>
  )
}


