import React, { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../../main';
import {
  addAssignment,
  clearDraft,
  setDraftActive,
  setDraftError,
  setDraftIds,
  setDraftName,
  hydrateAssignments,
} from '../../slices/assignmentsSlice';
import { deleteSelectedFeature, removeSelectedFeature, normalizeSelectedFeatures } from '../../slices/selectedFeaturesSlice';

const formatDefaultName = () => {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  const yyyy = d.getFullYear();
  const mm = pad(d.getMonth() + 1);
  const dd = pad(d.getDate());
  const hh = pad(d.getHours());
  const mi = pad(d.getMinutes());
  return `Buildings-${yyyy}-${mm}-${dd}-${hh}${mi}`;
};

const storageKey = (scenarioId: string) => `scenario:${scenarioId}:assignments`;

const AssignmentManager: React.FC<{ scenarioId: string; onNavigateToAssignments?: () => void }> = ({ scenarioId, onNavigateToAssignments }) => {
  const dispatch = useDispatch();
  const draft = useSelector((s: RootState) => s.assignments.draft);
  const assignments = useSelector((s: RootState) => s.assignments.assignments);
  const _selectedIds = useSelector((s: RootState) => s.selectedFeatures.selectedFeatures);
  const selectedIds: (string | number)[] = Array.isArray(_selectedIds) ? _selectedIds : [];
  const [hoveredBuildingId, setHoveredBuildingId] = useState<string | number | null>(null);

  // hydrate on first mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(storageKey(scenarioId));
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) dispatch(hydrateAssignments(parsed));
      }
    } catch {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scenarioId]);

  // normalize selected features to ensure they are all string IDs
  useEffect(() => {
    dispatch(normalizeSelectedFeatures());
  }, [dispatch]);

  // keep draft ids in sync with map selection
  useEffect(() => {
    const unique = Array.from(new Set(selectedIds));
    dispatch(setDraftIds(unique));
    dispatch(setDraftActive(unique.length > 0 || !!draft.name));
    if (!draft.name && unique.length > 0) {
      dispatch(setDraftName(formatDefaultName()));
    }
  }, [selectedIds]);

  // persist assignments on change
  useEffect(() => {
    try {
      localStorage.setItem(storageKey(scenarioId), JSON.stringify(assignments));
    } catch {}
  }, [assignments, scenarioId]);

  const isNameValid = useMemo(() => {
    const n = (draft.name || '').trim();
    if (n.length < 3 || n.length > 48) return false;
    const exists = assignments.some(a => a.name.toLowerCase() === n.toLowerCase());
    if (exists) return false;
    return true;
  }, [draft.name, assignments]);

  const onSave = () => {
    if (!draft.ids.length || !isNameValid) return;
    const name = draft.name.trim();
    const assignment = {
      id: `${Date.now()}`,
      name,
      entityType: 'building' as const,
      ids: draft.ids,
      count: draft.ids.length,
      createdAt: new Date().toISOString(),
    };
    dispatch(addAssignment(assignment));
    // clear map selection
    dispatch(deleteSelectedFeature());
    // clear draft and close
    dispatch(clearDraft());
    // Navigate to assignments view
    if (onNavigateToAssignments) {
      onNavigateToAssignments();
    }
  };

  const onClear = () => {
    dispatch(deleteSelectedFeature());
    dispatch(clearDraft());
  };

  const onCancel = () => {
    dispatch(setDraftActive(false));
    dispatch(setDraftError(undefined));
  };

  const onRemoveBuilding = (buildingId: string | number) => {
    // Remove from both selected features and draft IDs
    dispatch(removeSelectedFeature(String(buildingId)));
    // Also directly update draft IDs to ensure immediate UI update
    const updatedDraftIds = draft.ids.filter(id => String(id) !== String(buildingId));
    dispatch(setDraftIds(updatedDraftIds));
  };

  if (!draft.active) return null;

  const idsPreview = draft.ids.slice(0, 5);
  const remaining = Math.max(0, draft.ids.length - idsPreview.length);

  return (
    <div
      aria-modal
      role="dialog"
      style={{
        position: 'absolute',
        top: 16,
        left: 16,
        zIndex: 12000,
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          pointerEvents: 'auto',
          backdropFilter: 'saturate(120%) blur(4px)',
          background: 'rgba(255,255,255,0.9)',
          border: '1px solid rgba(0,0,0,0.08)',
          borderRadius: 16,
          boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
          width: 320,
          padding: 12,
          animation: 'am-fade 150ms ease-out',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <div style={{ fontWeight: 700 }}>Assignment manager</div>
        </div>

        <div style={{ fontSize: 12, color: '#374151', marginBottom: 6 }}>
          {draft.ids.length} building{draft.ids.length === 1 ? '' : 's'} selected
        </div>
        {idsPreview.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
            {idsPreview.map((id) => (
              <span 
                key={String(id)} 
                style={{ 
                  fontSize: 11, 
                  background: hoveredBuildingId === id ? '#E5E7EB' : '#F3F4F6', 
                  border: '1px solid #E5E7EB', 
                  padding: '2px 6px', 
                  borderRadius: 999,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s'
                }}
                onMouseEnter={() => setHoveredBuildingId(id)}
                onMouseLeave={() => setHoveredBuildingId(null)}
              >
                {String(id)}
                {hoveredBuildingId === id && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      e.preventDefault();
                      onRemoveBuilding(id);
                    }}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '2px',
                      margin: '0',
                      fontSize: '12px',
                      color: '#DC2626',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '16px',
                      height: '16px',
                      borderRadius: '50%',
                      transition: 'background-color 0.2s',
                      zIndex: 1,
                      position: 'relative'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#FEE2E2';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                    title="Remove building"
                  >
                    ×
                  </button>
                )}
              </span>
            ))}
            {remaining > 0 && (
              <span style={{ fontSize: 11, color: '#6B7280' }}>+{remaining} more</span>
            )}
          </div>
        )}

        <div style={{ marginBottom: 8 }}>
          <label style={{ display: 'block', fontSize: 12, color: '#374151', marginBottom: 4 }}>Name</label>
          <input
            value={draft.name}
            onChange={(e) => dispatch(setDraftName(e.target.value))}
            placeholder="Assignment name"
            style={{ width: '100%', padding: '8px 10px', borderRadius: 8, border: '1px solid #E5E7EB', fontSize: 13 }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && draft.ids.length && isNameValid) onSave();
              if (e.key === 'Escape') onCancel();
            }}
          />
          {!isNameValid && (
            <div style={{ color: '#DC2626', fontSize: 11, marginTop: 4 }}>
              Name must be 3–48 chars and unique.
            </div>
          )}
        </div>

        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button 
            onClick={onCancel} 
            style={{ 
              border: '1px solid #E5E7EB', 
              background: 'white', 
              color: '#111827', 
              borderRadius: 8, 
              padding: '6px 10px', 
              fontSize: 13,
              cursor: 'pointer',
              transition: 'background-color 0.2s, border-color 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F9FAFB';
              e.currentTarget.style.borderColor = '#D1D5DB';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
              e.currentTarget.style.borderColor = '#E5E7EB';
            }}
          >
            Cancel
          </button>
          <button 
            onClick={onClear} 
            style={{ 
              border: '1px solid #E5E7EB', 
              background: 'white', 
              color: '#111827', 
              borderRadius: 8, 
              padding: '6px 10px', 
              fontSize: 13,
              cursor: 'pointer',
              transition: 'background-color 0.2s, border-color 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F9FAFB';
              e.currentTarget.style.borderColor = '#D1D5DB';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
              e.currentTarget.style.borderColor = '#E5E7EB';
            }}
          >
            Clear
          </button>
          <button 
            disabled={!draft.ids.length || !isNameValid} 
            onClick={onSave} 
            style={{ 
              opacity: (!draft.ids.length || !isNameValid) ? 0.5 : 1, 
              border: '1px solid #000000', 
              background: '#000000', 
              color: 'white', 
              borderRadius: 8, 
              padding: '6px 12px', 
              fontSize: 13,
              cursor: (!draft.ids.length || !isNameValid) ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s, border-color 0.2s'
            }}
            onMouseEnter={(e) => {
              if (!(!draft.ids.length || !isNameValid)) {
                e.currentTarget.style.backgroundColor = '#333333';
                e.currentTarget.style.borderColor = '#333333';
              }
            }}
            onMouseLeave={(e) => {
              if (!(!draft.ids.length || !isNameValid)) {
                e.currentTarget.style.backgroundColor = '#000000';
                e.currentTarget.style.borderColor = '#000000';
              }
            }}
          >
            Save
          </button>
        </div>

        <div style={{ marginTop: 6, fontSize: 11, color: '#6B7280' }}>
          Saved batches appear in Assignments. You can bind them to models later.
        </div>
      </div>

      <style>{`@keyframes am-fade{from{opacity:0; transform: translateY(-4px)} to{opacity:1; transform: translateY(0)}}`}</style>
    </div>
  );
};

export default AssignmentManager;





