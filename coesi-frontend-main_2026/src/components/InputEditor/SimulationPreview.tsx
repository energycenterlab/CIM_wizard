import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiService } from '../../services/api';
import SimulationResults from './SimulationResults';

interface SimulationPreviewProps {
  onComplete: () => void;
  onModalToggle?: (isOpen: boolean) => void;
  simulationState: {
    currentStep: number;
    isComplete: boolean;
    isModalOpen: boolean;
  };
  setSimulationState: React.Dispatch<React.SetStateAction<{
    currentStep: number;
    isComplete: boolean;
    isModalOpen: boolean;
  }>>;
  // Callbacks for each step
  onPreflight?: () => Promise<void>;
  onBuildScenario?: () => Promise<{ jsonData: any }>;
  onGenerateConfig?: (jsonData: any) => Promise<{ yamlContent: string; filename: string }>;
  onSubmitJob?: (yamlContent: string, filename: string) => Promise<{ simulationId: string }>;
}

interface TypewriterTextProps {
  text: string;
}

const TypewriterText: React.FC<TypewriterTextProps> = ({ text }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timer = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, 50);

      return () => clearTimeout(timer);
    }
  }, [currentIndex, text]);

  return (
    <div style={{
      margin: 0,
      fontSize: '12px',
      color: '#64748b',
      lineHeight: '1.4',
      minHeight: '16px',
      textAlign: 'left',
      width: '100%',
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'flex-start'
    }}>
      <span style={{
        whiteSpace: 'normal',
        wordWrap: 'break-word',
        overflow: 'hidden'
      }}>
        {displayedText}
        <span style={{
          animation: 'blink 1s infinite',
          marginLeft: '2px'
        }}>|</span>
      </span>
    </div>
  );
};

interface SimulationStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  active: boolean;
  failed: boolean;
  errorMessage?: string;
}

