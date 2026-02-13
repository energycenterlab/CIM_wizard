import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useBuildingsData } from '../../lib/buildings/useBuildingsData';
import { useAssignmentsStore } from '../../store/assignmentsStore';
import { applyClauses, samplePercentWeighted } from '../../lib/buildings/filterEngine';
import { addAssignment as addAssignmentRedux } from '../../slices/assignmentsSlice';
import { removeSelectedFeature, deleteSelectedFeature } from '../../slices/selectedFeaturesSlice';
import { useToast } from '../../contexts/ToastContext';
import InputEditorMap from './InputEditorMap';
import MapRightSidebar from './MapRightSidebar';
import type { Feature } from 'geojson';

const AssignmentsView: React.FC = () => {
  const { features } = useBuildingsData();
  const ensureDefaultAllBatch = useAssignmentsStore(s => s.ensureDefaultAllBatch);
  const previewIds = useAssignmentsStore(s => s.previewIds);
  const setPreview = useAssignmentsStore(s => s.setPreview);
  const addBatch = useAssignmentsStore(s => s.addBatch);
  const dispatch = useDispatch();
  const { showToast } = useToast();
  
  // Get selected features from Redux state
  const selectedFeatures = useSelector((state: any) => state.selectedFeatures.selectedFeatures);
  const selectedIds = Array.isArray(selectedFeatures) ? selectedFeatures : [];
  const [activeTab, setActiveTab] = useState<'filters'|'split'|'map'>('filters');
  const [mapBatchName, setMapBatchName] = useState('');
  const [clauses, setClauses] = useState<any[]>([]);
  const [qFilters, setQFilters] = useState({
    selectAll: { enabled: false },
    height: { enabled: false, op: 'gte', min: 0, max: 0 },
    year: { enabled: false, op: 'between', min: 1900, max: 2025 },
    usage_category: { enabled: false, values: [] as string[] },
    building_type: { enabled: false, values: [] as string[] },
    total_floors: { enabled: false, op: 'gte', min: 0, max: 0 },
    surface_area: { enabled: false, op: 'gte', min: 0, max: 0 },
  });
  const [randomPercent, setRandomPercent] = useState<number>(50);
  const [randomSeed, setRandomSeed] = useState<number>(42);
  const [weightBy, setWeightBy] = useState<string>('uniform');
  const [splitGroups, setSplitGroups] = useState<{A:(string|number)[];B:(string|number)[]}|null>(null);
  const [previewGroup, setPreviewGroup] = useState<'A'|'B'>('A');
  const [splitViewMode, setSplitViewMode] = useState<'data'|'analytics'>('analytics');
  const [splitSaveOpen, setSplitSaveOpen] = useState(false);
  const [splitSaveA, setSplitSaveA] = useState(true);
  const [splitSaveB, setSplitSaveB] = useState(true);
  const [splitNameA, setSplitNameA] = useState('');
  const [splitNameB, setSplitNameB] = useState('');

  // Right sidebar state for map tab
  const [isDrawingPolygon, setIsDrawingPolygon] = useState(false);
  const [showBuildingDetails, setShowBuildingDetails] = useState(false);
  const [selectedBuildingDetails, setSelectedBuildingDetails] = useState<Feature | null>(null);

  // Persist state in localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem('assignmentsView:v1');
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed.qFilters) setQFilters(parsed.qFilters);
        if (parsed.clauses) setClauses(parsed.clauses);
        if (parsed.randomPercent) setRandomPercent(parsed.randomPercent);
        if (parsed.randomSeed) setRandomSeed(parsed.randomSeed);
        if (parsed.activeTab) setActiveTab(parsed.activeTab);
        if (parsed.previewGroup) setPreviewGroup(parsed.previewGroup);
      }
    } catch {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    try {
      localStorage.setItem('assignmentsView:v1', JSON.stringify({ qFilters, clauses, randomPercent, randomSeed, activeTab, previewGroup }));
    } catch {}
  }, [qFilters, clauses, randomPercent, randomSeed, activeTab, previewGroup]);

  useEffect(() => {
    if (features.length) ensureDefaultAllBatch(features);
  }, [features]);

  // Update suggested name when selected buildings change
  useEffect(() => {
    if (selectedIds.length > 0) {
      setMapBatchName(`batch_map_${selectedIds.length}`);
    } else {
      setMapBatchName('');
    }
  }, [selectedIds]);

  // Handle removing a building from selection
  const handleRemoveBuilding = (id: string | number) => {
    dispatch(removeSelectedFeature(String(id)));
  };

  // Right sidebar handlers
  const handleStartPolygonDrawing = () => {
    setIsDrawingPolygon(true);
  };

  const handleStopPolygonDrawing = () => {
    setIsDrawingPolygon(false);
  };

  const handleCloseBuildingDetails = () => {
    setShowBuildingDetails(false);
    setSelectedBuildingDetails(null);
  };

  const handleBuildingClick = (building: Feature) => {
    setSelectedBuildingDetails(building);
    setShowBuildingDetails(true);
  };

  const handleFitToView = () => {
    // Call the fit to view function exposed by InputEditorMap
    if ((window as any).fitToView) {
      (window as any).fitToView();
    }
  };

  // Reset state after creating batch
  const resetStateAfterCreate = () => {
    // Clear selected buildings from map
    dispatch(deleteSelectedFeature());
    // Reset map batch name
    setMapBatchName('');
    // Clear preview if any
    setPreview([]);
  };
  console.debug('AssignmentsView mounted');
  return (
    <div style={{ 
      position: 'relative', 
      width: '100%', 
      height: '100%', 
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{ 
        padding: '12px 16px',
        borderBottom: '1px solid #e0e0e0',
        flexShrink: 0
      }}>
        {/* Tabs - match Projects page style */}
        <div style={{ display: 'flex', borderBottom: '1px solid #e0e0e0', marginBottom: 20 }}>
          <button
            onClick={() => setActiveTab('filters')}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: activeTab === 'filters' ? '#4CAF50' : '#f5f5f5',
              color: activeTab === 'filters' ? 'white' : '#333',
              cursor: 'pointer',
              borderBottom: activeTab === 'filters' ? '3px solid #4CAF50' : '3px solid transparent',
              fontWeight: activeTab === 'filters' ? 600 : 400,
              transition: 'all 0.2s ease',
              borderRadius: '4px 4px 0 0'
            }}
            onMouseEnter={(e) => {
              if (activeTab !== 'filters') {
                (e.currentTarget as HTMLButtonElement).style.background = '#e8f5e8';
                (e.currentTarget as HTMLButtonElement).style.color = '#2e7d32';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== 'filters') {
                (e.currentTarget as HTMLButtonElement).style.background = '#f5f5f5';
                (e.currentTarget as HTMLButtonElement).style.color = '#333';
              }
            }}
          >
            Filters
          </button>
          <button
            onClick={() => setActiveTab('split')}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: activeTab === 'split' ? '#2196F3' : '#f5f5f5',
              color: activeTab === 'split' ? 'white' : '#333',
              cursor: 'pointer',
              borderBottom: activeTab === 'split' ? '3px solid #2196F3' : '3px solid transparent',
              fontWeight: activeTab === 'split' ? 600 : 400,
              transition: 'all 0.2s ease',
              borderRadius: '4px 4px 0 0'
            }}
            onMouseEnter={(e) => {
              if (activeTab !== 'split') {
                (e.currentTarget as HTMLButtonElement).style.background = '#e3f2fd';
                (e.currentTarget as HTMLButtonElement).style.color = '#1976d2';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== 'split') {
                (e.currentTarget as HTMLButtonElement).style.background = '#f5f5f5';
                (e.currentTarget as HTMLButtonElement).style.color = '#333';
              }
            }}
          >
            Split/Random
          </button>
          <button
            onClick={() => setActiveTab('map')}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: activeTab === 'map' ? '#FF9800' : '#f5f5f5',
              color: activeTab === 'map' ? 'white' : '#333',
              cursor: 'pointer',
              borderBottom: activeTab === 'map' ? '3px solid #FF9800' : '3px solid transparent',
              fontWeight: activeTab === 'map' ? 600 : 400,
              transition: 'all 0.2s ease',
              borderRadius: '4px 4px 0 0'
            }}
            onMouseEnter={(e) => {
              if (activeTab !== 'map') {
                (e.currentTarget as HTMLButtonElement).style.background = '#fff3e0';
                (e.currentTarget as HTMLButtonElement).style.color = '#f57c00';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== 'map') {
                (e.currentTarget as HTMLButtonElement).style.background = '#f5f5f5';
                (e.currentTarget as HTMLButtonElement).style.color = '#333';
              }
            }}
          >
            Select from Map
          </button>
        </div>

      </div>

      {/* Main content area - scrollable */}
      <div style={{ 
        flex: 1, 
        minHeight: 0, 
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Three-column layout: left sidebar, map, right sidebar */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: activeTab === 'map' ? 'minmax(300px, 400px) 1fr minmax(150px, 200px)' : 'minmax(300px, 400px) minmax(0,1fr)', 
          columnGap: 24, 
          alignItems: 'start', 
          maxWidth: '100%', 
          boxSizing: 'border-box', 
          height: '100%', 
          padding: '12px 16px' 
        }}>
          {/* Left sidebar rail */}
          <div style={{ 
            background: '#fff', 
            borderRight: '1px solid #eee', 
            padding: '16px', 
            borderRadius: 8, 
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column',
            overflow: 'hidden'
          }}>
            <div style={{ flex: 1, overflow: 'auto', minHeight: 0, paddingBottom: '60px' }}>
              {activeTab === 'filters' && (
              <FiltersPanel
                qFilters={qFilters}
                setQFilters={setQFilters}
                clauses={clauses}
                setClauses={setClauses}
                features={features}
                valid={validateFilters(qFilters)}
              />
            )}
            {activeTab === 'map' && (
              <MapSelectionPanel
                selectedIds={selectedIds}
                onApply={() => {
                  setPreview(selectedIds);
                }}
                onSave={() => {
                  if (!selectedIds.length) return;
                  const batchName = mapBatchName || `batch_map_${selectedIds.length}`;
                  const rule = { kind: 'map', selectedIds: selectedIds } as any;
                  const batch = { id: `${Date.now()}`, name: batchName, createdAt: Date.now(), size: selectedIds.length, ids: selectedIds, rule } as any;
                  addBatch(batch);
                  dispatch(addAssignmentRedux({ id: batch.id, name: batch.name, entityType: 'building', ids: batch.ids, count: batch.size, createdAt: new Date().toISOString() } as any));
                  showToast && showToast(`Created '${batch.name}' (${batch.size})`, 'success', 2000);
                  // Reset state after creating batch
                  resetStateAfterCreate();
                }}
                onRemoveBuilding={handleRemoveBuilding}
                suggestedName={mapBatchName}
                onNameChange={setMapBatchName}
              />
            )}
            {activeTab === 'split' && (
              <SplitPanel
                percent={randomPercent}
                setPercent={setRandomPercent}
                seed={randomSeed}
                setSeed={setRandomSeed}
                weightBy={weightBy}
                setWeightBy={setWeightBy}
              />
            )}
            </div>
          </div>

          {/* Center section content */}
          <div style={{ minWidth: 0, maxWidth: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
            {activeTab === 'map' ? (
              /* Map for building selection */
              <div style={{ flex: 1, border: '1px solid #e5e7eb', borderRadius: 8, overflow: 'hidden' }}>
                <InputEditorMap 
                  disablePopup={true} 
                  filterLayers={['line_wgs84', 'buses_sansa']} 
                  customVisibleLayers={['Casestudy_Sansalvario']}
                  is2D={true}
                  isDrawingPolygon={isDrawingPolygon}
                  onStartPolygonDrawing={handleStartPolygonDrawing}
                  onStopPolygonDrawing={handleStopPolygonDrawing}
                  showBuildingDetails={showBuildingDetails}
                  selectedBuildingDetails={selectedBuildingDetails}
                  onCloseBuildingDetails={handleCloseBuildingDetails}
                  onBuildingClick={handleBuildingClick}
                  onFitToView={handleFitToView}
                />
              </div>
            ) : (
              /* Preview table for other tabs */
              <>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                  <span style={{ fontSize: 12, background: '#EEF2FF', border: '1px solid #E5E7EB', padding: '4px 8px', borderRadius: 999 }}>Preview: {previewIds.length} buildings</span>
                </div>
            {(previewIds.length > 0) ? (
              activeTab === 'split' && splitGroups ? (
                <SplitAnalyticsPanel 
                  splitGroups={splitGroups} 
                  features={features}
                  previewGroup={previewGroup}
                  viewMode={splitViewMode}
                  onToggleGroup={(g: 'A'|'B') => { setPreviewGroup(g); if (splitGroups) setPreview(g==='A'? splitGroups.A : splitGroups.B); }}
                  onToggleViewMode={setSplitViewMode}
                />
              ) : (
                <div style={{ maxHeight: '48vh', overflowY: 'auto', border: '1px solid #F3F4F6', borderRadius: 6 }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                  <thead>
                    <tr>
                      <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: '4px' }}>ID</th>
                      <th style={{ textAlign: 'right', borderBottom: '1px solid #e5e7eb', padding: '4px' }}>Height</th>
                      <th style={{ textAlign: 'right', borderBottom: '1px solid #e5e7eb', padding: '4px' }}>Year</th>
                      <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: '4px' }}>Usage</th>
                      <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: '4px' }}>Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {previewIds.map((id) => {
                      const row = features.find(f => String(f.id) === String(id));
                      return (
                        <tr key={String(id)}>
                          <td style={{ padding: '4px', borderBottom: '1px solid #F3F4F6' }}>{String(id)}</td>
                          <td style={{ padding: '4px', borderBottom: '1px solid #F3F4F6', textAlign: 'right' }}>{row?.height ?? ''}</td>
                          <td style={{ padding: '4px', borderBottom: '1px solid #F3F4F6', textAlign: 'right' }}>{row?.year ?? ''}</td>
                          <td style={{ padding: '4px', borderBottom: '1px solid #F3F4F6' }}>{row?.usage_category ?? row?.usage_type ?? ''}</td>
                          <td style={{ padding: '4px', borderBottom: '1px solid #F3F4F6' }}>{row?.building_type ?? ''}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                </div>
              )
            ) : (
              <div style={{ color: '#6B7280' }}>No buildings match the current filters. <button onClick={() => { setQFilters({
                selectAll: { enabled: false },
                height: { enabled: false, op: 'gte', min: 0, max: 0 },
                year: { enabled: false, op: 'between', min: 1900, max: 2025 },
                usage_category: { enabled: false, values: [] },
                building_type: { enabled: false, values: [] },
                total_floors: { enabled: false, op: 'gte', min: 0, max: 0 },
                surface_area: { enabled: false, op: 'gte', min: 0, max: 0 },
              }); setClauses([]); setPreview([]); }} style={{ border: '1px solid #e5e7eb', background: '#fff', borderRadius: 8, padding: '4px 8px', fontSize: 12, marginLeft: 8 }}>Reset filters</button></div>
            )}
              </>
            )}
          </div>

          {/* Right sidebar - only for map tab */}
          {activeTab === 'map' && (
            <MapRightSidebar
              isDrawingPolygon={isDrawingPolygon}
              onStartPolygonDrawing={handleStartPolygonDrawing}
              onStopPolygonDrawing={handleStopPolygonDrawing}
              showBuildingDetails={showBuildingDetails}
              selectedBuildingDetails={selectedBuildingDetails}
              onCloseBuildingDetails={handleCloseBuildingDetails}
              onFitToView={handleFitToView}
            />
          )}
        </div>
      </div>


      {/* Save split modal */}
      {splitSaveOpen && splitGroups && (
        <div role="dialog" aria-modal="true" style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 60 }}>
          <div style={{ background: '#fff', borderRadius: 8, minWidth: 380, maxWidth: 560, padding: 16, boxShadow: '0 10px 30px rgba(0,0,0,0.2)' }}>
            <div style={{ fontWeight: 600, marginBottom: 8 }}>Save split groups</div>
            <div style={{ display: 'grid', gap: 10 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input type="checkbox" checked={splitSaveA} onChange={(e) => setSplitSaveA(e.target.checked)} />
                <span style={{ minWidth: 80 }}>Group A</span>
                <input value={splitNameA} onChange={(e) => setSplitNameA(e.target.value)} style={{ flex: 1, border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }} />
                <span style={{ fontSize: 12, color: '#6B7280' }}>{splitGroups.A.length} blds</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input type="checkbox" checked={splitSaveB} onChange={(e) => setSplitSaveB(e.target.checked)} />
                <span style={{ minWidth: 80 }}>Group B</span>
                <input value={splitNameB} onChange={(e) => setSplitNameB(e.target.value)} style={{ flex: 1, border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }} />
                <span style={{ fontSize: 12, color: '#6B7280' }}>{splitGroups.B.length} blds</span>
              </label>
            </div>
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 12 }}>
              <button onClick={() => setSplitSaveOpen(false)} style={{ border: '1px solid #e5e7eb', background: '#fff', borderRadius: 8, padding: '6px 12px' }}>Cancel</button>
              <button disabled={!splitSaveA && !splitSaveB} onClick={() => {
                if (splitSaveA) {
                  const a = { id: `${Date.now()}a`, name: splitNameA || `batch_split_A_${splitGroups.A.length}`, createdAt: Date.now(), size: splitGroups.A.length, ids: splitGroups.A, rule: { kind: 'random', percent: 50, seed: randomSeed } } as any;
                  addBatch(a);
                  dispatch(addAssignmentRedux({ id: a.id, name: a.name, entityType: 'building', ids: a.ids, count: a.size, createdAt: new Date().toISOString() } as any));
                }
                if (splitSaveB) {
                  const b = { id: `${Date.now()}b`, name: splitNameB || `batch_split_B_${splitGroups.B.length}`, createdAt: Date.now(), size: splitGroups.B.length, ids: splitGroups.B, rule: { kind: 'random', percent: 50, seed: randomSeed } } as any;
                  addBatch(b);
                  dispatch(addAssignmentRedux({ id: b.id, name: b.name, entityType: 'building', ids: b.ids, count: b.size, createdAt: new Date().toISOString() } as any));
                }
                showToast && showToast('Split saved', 'success', 2000);
                setSplitSaveOpen(false);
              }} style={{ border: '1px solid #2563EB', background: '#2563EB', color: '#fff', borderRadius: 8, padding: '6px 12px' }}>Save</button>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Bar with Apply, Reset and Create buttons */}
      <div style={{
        background: '#fff',
        borderTop: '1px solid #e0e0e0',
        padding: '12px 16px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '12px',
        boxShadow: '0 -2px 8px rgba(0,0,0,0.1)',
        flexShrink: 0
      }}>
        {/* Left side - Apply button (only for filters and split tabs) */}
        <div>
          {(activeTab === 'filters' || activeTab === 'split') && (
            <button
              onClick={() => {
                if (activeTab === 'filters') {
                  // Handle Select All filter
                  if (qFilters.selectAll.enabled) {
                    // Select all buildings
                    const allBuildingIds = features?.map((f: any) => f.id) || [];
                    setPreview(allBuildingIds);
                  } else {
                    // Apply other filters (excluding selectAll)
                    const built = buildClausesFromQuick(qFilters);
                    const all = [...built, ...clauses];
                    const out = applyClauses(features as any, all as any);
                    setPreview(out.map((f:any) => f.id));
                  }
                } else if (activeTab === 'split') {
                  // Apply logic for split tab - generate split
                  // Always use the full dataset, not the preview
                  const baseIds = features.map(f => f.id);
                  const idsA = samplePercentWeighted(baseIds, randomPercent, randomSeed, weightBy, features);
                  const setA = new Set(idsA);
                  const idsB = baseIds.filter(id => !setA.has(id));
                  setSplitGroups({ A: idsA, B: idsB });
                  setPreview(idsA);
                  setPreviewGroup('A');
                }
              }}
              style={{
                padding: '8px 16px',
                border: 'none',
                background: 'black',
                color: 'white',
                borderRadius: 6,
                cursor: 'pointer',
                fontSize: 14,
                fontWeight: 500,
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = '#333';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = 'black';
              }}
            >
              Apply
            </button>
          )}
        </div>
        
        {/* Right side - Reset and Create buttons */}
        <div style={{ display: 'flex', gap: '12px' }}>
        <button
          onClick={() => {
            // Reset logic based on active tab
            if (activeTab === 'filters') {
              setQFilters({
                selectAll: { enabled: false },
                height: { enabled: false, op: 'gte', min: 0, max: 0 },
                year: { enabled: false, op: 'between', min: 1900, max: 2025 },
                usage_category: { enabled: false, values: [] },
                building_type: { enabled: false, values: [] },
                total_floors: { enabled: false, op: 'gte', min: 0, max: 0 },
                surface_area: { enabled: false, op: 'gte', min: 0, max: 0 },
              });
              setClauses([]);
            } else if (activeTab === 'split') {
              setRandomPercent(50);
              setRandomSeed(42);
              setWeightBy('uniform');
              setSplitGroups(null);
              setPreviewGroup('A');
              setSplitViewMode('analytics');
            } else if (activeTab === 'map') {
              // Clear selected features for map tab
              if (Array.isArray(selectedFeatures)) {
                selectedFeatures.forEach((id: string | number) => {
                  dispatch(removeSelectedFeature(String(id)));
                });
              }
            }
            setPreview([]);
          }}
          style={{
            padding: '8px 16px',
            border: 'none',
            background: '#ffebee',
            color: '#d32f2f',
            borderRadius: 6,
            cursor: 'pointer',
            fontSize: 14,
            fontWeight: 500,
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = '#ffcdd2';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = '#ffebee';
          }}
        >
          Reset
        </button>
        
        <button
          onClick={() => {
            // Save logic based on active tab
            if (activeTab === 'filters') {
              if (!previewIds.length) return;
              const batchName = qFilters.selectAll.enabled ? `batch_all_${previewIds.length}` : `batch_filters_${previewIds.length}`;
              const rule = qFilters.selectAll.enabled 
                ? { kind: 'selectAll' } 
                : { kind: 'filter', clauses: [...buildClausesFromQuick(qFilters), ...clauses] } as any;
              const batch = { id: `${Date.now()}`, name: batchName, createdAt: Date.now(), size: previewIds.length, ids: previewIds, rule } as any;
              addBatch(batch);
              dispatch(addAssignmentRedux({ id: batch.id, name: batch.name, entityType: 'building', ids: batch.ids, count: batch.size, createdAt: new Date().toISOString() } as any));
              showToast && showToast(`Created '${batch.name}' (${batch.size})`, 'success', 2000);
              // Reset state after creating batch
              setPreview([]);
            } else if (activeTab === 'split') {
              if (!splitGroups) return;
              // Create both batches directly
              const batchA = { 
                id: `${Date.now()}_A`, 
                name: `batch_split_A_${splitGroups.A.length}`, 
                createdAt: Date.now(), 
                size: splitGroups.A.length, 
                ids: splitGroups.A, 
                rule: { kind: 'splitTo' as const, sourceBatchId: 'original', percent: randomPercent, seed: randomSeed } 
              };
              const batchB = { 
                id: `${Date.now()}_B`, 
                name: `batch_split_B_${splitGroups.B.length}`, 
                createdAt: Date.now(), 
                size: splitGroups.B.length, 
                ids: splitGroups.B, 
                rule: { kind: 'splitTo' as const, sourceBatchId: 'original', percent: 100 - randomPercent, seed: randomSeed } 
              };
              
              addBatch(batchA);
              addBatch(batchB);
              dispatch(addAssignmentRedux({ id: batchA.id, name: batchA.name, entityType: 'building', ids: batchA.ids, count: batchA.size, createdAt: new Date().toISOString() } as any));
              dispatch(addAssignmentRedux({ id: batchB.id, name: batchB.name, entityType: 'building', ids: batchB.ids, count: batchB.size, createdAt: new Date().toISOString() } as any));
              showToast && showToast(`Created '${batchA.name}' (${batchA.size}) and '${batchB.name}' (${batchB.size})`, 'success', 2000);
              
              // Reset state after creating batches
              setSplitGroups(null);
              setPreview([]);
            } else if (activeTab === 'map') {
              if (!selectedIds.length) return;
              const batchName = mapBatchName || `batch_map_${selectedIds.length}`;
              const rule = { kind: 'map', selectedIds: selectedIds } as any;
              const batch = { id: `${Date.now()}`, name: batchName, createdAt: Date.now(), size: selectedIds.length, ids: selectedIds, rule } as any;
              addBatch(batch);
              dispatch(addAssignmentRedux({ id: batch.id, name: batch.name, entityType: 'building', ids: batch.ids, count: batch.size, createdAt: new Date().toISOString() } as any));
              showToast && showToast(`Created '${batch.name}' (${batch.size})`, 'success', 2000);
              // Reset state after creating batch
              resetStateAfterCreate();
            }
          }}
          disabled={activeTab === 'map' ? !selectedIds.length : !previewIds.length}
          style={{
            padding: '8px 16px',
            border: 'none',
            background: (activeTab === 'map' ? !selectedIds.length : !previewIds.length) ? '#ccc' : 'black',
            color: 'white',
            borderRadius: 6,
            cursor: (activeTab === 'map' ? !selectedIds.length : !previewIds.length) ? 'not-allowed' : 'pointer',
            fontSize: 14,
            fontWeight: 500,
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => {
            if ((activeTab === 'map' ? !selectedIds.length : !previewIds.length)) return;
            (e.currentTarget as HTMLButtonElement).style.background = '#333';
          }}
          onMouseLeave={(e) => {
            if ((activeTab === 'map' ? !selectedIds.length : !previewIds.length)) return;
            (e.currentTarget as HTMLButtonElement).style.background = 'black';
          }}
        >
          Create
        </button>
        </div>
      </div>
    </div>
  );
};

