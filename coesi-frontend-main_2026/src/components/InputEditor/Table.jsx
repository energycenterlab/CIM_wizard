import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { TabulatorFull } from 'tabulator-tables';
import axios from 'axios';
import routes from '../../constants/routes.json';
import tableDep from '../../constants/tableDependency.json';

import { useDispatch, useSelector } from 'react-redux';
import { removeSelectedFeature, addSelectedFeature, deleteSelectedFeature } from '../../slices/selectedFeaturesSlice';
import 'tabulator-tables/dist/css/tabulator.min.css';
import './Table.css'


const Table = ({ tab, data, columns}) => {
  //const { scenarioInfo } = useParams();
  const scenarioInfo = "baselineDemo==id5678"
  const [scenarioName, scenarioId] = scenarioInfo.split('==');
  const tabulator = useRef(null);

  return (
    <>
        <div className="card-title">
          <TableButtons tabulator={tabulator} scenarioName={scenarioName} />
        </div>
        {scenarioName === "baseline" ? (
          <TableBaseline data={data} columns={columns} tabulator={tabulator} />
        ) : (
          <TableEditor
            tab={tab}
            data={data}
            columns={columns}
            tabulator={tabulator}
          />
        )}
    </>
  );
};

const TableButtons = ({ tabulator, scenarioName }) => {
  const [changeInfoVisible, setChangeInfoVisible] = useState(false);
  const [changesLog, setChangesLog] = useState([]);
  const [filterActive, setFilterActive] = useState(false);
  
  const dispatch = useDispatch();
  const selectedRows = useSelector((state) => state.selectedFeatures.selectedFeatures);

  const selectAll = () => {
    tabulator.current.selectRow();
    const allRows = tabulator.current.getData();
    const allFeatureIds = allRows.map((row) => row.id);
    allFeatureIds.forEach((id) => {
      if (!selectedRows.includes(id)) {
        dispatch(addSelectedFeature(id));
      }
    });
  };

  const clearSelected = () => {
    tabulator.current.deselectRow();
    dispatch(deleteSelectedFeature());
  }

  const toggleFilter = () => {
    if (filterActive) {
      tabulator.current.clearFilter();
      tabulator.current.selectRow(selectedRows);
    } else {
      tabulator.current.setFilter("id", "in", selectedRows);
    }
    setFilterActive(!filterActive);
  };

  const saveChangesforConfirm = () => {
    const changes = tabulator.current.getEditedCells();
    let changeArray = [];
    changes.forEach(change => {
      changeArray = [...changeArray, { id: change._cell.row.data.id, field: change._cell.column.field, old_value: change._cell.oldValue, new_value: change._cell.value }]
    });
    setChangesLog(changeArray);
    setChangeInfoVisible(true);
  };

  return (
    <div className="table-buttons" style={{width:"100%"}}>
      <button className="table-btn" onClick={selectAll}>Select All</button>
      <button className="table-btn" onClick={clearSelected}>Clear Selection</button>
      <button className="table-btn" onClick={toggleFilter}>
        {filterActive ? "Clear Filter" : "Filter Selection"}
      </button>
      {scenarioName !== "baseline" && (
        <button className="table-btn" onClick={saveChangesforConfirm}>
          Change Summary
        </button>
      )}
      <TableChangeConfirm
        changeInfoVisible={changeInfoVisible}
        setChangeInfoVisible={setChangeInfoVisible}
        changes={changesLog}
        table={tabulator.current}
      />
    </div>
  );
};

