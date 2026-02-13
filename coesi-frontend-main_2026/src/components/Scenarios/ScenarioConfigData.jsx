import React, { useEffect, useState } from 'react';
import './ScenarioConfigData.css'; // <- new CSS import
import fileConfig from '../../constants/newProjFileConfig.json';

const ScenarioConfigData = ({ fileList, setFileList, setFilesConfig, selectedTool, setSelectedTool }) => {

  const [visibilityState, setVisibilityState] = useState({});
  const [optionsState, setOptionsState] = useState({});


  /*
  const createUploadProps = (key) => {
    return {
      onRemove: (index) => {
        const newFileList = fileList.slice();
        newFileList.splice(index, 1);
        setFileList(newFileList);
        setVisibilityState((prevState) => ({
          ...prevState,
          [key]: false,
        }));
      },

      beforeUpload: (file) => {
        setFileList([...fileList, file]);
        setFilesConfig((prevFilesConfig) => ({...prevFilesConfig, ...filesCF}));
      },
    };
  };*/



const handleCheckboxChange = (value) => {
  const predefinedOrder = ['geometry', 'demographic', 'energy'];
  setSelectedTool((prevSelectedTool) => {
    let updatedSelectedTool;
    if (prevSelectedTool.includes(value)) {
      // Remove the item if it's already selected
      updatedSelectedTool = prevSelectedTool.filter((tool) => tool !== value);
    } else {
      // Add the new item to the list
      updatedSelectedTool = [...prevSelectedTool, value];
    }

    // Sort the updated list based on the predefined order
    return updatedSelectedTool.sort((a, b) => predefinedOrder.indexOf(a) - predefinedOrder.indexOf(b));
  });
};



const handleFileChange = (e, key) => {
  const file = e.target.files[0];
  if (!file) return;

  const fileExtension = file.name.split('.').pop().toLowerCase();
  const reader = new FileReader();

  reader.onload = (e) => {
    try {
      let parsedFile = null;

      if (fileExtension === 'csv') {
        const csvContent = e.target.result;
        const lines = csvContent.split('\n');
        const keys = lines[0].split(',').map(key => key.trim());
        const data = lines.slice(1).map(line => {
          const values = line.split(',').map(val => val.trim());
          return keys.reduce((obj, key, index) => {
            obj[key] = values[index];
            return obj;
          }, {});
        });

        parsedFile = {
          type: 'csv',
          name: file.name,
          keys,
          data,
        };

        setOptionsState((prevState) => ({
          ...prevState,
          [key]: keys.map((k) => ({ label: k, value: k })),
        }));

        setVisibilityState((prevState) => ({
          ...prevState,
          [key]: true,
        }));

      } else if (fileExtension === 'json' || fileExtension === 'geojson') {
        const parsedJson = JSON.parse(e.target.result);

        if (parsedJson.features && parsedJson.features[0] && parsedJson.features[0].properties) {
          const keys = Object.keys(parsedJson.features[0].properties);
          const data = parsedJson.features.map(feature => feature.properties);

          parsedFile = {
            type: fileExtension,
            name: file.name,
            keys,
            data,
          };

          setOptionsState((prevState) => ({
            ...prevState,
            [key]: keys.map((k) => ({ label: k, value: k })),
          }));

          setVisibilityState((prevState) => ({
            ...prevState,
            [key]: true,
          }));
        } else {
          alert('Invalid JSON structure.');
        }
      }

      // Add parsed file to fileList
      if (parsedFile) {
        setFileList((prevFileList) => [...prevFileList, { key, file: parsedFile }]);
      }

    } catch (error) {
      alert('Error parsing file.');
    }
  };

  if (['csv', 'json', 'geojson'].includes(fileExtension)) {
    reader.readAsText(file);
  } else {
    alert('Please upload a valid file.');
  }
};

const handleFileDelete = (key) => {
  setFileList((prevFileList) => prevFileList.filter((item) => item.key !== key));
  setVisibilityState((prevState) => ({ ...prevState, [key]: false }));
  setOptionsState((prevState) => ({ ...prevState, [key]: [] }));
  setFilesConfig((prevFilesConfig) => {
    const updatedFilesConfig = { ...prevFilesConfig };
    delete updatedFilesConfig[key];
    return updatedFilesConfig;
  });
};



  return (
    <>
      {Object.keys(fileConfig).map((key) => (
          <div
              key={key}
              className="scenario-grid"
          >
            <div className="scenario-form-row">
              <div className="scenario-form-label">
                {key}
                <br/>
                <small>
                  {fileConfig[key].prompt}
                </small>
              </div>
              <div className="scenario-form-content">
                <div
                    className="scenario-upload-dropbox"
                    tabIndex={0}
                    onClick={e => e.currentTarget.querySelector('input[type=file]').click()}
                    onDragOver={e => e.preventDefault()}
                    onDrop={e => {
                      e.preventDefault();
                      // The input file event and dropped files have the same structure: { target: { files } }
                      // So we simulate an input event for your existing handleFileChange:
                      handleFileChange(
                          {target: {files: e.dataTransfer.files}},
                          key
                      );
                    }}
                >
                  <input
                      type="file"
                      className="scenario-upload-file"
                      accept={fileConfig[key].type.map((ext) => `.${ext}`).join(', ')}
                      onChange={e => handleFileChange(e, key)}
                  />
                  <span style={{fontSize: "17px"}}>
    Drag a file {" "} <br/> <span> or {" "}</span> <br/>
                    <span style={{textDecoration: "underline", color: "#777", fontSize: "17px"}}>
      search in your pc
    </span>
  </span>
                </div>

                {visibilityState[key] && (
                    <button
                        onClick={() => handleFileDelete(key)}
                        className="scenario-delete-btn"
                    >
                      Delete
                    </button>
                )}
              </div>
            </div>

            {visibilityState[key] && (
                <FileConfiger
                    name={key}
                    keys={optionsState[key]}
                    config={fileConfig[key].config}
                    setFilesCF={setFilesConfig}
                />
            )}
            <div className="scenario-generate-title">or automatically generate data with our tool</div>
            <div>
              <label className="scenario-checkbox-label">
                <input
                    type="checkbox"
                    value="geometry"
                    onChange={() => handleCheckboxChange('geometry')}
                    checked={selectedTool.includes('geometry')}
                    className="scenario-checkbox"
                /> Geometry data
              </label>
              <label className="scenario-checkbox-label">
                <input
                    type="checkbox"
                    value="demographic"
                    onChange={() => handleCheckboxChange('demographic')}
                    checked={selectedTool.includes('demographic')}
                    className="scenario-checkbox"
                /> Demographic
              </label>
              <label className="scenario-checkbox-label">
                <input
                    type="checkbox"
                    value="energy"
                    onChange={() => handleCheckboxChange('energy')}
                    checked={selectedTool.includes('energy')}
                    className="scenario-checkbox"
                /> Energy
              </label>
            </div>
          </div>
      ))}
    </>
  );
};

export default ScenarioConfigData;

const FileConfiger = ({name, keys, config, setFilesCF}) => {
  const [fileConfig, setFileConfig] = useState(config);

  const handleSelectChange = (key, value) => {
    setFileConfig((prevValues) => ({
      ...prevValues,
      [key]: value,
    }));
  };

  useEffect(() => {
    const addConfig = {[name]: fileConfig};
    setFilesCF((prevFilesCF) => ({...prevFilesCF, ...addConfig}));
  }, [fileConfig]);

  return (
      <div className="scenario-file-configer">
        <span className="scenario-file-configer-title">Please configure the columns' names</span>
        {Object.keys(config).map((label) => (
            <div key={label} className="scenario-file-configer-row">
              <span>{label}</span>
              <select
                  className="scenario-file-configer-select"
                  value={fileConfig[label]}
                  onChange={(e) => handleSelectChange(label, e.target.value)}
          >
            {keys.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>
      ))}
    </div>
  );
};
