import React, { useEffect, useMemo, useState, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useReactFlow } from '@xyflow/react';

export default function ParamEditorModal({
  nodeId,
  totalEntities: totalEntitiesProp = 0,
  onClose,
}: {
  nodeId: string;
  totalEntities?: number;
  onClose: () => void;
}) {
  const { getNodes, getEdges, setNodes, setEdges } = useReactFlow();

  const node = useMemo(() => getNodes().find((n) => n.id === nodeId), [getNodes, nodeId]);
  const data = node?.data || {};

  // Check if model has entity port (can connect to entity batch)
  // Models with entity ports are those that are NOT timeseries and NOT scheduler
  const hasEntityPort = useMemo(() => {
    const tags = Array.isArray(data.tags) ? data.tags : (data.tags ? [data.tags] : []);
    const tagStrings = tags.map(t => String(t).toLowerCase());
    return !tagStrings.includes('timeseries') && !tagStrings.includes('scheduler');
  }, [data.tags]);

  // Use totalEntities from parent component (calculated by traversing pink connections)
  const totalEntities = totalEntitiesProp;

  const [activeTab, setActiveTab] = useState<'model-parameter' | 'computation-setting'>('model-parameter');

  // Reset to model-parameter tab when modal opens
  useEffect(() => {
    setActiveTab('model-parameter');
  }, [nodeId]);

  // Process count state - default to totalEntities (high performance default)
  const [processCount, setProcessCount] = useState<number>(() => {
    const compSetting = data.computation_setting as any;
    const saved = compSetting?.process_count;
    // If saved value is invalid (e.g. > current entities), clamp it.
    // If no saved value, use totalEntities.
    if (saved !== undefined) return saved;
    return totalEntities > 0 ? totalEntities : 1;
  });

  const prevTotalEntitiesRef = useRef<number>(totalEntities);
  
  // Update processCount when totalEntities changes
  // If totalEntities changes (e.g., user switches batch connection), reset to new totalEntities (high performance default)
  useEffect(() => {
    // Case 1: Entities changed from X to Y. Update default to Max (Y).
    if (totalEntities !== prevTotalEntitiesRef.current) {
      if (totalEntities > 0) {
        console.log(`[ParamEditorModal] Entities updated (${prevTotalEntitiesRef.current} -> ${totalEntities}). Auto-setting max processes.`);
        setProcessCount(totalEntities);
      }
      prevTotalEntitiesRef.current = totalEntities;
    }
  }, [totalEntities]);

  // Persist computation_setting.process_count immediately so exporter can rely on it
  useEffect(() => {
    if (!hasEntityPort) return;
    setNodes((nds) =>
      nds.map((n) => {
        if (n.id !== nodeId) return n;
        const current = (n.data?.computation_setting as any) || {};
        if (current.process_count === processCount) return n;
        return {
          ...n,
          data: {
            ...n.data,
            computation_setting: {
              ...current,
              process_count: processCount,
            },
          },
        };
      })
    );
  }, [hasEntityPort, processCount, nodeId, setNodes]);

  // Local editable copies sourced from node.data JSON
  const [simulationParameters, setSimulationParameters] = useState<any[]>(() => Array.isArray(data.simulation_parameters) ? JSON.parse(JSON.stringify(data.simulation_parameters)) : []);
  const [inputVariables, setInputVariables] = useState<any[]>(() => Array.isArray(data.input_variables) ? JSON.parse(JSON.stringify(data.input_variables)) : []);
  const [outputVariables, setOutputVariables] = useState<any[]>(() => Array.isArray(data.output_variables) ? JSON.parse(JSON.stringify(data.output_variables)) : []);
  const [modelParameters, setModelParameters] = useState<any[]>(() => Array.isArray(data.model_parameters) ? JSON.parse(JSON.stringify(data.model_parameters)) : []);
  const [selectedSimulator, setSelectedSimulator] = useState<string>(() => {
    const simNames = Array.isArray(data.simulator_names) ? data.simulator_names : [];
    return data.selected_simulator || (simNames.length > 0 ? simNames[0] : '');
  });

  const handleSimulatorChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setSelectedSimulator(value);
    // persist immediately to the node so exports pick it up without requiring Save
    setNodes((nds) => nds.map((n) => (
      n.id === nodeId
        ? { ...n, data: { ...n.data, selected_simulator: value } }
        : n
    )));
  }, [nodeId, setNodes]);

  const handleSave = useCallback(() => {
    setNodes((nds) => nds.map((n) => (
      n.id === nodeId
        ? {
            ...n,
            data: {
              ...n.data,
              simulation_parameters: Array.isArray(simulationParameters) ? simulationParameters : [],
              input_variables: Array.isArray(inputVariables) ? inputVariables : [],
              output_variables: Array.isArray(outputVariables) ? outputVariables : [],
              model_parameters: Array.isArray(modelParameters) ? modelParameters : [],
              selected_simulator: selectedSimulator,
              computation_setting: hasEntityPort ? {
                process_count: processCount,
              } : undefined,
            }
          }
        : n
    )));
    onClose();
  }, [nodeId, setNodes, simulationParameters, inputVariables, outputVariables, modelParameters, selectedSimulator, hasEntityPort, processCount, onClose]);

  const handleRemoveModel = useCallback(() => {
    try {
      const nodes = getNodes() || [];
      const edges = getEdges() || [];
      const target = nodes.find((n: any) => n.id === nodeId);
      const compositeGroupId = target?.data?.compositeGroupId;

      // If it's part of a composite group, remove the whole group (consistent with right-click behavior)
      const nodeIdsToRemove = new Set<string>();
      if (compositeGroupId) {
        nodes.forEach((n: any) => {
          if (n?.data?.compositeGroupId === compositeGroupId) nodeIdsToRemove.add(n.id);
        });
      } else {
        nodeIdsToRemove.add(nodeId);
      }

      setNodes((nds: any[]) => nds.filter((n) => !nodeIdsToRemove.has(n.id)));
      setEdges((eds: any[]) => eds.filter((e) => !nodeIdsToRemove.has(e.source) && !nodeIdsToRemove.has(e.target)));
    } finally {
      onClose();
    }
  }, [getNodes, getEdges, nodeId, setNodes, setEdges, onClose]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.key === 'Escape')) {
        e.preventDefault();
        onClose();
      }
      if ((e.key === 'Enter' && (e.metaKey || e.ctrlKey))) {
        e.preventDefault();
        handleSave();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [handleSave, onClose]);

  const handleReset = () => {
    setSimulationParameters(Array.isArray(data.simulation_parameters) ? JSON.parse(JSON.stringify(data.simulation_parameters)) : []);
    setInputVariables(Array.isArray(data.input_variables) ? JSON.parse(JSON.stringify(data.input_variables)) : []);
    setOutputVariables(Array.isArray(data.output_variables) ? JSON.parse(JSON.stringify(data.output_variables)) : []);
    setModelParameters(Array.isArray(data.model_parameters) ? JSON.parse(JSON.stringify(data.model_parameters)) : []);
    const simNames = Array.isArray(data.simulator_names) ? data.simulator_names : [];
    setSelectedSimulator(data.selected_simulator || (simNames.length > 0 ? simNames[0] : ''));
    // Reset processCount to totalEntities (high performance default)
    setProcessCount(totalEntities > 0 ? totalEntities : 1);
  };

  if (!node) return null;

  // removed: listSections()

  const content = (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.35)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        zIndex: 99999,
        overflow: 'auto',
        padding: '24px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'white',
          width: '720px',
          maxWidth: '90vw',
          maxHeight: 'calc(100vh - 48px)',
          borderRadius: 12,
          boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ padding: 20, borderBottom: '1px solid #eee' }}>
          <h2 style={{ margin: 0 }}>{String(node.data?.name || node.data?.label || '')} parameters</h2>
          <div style={{ color: '#666', marginTop: 6 }}>{String(node.data?.description || '')}</div>
        </div>

        {/* Tabs */}
        {hasEntityPort && (
          <div style={{ display: 'flex', borderBottom: '1px solid #eee', padding: '0 20px' }}>
            <button
              onClick={() => setActiveTab('model-parameter')}
              style={{
                padding: '12px 20px',
                border: 'none',
                background: 'transparent',
                borderBottom: activeTab === 'model-parameter' ? '2px solid #2563eb' : '2px solid transparent',
                color: activeTab === 'model-parameter' ? '#2563eb' : '#666',
                fontWeight: activeTab === 'model-parameter' ? 600 : 400,
                cursor: 'pointer',
                fontSize: 14,
              }}
            >
              Model parameter
            </button>
            <button
              onClick={() => setActiveTab('computation-setting')}
              style={{
                padding: '12px 20px',
                border: 'none',
                background: 'transparent',
                borderBottom: activeTab === 'computation-setting' ? '2px solid #2563eb' : '2px solid transparent',
                color: activeTab === 'computation-setting' ? '#2563eb' : '#666',
                fontWeight: activeTab === 'computation-setting' ? 600 : 400,
                cursor: 'pointer',
                fontSize: 14,
              }}
            >
              Computation setting
            </button>
          </div>
        )}

        <div style={{ padding: 20, flex: 1, minHeight: 0, overflowY: 'auto' }}>
          {(!hasEntityPort || activeTab === 'model-parameter') && (
            <>
          {/* Simulation Parameters */}
          <details open style={{ marginBottom: 16 }}>
            <summary style={{ fontWeight: 600, marginBottom: 8 }}>Simulation Parameters</summary>
            {simulationParameters.length === 0 ? (
              <div style={{ color: '#666' }}>No simulation parameters</div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 200px 100px 120px', gap: 8, alignItems: 'center' }}>
                {simulationParameters.map((p, idx) => (
                  <React.Fragment key={p.name || idx}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <label style={{ fontWeight: 500 }}>{p.name}</label>
                      <small style={{ color: '#666' }}>{p.description}</small>
                    </div>
                    <input
                      value={String(p.value ?? '')}
                      onChange={(e)=>{
                        const v=e.target.value; setSimulationParameters(prev=>prev.map((x,i)=>i===idx?{...x,value:v}:x));
                      }}
                    />
                    <div style={{ color:'#555' }}>{p.unit || ''}</div>
                    <div style={{ color:'#555', fontSize:12 }}>{p.data_type || ''}</div>
                  </React.Fragment>
                ))}
              </div>
            )}
          </details>

          {/* Simulator Selection */}
          {Array.isArray(data.simulator_names) && data.simulator_names.length > 0 && (
            <details open style={{ marginBottom: 16 }}>
              <summary style={{ fontWeight: 600, marginBottom: 8 }}>Simulator Selection</summary>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <label style={{ fontWeight: 500, marginBottom: 4 }}>Available Simulators</label>
                  <small style={{ color: '#666', marginBottom: 8 }}>
                    Choose which simulator to use for this model. Different simulators may have different capabilities or performance characteristics.
                  </small>
                </div>
                <select
                  value={selectedSimulator}
                  onChange={handleSimulatorChange}
                  style={{
                    padding: '8px 12px',
                    border: '1px solid #ddd',
                    borderRadius: 6,
                    fontSize: 14,
                    backgroundColor: 'white',
                    minWidth: 200
                  }}
                >
                  {(Array.isArray(data.simulator_names) ? data.simulator_names : []).map((simulator: string) => (
                    <option key={simulator} value={simulator}>
                      {simulator}
                    </option>
                  ))}
                          </select>
                {selectedSimulator && (
                  <div style={{ 
                    padding: 8, 
                    backgroundColor: '#f0f9ff', 
                    border: '1px solid #bae6fd', 
                    borderRadius: 6,
                    fontSize: 14,
                    color: '#0369a1'
                  }}>
                    Selected: <strong>{selectedSimulator}</strong>
                  </div>
                )}
              </div>
            </details>
          )}

          {/* Input Variables */}
          <details open style={{ marginBottom: 16 }}>
            <summary style={{ fontWeight: 600, marginBottom: 8 }}>Input Variables</summary>
            {inputVariables.length === 0 ? (
              <div style={{ color: '#666' }}>No input variables</div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 160px 100px 120px', gap: 8, alignItems: 'center' }}>
                {inputVariables.map((p, idx) => (
                  <React.Fragment key={p.name || idx}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <label style={{ fontWeight: 500 }}>{p.name}</label>
                      <small style={{ color: '#666' }}>{p.description}</small>
                    </div>
                        <input
                      value={String(p.start_value ?? '')}
                      onChange={(e)=>{
                        const v=e.target.value; setInputVariables(prev=>prev.map((x,i)=>i===idx?{...x,start_value:v}:x));
                      }}
                    />
                    <div style={{ color:'#555' }}>{p.unit || ''}</div>
                    <div style={{ color:'#555', fontSize:12 }}>{p.data_type || ''}</div>
                  </React.Fragment>
                ))}
              </div>
            )}
          </details>

          {/* Output Variables */}
          <details open style={{ marginBottom: 16 }}>
            <summary style={{ fontWeight: 600, marginBottom: 8 }}>Output Variables</summary>
            {outputVariables.length === 0 ? (
              <div style={{ color: '#666' }}>No output variables</div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 160px 100px 120px', gap: 8, alignItems: 'center' }}>
                {outputVariables.map((p, idx) => (
                  <React.Fragment key={p.name || idx}>
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <label style={{ fontWeight: 500 }}>{p.name}</label>
                      <small style={{ color: '#666' }}>{p.description}</small>
                    </div>
                    <input
                      value={String(p.start_value ?? '')}
                      onChange={(e)=>{
                        const v=e.target.value; setOutputVariables(prev=>prev.map((x,i)=>i===idx?{...x,start_value:v}:x));
                      }}
                    />
                    <div style={{ color:'#555' }}>{p.unit || ''}</div>
                    <div style={{ color:'#555', fontSize:12 }}>{p.data_type || ''}</div>
                  </React.Fragment>
                ))}
                        </div>
            )}
          </details>

          {/* Model Parameters */}
          <details open style={{ marginBottom: 16 }}>
            <summary style={{ fontWeight: 600, marginBottom: 8 }}>Model Parameters</summary>
            {modelParameters.length === 0 ? (
              <div style={{ color: '#666' }}>No model parameters</div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 200px 100px 120px', gap: 8, alignItems: 'center' }}>
                {modelParameters.map((p, idx) => (
                  <React.Fragment key={p.name || idx}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <label style={{ fontWeight: 500 }}>{p.name}</label>
                      <small style={{ color: '#666' }}>{p.description}</small>
                        </div>
                    <input
                      value={String((p.default_value ?? p.value) ?? '')}
                      onChange={(e)=>{
                        const v=e.target.value; setModelParameters(prev=>prev.map((x,i)=>i===idx?{...x,default_value:v}:x));
                      }}
                    />
                    <div style={{ color:'#555' }}>{p.unit || ''}</div>
                    <div style={{ color:'#555', fontSize:12 }}>{p.data_type || ''}</div>
                      </React.Fragment>
                ))}
                </div>
            )}
              </details>
            </>
          )}

          {hasEntityPort && activeTab === 'computation-setting' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              {/* Description Header */}
              <div>
                <h3 style={{ margin: '0 0 8px 0', fontSize: 18, fontWeight: 600, color: '#1a202c' }}>
                  Parallelization Strategy
                </h3>
                <p style={{ margin: 0, fontSize: 12, color: '#666', lineHeight: 1.5 }}>
                  Define how the simulation models are distributed across system processes.
                </p>
              </div>

              {/* Configuration Input */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <label style={{ fontSize: 14, fontWeight: 500, color: '#374151' }}>
                  Number of Parallel Processes
                </label>
                <input
                  type="number"
                  min={1}
                  max={totalEntities || 1}
                  value={processCount}
                  onChange={(e) => {
                    const value = parseInt(e.target.value, 10);
                    if (!isNaN(value)) {
                      const clamped = Math.max(1, Math.min(totalEntities || 1, value));
                      setProcessCount(clamped);
                    }
                  }}
                  style={{
                    padding: '10px 12px',
                    border: '1px solid #d1d5db',
                    borderRadius: 6,
                    fontSize: 14,
                    width: '200px',
                    outline: 'none',
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#2563eb';
                    e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#d1d5db';
                    e.target.style.boxShadow = 'none';
                  }}
                />
                <small style={{ fontSize: 12, color: '#6b7280' }}>
                  Minimum: 1, Maximum: {totalEntities || 0}
                </small>
              </div>

              {/* Visual Summary Card */}
              {totalEntities > 0 && (
                <div style={{
                  backgroundColor: '#f9fafb',
                  border: '1px solid #e5e7eb',
                  borderRadius: 8,
                  padding: 20,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 12,
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 14, color: '#6b7280' }}>Total Models Detected</span>
                    <span style={{ fontSize: 16, fontWeight: 600, color: '#1a202c' }}>{totalEntities}</span>
                  </div>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    paddingTop: 12,
                    borderTop: '1px solid #e5e7eb',
                  }}>
                    <span style={{ fontSize: 14, fontWeight: 500, color: '#374151' }}>Load Distribution</span>
                    <span style={{ fontSize: 16, fontWeight: 600, color: '#2563eb' }}>
                      ~{Math.ceil(totalEntities / processCount)} Models per Process
                    </span>
                  </div>
                  {processCount === totalEntities && totalEntities > 0 && (
                    <div style={{
                      marginTop: 8,
                      padding: '10px 12px',
                      backgroundColor: '#dbeafe',
                      border: '1px solid #93c5fd',
                      borderRadius: 6,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                    }}>
                      <span style={{ fontSize: 16 }}>✓</span>
                      <span style={{ fontSize: 13, color: '#1e40af' }}>
                        Maximum Parallelism Active (1 Simulation per Model)
                      </span>
                    </div>
                  )}
                </div>
              )}

              {totalEntities === 0 && (
                <div style={{
                  padding: 20,
                  backgroundColor: '#fef3c7',
                  border: '1px solid #fde68a',
                  borderRadius: 8,
                  textAlign: 'center',
                }}>
                  <p style={{ margin: 0, fontSize: 14, color: '#92400e' }}>
                    No entities detected. Connect this model to an entity batch to configure parallel processing.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        <div style={{ padding: 20, display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #eee', flex: 'none' }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={handleRemoveModel}
              style={{
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: 6,
                padding: '8px 12px',
                cursor: 'pointer',
                fontWeight: 600,
              }}
              title="Remove this model from workspace"
            >
              Remove Model
            </button>
            <button onClick={handleReset} style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 6, padding: '8px 12px' }}>
              Reset to defaults
            </button>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={onClose} style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 6, padding: '8px 12px' }}>Cancel</button>
            <button onClick={handleSave} style={{ background: '#2563eb', color: 'white', border: 'none', borderRadius: 6, padding: '8px 12px' }}>Save</button>
          </div>
        </div>
      </div>
    </div>
  );

  return createPortal(content, document.body);
}