export default AssignmentsView;

// Helpers
function buildClausesFromQuick(q: any) {
  const res: any[] = [];
  // Skip selectAll filter as it's handled separately
  if (q.height.enabled) {
    if (q.height.op === 'between') res.push({ attr: 'height', op: 'between', range: [Number(q.height.min||0), Number(q.height.max||0)] });
    if (q.height.op === 'gte') res.push({ attr: 'height', op: 'gte', value: Number(q.height.min||0) });
    if (q.height.op === 'lte') res.push({ attr: 'height', op: 'lte', value: Number(q.height.min||0) });
  }
  if (q.year.enabled) {
    if (q.year.op === 'between') res.push({ attr: 'year', op: 'between', range: [Number(q.year.min||0), Number(q.year.max||0)] });
    if (q.year.op === 'gte') res.push({ attr: 'year', op: 'gte', value: Number(q.year.min||0) });
    if (q.year.op === 'lte') res.push({ attr: 'year', op: 'lte', value: Number(q.year.min||0) });
  }
  if (q.usage_category.enabled && q.usage_category.values.length) res.push({ attr: 'usage_category', op: 'in', values: q.usage_category.values });
  if (q.building_type.enabled && q.building_type.values.length) res.push({ attr: 'building_type', op: 'in', values: q.building_type.values });
  if (q.total_floors.enabled) {
    if (q.total_floors.op === 'between') res.push({ attr: 'total_floors', op: 'between', range: [Number(q.total_floors.min||0), Number(q.total_floors.max||0)] });
    if (q.total_floors.op === 'gte') res.push({ attr: 'total_floors', op: 'gte', value: Number(q.total_floors.min||0) });
    if (q.total_floors.op === 'lte') res.push({ attr: 'total_floors', op: 'lte', value: Number(q.total_floors.min||0) });
  }
  if (q.surface_area.enabled) {
    if (q.surface_area.op === 'between') res.push({ attr: 'surface_area', op: 'between', range: [Number(q.surface_area.min||0), Number(q.surface_area.max||0)] });
    if (q.surface_area.op === 'gte') res.push({ attr: 'surface_area', op: 'gte', value: Number(q.surface_area.min||0) });
    if (q.surface_area.op === 'lte') res.push({ attr: 'surface_area', op: 'lte', value: Number(q.surface_area.min||0) });
  }
  return res;
}

