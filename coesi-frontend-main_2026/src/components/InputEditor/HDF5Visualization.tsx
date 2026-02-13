import React, { useState, useEffect } from "react";
import "./HDF5Visualization.css";
import { COESI_API_URLS } from "../../config/apiConfig";

interface HDF5File {
  name: string;
  size: string;
  scenario_name?: string;
}

interface HDF5Data {
  hdf5_files?: HDF5File[];
  message?: string;
}

interface HDF5VisualizationProps {
  data: HDF5Data | null;
  simulationId: string;
  apiBaseUrl?: string;
}

interface DatasetInfo {
  [key: string]: {
    shape: number[];
    dtype: string;
    attributes?: any;
  };
}

interface FileInfo {
  size: string;
  groups: any;
  datasets: DatasetInfo;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    tension: number;
  }[];
}

interface GroupedDatasets {
  [groupName: string]: {
    displayName: string;
    attributes: string[];
    fullPaths: string[];
  };
}

const HDF5Visualization: React.FC<HDF5VisualizationProps> = ({
  data,
  simulationId,
  apiBaseUrl = COESI_API_URLS.SIMULATIONS,
}) => {
  const [selectedFile, setSelectedFile] = useState<string>("");
  const [fileInfo, setFileInfo] = useState<FileInfo | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<string>("");
  const [groupedDatasets, setGroupedDatasets] = useState<GroupedDatasets>({});
  const [chartData, setChartData] = useState<{
    [groupName: string]: ChartData;
  }>({});
  const [loading, setLoading] = useState<{ [groupName: string]: boolean }>({});
  const [expandedGroups, setExpandedGroups] = useState<{
    [groupName: string]: boolean;
  }>({});

  const colors = [
    "#3B82F6",
    "#EF4444",
    "#10B981",
    "#F59E0B",
    "#8B5CF6",
    "#06B6D4",
    "#84CC16",
    "#F97316",
    "#EC4899",
    "#6366F1",
  ];

  useEffect(() => {
    if (data?.hdf5_files && data.hdf5_files.length > 0 && !selectedFile) {
      setSelectedFile(data.hdf5_files[0].name);
    }
  }, [data, selectedFile]);

  useEffect(() => {
    if (selectedFile) {
      loadFileInfo();
    }
  }, [selectedFile]);

  const loadFileInfo = async () => {
    if (!selectedFile) return;

    try {
      const baseUrl = apiBaseUrl.replace('/api/v1/simulations', '');
      const response = await fetch(
        `${baseUrl}/api/v1/simulations/${simulationId}/results/files/${selectedFile}/info`
      );
      if (response.ok) {
        const info = await response.json();
        setFileInfo(info);

        // Process groups to create grouped datasets
        const grouped: GroupedDatasets = {};

        if (info.groups) {
          const groupKeys = Object.keys(info.groups);
          groupKeys.forEach((groupPath: string) => {
            const groupInfo = info.groups[groupPath];
            if (groupPath.startsWith("Series/") && groupPath !== "Series") {
              const entityName = groupPath.replace("Series/", "");
              const attributes = groupInfo.items || [];

              const fullPaths = attributes.map(
                (attr: string) => `${groupPath}/${attr}`
              );

              grouped[entityName] = {
                displayName: entityName,
                attributes: attributes,
                fullPaths: fullPaths,
              };
            }
          });
        }

        setGroupedDatasets(grouped);

        const groupKeys = Object.keys(grouped);
        if (groupKeys.length > 0 && !selectedGroup) {
          setSelectedGroup(groupKeys[0]);
        }
      }
    } catch (error) {
      console.error("Error loading file info:", error);
    }
  };

  const loadDatasetData = async (groupName: string) => {
    if (!selectedFile || !groupName || !groupedDatasets[groupName]) return;

    const selectedGroupData = groupedDatasets[groupName];
    const selectedDatasets = selectedGroupData.fullPaths;

    setLoading((prev) => ({ ...prev, [groupName]: true }));
    try {
      const datasetsParam = selectedDatasets.join(",");
      const baseUrl = apiBaseUrl.replace('/api/v1/simulations', '');
      const response = await fetch(
        `${baseUrl}/api/v1/simulations/${simulationId}/results/files/${selectedFile}?datasets=${encodeURIComponent(
          datasetsParam
        )}`
      );

      if (response.ok) {
        const responseData = await response.json();

        if (responseData.datasets) {
          const timeInfo = responseData.time_info || {};
          const timeSteps = timeInfo.time_steps || [];

          const datasets = selectedDatasets.map(
            (datasetPath: string, index: number) => {
              const pathParts = datasetPath.split("/");

              if (pathParts.length >= 3) {
                const entity = pathParts[1];
                const attribute = pathParts[2];

                const entityData = responseData.datasets[entity];
                const attributeData = entityData?.[attribute];
                const values = attributeData?.values || [];

                return {
                  label: attribute,
                  data: Array.isArray(values) ? values : [values],
                  borderColor: colors[index % colors.length],
                  backgroundColor: colors[index % colors.length] + "20",
                  tension: 0.1,
                };
              }

              return {
                label: datasetPath.split("/").pop() || datasetPath,
                data: [],
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + "20",
                tension: 0.1,
              };
            }
          );

          const maxDataLength = Math.max(
            ...datasets.map((ds: any) => ds.data.length)
          );
          const labels =
            timeSteps.length >= maxDataLength
              ? timeSteps.slice(0, maxDataLength)
              : Array.from({ length: maxDataLength }, (_, i) => i.toString());

          const processedChartData = {
            labels,
            datasets: datasets.filter((ds: any) => ds.data.length > 0),
          };

          setChartData((prev) => ({
            ...prev,
            [groupName]: processedChartData,
          }));
          setExpandedGroups((prev) => ({ ...prev, [groupName]: true }));
        }
      }
    } catch (error) {
      console.error("Error loading dataset data:", error);
    } finally {
      setLoading((prev) => ({ ...prev, [groupName]: false }));
    }
  };

  const handleGroupSelection = (groupName: string) => {
    setSelectedGroup(groupName);
  };

  const toggleGroupExpansion = (groupName: string) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [groupName]: !prev[groupName],
    }));
  };

  const renderSimpleChart = (groupName: string, data: ChartData) => {
    if (!data || data.datasets.length === 0) {
      return <div className="no-chart">No data to display</div>;
    }

    const maxValue = Math.max(...data.datasets.flatMap((ds) => ds.data));
    const minValue = Math.min(...data.datasets.flatMap((ds) => ds.data));
    const range = maxValue - minValue || 1;

    return (
      <div className="simple-chart">
        <div className="chart-header">
          <h4>{groupName} - Time Series Data</h4>
          <div className="chart-legend">
            {data.datasets.map((dataset: any, index: number) => (
              <div key={index} className="legend-item">
                <div
                  className="legend-color"
                  style={{ backgroundColor: dataset.borderColor }}
                ></div>
                <span>{dataset.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="chart-container">
          <svg width="100%" height="400" viewBox="0 0 800 400">
            {/* Grid lines */}
            {[0, 1, 2, 3, 4].map((i) => (
              <line
                key={`grid-${i}`}
                x1="50"
                y1={50 + i * 80}
                x2="750"
                y2={50 + i * 80}
                stroke="#e5e5e5"
                strokeWidth="1"
              />
            ))}

            {/* Y-axis labels */}
            {[0, 1, 2, 3, 4].map((i) => {
              const value = maxValue - (i * range) / 4;
              return (
                <text
                  key={`y-label-${i}`}
                  x="40"
                  y={55 + i * 80}
                  textAnchor="end"
                  fontSize="12"
                  fill="#666"
                >
                  {value.toFixed(2)}
                </text>
              );
            })}

            {/* Data lines */}
            {data.datasets.map((dataset: any, datasetIndex: number) => {
              const points = dataset.data.map((value: number, i: number) => {
                const x = 50 + (i * 700) / (data.labels.length - 1 || 1);
                const y = 50 + ((maxValue - value) * 320) / range;
                return `${x},${y}`;
              });

              return (
                <polyline
                  key={datasetIndex}
                  points={points.join(" ")}
                  fill="none"
                  stroke={dataset.borderColor}
                  strokeWidth="2"
                />
              );
            })}

            {/* X-axis labels */}
            <text x="50" y="390" textAnchor="middle" fontSize="12" fill="#666">
              0
            </text>
            <text x="400" y="390" textAnchor="middle" fontSize="12" fill="#666">
              {Math.floor(data.labels.length / 2)}
            </text>
            <text x="750" y="390" textAnchor="middle" fontSize="12" fill="#666">
              {data.labels.length - 1}
            </text>
          </svg>
        </div>
      </div>
    );
  };

  if (!data) {
    return (
      <div className="hdf5-visualization">
        <div className="no-data">
          <h3>📊 HDF5 Data Visualization</h3>
          <p>❌ No HDF5 data available</p>
        </div>
      </div>
    );
  }

  if (!data.hdf5_files || data.hdf5_files.length === 0) {
    return (
      <div className="hdf5-visualization">
        <div className="no-data">
          <h3>📊 HDF5 Data Visualization</h3>
          <p>
            ⚠️ No HDF5 files found. Make sure your scenario has HDF5 output
            enabled in the SCEN_OUTPUTS section.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="hdf5-visualization">
      <h3>📊 HDF5 Simulation Data</h3>

      {/* File Selection */}
      <div className="file-selection">
        <h4>📁 Select HDF5 File</h4>
        <select
          value={selectedFile}
          onChange={(e) => setSelectedFile(e.target.value)}
          className="file-select"
        >
          {data.hdf5_files?.map((file) => (
            <option key={file.name} value={file.name}>
              {file.scenario_name || file.name} ({file.size})
            </option>
          ))}
        </select>
      </div>

      {fileInfo && (
        <>
          {/* File Information */}
          <div className="file-info">
            <h4>📋 File Information</h4>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">File Size:</span>
                <span className="info-value">{fileInfo.size}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Groups:</span>
                <span className="info-value">
                  {Object.keys(fileInfo.groups || {}).length}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Datasets:</span>
                <span className="info-value">
                  {Object.keys(fileInfo.datasets || {}).length}
                </span>
              </div>
            </div>
          </div>

          {/* Group Selection */}
          {Object.keys(groupedDatasets).length > 0 && (
            <div className="group-selection">
              <h4>🏗️ Select Component/System Group</h4>
              <p>Choose a system component to visualize all its attributes:</p>

              <div className="groups-grid">
                {Object.keys(groupedDatasets).map((groupName: string) => {
                  const groupInfo = groupedDatasets[groupName];
                  const isSelected = selectedGroup === groupName;
                  const isLoading = loading[groupName] || false;
                  const isExpanded = expandedGroups[groupName] || false;
                  const hasData = chartData[groupName];

                  return (
                    <div key={groupName} className="group-container">
                      <div
                        className={`group-item${isSelected ? " selected" : ""}`}
                        onClick={() => handleGroupSelection(groupName)}
                      >
                        <div className="group-content">
                          <div className="group-name">
                            {groupInfo.displayName}
                          </div>
                          <div className="group-info">
                            {groupInfo.attributes.length} attribute
                            {groupInfo.attributes.length !== 1 ? "s" : ""}:{" "}
                            <span>{groupInfo.attributes.join(", ")}</span>
                          </div>
                        </div>
                        <div className="group-actions">
                          <button
                            className="visualize-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              loadDatasetData(groupName);
                            }}
                            disabled={isLoading}
                          >
                            {isLoading
                              ? "⏳ Loading..."
                              : hasData
                              ? "🔄 Reload"
                              : "📊 Visualize"}
                          </button>
                          {hasData && (
                            <button
                              className="toggle-btn"
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleGroupExpansion(groupName);
                              }}
                            >
                              {isExpanded ? "▲" : "▼"}
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Chart visualization for this specific group */}
                      {hasData && isExpanded && (
                        <div className="group-visualization">
                          {renderSimpleChart(groupName, chartData[groupName])}

                          {/* Statistical Summary for this group */}
                          <div className="stats-summary">
                            <h4>📊 Statistical Summary - {groupName}</h4>
                            <div className="stats-table">
                              <table>
                                <thead>
                                  <tr>
                                    <th>Dataset</th>
                                    <th>Min</th>
                                    <th>Max</th>
                                    <th>Mean</th>
                                    <th>Std Dev</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {chartData[groupName].datasets.map(
                                    (dataset, index) => {
                                      const data = dataset.data;
                                      const min = Math.min(...data);
                                      const max = Math.max(...data);
                                      const mean =
                                        data.reduce((a, b) => a + b, 0) /
                                        data.length;
                                      const variance =
                                        data.reduce(
                                          (a, b) => a + Math.pow(b - mean, 2),
                                          0
                                        ) / data.length;
                                      const stdDev = Math.sqrt(variance);

                                      return (
                                        <tr key={index}>
                                          <td>{dataset.label}</td>
                                          <td>{min.toFixed(3)}</td>
                                          <td>{max.toFixed(3)}</td>
                                          <td>{mean.toFixed(3)}</td>
                                          <td>{stdDev.toFixed(3)}</td>
                                        </tr>
                                      );
                                    }
                                  )}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default HDF5Visualization;