const TableEditor = ({ data, columns, tabulator}) => {
  const divRef = useRef(null);
  const editableColumns = columns.map((col) => ({
    ...col,
    editable: true ,
   // editor:"input"
  }));

  const dispatch = useDispatch();
  const selectedRows = useSelector((state) => state.selectedFeatures.selectedFeatures);

  useEffect(() => {
    // Destroy existing table if it exists
    if (tabulator.current) {
      tabulator.current.destroy();
    }
    
    tabulator.current = new TabulatorFull(divRef.current, {
      data,
      index: "id",
      columns:editableColumns,
      layout: "fitDataFill",
      height: "100%",
      width: "100%" ,
      selectable: true,
      history: true,
     // editTriggerEvent: "dblclick",
      editable: true,
      virtualDom: false, // Disable virtual DOM for better scrolling
      scrollToRowPosition: "top",
      scrollToRowIfVisible: true
    });


  tabulator.current.on("cellContextMenu", (e, cell) => {
    e.preventDefault(); 
    const field = cell.getField();
    const value = cell.getValue();
    console.log("Right-click Editing Cell:", field, value);

    cell.edit(true);
  });

  tabulator.current.on("cellDblClick", (e, cell) => {
    const rowData = cell.getRow().getData(); // Get the full row data
    console.log("Double-clicked row data:", rowData);

    const buildingId = rowData.id;
    const row = cell.getRow();

    if (row.isSelected()) {
      row.deselect();
      if (selectedRows.includes(buildingId)) {
        dispatch(removeSelectedFeature(buildingId));
      }
    } else {
      row.select();
      if (!selectedRows.includes(buildingId)) {
        dispatch(addSelectedFeature(buildingId));
      }
    }
  });


    tabulator.current.on("tableBuilt", () => {
      if (selectedRows && selectedRows.length > 0) {
        tabulator.current.selectRow(selectedRows); // Select rows matching state
      }
    });

    /*
    tabulator.current.on("cellClick", (e, cell) => {
      const rowData = cell.getRow().getData(); // Get the full row data
      console.log('Row data:', rowData); // Log the full row data
      
      const buildingId = rowData.id; 
      const row = cell.getRow();
    
      if (row.isSelected()) {
        row.deselect(); 
        if (selectedRows.includes(buildingId)) {
          dispatch(removeSelectedFeature(buildingId)); 
        }
      } else {
        row.select();
        if (!selectedRows.includes(buildingId)) {
          dispatch(addSelectedFeature(buildingId));
        }
      }
    });*/



    return () => {
      if (tabulator.current) {
        tabulator.current.destroy();
      }
    };
  }, [data, columns, selectedRows]);

  return <div ref={divRef} style={{ display: data ? "block" : "none" }} />;
};

const FeatureUpdatePut = async ({newTabledata, params, mapCenter}) => {
  try {
    // Construct the features array by fetching geometries and combining them with table data
    const features = await Promise.all(
      newTabledata.map(async (item) => {
        try {
          const response = await axios.get(`${routes.ALIDB}/api/bgeo/${item.id}/`);
          const coordinates = response.data.coordinates[0];

          return {
            type: "Feature",
            properties: {
              ...item,
            },
            geometry: {
              type: "Polygon",
              coordinates,
            },
          };
        } catch (error) {
          console.error(`Failed to fetch geometry for id: ${item.id}`, error);
          throw error; // Re-throw error to be handled globally
        }
      })
    );

    // Construct the complete request payload
    const updatePayload = {
      project_id: params.projectId,
      scenario_id: params.scenarioId,
      projectName: params.projname,
      scenario_name: params.scenarioName,
      mapCenter: mapCenter,
      scenarioList: ["update"],
      crs: 4326,
      polygonArray: [],
      buildingGeometry: {
        type: "FeatureCollection",
        crs: {
          type: "name",
          properties: {
            name: "EPSG:4326",
          },
        },
        features,
      },
    };

    // Log or send the constructed payload
    console.log("Update Payload:", JSON.stringify(updatePayload, null, 2));
    console.log(updatePayload)

    // Uncomment and use the appropriate API endpoint for sending the payload
    const response = await axios.post(`${routes.SHELPER}/updateBuildings`, updatePayload);
     console.log("Response from server:", response.data);

  } catch (error) {
    console.error("Error creating the update request payload:", error);
  }
};