function SimpleClauseBuilder({ clauses, setClauses }: { clauses: any[]; setClauses: (v: any[]) => void }) {
  const numericAttrs = ['height','surface_area','year','number_of_people','number_of_families','total_floors'];
  const stringAttrs = ['usage_category','construction_period','building_type','usage_type'];
  const allAttrs = [...numericAttrs, ...stringAttrs];
  const add = () => setClauses([...(clauses||[]), { attr: 'height', op: 'gte', value: 0 }]);
  const remove = (i: number) => setClauses(clauses.filter((_: any, idx: number) => idx !== i));
  const update = (i: number, patch: any) => setClauses(clauses.map((c: any, idx: number) => idx === i ? { ...c, ...patch } : c));
  return (
    <div>
      <div style={{ display: 'grid', gap: 8 }}>
        {(clauses||[]).map((c: any, i: number) => {
          const isNum = numericAttrs.includes(c.attr);
          return (
            <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: 6, alignItems: 'center' }}>
              <select value={c.attr} onChange={(e) => update(i, { attr: e.target.value, op: isNum ? 'gte' : 'eq', value: undefined, range: undefined })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }}>
                {allAttrs.map(a => <option key={a} value={a}>{a}</option>)}
              </select>
              <select value={c.op} onChange={(e) => update(i, { op: e.target.value })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }}>
                {numericAttrs.includes(c.attr) ? (
                  <>
                    <option value="gt">gt</option>
                    <option value="gte">gte</option>
                    <option value="lt">lt</option>
                    <option value="lte">lte</option>
                    <option value="between">between</option>
                  </>
                ) : (
                  <>
                    <option value="eq">eq</option>
                    <option value="neq">neq</option>
                    <option value="in">in</option>
                    <option value="contains">contains</option>
                  </>
                )}
              </select>
              {c.op === 'between' ? (
                <div style={{ display: 'flex', gap: 6 }}>
                  <input type="number" value={c.range?.[0] ?? ''} onChange={(e) => update(i, { range: [Number(e.target.value||0), c.range?.[1] ?? 0] })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '30px', minWidth: '30px' }} />
                  <input type="number" value={c.range?.[1] ?? ''} onChange={(e) => update(i, { range: [c.range?.[0] ?? 0, Number(e.target.value||0)] })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '30px', minWidth: '30px' }} />
                </div>
              ) : (
                <input value={c.value ?? ''} onChange={(e) => update(i, { value: numericAttrs.includes(c.attr) ? Number(e.target.value||0) : e.target.value })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '40px', minWidth: '40px' }} />
              )}
              <button onClick={() => remove(i)} style={{ border: '1px solid #e5e7eb', background: '#fff', borderRadius: 6, padding: '6px 8px' }}>×</button>
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 8 }}>
        <button onClick={add} style={{ border: '1px solid #e5e7eb', background: '#fff', borderRadius: 8, padding: '6px 12px', fontSize: 13 }}>+ Add clause</button>
      </div>
    </div>
  );
}

