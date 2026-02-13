import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ReactFlowErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ReactFlow Error Boundary caught an error:', error, errorInfo);
    
    // Check if this is a frozen object error
    if (error.message.includes('Cannot assign to read only property')) {
      console.error('🚨 FROZEN OBJECT ERROR DETECTED!');
      console.error('This is likely caused by Redux middleware freezing objects.');
      console.error('Check that all nodes/edges are properly cloned before passing to ReactFlow.');
    }
  }

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div style={{
          padding: '20px',
          border: '2px solid #ff6b6b',
          borderRadius: '8px',
          backgroundColor: '#ffe0e0',
          color: '#d63031',
          margin: '20px',
          textAlign: 'center'
        }}>
          <h3>ReactFlow Error</h3>
          <p>Something went wrong with the node editor.</p>
          <details style={{ marginTop: '10px', textAlign: 'left' }}>
            <summary>Error Details</summary>
            <pre style={{ 
              marginTop: '10px', 
              padding: '10px', 
              backgroundColor: '#f8f9fa', 
              borderRadius: '4px',
              fontSize: '12px',
              overflow: 'auto'
            }}>
              {this.state.error?.message}
            </pre>
          </details>
          <button 
            onClick={() => this.setState({ hasError: false, error: undefined })}
            style={{
              marginTop: '10px',
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ReactFlowErrorBoundary;





