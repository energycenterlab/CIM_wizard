import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useDnD } from './DnDContext';
import { instantiateComposite } from '../../utils/compositeHelpers';
import { deleteComposite } from '../../slices/compositeModelsSlice';
import { useToast } from '../../contexts/ToastContext';
import { removeAssignment } from '../../slices/assignmentsSlice';
import './SidebarLeft.css';
import { loadModels } from '../../utils/localModelStore';
import { coesiModelService } from '../../services/coesiModels';
import { setGraph } from '../../slices/rfGraphSlice';
import AssignmentsView from '../InputEditor/AssignmentsView';

const SidebarLeft = ({ setNodes, setEdges }) => {
  const [_, setType] = useDnD();
  const dispatch = useDispatch();
  const { showToast } = useToast();
  
  // State for confirmation dialogs
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [itemToDelete, setItemToDelete] = useState(null);
  
  // State for assignment manager popup
  const [showAssignmentManager, setShowAssignmentManager] = useState(false);
  
  // Dispatch events when assignment manager opens/closes
  useEffect(() => {
    if (showAssignmentManager) {
      window.dispatchEvent(new CustomEvent('assignment-manager-opened'));
    } else {
      window.dispatchEvent(new CustomEvent('assignment-manager-closed'));
    }
  }, [showAssignmentManager]);
  
  // Get composite models from Redux store
  const compositeModels = useSelector((state) => state.compositeModels?.composites || []);
  // Also get current graph so we can push composites via Redux
  const rfNodes = useSelector((state) => state.rfGraph.nodes);
  const rfEdges = useSelector((state) => state.rfGraph.edges);

  // Load custom and COESI models (real sources)
  const projectId = 'defaultProject';
  const [customModels, setCustomModels] = useState([]);
  const [coesiModels, setCoesiModels] = useState([]);
  const [isLoadingModels, setIsLoadingModels] = useState(true);
  
  useEffect(() => {
    const loadAllModels = async () => {
      try {
        setIsLoadingModels(true);
        const userModels = loadModels(projectId);
        const response = await coesiModelService.getModels();
        const coesiModelNames = response.models.map(m => ({ name: m.name }));
        const names = new Set();
        const merged = [];
        for (const x of [...coesiModelNames, ...userModels.map(m => ({ name: m.name }))]) {
          if (!names.has(x.name)) { names.add(x.name); merged.push(x); }
        }
        setCustomModels(merged);
        setCoesiModels(response.models);
      } catch (error) {
        console.error('Failed to load COESI models:', error);
        const userModels = loadModels(projectId);
        setCustomModels(userModels.map(m => ({ name: m.name })));
        setCoesiModels([]);
      } finally {
        setIsLoadingModels(false);
      }
    };
    loadAllModels();
  }, []);

  const iconPathFor = (modelName) => {
    try {
      const name = String(modelName || '').toLowerCase();
      const m = (coesiModels || []).find((mm) => (mm?.name || '').toLowerCase() === name);
      let key = String(m?.ui_schema?.icon || '').toLowerCase();
      // Normalize synonyms and fall back to heuristics if missing
      if (!key) {
        if (name.includes('weather') || name.includes('cloud')) key = 'cloud';
        else if (name.includes('battery')) key = 'battery';
        else if (name.includes('building') || name.includes('home')) key = 'home';
        else if (name.includes('pv') || name.includes('solar') || name.includes('sun')) key = 'sun';
        else if (name.includes('power') || name.includes('node') || name.includes('zap')) key = 'zap';
        else if (name.includes('heat') || name.includes('pump') || name.includes('thermo')) key = 'thermometer';
        else if (name.includes('schedule') || name.includes('cube')) key = 'cube';
        else key = 'other';
      }
      if (key === 'power' || key === 'powernode' || key === 'zap' || key === 'bolt') key = 'zap';
      if (key === 'cloud' || key === 'weather') key = 'cloud';
      switch (key) {
        case 'cube': return '/icons/cube.svg';
        case 'cloud': return '/icons/weather.svg';
        case 'zap': return '/icons/zap.svg';
        case 'home': return '/icons/home.svg';
        case 'battery': return '/icons/battery.svg';
        case 'sun': return '/icons/sun.svg';
        case 'thermometer': return '/icons/thermometer.svg';
        default: return '/icons/other.svg';
      }
    } catch { return '/icons/other.svg'; }
  };

  const onDragStart = (event, nodeType) => {
    setType(nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const handleCompositeClick = (composite) => {
    const origin = { x: 200, y: 200 };
    const { nodes: newNodes, edges: newEdges } = instantiateComposite(composite, origin);
    const nextNodes = [...rfNodes, ...newNodes];
    const nextEdges = [...rfEdges, ...newEdges];
    dispatch(setGraph({ nodes: nextNodes, edges: nextEdges }));
    if (setNodes) setNodes(nextNodes);
    if (setEdges) setEdges(nextEdges);
    showToast && showToast('Composite added to workspace', 'success', 1500);
  };

  const handleDeleteComposite = (composite, event) => {
    event.stopPropagation();
    setItemToDelete({ type: 'composite', id: composite.id, name: composite.name });
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (itemToDelete) {
      if (itemToDelete.type === 'composite') {
        dispatch(deleteComposite(itemToDelete.id));
        showToast(`Composite "${itemToDelete.name}" deleted successfully`, 'success', 2500);
      } else if (itemToDelete.type === 'assignment') {
        dispatch(removeAssignment(itemToDelete.id));
        showToast(`Assignment "${itemToDelete.name}" deleted successfully`, 'success', 2500);
      }
    }
    setShowDeleteDialog(false);
    setItemToDelete(null);
  };

  const cancelDelete = () => {
    setShowDeleteDialog(false);
    setItemToDelete(null);
  };

  // Loading indicator component
  const LoadingIndicator = () => (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      color: '#666',
      fontSize: '14px',
      fontWeight: '500'
    }}>
      <span style={{ marginRight: '8px' }}>Loading models</span>
      <div style={{
        display: 'flex',
        gap: '2px'
      }}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: '#DFF900',
              animation: `loadingDots 1.4s infinite ease-in-out both`,
              animationDelay: `${i * 0.16}s`
            }}
          />
        ))}
      </div>
    </div>
  );

  return (
  <aside
    style={{
      maxWidth: "310px",     
      width: "310px",
      height:"100%",        
      padding: "10px",
      borderRight: "1px solid #ccc", 
      backgroundColor: "white",
      display: 'grid',
      gridTemplateRows: '40% 30% 30%',
      minHeight: 0,
      alignItems:"stretch",
      rowGap: '0'
    }}
    className="sidebar-left-root"
  >
    {/* Models Section */}
    <div
      data-testid="sidebar-models"
      style={{
        overflow: 'hidden',
        minHeight: '220px',
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
      }}
    >
      <div className="sidebar-section-header" style={{ margin: '4px 0' }}>Models</div>
      <div style={{
        flex: 1,
        minHeight: 0,
        overflowY: 'auto',
        scrollbarWidth: 'none',
        msOverflowStyle: 'none',
        padding: 0
      }}>
        {isLoadingModels ? (
          <LoadingIndicator />
        ) : (
          <div className="models-grid">
          {customModels.map((model) => (
            <div
              key={model.name}
              onDragStart={(event) => onDragStart(event, model.name)}
              draggable
              className="draggable-node"
              style={{
                width: '100%',
                height: '44px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-start',
                padding: '0 8px',
                border: '1px solid #e0e0e0',
                borderRadius: '6px',
                backgroundColor: '#fff',
                fontWeight: 'bold',
                fontSize: '13px',
                color: '#333',
                cursor: 'grab',
                textTransform: 'none',
                transition: 'all 0.2s ease-in-out',
                boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                textAlign: 'left',
                boxSizing: 'border-box'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f8f9fa';
                e.currentTarget.style.borderColor = '#4A90E2';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(74, 144, 226, 0.15)';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.color = '#4A90E2';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fff';
                e.currentTarget.style.borderColor = '#e0e0e0';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.color = '#333';
              }}
              title={model.name}
            >
              <img src={iconPathFor(model.name)} alt="" style={{ width: 16, height: 16, marginRight: 8, filter: 'grayscale(1) contrast(0) brightness(0)' }} />
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{model.name}</span>
            </div>
          ))}
          </div>
        )}
      </div>
    </div>

    {/* Entity Section */}
    <div
      data-testid="sidebar-assignments"
      style={{
        overflow: 'hidden',
        minHeight: '160px',
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
      }}
    >
      <div className="sidebar-section-header" style={{ margin: '8px 0' }}>Entity</div>
      <div style={{
        flex: 1,
        minHeight: 0,
        overflowY: 'auto',
        scrollbarWidth: 'none',
        msOverflowStyle: 'none',
        padding: 0
      }}>
      <div className="models-grid" style={{ paddingTop: 0 }}>
          {/* Create Entity Button - Always at the top */}
          <button
            onClick={() => setShowAssignmentManager(true)}
            style={{
              width: '100%',
              height: '44px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '0 10px',
              border: '2px dashed #4A90E2',
              borderRadius: '6px',
              backgroundColor: '#f8f9ff',
              fontWeight: 'bold',
              fontSize: '13px',
              color: '#4A90E2',
              cursor: 'pointer',
              textTransform: 'none',
              transition: 'all 0.2s ease-in-out',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
              textAlign: 'center',
              boxSizing: 'border-box',
              position: 'relative',
              overflow: 'visible',
              marginBottom: '8px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#e6f2ff';
              e.currentTarget.style.borderColor = '#2563eb';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(37, 99, 235, 0.15)';
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.color = '#2563eb';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#f8f9ff';
              e.currentTarget.style.borderColor = '#4A90E2';
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.color = '#4A90E2';
            }}
            title="Create Entity"
          >
            <span style={{ fontSize: '16px', marginRight: '8px' }}>+</span>
            <span>Create Entity</span>
          </button>

          {/* Entity List - New entities appear below the Create button */}
          {(() => {
            const assignments = useSelector((state) => state.assignments.assignments) || [];
            useEffect(() => {
              try { localStorage.setItem('scenario:id5678:assignments', JSON.stringify(assignments)); } catch {}
            }, [assignments]);
            return assignments.map((a) => (
              <div
                key={a.id}
                className="draggable-node"
                draggable
                onDragStart={(event) => {
                  setType(`assignment-batch:${a.id}`);
                  event.dataTransfer.effectAllowed = 'move';
                }}
                title={`${a.name} — ${a.count} building IDs`}
                style={{
                  width: '100%',
                  height: '44px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0 10px',
                  border: '1px solid #e0e0e0',
                  borderRadius: '6px',
                  backgroundColor: '#fff',
                  fontWeight: 'bold',
                  fontSize: '13px',
                  color: '#333',
                  cursor: 'grab',
                  transition: 'all 0.2s ease-in-out',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                  boxSizing: 'border-box',
                  position: 'relative',
                  overflow: 'visible',
                  marginBottom: '4px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f8f9fa';
                  e.currentTarget.style.borderColor = '#4A90E2';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(74, 144, 226, 0.15)';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.color = '#4A90E2';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#fff';
                  e.currentTarget.style.borderColor = '#e0e0e0';
                  e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.color = '#333';
                }}
              >
                <span title={a.name} style={{
                  overflow: 'hidden',
                  whiteSpace: 'normal',
                  fontSize: '11px',
                  lineHeight: '14px',
                  flex: 1,
                  marginRight: '8px',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical'
                }}>{a.name}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setItemToDelete({ type: 'assignment', id: a.id, name: a.name });
                    setShowDeleteDialog(true);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#dc3545',
                    cursor: 'pointer',
                    padding: '4px',
                    fontSize: '12px',
                    borderRadius: '3px',
                    flexShrink: 0,
                    width: '20px',
                    height: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  title="Delete assignment"
                >
                  x
                </button>
              </div>
            ));
          })()}
        </div>
      </div>
    </div>

    <div
      data-testid="sidebar-configs"
      style={{
        overflow: 'hidden',
        minHeight: '160px',
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
      }}
    >
      <div className="sidebar-section-header" style={{ margin: '8px 0' }}>Your configuration</div>
      <div style={{
        flex: 1,
        minHeight: 0,
        overflowY: 'auto',
        scrollbarWidth: 'none',
        msOverflowStyle: 'none',
        padding: 0
      }}>
        {compositeModels.length === 0 ? (
          <div style={{
            padding: '12px',
            textAlign: 'center',
            color: '#666',
            fontSize: '14px',
            fontStyle: 'italic'
          }}>
            No saved configurations yet.
          </div>
        ) : (
          compositeModels.map((composite) => (
            <div
              key={composite.id}
              onClick={() => handleCompositeClick(composite)}
              style={{
                width: '100%',
                marginBottom: '8px',
                padding: '12px',
                border: '1px solid #e0e0e0',
                borderRadius: '6px',
                backgroundColor: '#fff',
                cursor: 'pointer',
                position: 'relative',
                transition: 'all 0.2s ease-in-out',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f8f9fa';
                e.currentTarget.style.borderColor = '#28a745';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(40, 167, 69, 0.15)';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.querySelector('div').style.color = '#28a745';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fff';
                e.currentTarget.style.borderColor = '#e0e0e0';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.querySelector('div').style.color = '#333';
              }}
            >
              <div style={{
                flex: 1,
                fontSize: '14px',
                fontWeight: '500',
                color: '#333',
                marginRight: '8px',
                whiteSpace: 'normal',
                overflow: 'hidden',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical'
              }} title={composite.name}>
                {composite.name}
              </div>
              <button
                onClick={(e) => handleDeleteComposite(composite, e)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#dc3545',
                  cursor: 'pointer',
                  padding: '4px',
                  fontSize: '12px',
                  borderRadius: '3px',
                  transition: 'background-color 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f8d7da';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
                title="Delete composite"
              >
                x
              </button>
            </div>
          ))
        )}
      </div>
    </div>
    
    {/* Confirmation Dialog */}
    {showDeleteDialog && (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000
        }}
      >
        <div
          style={{
            pointerEvents: 'auto',
            backdropFilter: 'saturate(120%) blur(4px)',
            background: 'rgba(255,255,255,0.95)',
            border: '1px solid rgba(0,0,0,0.08)',
            borderRadius: 16,
            boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
            padding: 20,
            maxWidth: '400px',
            width: '90%'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <div style={{ fontWeight: 700, fontSize: 16, color: '#111827' }}>
              Delete {itemToDelete?.type === 'composite' ? 'Composite' : 'Assignment'}
            </div>
          </div>
          
          <div style={{ fontSize: 13, color: '#374151', marginBottom: 20, lineHeight: '1.5' }}>
            Are you sure you want to delete the {itemToDelete?.type === 'composite' ? 'composite' : 'assignment'} <strong>"{itemToDelete?.name}"</strong>? This action cannot be undone.
          </div>
          
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <button
              onClick={cancelDelete}
              style={{
                border: '1px solid #E5E7EB',
                background: 'white',
                color: '#111827',
                borderRadius: 8,
                padding: '6px 12px',
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
              onClick={confirmDelete}
              style={{
                border: '1px solid #DC2626',
                background: '#DC2626',
                color: 'white',
                borderRadius: 8,
                padding: '6px 12px',
                fontSize: 13,
                cursor: 'pointer',
                transition: 'background-color 0.2s, border-color 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#B91C1C';
                e.currentTarget.style.borderColor = '#B91C1C';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#DC2626';
                e.currentTarget.style.borderColor = '#DC2626';
              }}
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    )}
    
    {/* Full-screen Assignment Manager Popup */}
    {showAssignmentManager && (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px'
        }}
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            setShowAssignmentManager(false);
          }
        }}
      >
        <div
          style={{
            width: '90%',
            height: '85%',
            backgroundColor: 'white',
            borderRadius: '12px',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}
        >
          {/* Header */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px 20px',
            borderBottom: '1px solid #e5e7eb',
            backgroundColor: '#f9fafb'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <img src="/icons/assign.svg" alt="Assignments" width={24} height={24} />
              <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '700', color: '#111827' }}>
                Create Entity
              </h2>
            </div>
            <button
              onClick={() => setShowAssignmentManager(false)}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: '#6b7280',
                padding: '4px',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '32px',
                height: '32px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f3f4f6';
                e.currentTarget.style.color = '#374151';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = '#6b7280';
              }}
            >
              ×
            </button>
          </div>
          
          {/* Content */}
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <AssignmentsView />
          </div>
        </div>
      </div>
    )}
    </aside>
  );
};

export default SidebarLeft;