function FiltersPanel({ qFilters, setQFilters, clauses, setClauses, features }: any) {
  const toggle = (key: string) => setQFilters({ ...qFilters, [key]: { ...qFilters[key], enabled: !qFilters[key].enabled } });
  const setField = (key: string, patch: any) => setQFilters({ ...qFilters, [key]: { ...qFilters[key], ...patch } });
  const allChips = [
    qFilters.selectAll.enabled ? 'Select All Buildings' : null,
    qFilters.height.enabled ? `Height ${qFilters.height.op} ${qFilters.height.op==='between'?`${qFilters.height.min}-${qFilters.height.max}`:qFilters.height.min}` : null,
    qFilters.year.enabled ? `Year ${qFilters.year.op} ${qFilters.year.op==='between'?`${qFilters.year.min}-${qFilters.year.max}`:qFilters.year.min}` : null,
    qFilters.usage_category.enabled && qFilters.usage_category.values.length ? `Usage in ${qFilters.usage_category.values.length}` : null,
    qFilters.building_type.enabled && qFilters.building_type.values.length ? `Type in ${qFilters.building_type.values.length}` : null,
    qFilters.total_floors.enabled ? `Floors ${qFilters.total_floors.op} ${qFilters.total_floors.op==='between'?`${qFilters.total_floors.min}-${qFilters.total_floors.max}`:qFilters.total_floors.min}` : null,
    qFilters.surface_area.enabled ? `Surface ${qFilters.surface_area.op} ${qFilters.surface_area.op==='between'?`${qFilters.surface_area.min}-${qFilters.surface_area.max}`:qFilters.surface_area.min}` : null,
  ].filter(Boolean) as string[];
  return (
    <div style={{ display: 'grid', gap: 12 }}>
      <div style={{ fontSize: 12, color: '#6B7280' }}>Quick filters</div>
      {/* Select All */}
      <div style={{ display: 'grid', gap: 6 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={qFilters.selectAll.enabled} onChange={() => toggle('selectAll')} />
          <span>Select All Buildings</span>
        </label>
        {qFilters.selectAll.enabled && (
          <div style={{ padding: '8px', background: '#f0f8ff', border: '1px solid #b3d9ff', borderRadius: 6, fontSize: 12, color: '#0066cc' }}>
            This will select all {features?.length || 0} buildings in the dataset.
          </div>
        )}
      </div>
      {/* Height */}
      <div style={{ display: 'grid', gap: 6 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={qFilters.height.enabled} onChange={() => toggle('height')} />
          <span>Height</span>
        </label>
        {qFilters.height.enabled && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
            <select value={qFilters.height.op} onChange={(e) => setField('height', { op: e.target.value })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }}>
              <option value="gte">≥</option>
              <option value="lte">≤</option>
              <option value="between">between</option>
            </select>
            {qFilters.height.op === 'between' ? (
              <div style={{ display: 'flex', gap: 6 }}>
                <input type="number" value={qFilters.height.min} onChange={(e) => setField('height', { min: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '50%' }} />
                <input type="number" value={qFilters.height.max} onChange={(e) => setField('height', { max: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '50%' }} />
              </div>
            ) : (
              <input type="number" value={qFilters.height.min} onChange={(e) => setField('height', { min: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }} />
            )}
          </div>
        )}
      </div>
      {/* Year */}
      <div style={{ display: 'grid', gap: 6 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={qFilters.year.enabled} onChange={() => toggle('year')} />
          <span>Year (construction)</span>
        </label>
        {qFilters.year.enabled && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
            <select value={qFilters.year.op} onChange={(e) => setField('year', { op: e.target.value })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }}>
              <option value="between">between</option>
              <option value="gte">≥</option>
              <option value="lte">≤</option>
            </select>
            {qFilters.year.op === 'between' ? (
              <div style={{ display: 'flex', gap: 6 }}>
                <input type="number" value={qFilters.year.min} onChange={(e) => setField('year', { min: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '50%' }} />
                <input type="number" value={qFilters.year.max} onChange={(e) => setField('year', { max: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '50%' }} />
              </div>
            ) : (
              <input type="number" value={qFilters.year.min} onChange={(e) => setField('year', { min: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }} />
            )}
          </div>
        )}
      </div>
      {/* Usage Category */}
      <div style={{ display: 'grid', gap: 6 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={qFilters.usage_category.enabled} onChange={() => toggle('usage_category')} />
          <span>Usage Category</span>
        </label>
        {qFilters.usage_category.enabled && (
          <ChipsMulti values={qFilters.usage_category.values} setValues={(v: string[]) => setField('usage_category', { values: v })} options={inferStringOptions(features, ['usage_category','usage_type'])} />
        )}
      </div>
      {/* Building Type */}
      <div style={{ display: 'grid', gap: 6 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={qFilters.building_type.enabled} onChange={() => toggle('building_type')} />
          <span>Building Type</span>
        </label>
        {qFilters.building_type.enabled && (
          <ChipsMulti values={qFilters.building_type.values} setValues={(v: string[]) => setField('building_type', { values: v })} options={inferStringOptions(features, ['building_type'])} />
        )}
      </div>
      {/* Floors */}
      <div style={{ display: 'grid', gap: 6 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={qFilters.total_floors.enabled} onChange={() => toggle('total_floors')} />
          <span>Number of Floors</span>
        </label>
        {qFilters.total_floors.enabled && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
            <select value={qFilters.total_floors.op} onChange={(e) => setField('total_floors', { op: e.target.value })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }}>
              <option value="gte">≥</option>
              <option value="lte">≤</option>
              <option value="between">between</option>
            </select>
            {qFilters.total_floors.op === 'between' ? (
              <div style={{ display: 'flex', gap: 6 }}>
                <input type="number" value={qFilters.total_floors.min} onChange={(e) => setField('total_floors', { min: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '50%' }} />
                <input type="number" value={qFilters.total_floors.max} onChange={(e) => setField('total_floors', { max: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '50%' }} />
              </div>
            ) : (
              <input type="number" value={qFilters.total_floors.min} onChange={(e) => setField('total_floors', { min: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }} />
            )}
          </div>
        )}
      </div>
      {/* Surface area */}
      <div style={{ display: 'grid', gap: 6 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={qFilters.surface_area.enabled} onChange={() => toggle('surface_area')} />
          <span>Surface Area</span>
        </label>
        {qFilters.surface_area.enabled && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
            <select value={qFilters.surface_area.op} onChange={(e) => setField('surface_area', { op: e.target.value })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }}>
              <option value="gte">≥</option>
              <option value="lte">≤</option>
              <option value="between">between</option>
            </select>
            {qFilters.surface_area.op === 'between' ? (
              <div style={{ display: 'flex', gap: 6 }}>
                <input type="number" value={qFilters.surface_area.min} onChange={(e) => setField('surface_area', { min: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '50%' }} />
                <input type="number" value={qFilters.surface_area.max} onChange={(e) => setField('surface_area', { max: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px', width: '50%' }} />
              </div>
            ) : (
              <input type="number" value={qFilters.surface_area.min} onChange={(e) => setField('surface_area', { min: Number(e.target.value||0) })} style={{ border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 8px' }} />
            )}
          </div>
        )}
      </div>

      <div style={{ height: 1, background: '#eee', margin: '6px 0' }} />
      <div style={{ fontSize: 12, color: '#6B7280' }}>Custom clauses</div>
      <SimpleClauseBuilder clauses={clauses} setClauses={setClauses} />

          {allChips.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {allChips.map((c, idx) => (
                <span key={idx} style={{ fontSize: 12, background: '#F3F4F6', border: '1px solid #E5E7EB', padding: '4px 8px', borderRadius: 999 }}>{c}</span>
              ))}
            </div>
          )}
    </div>
  );
}

function SplitPanel({ percent, setPercent, seed, setSeed, weightBy, setWeightBy }: any) {
  return (
    <div style={{ display: 'grid', gap: 12 }}>
      <div style={{ display: 'grid', gap: 8 }}>
        {/* Side by side inputs */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div style={{ display: 'grid', gap: 4 }}>
            <label style={{ fontSize: 12 }}>Percent (%)</label>
            <input 
              type="number" 
              min={0} 
              max={100} 
              value={percent} 
              onChange={(e) => setPercent(Number(e.target.value||50))} 
              style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: 6, 
                padding: '6px 8px',
                fontSize: 12
              }} 
            />
          </div>
          <div style={{ display: 'grid', gap: 4 }}>
            <label style={{ fontSize: 12 }}>Seed</label>
            <input 
              type="number" 
              value={seed} 
              onChange={(e) => setSeed(Number(e.target.value||0))} 
              style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: 6, 
                padding: '6px 8px',
                fontSize: 12
              }} 
            />
          </div>
        </div>
        
        {/* Weighted Random Split */}
        <div style={{ display: 'grid', gap: 8 }}>
          <label style={{ fontSize: 12, display: 'flex', alignItems: 'center', gap: 4 }}>
            Weight by
            <span 
              style={{ 
                fontSize: 10, 
                color: '#666', 
                background: '#f0f0f0', 
                padding: '2px 4px', 
                borderRadius: 3,
                cursor: 'help'
              }}
              title="Selection probability ∝ chosen weight"
            >
              ?
            </span>
          </label>
          <div style={{ display: 'grid', gap: 6 }}>
            {[
              { value: 'uniform', label: 'Uniform Random' },
              { value: 'surface_area', label: 'Surface Area' },
              { value: 'height', label: 'Height' },
              { value: 'year', label: 'Year' },
              { value: 'total_floors', label: 'Number of Floors' }
            ].map((option) => (
              <label 
                key={option.value}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 8, 
                  padding: '6px 8px',
                  borderRadius: 6,
                  cursor: 'pointer',
                  background: weightBy === option.value ? '#f0f8ff' : 'transparent',
                  border: weightBy === option.value ? '1px solid #2196F3' : '1px solid transparent',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if (weightBy !== option.value) {
                    e.currentTarget.style.background = '#f8f9fa';
                    e.currentTarget.style.borderColor = '#e5e7eb';
                  }
                }}
                onMouseLeave={(e) => {
                  if (weightBy !== option.value) {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.borderColor = 'transparent';
                  }
                }}
              >
                <input
                  type="radio"
                  name="weightBy"
                  value={option.value}
                  checked={weightBy === option.value}
                  onChange={(e) => setWeightBy(e.target.value)}
                  style={{ 
                    margin: 0,
                    accentColor: '#2196F3'
                  }}
                />
                <span style={{ fontSize: 12, fontWeight: weightBy === option.value ? 500 : 400 }}>
                  {option.label}
                </span>
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function ChipsMulti({ values, setValues, options }: { values: string[]; setValues: (v: string[]) => void; options: string[] }) {
  const toggle = (val: string) => {
    if (values.includes(val)) setValues(values.filter(v => v !== val)); else setValues([...values, val]);
  };
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
      {options.map(opt => (
        <button key={opt} onClick={() => toggle(opt)} style={{ fontSize: 12, border: '1px solid #e5e7eb', background: values.includes(opt) ? '#E0E7FF' : '#fff', borderRadius: 999, padding: '4px 8px' }}>{opt}</button>
      ))}
    </div>
  );
}

function inferStringOptions(features: any[], keys: string[]) {
  const set = new Set<string>();
  for (const f of features) {
    for (const k of keys) {
      if (f[k]) set.add(String(f[k]));
    }
  }
  return Array.from(set).sort();
}

function validateFilters(q: any) {
  const betweenValid = (x: any) => Number(x.min) <= Number(x.max);
  if (q.height.enabled && q.height.op === 'between' && !betweenValid(q.height)) return false;
  if (q.year.enabled && q.year.op === 'between' && !betweenValid(q.year)) return false;
  if (q.total_floors.enabled && q.total_floors.op === 'between' && !betweenValid(q.total_floors)) return false;
  if (q.surface_area.enabled && q.surface_area.op === 'between' && !betweenValid(q.surface_area)) return false;
  return true;
}

// Split Analytics Panel Component
const SplitAnalyticsPanel: React.FC<{
  splitGroups: {A: (string|number)[]; B: (string|number)[]};
  features: any[];
  previewGroup: 'A'|'B';
  viewMode: 'data'|'analytics';
  onToggleGroup: (g: 'A'|'B') => void;
  onToggleViewMode: (mode: 'data'|'analytics') => void;
}> = ({ splitGroups, features, previewGroup, viewMode, onToggleGroup, onToggleViewMode }) => {
  const calculateAnalytics = (groupIds: (string|number)[]) => {
    const groupFeatures = groupIds.map(id => features.find(f => String(f.id) === String(id))).filter(Boolean);
    
    if (groupFeatures.length === 0) {
      return {
        count: 0,
        meanHeight: 0,
        avgYear: 0,
        meanSurfaceArea: 0,
        usageDistribution: {}
      };
    }
    
    const heights = groupFeatures.map(f => f.height).filter(h => typeof h === 'number' && !isNaN(h));
    const years = groupFeatures.map(f => f.year).filter(y => typeof y === 'number' && !isNaN(y));
    const surfaceAreas = groupFeatures.map(f => f.surface_area).filter(s => typeof s === 'number' && !isNaN(s));
    const usages = groupFeatures.map(f => f.usage_category || f.usage_type || 'Unknown').filter(Boolean);
    
    const meanHeight = heights.length > 0 ? heights.reduce((sum, h) => sum + h, 0) / heights.length : 0;
    const avgYear = years.length > 0 ? years.reduce((sum, y) => sum + y, 0) / years.length : 0;
    const meanSurfaceArea = surfaceAreas.length > 0 ? surfaceAreas.reduce((sum, s) => sum + s, 0) / surfaceAreas.length : 0;
    
    const usageDistribution: {[key: string]: number} = {};
    usages.forEach(usage => {
      usageDistribution[usage] = (usageDistribution[usage] || 0) + 1;
    });
    
    return {
      count: groupFeatures.length,
      meanHeight: Math.round(meanHeight * 10) / 10,
      avgYear: Math.round(avgYear),
      meanSurfaceArea: Math.round(meanSurfaceArea * 10) / 10,
      usageDistribution
    };
  };
  
  const analyticsA = calculateAnalytics(splitGroups.A);
  const analyticsB = calculateAnalytics(splitGroups.B);
  
  return (
    <div style={{ display: 'grid', gap: 16 }}>
      {/* View Mode Tabs */}
      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
        <span style={{ fontSize: 12, color: '#6B7280' }}>View:</span>
        <div style={{ border: '1px solid #e5e7eb', borderRadius: 6, overflow: 'hidden' }}>
          <button 
            onClick={() => onToggleViewMode('analytics')} 
            style={{ 
              padding: '4px 10px', 
              fontSize: 12, 
              background: viewMode==='analytics'?'#f3f4f6':'#fff', 
              borderRight: '1px solid #e5e7eb',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            Analytics
          </button>
          <button 
            onClick={() => onToggleViewMode('data')} 
            style={{ 
              padding: '4px 10px', 
              fontSize: 12, 
              background: viewMode==='data'?'#f3f4f6':'#fff',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            Data Review
          </button>
        </div>
      </div>
      
      {/* Group Toggle - only show in data review mode */}
      {viewMode === 'data' && (
        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <span style={{ fontSize: 12, color: '#6B7280' }}>Previewing:</span>
          <div style={{ border: '1px solid #e5e7eb', borderRadius: 6, overflow: 'hidden' }}>
            <button 
              onClick={() => onToggleGroup('A')} 
              style={{ 
                padding: '4px 10px', 
                fontSize: 12, 
                background: previewGroup==='A'?'#f3f4f6':'#fff', 
                borderRight: '1px solid #e5e7eb',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              Group A
            </button>
            <button 
              onClick={() => onToggleGroup('B')} 
              style={{ 
                padding: '4px 10px', 
                fontSize: 12, 
                background: previewGroup==='B'?'#f3f4f6':'#fff',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              Group B
            </button>
          </div>
        </div>
      )}
      
      {/* Content based on view mode */}
      {viewMode === 'analytics' ? (
        /* Analytics Table */
        <div style={{ border: '1px solid #F3F4F6', borderRadius: 6, overflow: 'hidden', maxHeight: '50vh', overflowY: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead style={{ position: 'sticky', top: 0, background: '#f8f9fa', zIndex: 10 }}>
              <tr>
                <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #e5e7eb', fontWeight: 600 }}>Metric</th>
                <th style={{ textAlign: 'center', padding: '8px', borderBottom: '1px solid #e5e7eb', fontWeight: 600 }}>Group A</th>
                <th style={{ textAlign: 'center', padding: '8px', borderBottom: '1px solid #e5e7eb', fontWeight: 600 }}>Group B</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', fontWeight: 500 }}>Count</td>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', textAlign: 'center' }}>{analyticsA.count}</td>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', textAlign: 'center' }}>{analyticsB.count}</td>
              </tr>
              <tr>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', fontWeight: 500 }}>Mean Height</td>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', textAlign: 'center' }}>{analyticsA.meanHeight}m</td>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', textAlign: 'center' }}>{analyticsB.meanHeight}m</td>
              </tr>
              <tr>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', fontWeight: 500 }}>Avg Year</td>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', textAlign: 'center' }}>{analyticsA.avgYear}</td>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', textAlign: 'center' }}>{analyticsB.avgYear}</td>
              </tr>
              <tr>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', fontWeight: 500 }}>Mean Surface Area</td>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', textAlign: 'center' }}>{analyticsA.meanSurfaceArea}m²</td>
                <td style={{ padding: '8px', borderBottom: '1px solid #F3F4F6', textAlign: 'center' }}>{analyticsB.meanSurfaceArea}m²</td>
              </tr>
              <tr>
                <td style={{ padding: '8px', fontWeight: 500 }}>Usage Distribution</td>
                <td style={{ padding: '8px', textAlign: 'center' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 2, fontSize: 10 }}>
                    {Object.entries(analyticsA.usageDistribution).map(([usage, count]) => (
                      <div key={usage} style={{ color: '#666' }}>
                        {usage}: {Math.round((count / analyticsA.count) * 100)}%
                      </div>
                    ))}
                  </div>
                </td>
                <td style={{ padding: '8px', textAlign: 'center' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 2, fontSize: 10 }}>
                    {Object.entries(analyticsB.usageDistribution).map(([usage, count]) => (
                      <div key={usage} style={{ color: '#666' }}>
                        {usage}: {Math.round((count / analyticsB.count) * 100)}%
                      </div>
                    ))}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      ) : (
        /* Data Review Table */
        <div style={{ maxHeight: '50vh', overflowY: 'auto', border: '1px solid #F3F4F6', borderRadius: 6 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead style={{ position: 'sticky', top: 0, background: '#f8f9fa', zIndex: 10 }}>
              <tr>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: '4px' }}>ID</th>
                <th style={{ textAlign: 'right', borderBottom: '1px solid #e5e7eb', padding: '4px' }}>Height</th>
                <th style={{ textAlign: 'right', borderBottom: '1px solid #e5e7eb', padding: '4px' }}>Year</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: '4px' }}>Usage</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb', padding: '4px' }}>Type</th>
              </tr>
            </thead>
            <tbody>
              {(previewGroup === 'A' ? splitGroups.A : splitGroups.B).map((id) => {
                const row = features.find(f => String(f.id) === String(id));
                return (
                  <tr key={String(id)}>
                    <td style={{ padding: '4px', borderBottom: '1px solid #F3F4F6' }}>{String(id)}</td>
                    <td style={{ padding: '4px', borderBottom: '1px solid #F3F4F6', textAlign: 'right' }}>{row?.height ?? ''}</td>
                    <td style={{ padding: '4px', borderBottom: '1px solid #F3F4F6', textAlign: 'right' }}>{row?.year ?? ''}</td>
                    <td style={{ padding: '4px', borderBottom: '1px solid #F3F4F6' }}>{row?.usage_category ?? row?.usage_type ?? ''}</td>
                    <td style={{ padding: '4px', borderBottom: '1px solid #F3F4F6' }}>{row?.building_type ?? ''}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Footer text */}
      <div style={{ fontSize: 10, color: '#6B7280', textAlign: 'center' }}>
        Values computed on the current split sample.
      </div>
    </div>
  );
};

// Map Selection Panel Component
const MapSelectionPanel: React.FC<{
  selectedIds: (string | number)[];
  onApply: () => void;
  onSave: () => void;
  onRemoveBuilding: (id: string | number) => void;
  suggestedName: string;
  onNameChange: (name: string) => void;
}> = ({ selectedIds, onRemoveBuilding, suggestedName, onNameChange }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ padding: '12px', background: '#f8f9fa', borderRadius: 8, border: '1px solid #e9ecef' }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: 600, color: '#333' }}>
          Select Buildings from Map
        </h3>
        
        {selectedIds.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#333', marginBottom: 4 }}>
              Batch Name:
            </label>
            <input
              type="text"
              value={suggestedName}
              onChange={(e) => onNameChange(e.target.value)}
              placeholder="Enter batch name..."
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #ddd',
                borderRadius: 4,
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#2196F3';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#ddd';
              }}
            />
          </div>
        )}
      </div>
      
      {selectedIds.length > 0 && (
        <div style={{ padding: '12px', background: '#e8f5e8', borderRadius: 6, border: '1px solid #c8e6c9' }}>
          <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 600, color: '#2e7d32' }}>
            Selected Buildings ({selectedIds.length})
          </h4>
          <div style={{ maxHeight: '120px', overflowY: 'auto' }}>
            {selectedIds.slice(0, 10).map((id) => (
              <div 
                key={id} 
                style={{ 
                  padding: '4px 8px', 
                  fontSize: '12px', 
                  color: '#2e7d32',
                  backgroundColor: 'rgba(76, 175, 80, 0.1)',
                  borderRadius: 3,
                  marginBottom: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <span>Building {id}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveBuilding(id);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#d32f2f',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    padding: '2px 4px',
                    borderRadius: '2px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '16px',
                    height: '16px',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(211, 47, 47, 0.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                  title="Remove building"
                >
                  ×
                </button>
              </div>
            ))}
            {selectedIds.length > 10 && (
              <div style={{ 
                padding: '4px 8px', 
                fontSize: '12px', 
                color: '#666',
                fontStyle: 'italic'
              }}>
                ... and {selectedIds.length - 10} more
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
