import React, { useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../../main';
import {
  setDrawerOpen,
  setActiveTab,
  setWorkingIds,
  setWorkingSource,
  setWorkingRule,
  resetWorking,
  addAssignment,
} from '../../slices/assignmentsSlice';

const AssignmentsDrawer: React.FC<{ scenarioId: string }> = ({ scenarioId }) => {
  const dispatch = useDispatch();
  const open = useSelector((s: RootState) => s.assignments.drawerOpen);
  const activeTab = useSelector((s: RootState) => s.assignments.activeTab);
  const working = useSelector((s: RootState) => s.assignments.working);
  const selectedIds = useSelector((s: RootState) => s.selectedFeatures.selectedFeatures);
  const rfNodes = useSelector((s: RootState) => s.rfGraph.nodes);
  const assignments = useSelector((s: RootState) => s.assignments.assignments);

  if (!open) return null;

  const tabs = ['Select', 'Filter', 'Random', 'Stratified', 'Split', 'Preview & Save'];

  const onClose = () => dispatch(setDrawerOpen(false));

  const onUseSelection = () => {
    const uniq = Array.from(new Set(selectedIds));
    dispatch(setWorkingIds(uniq));
    dispatch(setWorkingSource('map'));
    dispatch(setActiveTab('Preview & Save'));
  };

  const canSave = (working.ids?.length || 0) > 0;

  const defaultName = useMemo(() => {
    const d = new Date();
    const pad = (n: number) => String(n).padStart(2, '0');
    return `Buildings-${working.source || 'map'}-${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}`;
  }, [working.source]);

  const onSave = () => {
    if (!canSave) return;
    const name = defaultName;
    if (assignments.some(a => a.name.toLowerCase() === name.toLowerCase())) return;
    dispatch(addAssignment({ id: `${Date.now()}`, name, entityType: 'building', ids: working.ids, count: working.ids.length, createdAt: new Date().toISOString(), rule: { source: working.source || 'map', ...working.rule } } as any));
    dispatch(setDrawerOpen(false));
    dispatch(resetWorking());
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      onKeyDown={(e) => { if (e.key === 'Escape') onClose(); }}
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        height: '100vh',
        width: 460,
        background: '#fff',
        borderLeft: '1px solid #e5e7eb',
        boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
        zIndex: 20000,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 12, borderBottom: '1px solid #e5e7eb' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <img src="/icons/assign.svg" alt="Assignments" width={18} height={18} />
          <div style={{ fontWeight: 700 }}>Assignments manager</div>
        </div>
        <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: 18, cursor: 'pointer' }}>×</button>
      </div>

      {/* Helper */}
      <div style={{ padding: '8px 12px', fontSize: 12, color: '#374151', borderBottom: '1px solid #f3f4f6' }}>
        Bind entities to a node via Map selection / Filter / Random / Stratified / Split. We store the rule and the resolved IDs for reproducibility.
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, padding: '8px 12px', borderBottom: '1px solid #e5e7eb' }}>
        {tabs.map(t => (
          <button key={t} onClick={() => dispatch(setActiveTab(t))} style={{ border: '1px solid #e5e7eb', background: activeTab === t ? '#f3f4f6' : '#fff', borderRadius: 8, padding: '6px 10px', fontSize: 12, cursor: 'pointer' }}>{t}</button>
        ))}
      </div>

      {/* Body */}
      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: 12 }}>
        {activeTab === 'Select' && (
          <div>
            <div style={{ marginBottom: 8, fontSize: 13 }}>{selectedIds.length} building{selectedIds.length === 1 ? '' : 's'} selected on map</div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={onUseSelection} style={{ border: '1px solid #2563EB', background: '#2563EB', color: 'white', borderRadius: 8, padding: '6px 10px', fontSize: 13 }}>Use selection</button>
              <button onClick={() => dispatch(require('../../slices/selectedFeaturesSlice').deleteSelectedFeature())} style={{ border: '1px solid #e5e7eb', background: '#fff', borderRadius: 8, padding: '6px 10px', fontSize: 13 }}>Clear selection</button>
            </div>
          </div>
        )}

        {activeTab === 'Filter' && (
          <div>
            <div style={{ fontSize: 12, marginBottom: 8, color: '#6B7280' }}>Simple demo filter: height {'>'} 0 will include all current buildings in dataset.</div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={() => { dispatch(setWorkingIds(selectedIds)); dispatch(setWorkingSource('filter')); dispatch(setWorkingRule({ filters: [{ attr: 'height', op: '>', val: 0 }] })); dispatch(setActiveTab('Preview & Save')); }} style={{ border: '1px solid #2563EB', background: '#2563EB', color: 'white', borderRadius: 8, padding: '6px 10px', fontSize: 13 }}>Apply filter</button>
              <button onClick={() => dispatch(resetWorking())} style={{ border: '1px solid #e5e7eb', background: '#fff', borderRadius: 8, padding: '6px 10px', fontSize: 13 }}>Reset</button>
            </div>
          </div>
        )}

        {activeTab === 'Preview & Save' && (
          <div>
            <div style={{ marginBottom: 8, fontSize: 13 }}>{working.ids.length} buildings in working set</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 10 }}>
              {working.ids.slice(0, 10).map((id) => (
                <span key={String(id)} style={{ fontSize: 11, background: '#F3F4F6', border: '1px solid #E5E7EB', padding: '2px 6px', borderRadius: 999 }}>{String(id)}</span>
              ))}
              {working.ids.length > 10 && (
                <span style={{ fontSize: 11, color: '#6B7280' }}>+{working.ids.length - 10} more</span>
              )}
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button disabled={!canSave} onClick={onSave} style={{ opacity: canSave ? 1 : 0.5, border: '1px solid #2563EB', background: '#2563EB', color: 'white', borderRadius: 8, padding: '6px 10px', fontSize: 13 }}>Save</button>
              <button onClick={() => dispatch(resetWorking())} style={{ border: '1px solid #e5e7eb', background: '#fff', borderRadius: 8, padding: '6px 10px', fontSize: 13 }}>Reset</button>
            </div>
          </div>
        )}

        {['Random','Stratified','Split'].includes(activeTab) && (
          <div style={{ fontSize: 12, color: '#6B7280' }}>Scaffold ready. I can wire Random/Stratified/Split next with seedable sampling and node pickers.</div>
        )}
      </div>
    </div>
  );
};

export default AssignmentsDrawer;