const TableChangeConfirm = ({ changeInfoVisible, setChangeInfoVisible, changes, table }) => {
  //const { projectInfo, scenarioInfo } = useParams();
  const projectInfo = "projectDemo==id1234"
  const scenarioInfo = "baselineDemo==id5678"
  const [projname, projectId] = projectInfo.split('==');
  const [scenarioName, scenarioId] = scenarioInfo.split('==');
  
  const params = {
    projectId,
    projname,
    scenarioName,
    scenarioId
  }
  const mapCenter = useSelector((state) => state.projectPolygonInfo.mapCenter);
  let newTabledata = [];


  const confirmTableChange = async () => {   

    changes.forEach(change => {
      // Check if old_value and new_value are different
      if (change.old_value !== change.new_value) {
        const fieldKey = change.field; 
        const dependencyArray = tableDep[fieldKey];   
        if (Array.isArray(dependencyArray)) {
          const row = table.getRow(change.id);
          if (row) {
            const rowData = row._row.data
            dependencyArray.forEach(dependentField => {
              if (rowData.hasOwnProperty(dependentField)) {
              rowData[dependentField] = null; // Set the value to null
              //rowData[dependentField] = 1000 * Math.random();//this is only for faking
              } else {
                console.warn(`Field '${dependentField}' not found in row data.`);
              }
            });
            
            row.update(rowData); 
            newTabledata.push(rowData)

          } else {
            console.warn(`No row found for id: ${change.id}`);
          }

        } else {
          console.warn(`1No array found for field '${fieldKey}' in tabledependency.`);
        }
      }
    });


    console.log('new data',newTabledata);
    FeatureUpdatePut({newTabledata,params,mapCenter})


    table.clearCellEdited();
    setChangeInfoVisible(false);
  };

  const cancelTableChange = () => {
    const changesArray = table.getEditedCells();
    changesArray.forEach(cell => { cell.restoreOldValue(); });
    table.redraw(true);
    console.log('restored');
    table.clearCellEdited();
    setChangeInfoVisible(false);
  };

  return (
    <div style={{ display: changeInfoVisible ? 'block' : 'none' }}>
      <h2>Table Change Summary</h2>
      {changes.map((item, index) => (
        <div key={index}>
          id: {item.id},
          field: {item.field},
          old value: {item.old_value},
          new value: {item.new_value},
        </div>
      ))}
      <button onClick={confirmTableChange}>Confirm Changes</button>
      <button onClick={cancelTableChange}>Discard Changes</button>
    </div>
  );
};

const TableBaseline = ({ data, columns, tabulator }) => {
  const divRef = useRef(null);
  
  const dispatch = useDispatch();
  const selectedRows = useSelector((state) => state.selectedFeatures.selectedFeatures);

  useEffect(() => {
    // Destroy existing table if it exists
    if (tabulator.current) {
      tabulator.current.destroy();
    }
    
    const nonEditableColumns = columns.map(col => ({
      ...col,
      editable: false
    }));

    tabulator.current = new TabulatorFull(divRef.current, {
      data,
      index: 'id',
      columns: nonEditableColumns,
      layout: 'fitDataFill',
      height: '100%',
      selectable: true,
      history: true,
      editable: false,
      virtualDom: false, // Disable virtual DOM for better scrolling
      scrollToRowPosition: "top",
      scrollToRowIfVisible: true
    });

    tabulator.current.on("cellDblClick", (e, cell) => {
      alert("It is not possible to edit data in the baseline. If you want to do so, please create a new scenario.");
      e.stopPropagation();
    });

    tabulator.current.on("cellClick", (e, cell) => {
      const rowData = cell.getRow().getData(); // Get the full row data
      console.log('Row data:', rowData); // Log the full row data
      
      const buildingId = rowData.id; 
      const row = cell.getRow();
    
      if (row.isSelected()) {
        row.deselect(); 
        if (selectedRows.includes(buildingId)) {
          dispatch(removeSelectedFeature(buildingId)); 
        }
      } else {
        row.select();
        if (!selectedRows.includes(buildingId)) {
          dispatch(addSelectedFeature(buildingId));
        }
      }
    });
    
    return () => {
      if (tabulator.current) {
        tabulator.current.destroy(); 
      }
    };
  }, [data, columns, tabulator, selectedRows]);


  return <div ref={divRef} style={{ display: data ? 'block' : 'none' }} />;
};

export default Table;