const SimulationPreview: React.FC<SimulationPreviewProps> = ({ 
  onComplete, 
  onModalToggle, 
  simulationState, 
  setSimulationState,
  onPreflight,
  onBuildScenario,
  onGenerateConfig,
  onSubmitJob
}) => {
  const [currentStep, setCurrentStep] = useState(simulationState.currentStep);
  const [steps, setSteps] = useState<SimulationStep[]>([
    {
      id: 'preflight',
      title: 'Preflight',
      description: 'Validate required connections, port types/units, and timeseries CSV mapping.',
      completed: false,
      active: false,
      failed: false
    },
    {
      id: 'build',
      title: 'Build Scenario',
      description: 'Freeze the current canvas and assemble the scenario JSON from nodes/edges/settings.',
      completed: false,
      active: false,
      failed: false
    },
    {
      id: 'config',
      title: 'Generate Config',
      description: 'Convert scenario JSON to the engine YAML/config bundle.',
      completed: false,
      active: false,
      failed: false
    },
    {
      id: 'submit',
      title: 'Submit Job',
      description: 'Create the run, get a Job ID, move to queued/runnable state.',
      completed: false,
      active: false,
      failed: false
    },
    {
      id: 'execute',
      title: 'Execute Simulation',
      description: 'Engine runs the models; show live percent/log tickers.',
      completed: false,
      active: false,
      failed: false
    },
    {
      id: 'process',
      title: 'Process Outputs',
      description: 'Gather artifacts (HDF5/CSV/logs), compute quick metrics.',
      completed: false,
      active: false,
      failed: false
    },
    {
      id: 'prepare',
      title: 'Prepare Results',
      description: 'Build a results manifest for charts/tables and cache previews.',
      completed: false,
      active: false,
      failed: false
    }
  ]);

  const [isViewResultsEnabled, setIsViewResultsEnabled] = useState(false);
  const [showResultsModal, setShowResultsModal] = useState(simulationState.isModalOpen);
  const [isCancelEnabled, setIsCancelEnabled] = useState(true); // Enabled during preflight
  const [isSimulationComplete, setIsSimulationComplete] = useState(simulationState.isComplete);
  const [simulationId, setSimulationId] = useState<string | null>(null);
  const [scenarioName, setScenarioName] = useState<string | null>(null);
  
  const abortControllerRef = useRef<AbortController | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const stepDataRef = useRef<{ jsonData?: any; yamlContent?: string; yamlFilename?: string }>({});
  const stepExecutionRef = useRef<{ [key: number]: boolean }>({}); // Track which steps have been executed
  const lastSyncedStateRef = useRef({ currentStep: -1, isModalOpen: false, isComplete: false });

  // Sync local state with persistent state (only when props actually change)
  useEffect(() => {
    const propsChanged = 
      lastSyncedStateRef.current.currentStep !== simulationState.currentStep ||
      lastSyncedStateRef.current.isModalOpen !== simulationState.isModalOpen ||
      lastSyncedStateRef.current.isComplete !== simulationState.isComplete;

    if (propsChanged) {
      if (currentStep !== simulationState.currentStep) {
    setCurrentStep(simulationState.currentStep);
      }
      if (showResultsModal !== simulationState.isModalOpen) {
    setShowResultsModal(simulationState.isModalOpen);
      }
      if (isSimulationComplete !== simulationState.isComplete) {
    setIsSimulationComplete(simulationState.isComplete);
      }
      // Update ref to track what we last synced from props
      lastSyncedStateRef.current = {
        currentStep: simulationState.currentStep,
        isModalOpen: simulationState.isModalOpen,
        isComplete: simulationState.isComplete
      };
    }
  }, [simulationState.currentStep, simulationState.isModalOpen, simulationState.isComplete, currentStep, showResultsModal, isSimulationComplete]);

  // Update persistent state when local state changes (only if values actually changed and didn't come from props)
  useEffect(() => {
    // Don't update if local state matches props (means we just synced from props)
    if (
      currentStep === simulationState.currentStep &&
      showResultsModal === simulationState.isModalOpen &&
      isSimulationComplete === simulationState.isComplete
    ) {
      // Update ref to match current state
      lastSyncedStateRef.current = {
        currentStep,
        isModalOpen: showResultsModal,
        isComplete: isSimulationComplete
      };
      return;
    }

    // Only update if local state is different from what we last synced
    const localChanged = 
      lastSyncedStateRef.current.currentStep !== currentStep ||
      lastSyncedStateRef.current.isModalOpen !== showResultsModal ||
      lastSyncedStateRef.current.isComplete !== isSimulationComplete;

    if (localChanged) {
      setSimulationState(prev => {
        // Only update if values actually changed
        if (
          prev.currentStep === currentStep &&
          prev.isModalOpen === showResultsModal &&
          prev.isComplete === isSimulationComplete
        ) {
          return prev; // Return same object to prevent re-render
        }
        return {
      ...prev,
      currentStep,
      isModalOpen: showResultsModal,
      isComplete: isSimulationComplete
        };
      });
      // Update ref to track what we last synced
      lastSyncedStateRef.current = {
        currentStep,
        isModalOpen: showResultsModal,
        isComplete: isSimulationComplete
      };
    }
  }, [currentStep, showResultsModal, isSimulationComplete, setSimulationState, simulationState.currentStep, simulationState.isModalOpen, simulationState.isComplete]);

  // Reset execution flags when starting a new simulation (currentStep resets to 0)
  useEffect(() => {
    if (currentStep === 0 && !isSimulationComplete) {
      // Reset all execution flags when starting fresh
      stepExecutionRef.current = {};
      stepDataRef.current = {};
      setSimulationId(null);
    }
  }, [currentStep, isSimulationComplete]);

  // Mark all steps as completed if simulation is already complete
  useEffect(() => {
    if (isSimulationComplete) {
      setSteps(prev => prev.map(step => ({
        ...step,
        active: false,
        completed: true
      })));
      setIsViewResultsEnabled(true);
      setIsCancelEnabled(false);
    }
  }, [isSimulationComplete]);

  // Update step status helper
  const updateStep = useCallback((stepIndex: number, updates: Partial<SimulationStep>) => {
    setSteps(prev => prev.map((step, index) => 
      index === stepIndex ? { ...step, ...updates } : step
    ));
  }, []);

  // Move to next step helper
  const moveToNextStep = useCallback((stepIndex: number) => {
    if (stepIndex < steps.length - 1) {
      setCurrentStep(stepIndex + 1);
    } else {
      // All steps completed
      setSteps(prev => prev.map(step => ({
        ...step,
        active: false,
        completed: true
      })));
      setIsSimulationComplete(true);
    }
  }, [steps.length]);

  // Handle step failure
  const handleStepFailure = useCallback((stepIndex: number, error: Error) => {
    updateStep(stepIndex, {
      active: false,
      failed: true,
      errorMessage: error.message
    });
    // Stop the flow
    setIsCancelEnabled(false);
  }, [updateStep]);

  // Step 0: Preflight (4 seconds, cancel enabled)
  useEffect(() => {
    if (currentStep === 0 && !isSimulationComplete && !showResultsModal && !stepExecutionRef.current[0]) {
      stepExecutionRef.current[0] = true;
        setIsCancelEnabled(true);
      updateStep(0, { active: true, completed: false, failed: false });

      const startTime = Date.now();
      const minDuration = 4000; // 4 seconds

      const runPreflight = async () => {
        try {
          if (onPreflight) {
            await onPreflight();
          }
          
          const elapsed = Date.now() - startTime;
          const remaining = Math.max(0, minDuration - elapsed);
          
          await new Promise(resolve => setTimeout(resolve, remaining));
          
          // Disable cancel after preflight
        setIsCancelEnabled(false);
          moveToNextStep(0);
        } catch (error) {
          stepExecutionRef.current[0] = false;
          handleStepFailure(0, error as Error);
        }
      };

      runPreflight();
    }
  }, [currentStep, isSimulationComplete, showResultsModal, onPreflight, updateStep, moveToNextStep, handleStepFailure]);

  // Step 1: Build Scenario (at least 3 seconds or actual time)
  useEffect(() => {
    if (currentStep === 1 && !isSimulationComplete && !showResultsModal && !stepExecutionRef.current[1]) {
      stepExecutionRef.current[1] = true;
      updateStep(1, { active: true, completed: false, failed: false });

      const startTime = Date.now();
      const minDuration = 4000; // 4 seconds minimum

      const runBuildScenario = async () => {
        try {
          if (!onBuildScenario) {
            throw new Error('Build scenario callback not provided');
          }

          const result = await onBuildScenario();
          stepDataRef.current.jsonData = result.jsonData;
          
          const elapsed = Date.now() - startTime;
          const remaining = Math.max(0, minDuration - elapsed);
          
          await new Promise(resolve => setTimeout(resolve, remaining));
          
          updateStep(1, { completed: true, active: false });
          moveToNextStep(1);
        } catch (error) {
          stepExecutionRef.current[1] = false;
          handleStepFailure(1, error as Error);
        }
      };

      runBuildScenario();
    }
  }, [currentStep, isSimulationComplete, showResultsModal, onBuildScenario, updateStep, moveToNextStep, handleStepFailure]);

  // Step 2: Generate Config (at least 3 seconds or actual time)
  useEffect(() => {
    if (currentStep === 2 && !isSimulationComplete && !showResultsModal && !stepExecutionRef.current[2]) {
      stepExecutionRef.current[2] = true;
      updateStep(2, { active: true, completed: false, failed: false });

      const startTime = Date.now();
      const minDuration = 4000; // 4 seconds minimum

      const runGenerateConfig = async () => {
        try {
          if (!onGenerateConfig || !stepDataRef.current.jsonData) {
            throw new Error('Generate config callback not provided or JSON data missing');
          }

          const result = await onGenerateConfig(stepDataRef.current.jsonData);
          stepDataRef.current.yamlContent = result.yamlContent;
          stepDataRef.current.yamlFilename = result.filename;
          
          const elapsed = Date.now() - startTime;
          const remaining = Math.max(0, minDuration - elapsed);
          
          await new Promise(resolve => setTimeout(resolve, remaining));
          
          updateStep(2, { completed: true, active: false });
          moveToNextStep(2);
        } catch (error) {
          stepExecutionRef.current[2] = false;
          handleStepFailure(2, error as Error);
        }
      };

      runGenerateConfig();
    }
  }, [currentStep, isSimulationComplete, showResultsModal, onGenerateConfig, updateStep, moveToNextStep, handleStepFailure]);

  // Step 3: Submit Job (at least 3 seconds or actual time)
  useEffect(() => {
    if (currentStep === 3 && !isSimulationComplete && !showResultsModal && !stepExecutionRef.current[3]) {
      // Mark step as executing to prevent duplicate runs
      stepExecutionRef.current[3] = true;
      
      updateStep(3, { active: true, completed: false, failed: false });

      const startTime = Date.now();
      const minDuration = 4000; // 4 seconds minimum

      const runSubmitJob = async () => {
        try {
          if (!onSubmitJob || !stepDataRef.current.yamlContent || !stepDataRef.current.yamlFilename) {
            throw new Error('Submit job callback not provided or YAML data missing');
          }

          // Upload YAML to scenario manager
          const uploadResult = await apiService.uploadScenarioYAML(
            stepDataRef.current.yamlContent,
            stepDataRef.current.yamlFilename
          );
          
          const scenarioNameWithoutExt = uploadResult.filename.replace(/\.(yaml|yml)$/, '');
          setScenarioName(scenarioNameWithoutExt);

          // Start simulation
          const simResult = await apiService.startSimulation(scenarioNameWithoutExt);
          setSimulationId(simResult.simulation_id);
          
          const elapsed = Date.now() - startTime;
          const remaining = Math.max(0, minDuration - elapsed);
          
          await new Promise(resolve => setTimeout(resolve, remaining));
          
          updateStep(3, { completed: true, active: false });
          moveToNextStep(3);
        } catch (error) {
          // Reset execution flag on error so it can be retried
          stepExecutionRef.current[3] = false;
          handleStepFailure(3, error as Error);
        }
      };

      runSubmitJob();
    }
  }, [currentStep, isSimulationComplete, showResultsModal, onSubmitJob, updateStep, moveToNextStep, handleStepFailure]);

  // Step 4: Execute Simulation (at least 3 seconds, then show progress)
  useEffect(() => {
    if (currentStep === 4 && !isSimulationComplete && !showResultsModal && !stepExecutionRef.current[4]) {
      stepExecutionRef.current[4] = true;
      updateStep(4, { active: true, completed: false, failed: false });

      const startTime = Date.now();
      const minDuration = 4000; // 4 seconds minimum

      const runExecute = async () => {
        try {
          // Wait minimum duration
          const elapsed = Date.now() - startTime;
          const remaining = Math.max(0, minDuration - elapsed);
          await new Promise(resolve => setTimeout(resolve, remaining));
          
          updateStep(4, { completed: true, active: false });
          moveToNextStep(4);
        } catch (error) {
          stepExecutionRef.current[4] = false;
          handleStepFailure(4, error as Error);
        }
      };

      runExecute();
    }
  }, [currentStep, isSimulationComplete, showResultsModal, updateStep, moveToNextStep, handleStepFailure]);

  // Step 5: Process Outputs (poll simulation status)
  useEffect(() => {
    if (currentStep === 5 && !isSimulationComplete && !showResultsModal && simulationId && !stepExecutionRef.current[5]) {
      stepExecutionRef.current[5] = true;
      updateStep(5, { active: true, completed: false, failed: false });

      const pollStatus = async () => {
        try {
          const poll = async () => {
            if (!simulationId) return;

            const status = await apiService.getSimulationStatus(simulationId);
            
            if (status.status === 'completed') {
              // Stop polling
              if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
                pollingIntervalRef.current = null;
              }
              
              updateStep(5, { completed: true, active: false });
              moveToNextStep(5);
            } else if (status.status === 'failed') {
              // Stop polling
              if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
                pollingIntervalRef.current = null;
              }
              
              stepExecutionRef.current[5] = false;
              handleStepFailure(5, new Error(status.error_message || 'Simulation failed'));
            }
            // If still running, continue polling
          };

          // Poll immediately, then every 2 seconds
          await poll();
          pollingIntervalRef.current = setInterval(poll, 2000);
        } catch (error) {
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          stepExecutionRef.current[5] = false;
          handleStepFailure(5, error as Error);
        }
      };

      pollStatus();

      // Cleanup on unmount
      return () => {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      };
    }
  }, [currentStep, isSimulationComplete, showResultsModal, simulationId, updateStep, moveToNextStep, handleStepFailure]);

  // Step 6: Prepare Results (2 seconds wait before enabling results button)
  useEffect(() => {
    if (currentStep === 6 && !isSimulationComplete && !showResultsModal && !stepExecutionRef.current[6]) {
      stepExecutionRef.current[6] = true;
      updateStep(6, { active: true, completed: false, failed: false });

      const prepareResults = async () => {
        try {
          // Wait 2 seconds
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          updateStep(6, { completed: true, active: false });
          setIsViewResultsEnabled(true);
          setIsSimulationComplete(true);
        } catch (error) {
          stepExecutionRef.current[6] = false;
          handleStepFailure(6, error as Error);
        }
      };

      prepareResults();
    }
  }, [currentStep, isSimulationComplete, showResultsModal, updateStep, handleStepFailure]);


  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const handleCancel = async () => {
    if (!isCancelEnabled) return;

    try {
      // Abort any ongoing operations
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      // Stop simulation if it's running
      if (simulationId) {
        try {
          await apiService.stopSimulation(simulationId);
        } catch (e) {
          console.warn('Failed to stop simulation:', e);
        }
      }

      // Stop polling
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }

    onComplete();
    } catch (error) {
      console.error('Error cancelling simulation:', error);
      onComplete();
    }
  };

  const handleViewResults = () => {
    setShowResultsModal(true);
    onModalToggle?.(true);
    setCurrentStep(steps.length);
    setIsSimulationComplete(true);
  };

  const handleCloseResultsModal = () => {
    setShowResultsModal(false);
    onModalToggle?.(false);
    onComplete();
  };

  return (
    <div style={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      background: '#f8fafc'
    }}>
      {/* Header Section */}
      <div style={{ 
        height: '8vh',
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        borderBottom: '1px solid #e2e8f0',
        padding: '8px',
        background: 'rgba(255, 255, 255, 0.9)'
      }}>
        <h2 style={{ 
          margin: 0, 
          color: '#1e293b',
          fontSize: '18px',
          fontWeight: '600',
          display: 'flex',
          alignItems: 'center',
          gap: '4px'
        }}>
          {isSimulationComplete ? 'Simulation completed successfully' : 'Simulation is in progress'}
          {!isSimulationComplete && (
            <div style={{
              display: 'flex',
              gap: '2px',
              marginLeft: '4px'
            }}>
              <div style={{
                width: '4px',
                height: '4px',
                borderRadius: '50%',
                backgroundColor: '#10b981',
                animation: 'loadingDot1 1.4s infinite ease-in-out'
              }}></div>
              <div style={{
                width: '4px',
                height: '4px',
                borderRadius: '50%',
                backgroundColor: '#10b981',
                animation: 'loadingDot2 1.4s infinite ease-in-out',
                animationDelay: '0.2s'
              }}></div>
              <div style={{
                width: '4px',
                height: '4px',
                borderRadius: '50%',
                backgroundColor: '#10b981',
                animation: 'loadingDot3 1.4s infinite ease-in-out',
                animationDelay: '0.4s'
              }}></div>
            </div>
          )}
        </h2>
      </div>

      {/* Progress Section */}
      {!showResultsModal && (
      <div style={{ 
        height: '72vh',
        overflowY: 'auto',
        padding: '0',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          width: '100%',
          height: '100%',
          position: 'relative',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px'
        }}>
          {steps.map((step, index) => {
            const stepHeight = 100;
            const centerIndex = currentStep;
            const relativePosition = index - centerIndex;
            
            if (Math.abs(relativePosition) > 2) return null;
            
            let opacity = 1;
            if (Math.abs(relativePosition) === 2) {
              opacity = 0.4;
            } else if (Math.abs(relativePosition) === 1) {
              opacity = 0.65;
            } else {
              opacity = 1;
            }
            
            // Determine step color based on state
            let stepColor = '#e5e7eb'; // default gray
            if (step.failed) {
              stepColor = '#ef4444'; // red for failed
            } else if (step.completed) {
              stepColor = '#10b981'; // green for completed
            } else if (step.active) {
              stepColor = '#3b82f6'; // blue for active
            }

            let stepStyle: React.CSSProperties = {
              position: 'absolute',
              width: '300px',
              height: `${stepHeight}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
              transform: `translateY(${relativePosition * stepHeight}px)`,
              opacity: opacity,
              zIndex: relativePosition === 0 ? 10 : 5
            };

            if (step.completed) {
              stepStyle.opacity = opacity;
              stepStyle.transform = `translateY(${relativePosition * stepHeight - 20}px) scale(0.95)`;
            }

            return (
              <div key={step.id} style={stepStyle}>
                <div style={{
                  width: '100%',
                  height: '80px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: step.failed ? 'rgba(239, 68, 68, 0.1)' : 'rgba(255, 255, 255, 0.8)',
                  borderRadius: '12px',
                  border: step.failed ? '1px solid #ef4444' : '1px solid #e2e8f0',
                  boxShadow: relativePosition === 0 ? '0 4px 12px rgba(0, 0, 0, 0.1)' : '0 2px 6px rgba(0, 0, 0, 0.05)',
                  transition: 'all 0.3s ease',
                  position: 'relative',
                  paddingLeft: '20px'
                }}>
                  {/* Step Number/Status Circle */}
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    position: 'absolute',
                    left: '-20px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: stepColor,
                    transition: 'all 0.3s ease',
                    zIndex: 15,
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
                  }}>
                    {step.failed ? (
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="white"/>
                      </svg>
                    ) : step.completed ? (
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" fill="white"/>
                      </svg>
                    ) : step.active ? (
                      <div style={{
                        width: '14px',
                        height: '14px',
                        borderRadius: '50%',
                        background: '#3b82f6',
                        animation: 'pulse 2s infinite'
                      }}></div>
                    ) : (
                      <span style={{
                        fontSize: '14px',
                        fontWeight: 'bold',
                        color: '#6b7280'
                      }}>
                        {index + 1}
                      </span>
                    )}
                  </div>

                  {/* Step Title */}
                  <div style={{ 
                    flex: 1,
                    height: '60px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: step.completed || step.failed ? 'center' : 'flex-start',
                    alignItems: 'center'
                  }}>
                    <h3 style={{
                      margin: 0,
                      fontSize: '16px',
                      fontWeight: '600',
                      color: step.failed ? '#ef4444' : step.completed ? '#10b981' : step.active ? '#3b82f6' : '#6b7280',
                      transition: 'color 0.3s ease',
                      textAlign: 'center',
                      height: step.completed || step.failed ? 'auto' : '20px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      {step.title}
                    </h3>
                    {step.failed && step.errorMessage && (
                      <div style={{
                        fontSize: '11px',
                        color: '#ef4444',
                        marginTop: '4px',
                        textAlign: 'center',
                        padding: '0 8px'
                      }}>
                        {step.errorMessage}
                      </div>
                    )}
                    {step.active && !step.failed && (
                      <div style={{
                        height: '40px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '100%'
                      }}>
                        <div style={{
                          fontSize: '12px',
                          color: '#64748b',
                          lineHeight: '1.4',
                          textAlign: 'left',
                          width: '280px',
                          minHeight: '32px',
                          maxHeight: '48px',
                          display: 'flex',
                          alignItems: 'flex-start',
                          justifyContent: 'flex-start',
                          overflow: 'hidden',
                          border: '1px solid transparent',
                          paddingLeft: '8px',
                          paddingTop: '4px'
                        }}>
                          <TypewriterText text={step.description} />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      )}

      {/* Action Section */}
      <div style={{ 
        height: '20vh',
        display: 'flex', 
        alignItems: 'flex-start', 
        justifyContent: 'center',
        borderTop: '1px solid #e2e8f0',
        padding: '12px 12px 0 12px',
        background: 'rgba(255, 255, 255, 0.9)',
        gap: '12px'
      }}>
          <button
            onClick={isCancelEnabled ? handleCancel : undefined}
            disabled={!isCancelEnabled}
            style={{
              background: isCancelEnabled ? '#ef4444' : '#9ca3af',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: isCancelEnabled ? 'pointer' : 'not-allowed',
              transition: 'background-color 0.2s',
              opacity: isCancelEnabled ? 1 : 0.6
            }}
            onMouseEnter={(e) => {
              if (isCancelEnabled) {
                e.currentTarget.style.background = '#dc2626';
              }
            }}
            onMouseLeave={(e) => {
              if (isCancelEnabled) {
                e.currentTarget.style.background = '#ef4444';
              }
            }}
          >
            Cancel
          </button>
          <button
            onClick={isViewResultsEnabled ? handleViewResults : undefined}
            disabled={!isViewResultsEnabled}
            style={{
              background: isViewResultsEnabled ? '#10b981' : '#9ca3af',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: isViewResultsEnabled ? 'pointer' : 'not-allowed',
              transition: 'background-color 0.2s',
              opacity: isViewResultsEnabled ? 1 : 0.6
            }}
            onMouseEnter={(e) => {
              if (isViewResultsEnabled) {
                e.currentTarget.style.background = '#059669';
              }
            }}
            onMouseLeave={(e) => {
              if (isViewResultsEnabled) {
                e.currentTarget.style.background = '#10b981';
              }
            }}
          >
            {isViewResultsEnabled ? 'View Results' : 'In Progress'}
          </button>
      </div>

      <style>{`
        @keyframes loadingDot1 {
          0%, 80%, 100% {
            transform: scale(0);
            opacity: 0.5;
          }
          40% {
            transform: scale(1);
            opacity: 1;
          }
        }
        @keyframes loadingDot2 {
          0%, 80%, 100% {
            transform: scale(0);
            opacity: 0.5;
          }
          40% {
            transform: scale(1);
            opacity: 1;
          }
        }
        @keyframes loadingDot3 {
          0%, 80%, 100% {
            transform: scale(0);
            opacity: 0.5;
          }
          40% {
            transform: scale(1);
            opacity: 1;
          }
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.5;
            transform: scale(1.1);
          }
        }

        @keyframes blink {
          0%, 50% {
            opacity: 1;
          }
          51%, 100% {
            opacity: 0;
          }
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>

      {/* Results Modal */}
      {showResultsModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}>
          <div style={{
            width: '100%',
            height: '100%',
            backgroundColor: 'white',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative'
          }}>
            {/* Modal Header */}
            <div style={{
              padding: '20px',
              borderBottom: '1px solid #e2e8f0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <h2 style={{
                margin: 0,
                color: '#1e293b',
                fontSize: '24px',
                fontWeight: '600'
              }}>
                Simulation Results
              </h2>
              <button
                onClick={handleCloseResultsModal}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '24px',
                  cursor: 'pointer',
                  color: '#64748b',
                  padding: '4px',
                  borderRadius: '4px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f1f5f9';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                ×
              </button>
            </div>

            {/* Modal Content */}
            <div style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              padding: '0'
            }}>
              {simulationId ? (
                <SimulationResults
                  simulationId={simulationId}
                  scenarioName={scenarioName || undefined}
                />
              ) : (
              <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '60px 20px',
                color: '#64748b',
                  fontSize: '16px'
              }}>
                  <p>No simulation results available.</p>
              </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationPreview;
