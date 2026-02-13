import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { createPortal } from 'react-dom';
import routes from '../../constants/routes.json';
import { clearGraph } from '../../slices/rfGraphSlice';
import { clearComposites } from '../../slices/compositeModelsSlice';
import { hydrateAssignments } from '../../slices/assignmentsSlice';

interface BreadcrumbNavigationProps {
  scenarioName?: string;
  projectId?: string;
  projectName?: string;
}

const BreadcrumbNavigation: React.FC<BreadcrumbNavigationProps> = ({ 
  scenarioName = "baselineDemo", 
  projectId = "projid", 
  projectName = "projname" 
}) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });

  // Mock scenarios data - in real app this would come from props or API
  const scenarios = [
    { id: 'scenario1', name: 'baselineDemo', isActive: true },
    { id: 'scenario2', name: 'energyOptimization', isActive: false },
    { id: 'scenario3', name: 'sustainabilityPlan', isActive: false },
    { id: 'scenario4', name: 'costAnalysis', isActive: false }
  ];

  const handleScenarioSelect = (scenario: any) => {
    if (scenario.name !== scenarioName) {
      // Clear workspace when switching scenarios
      dispatch(clearGraph()); // Clear ReactFlow nodes and edges
      dispatch(clearComposites()); // Clear composite models
      dispatch(hydrateAssignments([])); // Clear assignments
      try {
        // Also clear any cached workspace in localStorage used by Node editor
        localStorage.removeItem('reactflow-nodes');
        localStorage.removeItem('reactflow-edges');
      } catch {}
      
      // Navigate to the selected scenario
      navigate(`/inputeditor/${projectId}==${projectName}-sceid==${scenario.name}-inputeditordemo`);
    }
    setIsDropdownOpen(false);
  };

  const handleNewScenario = () => {
    // Navigate to scenarios page to create new scenario with drawer open
    const targetUrl = routes.SCENARIOSDEMO + '?new=true';
    navigate(targetUrl);
    setIsDropdownOpen(false);
  };

  const handleBackToScenarios = () => {
    // Navigate to scenarios page
    navigate(routes.SCENARIOSDEMO);
    setIsDropdownOpen(false);
  };

  // Close dropdown when clicking outside (now handled by backdrop)
  // Removed the old click outside handler since we're using a backdrop

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      marginLeft: '24px',
      position: 'relative'
    }} ref={dropdownRef}>
      {/* Current Scenario Dropdown */}
      <button
        ref={buttonRef}
        onClick={() => {
          if (buttonRef.current) {
            const rect = buttonRef.current.getBoundingClientRect();
            setDropdownPosition({
              top: rect.bottom + window.scrollY + 8,
              left: rect.left + window.scrollX
            });
          }
          setIsDropdownOpen(!isDropdownOpen);
        }}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '8px 16px',
          borderRadius: '8px',
          transition: 'all 0.2s ease',
          fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
          backgroundColor: isDropdownOpen ? '#F3F4F6' : 'transparent'
        }}
        onMouseEnter={(e) => {
          if (!isDropdownOpen) {
            e.currentTarget.style.backgroundColor = '#F8FAFC';
          }
        }}
        onMouseLeave={(e) => {
          if (!isDropdownOpen) {
            e.currentTarget.style.backgroundColor = 'transparent';
          }
        }}
      >
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: '#374151',
          fontSize: '14px',
          fontWeight: '500'
        }}>
          <svg 
            width="16" 
            height="16" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
            style={{ color: '#6366F1' }}
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14,2 14,8 20,8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10,9 9,9 8,9"/>
          </svg>
          <span style={{ color: '#475569' }}>Working on</span>
          <span style={{ 
            color: '#1E293B', 
            fontWeight: '600',
            backgroundColor: '#E0E7FF',
            padding: '4px 12px',
            borderRadius: '6px',
            fontSize: '13px'
          }}>
            {scenarioName}
          </span>
          <svg 
            width="12" 
            height="12" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
            style={{ 
              color: '#6B7280',
              transform: isDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s ease'
            }}
          >
            <path d="m6 9 6 6 6-6"/>
          </svg>
        </div>
      </button>

      {/* Dropdown Menu - Rendered as Portal */}
      {isDropdownOpen && createPortal(
        <>
          {/* Invisible backdrop to capture clicks */}
          <div 
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 2147483646,
              pointerEvents: 'auto'
            }}
            onClick={() => setIsDropdownOpen(false)}
          />
          {/* Dropdown content */}
          <div style={{
            position: 'fixed',
            top: dropdownPosition.top,
            left: dropdownPosition.left,
            backgroundColor: 'white',
            border: '1px solid #E5E7EB',
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
            zIndex: 2147483647,
            minWidth: '280px',
            overflow: 'hidden',
            pointerEvents: 'auto',
            isolation: 'isolate'
          }}>
          {/* Header */}
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid #F3F4F6',
            backgroundColor: '#F8FAFC'
          }}>
            <div style={{
              fontSize: '12px',
              fontWeight: '600',
              color: '#6B7280',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              Available Scenarios
            </div>
          </div>

          {/* Scenario List */}
          <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
            {scenarios.map((scenario) => (
              <button
                key={scenario.id}
                onClick={() => handleScenarioSelect(scenario)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  border: 'none',
                  background: scenario.isActive ? '#F0F9FF' : 'transparent',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s ease',
                  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => {
                  if (!scenario.isActive) {
                    e.currentTarget.style.backgroundColor = '#F9FAFB';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!scenario.isActive) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }
                }}
              >
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: scenario.isActive ? '#3B82F6' : '#D1D5DB'
                }} />
                <div style={{
                  flex: 1,
                  fontSize: '14px',
                  fontWeight: scenario.isActive ? '600' : '500',
                  color: scenario.isActive ? '#1E40AF' : '#374151'
                }}>
                  {scenario.name}
                </div>
                {scenario.isActive && (
                  <svg 
                    width="16" 
                    height="16" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                    style={{ color: '#3B82F6' }}
                  >
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                )}
              </button>
            ))}
          </div>

          {/* Divider */}
          <div style={{
            height: '1px',
            backgroundColor: '#F3F4F6',
            margin: '4px 0'
          }} />

          {/* New Scenario Button */}
          <button
            onClick={handleNewScenario}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '12px 16px',
              border: 'none',
              background: 'transparent',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease',
              fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
              textAlign: 'left'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F0FDF4';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: '#10B981',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg 
                width="4" 
                height="4" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="3" 
                strokeLinecap="round" 
                strokeLinejoin="round"
                style={{ color: 'white' }}
              >
                <path d="M12 5v14M5 12h14"/>
              </svg>
            </div>
            <div style={{
              flex: 1,
              fontSize: '14px',
              fontWeight: '600',
              color: '#059669'
            }}>
              New Scenario
            </div>
            <svg 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
              style={{ color: '#059669' }}
            >
              <path d="M7 17L17 7M17 7H7M17 7v10"/>
            </svg>
          </button>

          {/* Back to Scenarios Button */}
          <button
            onClick={handleBackToScenarios}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '12px 16px',
              border: 'none',
              background: 'transparent',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease',
              fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
              textAlign: 'left'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F0FDF4';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: '#10B981'
            }} />
            <div style={{
              flex: 1,
              fontSize: '14px',
              fontWeight: '600',
              color: '#059669'
            }}>
              Back to Scenarios
            </div>
            <svg 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
              style={{ color: '#059669' }}
            >
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
          </button>
        </div>
        </>,
        document.body
      )}
    </div>
  );
};

export default BreadcrumbNavigation;
