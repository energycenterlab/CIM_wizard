import React, { useMemo, useRef, useState, useEffect, useImperativeHandle, forwardRef, useCallback } from 'react';
import {
  ModelJson,
  ParamItem,
  validateModelJson,
  buildPreview,
  modelExists,
  upsertModel,
} from '../../utils/localModelStore';
import { loadModels, removeModel } from '../../utils/localModelStore';
import { coesiModelService } from '../../services/coesiModels';
import { apiService } from '../../services/api';

export default function AddModelJsonDrawer({
  projectId,
  onAdded,
}: {
  projectId: string;
  onAdded: (model: ModelJson, replaced: boolean) => void;
}) {
  const [activeTab, setActiveTab] = useState<'data' | 'builder' | 'catalog'>('data');
  const [rawText, setRawText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [parsed, setParsed] = useState<ModelJson | null>(null);
  const [showReplace, setShowReplace] = useState<null | ModelJson>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [detailsFor, setDetailsFor] = useState<string | null>(null);
  const [shareToCommunity, setShareToCommunity] = useState<boolean>(true);
  const modelBuilderRef = useRef<{ handleAddModel: () => void; canAdd: boolean } | null>(null);
  const [builderCanAdd, setBuilderCanAdd] = useState(false);

  useEffect(() => {
    if (activeTab !== 'builder') {
      setBuilderCanAdd(false);
    }
  }, [activeTab]);

  // Debounced validation for code input
  useEffect(() => {
    if (activeTab !== 'data') return;
    const t = setTimeout(() => {
      if (!rawText.trim()) {
        setParsed(null);
        setError(null);
        return;
      }
      try {
        const obj = JSON.parse(rawText);
        const res = validateModelJson(obj);
        if (res.valid) {
          setParsed(res.parsed);
          setError(null);
        } else {
          setParsed(null);
          setError(`Invalid JSON: ${res.message}`);
        }
      } catch (e: any) {
        setParsed(null);
        setError(`Invalid JSON: ${e?.message || 'Parse error'}`);
      }
    }, 300);
    return () => clearTimeout(t);
  }, [rawText, activeTab]);

  const onDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    if (!e.dataTransfer.files?.length) return;
    await handleFile(e.dataTransfer.files[0]);
  };

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.json')) {
      setError('Invalid JSON: Only .json files are accepted');
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      setError('Invalid JSON: File exceeds 2 MB');
      return;
    }
    const text = await file.text();
    try {
      const obj = JSON.parse(text);
      const res = validateModelJson(obj);
      if (res.valid) {
        setParsed(res.parsed);
        setRawText(JSON.stringify(res.parsed, null, 2));
        setError(null);
      } else {
        setParsed(null);
        setError(`Invalid JSON: ${res.message}`);
      }
    } catch (e: any) {
      setParsed(null);
      setError(`Invalid JSON: ${e?.message || 'Parse error'}`);
    }
  };

  const onChooseFile = () => fileInputRef.current?.click();
  const onFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) await handleFile(file);
    e.currentTarget.value = '';
  };

  const formatJson = () => {
    try {
      const obj = JSON.parse(rawText);
      setRawText(JSON.stringify(obj, null, 2));
    } catch {}
  };
  const clearJson = () => {
    setRawText('');
    setParsed(null);
    setError(null);
  };

  const preview = useMemo(() => (parsed ? buildPreview(parsed) : null), [parsed]);
  const canAdd = Boolean(parsed && !error);

  const handleAddModel = async () => {
    if (!parsed) return;
    const exists = modelExists(projectId, parsed.name);
    if (exists && !showReplace) {
      setShowReplace(parsed);
      return;
    }
    try {
      if (shareToCommunity) {
        await apiService.addCOESIModel(parsed as any);
      }
    } catch (e) {
      console.warn('Model POST failed; saving locally anyway:', e);
    } finally {
      const { replaced } = upsertModel(projectId, parsed);
      onAdded(parsed, replaced);
    }
  };

  // Details-only view
  if (detailsFor) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', gap: 8 }}>
          <button onClick={() => setDetailsFor(null)} style={{ border: 'none', background: 'transparent', color: '#2563eb', cursor: 'pointer' }}>← Back to catalogue</button>
          <div style={{ fontWeight: 700 }}>{detailsFor}</div>
        </div>
        <div style={{ padding: 16, overflowY: 'auto' }}>
          <DetailsInline name={detailsFor} projectId={projectId} onRemoved={() => setDetailsFor(null)} />
        </div>
      </div>
    );
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Tab Navigation (match Projects page style) */}
      <div style={{ display: 'flex', borderBottom: '1px solid #e0e0e0', marginBottom: '20px' }}>
        <button
          onClick={() => setActiveTab('data')}
          style={{
            padding: '12px 24px',
            border: 'none',
            background: activeTab === 'data' ? '#4CAF50' : '#f5f5f5',
            color: activeTab === 'data' ? 'white' : '#333',
            cursor: 'pointer',
            borderBottom: activeTab === 'data' ? '3px solid #4CAF50' : '3px solid transparent',
            fontWeight: activeTab === 'data' ? '600' : '400',
            transition: 'all 0.2s ease',
            borderRadius: '4px 4px 0 0',
          }}
          onMouseEnter={(e) => {
            if (activeTab !== 'data') {
              (e.currentTarget as HTMLButtonElement).style.background = '#e8f5e8';
              (e.currentTarget as HTMLButtonElement).style.color = '#2e7d32';
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'data') {
              (e.currentTarget as HTMLButtonElement).style.background = '#f5f5f5';
              (e.currentTarget as HTMLButtonElement).style.color = '#333';
            }
          }}
        >
          Data input
        </button>
        <button
          onClick={() => setActiveTab('builder')}
          style={{
            padding: '12px 24px',
            border: 'none',
            background: activeTab === 'builder' ? '#FF9800' : '#f5f5f5',
            color: activeTab === 'builder' ? 'white' : '#333',
            cursor: 'pointer',
            borderBottom: activeTab === 'builder' ? '3px solid #FF9800' : '3px solid transparent',
            fontWeight: activeTab === 'builder' ? '600' : '400',
            transition: 'all 0.2s ease',
            borderRadius: '4px 4px 0 0',
          }}
          onMouseEnter={(e) => {
            if (activeTab !== 'builder') {
              (e.currentTarget as HTMLButtonElement).style.background = '#fff3e0';
              (e.currentTarget as HTMLButtonElement).style.color = '#e65100';
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'builder') {
              (e.currentTarget as HTMLButtonElement).style.background = '#f5f5f5';
              (e.currentTarget as HTMLButtonElement).style.color = '#333';
            }
          }}
        >
          Model builder
        </button>
        <button
          onClick={() => setActiveTab('catalog')}
          style={{
            padding: '12px 24px',
            backgroundColor: activeTab === 'catalog' ? '#9C27B0' : '#f5f5f5',
            color: activeTab === 'catalog' ? 'white' : '#333',
            cursor: 'pointer',
            borderTop: activeTab === 'catalog' ? '3px solid #9C27B0' : '1px solid #e0e0e0',
            borderLeft: activeTab === 'catalog' ? '3px solid #9C27B0' : '1px solid #e0e0e0',
            borderRight: activeTab === 'catalog' ? '3px solid #9C27B0' : '1px solid #e0e0e0',
            borderBottom: 'none',
            borderTopLeftRadius: 4,
            borderTopRightRadius: 4,
            fontWeight: activeTab === 'catalog' ? 600 as any : 400 as any,
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            if (activeTab !== 'catalog') {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#f3e5f5';
              (e.currentTarget as HTMLButtonElement).style.color = '#6a1b9a';
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'catalog') {
              (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#f5f5f5';
              (e.currentTarget as HTMLButtonElement).style.color = '#333';
            }
          }}
        >
          Model catalogue
        </button>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {activeTab === 'data' ? (
          <div>
            <div
              onDrop={onDrop}
              onDragOver={(e) => e.preventDefault()}
              style={{ border: '2px dashed #cbd5e1', borderRadius: 12, padding: '12px 24px', textAlign: 'center', marginBottom: 12 }}
            >
              <div style={{ marginBottom: 6, fontSize: 14 }}>Drop a .json file here or choose a file (max 2 MB).</div>
              <button onClick={onChooseFile} style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid #ddd', fontSize: 13 }}>Choose file</button>
              <input ref={fileInputRef} type="file" accept=".json" onChange={onFileChange} style={{ display: 'none' }} />
            </div>
            
            <div style={{ margin: '20px 0', display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ flex: 1, height: 1, background: 'linear-gradient(to right, transparent, #e5e7eb, transparent)' }}></div>
              <span style={{ color: '#9ca3af', fontSize: 13, fontWeight: 500, whiteSpace: 'nowrap' }}>or enter the code</span>
              <div style={{ flex: 1, height: 1, background: 'linear-gradient(to left, transparent, #e5e7eb, transparent)' }}></div>
            </div>
            
            <div style={{ position: 'relative', border: '1px solid #e5e7eb', borderRadius: 8, overflow: 'hidden', background: '#fafafa' }}>
              <div style={{ position: 'absolute', top: 8, right: 8, display: 'flex', gap: 6, zIndex: 10 }}>
                <button 
                  onClick={formatJson} 
                  style={{ 
                    padding: '4px 10px', 
                    borderRadius: 4, 
                    border: '1px solid #d1d5db', 
                    background: '#fff',
                    fontSize: 12,
                    cursor: 'pointer',
                    color: '#374151',
                    transition: 'all 0.2s',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#f3f4f6';
                    e.currentTarget.style.borderColor = '#9ca3af';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#fff';
                    e.currentTarget.style.borderColor = '#d1d5db';
                  }}
                >
                  Format
                </button>
                <button 
                  onClick={clearJson} 
                  style={{ 
                    padding: '4px 10px', 
                    borderRadius: 4, 
                    border: '1px solid #d1d5db', 
                    background: '#fff',
                    fontSize: 12,
                    cursor: 'pointer',
                    color: '#374151',
                    transition: 'all 0.2s',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#f3f4f6';
                    e.currentTarget.style.borderColor = '#9ca3af';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#fff';
                    e.currentTarget.style.borderColor = '#d1d5db';
                  }}
                >
                  Clear
                </button>
              </div>
              <textarea
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="paste or type json code here"
                style={{ 
                  width: '100%', 
                  minHeight: 180, 
                  maxHeight: 300,
                  fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
                  fontSize: 13,
                  lineHeight: 1.5,
                  padding: '12px',
                  paddingRight: '140px',
                  border: 'none',
                  outline: 'none',
                  background: 'transparent',
                  resize: 'vertical',
                  color: '#1f2937'
                }}
              />
            </div>
            {error && <div style={{ color: '#dc2626', marginTop: 8, fontSize: 13, padding: '8px 12px', background: '#fef2f2', borderRadius: 6, border: '1px solid #fecaca' }}>{error}</div>}
          </div>
        ) : activeTab === 'builder' ? (
          <ModelBuilder 
            ref={modelBuilderRef}
            projectId={projectId}
            onAdded={onAdded}
            shareToCommunity={shareToCommunity}
            setShareToCommunity={setShareToCommunity}
            setShowReplace={setShowReplace}
            setParsed={setParsed}
            setCanAdd={setBuilderCanAdd}
          />
        ) : (
          <Catalogue projectId={projectId} onAdded={onAdded} onViewDetails={(name) => setDetailsFor(name)} />
        )}

        {preview && activeTab === 'data' && !detailsFor && (
          <div style={{ marginTop: 12, padding: '8px 10px', border: '1px solid #eee', borderRadius: 6, fontSize: 11, background: '#fafafa' }}>
            <div style={{ fontWeight: 600, marginBottom: 4, fontSize: 11, color: '#374151' }}>Preview</div>
            <div style={{ marginBottom: 4, display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
              <span style={{ fontWeight: 500, fontSize: 11, color: '#1f2937' }}>{preview.name}</span>
              {preview.description && (
                <>
                  <span style={{ color: '#9ca3af', fontSize: 10 }}>•</span>
                  <span style={{ color: '#6b7280', fontSize: 10 }}>{preview.description}</span>
                </>
              )}
            </div>
            <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
              <Chip label={`Simulation: ${preview.simulationCount}`} />
              <Chip label={`Inputs: ${preview.inputCount}`} />
              <Chip label={`Outputs: ${preview.outputCount}`} />
              <Chip label={`Model params: ${preview.modelParamCount}`} />
            </div>
            {preview.possible?.length ? (
              <div style={{ marginTop: 4, color: '#6b7280', fontSize: 10 }}>
                Allowed connections: {preview.possible.join(', ')}
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{ padding: '16px 16px 16px 0', borderTop: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
        {(activeTab === 'data' || activeTab === 'builder') && (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <input id="shareModel" type="checkbox" checked={shareToCommunity} onChange={(e) => setShareToCommunity(e.target.checked)} />
              <label htmlFor="shareModel" style={{ fontSize: 13, color: '#374151', cursor: 'pointer' }}>
                I would like to share this model with the community
              </label>
            </div>
            <button 
              disabled={activeTab === 'data' ? !canAdd : !builderCanAdd} 
              onClick={activeTab === 'data' ? handleAddModel : () => modelBuilderRef.current?.handleAddModel()}
              style={{ 
                background: (activeTab === 'data' && !canAdd) || (activeTab === 'builder' && !builderCanAdd) ? '#94a3b8' : '#2563eb', 
                color: 'white', 
                border: 'none', 
                borderRadius: 6, 
                padding: '8px 12px', 
                whiteSpace: 'nowrap',
                cursor: (activeTab === 'data' && !canAdd) || (activeTab === 'builder' && !builderCanAdd) ? 'not-allowed' : 'pointer',
                opacity: (activeTab === 'data' && !canAdd) || (activeTab === 'builder' && !builderCanAdd) ? 0.6 : 1
              }}
            >
              Add model
            </button>
          </>
        )}
      </div>

      {showReplace && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100001 }}>
          <div style={{ background: 'white', padding: 16, borderRadius: 8, width: 420 }}>
            <h3 style={{ marginTop: 0 }}>Replace existing model?</h3>
            <p>A model named {showReplace.name} already exists. Do you want to replace it?</p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button onClick={() => setShowReplace(null)} style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 6, padding: '8px 12px' }}>No</button>
              <button onClick={() => { const { replaced } = upsertModel(projectId, showReplace); onAdded(showReplace, replaced); setShowReplace(null); }} style={{ background: '#2563eb', color: 'white', border: 'none', borderRadius: 6, padding: '8px 12px' }}>Replace</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Chip({ label }: { label: string }) {
  return (
    <span style={{ background: '#f1f5f9', color: '#334155', borderRadius: 6, padding: '2px 6px', fontSize: 10 }}>{label}</span>
  );
}

function Catalogue({ projectId, onAdded, onViewDetails }: { projectId: string; onAdded: (m: ModelJson, replaced: boolean) => void; onViewDetails: (name: string) => void }) {
  const [search, setSearch] = React.useState('');
  const [userModels, setUserModels] = React.useState<ModelJson[]>(() => loadModels(projectId));
  const [coesiModels, setCoesiModels] = React.useState<ModelJson[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  
  const refreshUser = React.useCallback(() => setUserModels(loadModels(projectId)), [projectId]);

  // Fetch COESI models from backend
  React.useEffect(() => {
    const fetchCoesiModels = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await coesiModelService.getModels();
        
        // Convert COESI models to ModelJson format
        const convertedModels = response.models.map(model => 
          coesiModelService.convertToModelJson(model)
        );
        
        setCoesiModels(convertedModels);
      } catch (err) {
        console.error('Failed to fetch COESI models:', err);
        setError('Failed to load models from backend. Please check if the COESI backend is running.');
        setCoesiModels([]); // No fallback to mock data
      } finally {
        setLoading(false);
      }
    };

    fetchCoesiModels();
  }, []);

  const sysFiltered = coesiModels.filter((m) => m.name.toLowerCase().includes(search.toLowerCase()));
  const userFiltered = userModels.filter((m) => m.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
        <input
          placeholder="Search models"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: '260px', padding: '10px 12px', border: '1px solid #e5e7eb', borderRadius: 10 }}
        />
        <button
          onClick={() => {
            setLoading(true);
            setError(null);
            coesiModelService.clearCache();
            // Re-fetch models
            coesiModelService.getModels().then(response => {
              const convertedModels = response.models.map(model => 
                coesiModelService.convertToModelJson(model)
              );
              setCoesiModels(convertedModels);
              setLoading(false);
            }).catch(err => {
              console.error('Failed to refresh models:', err);
              setError('Failed to refresh models from backend');
              setLoading(false);
            });
          }}
          style={{ 
            padding: '8px 12px', 
            border: '1px solid #e5e7eb', 
            borderRadius: 8, 
            background: '#fff',
            cursor: 'pointer',
            fontSize: 14
          }}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div style={{ 
          padding: '8px 12px', 
          background: '#FEF2F2', 
          border: '1px solid #FECACA', 
          borderRadius: 8, 
          color: '#DC2626', 
          fontSize: 14, 
          marginBottom: 12 
        }}>
          {error}
        </div>
      )}

      {/* System models */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        {loading ? (
          <div style={{ gridColumn: '1 / -1', padding: 16, textAlign: 'center', border: '1px dashed #e5e7eb', borderRadius: 12 }}>
            Loading model catalogue...
          </div>
        ) : sysFiltered.length === 0 ? (
          <div style={{ gridColumn: '1 / -1', padding: 16, textAlign: 'center', border: '1px dashed #e5e7eb', borderRadius: 12 }}>
            No models available.
          </div>
        ) : (
          sysFiltered.map((m) => (
            <ModelCard key={`sys-${m.name}`} model={m} onView={() => onViewDetails(m.name)} />
          ))
        )}
      </div>

      {/* Divider for user group if any */}
      <div style={{ margin: '16px 0', height: 1, background: '#e5e7eb' }} />
      <div style={{ margin: '8px 0', fontWeight: 700 }}>Your models</div>

      {/* User models */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        {userFiltered.length === 0 ? (
          <div style={{ gridColumn: '1 / -1', padding: 16, textAlign: 'center', border: '1px dashed #e5e7eb', borderRadius: 12 }}>No models available.</div>
        ) : (
          userFiltered.map((m) => (
            <ModelCard key={`usr-${m.name}`} model={m} onView={() => onViewDetails(m.name)} />
          ))
        )}
      </div>
    </div>
  );
}

function ModelCard({ model, onView, removable, onRemove }: { model: ModelJson; onView: () => void; removable?: boolean; onRemove?: () => void }) {
  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden', background: '#fff' }}>
      <div style={{ padding: 12, borderBottom: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
        <div style={{ fontWeight: 700, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }} title={model.name}>{model.name}</div>
        <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
          {removable && (
            <button onClick={onRemove} style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid #ef4444', background: '#fff', color: '#ef4444' }}>Remove</button>
          )}
          <button onClick={onView} style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid #e5e7eb', background: '#fff', fontSize: '13px' }}>View details</button>
        </div>
      </div>
      <div style={{ padding: 12, color: '#4b5563', minHeight: 48 }}>{model.description}</div>
    </div>
  );
}

function MiniTable({ title, headers, rows }: { title: string; headers: string[]; rows: any[][] }) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>{title}</div>
      <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${headers.length}, 1fr)`, background: '#f9fafb', padding: '8px 12px', fontWeight: 600 }}>
          {headers.map((h) => <div key={h}>{h}</div>)}
        </div>
        {rows.length === 0 ? (
          <div style={{ padding: 12 }}>No data</div>
        ) : rows.map((r, i) => (
          <div key={i} style={{ display: 'grid', gridTemplateColumns: `repeat(${headers.length}, 1fr)`, padding: '8px 12px', borderTop: '1px solid #f1f5f9' }}>
            {r.map((c, j) => <div key={j}>{String(c ?? '')}</div>)}
          </div>
        ))}
      </div>
    </div>
  );
}

function DetailsInline({ name, projectId, onRemoved }: { name: string; projectId: string; onRemoved: () => void }) {
  const [coesiModel, setCoesiModel] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);
  const userModels = loadModels(projectId);
  const fromUser = userModels.find((x) => x.name === name);
  
  React.useEffect(() => {
    const fetchModel = async () => {
      try {
        setLoading(true);
        const model = await coesiModelService.getModel(name);
        if (model) {
          const convertedModel = coesiModelService.convertToModelJson(model);
          setCoesiModel(convertedModel);
        }
      } catch (error) {
        console.error('Failed to fetch model details:', error);
        setCoesiModel(null);
      } finally {
        setLoading(false);
      }
    };

    if (!fromUser) {
      fetchModel();
    } else {
      setLoading(false);
    }
  }, [name, fromUser]);

  const m = fromUser || coesiModel;
  
  if (loading) {
    return (
      <div style={{ padding: 16, textAlign: 'center' }}>
        Loading model information...
      </div>
    );
  }
  
  if (!m) {
    return (
      <div style={{ padding: 16, textAlign: 'center', color: '#dc2626' }}>
        Model not found
      </div>
    );
  }
  
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ marginTop: 0 }}>{m.name}</h3>
        {fromUser && (
          <button
            onClick={() => { removeModel(projectId, name); onRemoved(); }}
            style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid #ef4444', background: '#fff', color: '#ef4444' }}
          >
            Remove
          </button>
        )}
      </div>
      <div style={{ color: '#6b7280', marginBottom: 12 }}>{m.description}</div>
      
      {/* Tags */}
      {m.tags && m.tags.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Tags</div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {m.tags.map((tag: string) => (
              <span key={tag} style={{ background: '#f1f5f9', color: '#334155', borderRadius: 12, padding: '4px 8px', fontSize: 12 }}>
                {tag}
              </span>
            ))}
            <span style={{ background: '#DCFCE7', color: '#166534', borderRadius: 12, padding: '4px 8px', fontSize: 12 }}>
              {fromUser ? 'User Model' : 'COESI'}
            </span>
          </div>
        </div>
      )}

      <MiniTable title="Simulation Parameters" rows={(m.simulation_parameters||[]).map((p: ParamItem) => [p.name, p.value, p.unit||'', p.data_type])} headers={[ 'Name','Value','Unit','Type' ]} />
      <MiniTable title="Input Variables" rows={(m.input_variables||[]).map((p: ParamItem) => [p.name, p.start_value, p.unit||'', p.data_type])} headers={[ 'Name','Start Value','Unit','Type' ]} />
      <MiniTable title="Output Variables" rows={(m.output_variables||[]).map((p: ParamItem) => [p.name, p.start_value, p.unit||'', p.data_type])} headers={[ 'Name','Start Value','Unit','Type' ]} />
      <MiniTable title="Model Parameters" rows={(m.model_parameters||[]).map((p: ParamItem) => [p.name, p.default_value, p.unit||'', p.data_type])} headers={[ 'Name','Default Value','Unit','Type' ]} />

      {/* Simulator Names */}
      {m.simulator_names && m.simulator_names.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Available Simulators</div>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {m.simulator_names.map((sim: string) => (
              <li key={sim} style={{ marginBottom: 4 }}>{sim}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Possible Connections */}
      {m.possible_connections && m.possible_connections.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Possible Connections</div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {m.possible_connections.map((connection: string) => (
              <span key={connection} style={{ background: '#EFF6FF', color: '#1E40AF', borderRadius: 12, padding: '4px 8px', fontSize: 12 }}>
                {connection}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Components (for composite models) */}
      {m.components && m.components.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Components</div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {m.components.map((component: string) => (
              <span key={component} style={{ background: '#F0FDF4', color: '#166534', borderRadius: 12, padding: '4px 8px', fontSize: 12 }}>
                {component}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Connections (for composite models) */}
      {m.connections && m.connections.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Connections</div>
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12 }}>
            {m.connections.map((connection: string, index: number) => (
              <div key={index} style={{ marginBottom: index < m.connections.length - 1 ? 8 : 0, fontFamily: 'monospace', fontSize: 12 }}>
                {connection}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* JSON Info */}
      <details style={{ marginTop: 16 }}>
        <summary style={{ fontWeight: 600, cursor: 'pointer', marginBottom: 8 }}>JSON Info</summary>
        <pre style={{ 
          background: '#0f172a', 
          color: '#e2e8f0', 
          padding: 12, 
          borderRadius: 8, 
          overflowX: 'auto',
          fontSize: 12,
          margin: 0
        }}>
          {JSON.stringify(m, null, 2)}
        </pre>
      </details>
    </div>
  );
}

const ModelBuilder = forwardRef<{ handleAddModel: () => void; canAdd: boolean }, {
  projectId: string;
  onAdded: (model: ModelJson, replaced: boolean) => void;
  shareToCommunity: boolean;
  setShareToCommunity: (value: boolean) => void;
  setShowReplace: (model: ModelJson | null) => void;
  setParsed: (model: ModelJson | null) => void;
  setCanAdd: (value: boolean) => void;
}>(({
  projectId,
  onAdded,
  shareToCommunity,
  setShareToCommunity,
  setShowReplace,
  setParsed,
  setCanAdd,
}, ref) => {
  const [modelData, setModelData] = useState({
    name: '',
    description: '',
    tags: [] as string[],
    solver: '',
    model_execution_cmd: '',
    simulator_names: [] as string[],
    simulation_parameters: [] as any[],
    input_variables: [] as any[],
    output_variables: [] as any[],
    model_parameters: [] as any[],
    components: [] as string[],
    connections: [] as string[],
    possible_connections: [] as string[],
  });

  const [newTag, setNewTag] = useState('');
  const [newSimulator, setNewSimulator] = useState('');
  const [newPossibleConnection, setNewPossibleConnection] = useState('');

  const buildModelJson = (): ModelJson | null => {
    if (!modelData.name || !modelData.model_execution_cmd) {
      return null;
    }

    const modelJson: any = {
      name: modelData.name,
      description: modelData.description || '',
      tags: modelData.tags,
      solver: modelData.solver || '',
      model_execution_cmd: modelData.model_execution_cmd,
      simulator_names: modelData.simulator_names,
      simulation_parameters: modelData.simulation_parameters,
      input_variables: modelData.input_variables,
      output_variables: modelData.output_variables,
      model_parameters: modelData.model_parameters,
      components: modelData.components,
      connections: modelData.connections,
      possible_connections: modelData.possible_connections,
    };

    const res = validateModelJson(modelJson);
    return res.valid ? res.parsed : null;
  };

  const handleAddModel = useCallback(async () => {
    if (!modelData.name || !modelData.model_execution_cmd) return;
    
    // Validate that all input and output variables have start_value
    const allInputsHaveStartValue = modelData.input_variables.every(
      (param) => param.start_value !== undefined && param.start_value !== null && String(param.start_value).trim() !== ''
    );
    const allOutputsHaveStartValue = modelData.output_variables.every(
      (param) => param.start_value !== undefined && param.start_value !== null && String(param.start_value).trim() !== ''
    );
    
    if (!allInputsHaveStartValue || !allOutputsHaveStartValue) {
      return; // Prevent adding model if start values are missing
    }
    
    const modelJson: any = {
      name: modelData.name,
      description: modelData.description || '',
      tags: modelData.tags,
      solver: modelData.solver || '',
      model_execution_cmd: modelData.model_execution_cmd,
      simulator_names: modelData.simulator_names,
      simulation_parameters: modelData.simulation_parameters,
      input_variables: modelData.input_variables,
      output_variables: modelData.output_variables,
      model_parameters: modelData.model_parameters,
      components: modelData.components,
      connections: modelData.connections,
      possible_connections: modelData.possible_connections,
    };
    
    const res = validateModelJson(modelJson);
    const parsed = res.valid ? res.parsed : null;
    if (!parsed) return;
    
    setParsed(parsed);
    const exists = modelExists(projectId, parsed.name);
    if (exists) {
      setShowReplace(parsed);
      return;
    }
    
    try {
      if (shareToCommunity) {
        await apiService.addCOESIModel(parsed as any);
      }
    } catch (e) {
      console.warn('Model POST failed; saving locally anyway:', e);
    } finally {
      const { replaced } = upsertModel(projectId, parsed);
      onAdded(parsed, replaced);
      // Reset form
      setModelData({
        name: '',
        description: '',
        tags: [],
        solver: '',
        model_execution_cmd: '',
        simulator_names: [],
        simulation_parameters: [],
        input_variables: [],
        output_variables: [],
        model_parameters: [],
        components: [],
        connections: [],
        possible_connections: [],
      });
    }
  }, [projectId, shareToCommunity, onAdded, setParsed, setShowReplace, modelData]);

  const canAdd = useMemo(() => {
    if (!modelData.name || !modelData.model_execution_cmd) return false;
    
    // Check that all input variables have a start_value
    const allInputsHaveStartValue = modelData.input_variables.every(
      (param) => param.start_value !== undefined && param.start_value !== null && String(param.start_value).trim() !== ''
    );
    
    // Check that all output variables have a start_value
    const allOutputsHaveStartValue = modelData.output_variables.every(
      (param) => param.start_value !== undefined && param.start_value !== null && String(param.start_value).trim() !== ''
    );
    
    if (!allInputsHaveStartValue || !allOutputsHaveStartValue) return false;
    
    const modelJson: any = {
      name: modelData.name,
      description: modelData.description || '',
      tags: modelData.tags,
      solver: modelData.solver || '',
      model_execution_cmd: modelData.model_execution_cmd,
      simulator_names: modelData.simulator_names,
      simulation_parameters: modelData.simulation_parameters,
      input_variables: modelData.input_variables,
      output_variables: modelData.output_variables,
      model_parameters: modelData.model_parameters,
      components: modelData.components,
      connections: modelData.connections,
      possible_connections: modelData.possible_connections,
    };
    const res = validateModelJson(modelJson);
    return res.valid;
  }, [modelData]);

  useEffect(() => {
    setCanAdd(canAdd);
  }, [canAdd, setCanAdd]);

  useImperativeHandle(ref, () => ({
    handleAddModel,
    canAdd,
  }), [canAdd, handleAddModel]);

  const addArrayItem = (field: string, value: string) => {
    if (!value.trim()) return;
    setModelData(prev => ({
      ...prev,
      [field]: [...prev[field as keyof typeof prev] as any[], value.trim()]
    }));
  };

  const removeArrayItem = (field: string, index: number) => {
    setModelData(prev => ({
      ...prev,
      [field]: (prev[field as keyof typeof prev] as any[]).filter((_, i) => i !== index)
    }));
  };

  const addParameter = (type: 'simulation' | 'input' | 'output' | 'model') => {
    const newParam: any = {
      name: '',
      unit: '',
      description: '',
      data_type: 'string',
      range: { min: '', max: '' },
      tags: [],
    };

    if (type === 'simulation') {
      newParam.value = '';
    } else if (type === 'input' || type === 'output') {
      newParam.start_value = '';
      newParam.hidden = false;
    } else if (type === 'model') {
      newParam.default_value = '';
    }

    setModelData(prev => ({
      ...prev,
      [`${type}_${type === 'simulation' ? 'parameters' : type === 'model' ? 'parameters' : 'variables'}`]: [
        ...prev[`${type}_${type === 'simulation' ? 'parameters' : type === 'model' ? 'parameters' : 'variables'}` as keyof typeof prev] as any[],
        newParam
      ]
    }));
  };

  const updateParameter = (type: 'simulation' | 'input' | 'output' | 'model', index: number, field: string, value: any) => {
    setModelData(prev => {
      const key = `${type}_${type === 'simulation' ? 'parameters' : type === 'model' ? 'parameters' : 'variables'}` as keyof typeof prev;
      const arr = [...(prev[key] as any[])];
      arr[index] = { ...arr[index], [field]: value };
      return { ...prev, [key]: arr };
    });
  };

  const removeParameter = (type: 'simulation' | 'input' | 'output' | 'model', index: number) => {
    setModelData(prev => {
      const key = `${type}_${type === 'simulation' ? 'parameters' : type === 'model' ? 'parameters' : 'variables'}` as keyof typeof prev;
      return {
        ...prev,
        [key]: (prev[key] as any[]).filter((_, i) => i !== index)
      };
    });
  };

  const addParameterTag = (type: 'simulation' | 'input' | 'output' | 'model', index: number, tag: string) => {
    if (!tag.trim()) return;
    setModelData(prev => {
      const key = `${type}_${type === 'simulation' ? 'parameters' : type === 'model' ? 'parameters' : 'variables'}` as keyof typeof prev;
      const arr = [...(prev[key] as any[])];
      if (!arr[index].tags) arr[index].tags = [];
      arr[index].tags = [...arr[index].tags, tag.trim()];
      return { ...prev, [key]: arr };
    });
  };

  const removeParameterTag = (type: 'simulation' | 'input' | 'output' | 'model', index: number, tagIndex: number) => {
    setModelData(prev => {
      const key = `${type}_${type === 'simulation' ? 'parameters' : type === 'model' ? 'parameters' : 'variables'}` as keyof typeof prev;
      const arr = [...(prev[key] as any[])];
      arr[index].tags = arr[index].tags.filter((_: any, i: number) => i !== tagIndex);
      return { ...prev, [key]: arr };
    });
  };

  return (
    <div style={{ padding: '0 16px 16px 16px' }}>
      <div style={{ marginBottom: 20 }}>
        {/* Basic Info */}
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500, fontSize: 13 }}>Name *</label>
          <input
            type="text"
            value={modelData.name}
            onChange={(e) => setModelData(prev => ({ ...prev, name: e.target.value }))}
            placeholder="e.g., heat_pump"
            style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13 }}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500, fontSize: 13 }}>Description</label>
          <textarea
            value={modelData.description}
            onChange={(e) => setModelData(prev => ({ ...prev, description: e.target.value }))}
            placeholder="Model description"
            style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13, minHeight: 60, resize: 'vertical' }}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500, fontSize: 13 }}>Tags</label>
          <div style={{ display: 'flex', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
            {modelData.tags.map((tag, i) => (
              <span key={i} style={{ background: '#e0e7ff', color: '#3730a3', padding: '4px 8px', borderRadius: 4, fontSize: 12, display: 'flex', alignItems: 'center', gap: 4 }}>
                {tag}
                <button onClick={() => removeArrayItem('tags', i)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#3730a3', fontSize: 14, padding: 0, marginLeft: 4 }}>×</button>
              </span>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => { if (e.key === 'Enter') { addArrayItem('tags', newTag); setNewTag(''); } }}
              placeholder="Add tag"
              style={{ flex: 1, padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13 }}
            />
            <button onClick={() => { addArrayItem('tags', newTag); setNewTag(''); }} style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, background: '#f3f4f6', cursor: 'pointer', fontSize: 13 }}>Add</button>
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500, fontSize: 13 }}>Solver</label>
          <input
            type="text"
            value={modelData.solver}
            onChange={(e) => setModelData(prev => ({ ...prev, solver: e.target.value }))}
            placeholder="e.g., DAE_Solver"
            style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13 }}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500, fontSize: 13 }}>Model Execution Command *</label>
          <input
            type="text"
            value={modelData.model_execution_cmd}
            onChange={(e) => setModelData(prev => ({ ...prev, model_execution_cmd: e.target.value }))}
            placeholder="e.g., python mk_fmu_pyfmi.py"
            style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13 }}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500, fontSize: 13 }}>Simulator Names</label>
          <div style={{ display: 'flex', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
            {modelData.simulator_names.map((sim, i) => (
              <span key={i} style={{ background: '#e0e7ff', color: '#3730a3', padding: '4px 8px', borderRadius: 4, fontSize: 12, display: 'flex', alignItems: 'center', gap: 4 }}>
                {sim}
                <button onClick={() => removeArrayItem('simulator_names', i)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#3730a3', fontSize: 14, padding: 0, marginLeft: 4 }}>×</button>
              </span>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              type="text"
              value={newSimulator}
              onChange={(e) => setNewSimulator(e.target.value)}
              onKeyPress={(e) => { if (e.key === 'Enter') { addArrayItem('simulator_names', newSimulator); setNewSimulator(''); } }}
              placeholder="e.g., mk_fmu_pyfmi.py"
              style={{ flex: 1, padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13 }}
            />
            <button onClick={() => { addArrayItem('simulator_names', newSimulator); setNewSimulator(''); }} style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, background: '#f3f4f6', cursor: 'pointer', fontSize: 13 }}>Add</button>
          </div>
        </div>

        {/* Simulation Parameters */}
        <div style={{ marginBottom: 20, padding: 12, border: '1px solid #e5e7eb', borderRadius: 8, background: '#fafafa' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <label style={{ fontWeight: 600, fontSize: 14 }}>Simulation Parameters</label>
            <button onClick={() => addParameter('simulation')} style={{ padding: '4px 8px', border: '1px solid #d1d5db', borderRadius: 4, background: '#fff', cursor: 'pointer', fontSize: 12 }}>+ Add</button>
          </div>
          {modelData.simulation_parameters.map((param, i) => (
            <div key={i} style={{ marginBottom: 12, padding: 12, background: '#fff', borderRadius: 6, border: '1px solid #e5e7eb' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <strong style={{ fontSize: 13 }}>Parameter {i + 1}</strong>
                <button onClick={() => removeParameter('simulation', i)} style={{ background: '#fee2e2', color: '#dc2626', border: 'none', borderRadius: 4, padding: '2px 6px', cursor: 'pointer', fontSize: 11 }}>Remove</button>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Name</label>
                  <input type="text" value={param.name || ''} onChange={(e) => updateParameter('simulation', i, 'name', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Unit</label>
                  <input type="text" value={param.unit || ''} onChange={(e) => updateParameter('simulation', i, 'unit', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Value</label>
                  <input type="text" value={param.value || ''} onChange={(e) => updateParameter('simulation', i, 'value', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Data Type</label>
                  <select value={param.data_type || 'string'} onChange={(e) => updateParameter('simulation', i, 'data_type', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }}>
                    <option value="string">string</option>
                    <option value="int">int</option>
                    <option value="float">float</option>
                    <option value="datetime">datetime</option>
                  </select>
                </div>
              </div>
              <div style={{ marginBottom: 8 }}>
                <label style={{ fontSize: 11, color: '#6b7280' }}>Description</label>
                <input type="text" value={param.description || ''} onChange={(e) => updateParameter('simulation', i, 'description', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Range Min</label>
                  <input type="text" value={param.range?.min || ''} onChange={(e) => updateParameter('simulation', i, 'range', { ...(param.range || {}), min: e.target.value })} placeholder="e.g., 0 or none" style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Range Max</label>
                  <input type="text" value={param.range?.max || ''} onChange={(e) => updateParameter('simulation', i, 'range', { ...(param.range || {}), max: e.target.value })} placeholder="e.g., 7 or none" style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Input Variables */}
        <div style={{ marginBottom: 20, padding: 12, border: '1px solid #e5e7eb', borderRadius: 8, background: '#fafafa' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <label style={{ fontWeight: 600, fontSize: 14 }}>Input Variables</label>
            <button onClick={() => addParameter('input')} style={{ padding: '4px 8px', border: '1px solid #d1d5db', borderRadius: 4, background: '#fff', cursor: 'pointer', fontSize: 12 }}>+ Add</button>
          </div>
          {modelData.input_variables.map((param, i) => (
            <div key={i} style={{ marginBottom: 12, padding: 12, background: '#fff', borderRadius: 6, border: '1px solid #e5e7eb' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <strong style={{ fontSize: 13 }}>Input {i + 1}</strong>
                <button onClick={() => removeParameter('input', i)} style={{ background: '#fee2e2', color: '#dc2626', border: 'none', borderRadius: 4, padding: '2px 6px', cursor: 'pointer', fontSize: 11 }}>Remove</button>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Name</label>
                  <input type="text" value={param.name || ''} onChange={(e) => updateParameter('input', i, 'name', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Unit</label>
                  <input type="text" value={param.unit || ''} onChange={(e) => updateParameter('input', i, 'unit', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Start Value <span style={{ color: '#dc2626' }}>*</span></label>
                  <input 
                    type="text" 
                    value={param.start_value || ''} 
                    onChange={(e) => updateParameter('input', i, 'start_value', e.target.value)} 
                    style={{ 
                      width: '100%', 
                      padding: '6px 8px', 
                      border: `1px solid ${(!param.start_value || String(param.start_value).trim() === '') ? '#dc2626' : '#d1d5db'}`, 
                      borderRadius: 4, 
                      fontSize: 12 
                    }} 
                    required
                  />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Data Type</label>
                  <select value={param.data_type || 'float'} onChange={(e) => updateParameter('input', i, 'data_type', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }}>
                    <option value="string">string</option>
                    <option value="int">int</option>
                    <option value="float">float</option>
                  </select>
                </div>
              </div>
              <div style={{ marginBottom: 8 }}>
                <label style={{ fontSize: 11, color: '#6b7280' }}>Description</label>
                <input type="text" value={param.description || ''} onChange={(e) => updateParameter('input', i, 'description', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
              </div>
              <div style={{ marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                <label style={{ fontSize: 11, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <input type="checkbox" checked={param.hidden || false} onChange={(e) => updateParameter('input', i, 'hidden', e.target.checked)} style={{ margin: 0 }} />
                  Hidden
                </label>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Range Min</label>
                  <input type="text" value={param.range?.min || ''} onChange={(e) => updateParameter('input', i, 'range', { ...(param.range || {}), min: e.target.value })} placeholder="e.g., - or none" style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Range Max</label>
                  <input type="text" value={param.range?.max || ''} onChange={(e) => updateParameter('input', i, 'range', { ...(param.range || {}), max: e.target.value })} placeholder="e.g., - or none" style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
              </div>
              <div>
                <label style={{ fontSize: 11, color: '#6b7280', marginBottom: 4, display: 'block' }}>Tags</label>
                <div style={{ display: 'flex', gap: 4, marginBottom: 4, flexWrap: 'wrap' }}>
                  {(param.tags || []).map((tag: string, tagIdx: number) => (
                    <span key={tagIdx} style={{ background: '#e0e7ff', color: '#3730a3', padding: '2px 6px', borderRadius: 3, fontSize: 10, display: 'flex', alignItems: 'center', gap: 2 }}>
                      {tag}
                      <button onClick={() => removeParameterTag('input', i, tagIdx)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#3730a3', fontSize: 12, padding: 0, marginLeft: 2 }}>×</button>
                    </span>
                  ))}
                </div>
                <input
                  type="text"
                  placeholder="Add tag"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                      addParameterTag('input', i, e.currentTarget.value);
                      e.currentTarget.value = '';
                    }
                  }}
                  style={{ width: '100%', padding: '4px 6px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 11 }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Output Variables */}
        <div style={{ marginBottom: 20, padding: 12, border: '1px solid #e5e7eb', borderRadius: 8, background: '#fafafa' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <label style={{ fontWeight: 600, fontSize: 14 }}>Output Variables</label>
            <button onClick={() => addParameter('output')} style={{ padding: '4px 8px', border: '1px solid #d1d5db', borderRadius: 4, background: '#fff', cursor: 'pointer', fontSize: 12 }}>+ Add</button>
          </div>
          {modelData.output_variables.map((param, i) => (
            <div key={i} style={{ marginBottom: 12, padding: 12, background: '#fff', borderRadius: 6, border: '1px solid #e5e7eb' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <strong style={{ fontSize: 13 }}>Output {i + 1}</strong>
                <button onClick={() => removeParameter('output', i)} style={{ background: '#fee2e2', color: '#dc2626', border: 'none', borderRadius: 4, padding: '2px 6px', cursor: 'pointer', fontSize: 11 }}>Remove</button>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Name</label>
                  <input type="text" value={param.name || ''} onChange={(e) => updateParameter('output', i, 'name', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Unit</label>
                  <input type="text" value={param.unit || ''} onChange={(e) => updateParameter('output', i, 'unit', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Start Value <span style={{ color: '#dc2626' }}>*</span></label>
                  <input 
                    type="text" 
                    value={param.start_value || ''} 
                    onChange={(e) => updateParameter('output', i, 'start_value', e.target.value)} 
                    style={{ 
                      width: '100%', 
                      padding: '6px 8px', 
                      border: `1px solid ${(!param.start_value || String(param.start_value).trim() === '') ? '#dc2626' : '#d1d5db'}`, 
                      borderRadius: 4, 
                      fontSize: 12 
                    }} 
                    required
                  />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Data Type</label>
                  <select value={param.data_type || 'float'} onChange={(e) => updateParameter('output', i, 'data_type', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }}>
                    <option value="string">string</option>
                    <option value="int">int</option>
                    <option value="float">float</option>
                  </select>
                </div>
              </div>
              <div style={{ marginBottom: 8 }}>
                <label style={{ fontSize: 11, color: '#6b7280' }}>Description</label>
                <input type="text" value={param.description || ''} onChange={(e) => updateParameter('output', i, 'description', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
              </div>
              <div style={{ marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                <label style={{ fontSize: 11, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <input type="checkbox" checked={param.hidden || false} onChange={(e) => updateParameter('output', i, 'hidden', e.target.checked)} style={{ margin: 0 }} />
                  Hidden
                </label>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Range Min</label>
                  <input type="text" value={param.range?.min || ''} onChange={(e) => updateParameter('output', i, 'range', { ...(param.range || {}), min: e.target.value })} placeholder="e.g., none" style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Range Max</label>
                  <input type="text" value={param.range?.max || ''} onChange={(e) => updateParameter('output', i, 'range', { ...(param.range || {}), max: e.target.value })} placeholder="e.g., none" style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
              </div>
              <div>
                <label style={{ fontSize: 11, color: '#6b7280', marginBottom: 4, display: 'block' }}>Tags</label>
                <div style={{ display: 'flex', gap: 4, marginBottom: 4, flexWrap: 'wrap' }}>
                  {(param.tags || []).map((tag: string, tagIdx: number) => (
                    <span key={tagIdx} style={{ background: '#e0e7ff', color: '#3730a3', padding: '2px 6px', borderRadius: 3, fontSize: 10, display: 'flex', alignItems: 'center', gap: 2 }}>
                      {tag}
                      <button onClick={() => removeParameterTag('output', i, tagIdx)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#3730a3', fontSize: 12, padding: 0, marginLeft: 2 }}>×</button>
                    </span>
                  ))}
                </div>
                <input
                  type="text"
                  placeholder="Add tag"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                      addParameterTag('output', i, e.currentTarget.value);
                      e.currentTarget.value = '';
                    }
                  }}
                  style={{ width: '100%', padding: '4px 6px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 11 }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Model Parameters */}
        <div style={{ marginBottom: 20, padding: 12, border: '1px solid #e5e7eb', borderRadius: 8, background: '#fafafa' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <label style={{ fontWeight: 600, fontSize: 14 }}>Model Parameters</label>
            <button onClick={() => addParameter('model')} style={{ padding: '4px 8px', border: '1px solid #d1d5db', borderRadius: 4, background: '#fff', cursor: 'pointer', fontSize: 12 }}>+ Add</button>
          </div>
          {modelData.model_parameters.map((param, i) => (
            <div key={i} style={{ marginBottom: 12, padding: 12, background: '#fff', borderRadius: 6, border: '1px solid #e5e7eb' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <strong style={{ fontSize: 13 }}>Parameter {i + 1}</strong>
                <button onClick={() => removeParameter('model', i)} style={{ background: '#fee2e2', color: '#dc2626', border: 'none', borderRadius: 4, padding: '2px 6px', cursor: 'pointer', fontSize: 11 }}>Remove</button>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Name</label>
                  <input type="text" value={param.name || ''} onChange={(e) => updateParameter('model', i, 'name', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Unit</label>
                  <input type="text" value={param.unit || ''} onChange={(e) => updateParameter('model', i, 'unit', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Default Value</label>
                  <input type="text" value={param.default_value || ''} onChange={(e) => updateParameter('model', i, 'default_value', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Data Type</label>
                  <select value={param.data_type || 'string'} onChange={(e) => updateParameter('model', i, 'data_type', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }}>
                    <option value="string">string</option>
                    <option value="int">int</option>
                    <option value="float">float</option>
                  </select>
                </div>
              </div>
              <div style={{ marginBottom: 8 }}>
                <label style={{ fontSize: 11, color: '#6b7280' }}>Description</label>
                <input type="text" value={param.description || ''} onChange={(e) => updateParameter('model', i, 'description', e.target.value)} style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Range Min</label>
                  <input type="text" value={param.range?.min || ''} onChange={(e) => updateParameter('model', i, 'range', { ...(param.range || {}), min: e.target.value })} placeholder="e.g., none" style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
                <div>
                  <label style={{ fontSize: 11, color: '#6b7280' }}>Range Max</label>
                  <input type="text" value={param.range?.max || ''} onChange={(e) => updateParameter('model', i, 'range', { ...(param.range || {}), max: e.target.value })} placeholder="e.g., none" style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 12 }} />
                </div>
              </div>
              <div>
                <label style={{ fontSize: 11, color: '#6b7280', marginBottom: 4, display: 'block' }}>Tags</label>
                <div style={{ display: 'flex', gap: 4, marginBottom: 4, flexWrap: 'wrap' }}>
                  {(param.tags || []).map((tag: string, tagIdx: number) => (
                    <span key={tagIdx} style={{ background: '#e0e7ff', color: '#3730a3', padding: '2px 6px', borderRadius: 3, fontSize: 10, display: 'flex', alignItems: 'center', gap: 2 }}>
                      {tag}
                      <button onClick={() => removeParameterTag('model', i, tagIdx)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#3730a3', fontSize: 12, padding: 0, marginLeft: 2 }}>×</button>
                    </span>
                  ))}
                </div>
                <input
                  type="text"
                  placeholder="Add tag"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                      addParameterTag('model', i, e.currentTarget.value);
                      e.currentTarget.value = '';
                    }
                  }}
                  style={{ width: '100%', padding: '4px 6px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 11 }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Possible Connections */}
        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500, fontSize: 13 }}>Possible Connections</label>
          <div style={{ display: 'flex', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
            {modelData.possible_connections.map((conn, i) => (
              <span key={i} style={{ background: '#e0e7ff', color: '#3730a3', padding: '4px 8px', borderRadius: 4, fontSize: 12, display: 'flex', alignItems: 'center', gap: 4 }}>
                {conn}
                <button onClick={() => removeArrayItem('possible_connections', i)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#3730a3', fontSize: 14, padding: 0, marginLeft: 4 }}>×</button>
              </span>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              type="text"
              value={newPossibleConnection}
              onChange={(e) => setNewPossibleConnection(e.target.value)}
              onKeyPress={(e) => { if (e.key === 'Enter') { addArrayItem('possible_connections', newPossibleConnection); setNewPossibleConnection(''); } }}
              placeholder="e.g., building"
              style={{ flex: 1, padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13 }}
            />
            <button onClick={() => { addArrayItem('possible_connections', newPossibleConnection); setNewPossibleConnection(''); }} style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, background: '#f3f4f6', cursor: 'pointer', fontSize: 13 }}>Add</button>
          </div>
        </div>

      </div>
    </div>
  );
});

ModelBuilder.displayName = 'ModelBuilder';
