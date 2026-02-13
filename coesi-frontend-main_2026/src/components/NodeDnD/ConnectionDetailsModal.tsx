import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';

interface ConnectionDetailsModalProps {
  visible: boolean;
  onClose: () => void;
  sourceModelName: string;
  sourcePort: string;
  targetModelName: string;
  targetPort: string;
  connectionType?: string;
  onConnectionTypeChange?: (type: string) => void;
  onDeleteConnection?: () => void;
}

const ConnectionDetailsModal: React.FC<ConnectionDetailsModalProps> = ({
  visible,
  onClose,
  sourceModelName,
  sourcePort,
  targetModelName,
  targetPort,
  connectionType: initialConnectionType = 'Same Time',
  onConnectionTypeChange,
  onDeleteConnection,
}) => {
  const [connectionType, setConnectionType] = useState(initialConnectionType);

  useEffect(() => {
    setConnectionType(initialConnectionType);
  }, [initialConnectionType]);

  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newType = e.target.value;
    setConnectionType(newType);
    onConnectionTypeChange?.(newType);
  };

  if (!visible) return null;

  return createPortal(
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 10000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'white',
          borderRadius: 8,
          width: 500,
          maxWidth: '90vw',
          boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)',
          position: 'relative',
          animation: 'fadeIn 0.3s ease-out forwards',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="modal-close"
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 10,
            right: 10,
            background: 'none',
            border: 'none',
            fontSize: 20,
            cursor: 'pointer',
          }}
        >
          ×
        </button>

        <div style={{ padding: 20 }}>
          <h1 style={{ fontSize: 25, fontWeight: 'bold', marginBottom: 20 }}>
            Connection Details
          </h1>

          <div style={{ marginBottom: 20 }}>
            <div style={{ marginBottom: 12 }}>
              <label
                style={{
                  display: 'block',
                  fontSize: 14,
                  fontWeight: 600,
                  color: '#374151',
                  marginBottom: 6,
                }}
              >
                From
              </label>
              <div
                style={{
                  padding: 12,
                  background: '#f9fafb',
                  borderRadius: 4,
                  border: '1px solid #e5e7eb',
                }}
              >
                <div style={{ fontWeight: 600, color: '#1f2937' }}>
                  {sourceModelName}
                </div>
                <div style={{ fontSize: 13, color: '#6b7280', marginTop: 4 }}>
                  Output: {sourcePort}
                </div>
              </div>
            </div>

            <div style={{ marginBottom: 12 }}>
              <label
                style={{
                  display: 'block',
                  fontSize: 14,
                  fontWeight: 600,
                  color: '#374151',
                  marginBottom: 6,
                }}
              >
                To
              </label>
              <div
                style={{
                  padding: 12,
                  background: '#f9fafb',
                  borderRadius: 4,
                  border: '1px solid #e5e7eb',
                }}
              >
                <div style={{ fontWeight: 600, color: '#1f2937' }}>
                  {targetModelName}
                </div>
                <div style={{ fontSize: 13, color: '#6b7280', marginTop: 4 }}>
                  Input: {targetPort}
                </div>
              </div>
            </div>

            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: 14,
                  fontWeight: 600,
                  color: '#374151',
                  marginBottom: 6,
                }}
              >
                Type
              </label>
              <select
                value={connectionType}
                onChange={handleTypeChange}
                style={{
                  width: '100%',
                  height: 40,
                  padding: '8px 12px',
                  border: '1px solid #53ab8b',
                  borderRadius: 4,
                  fontSize: 14,
                  backgroundColor: 'white',
                  color: 'black',
                  cursor: 'pointer',
                  transition: 'border-color 0.3s ease',
                }}
                onFocus={(e) => {
                  e.target.style.outline = 'none';
                  e.target.style.borderColor = '#1a1a1a';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#53ab8b';
                }}
              >
                <option value="Same Time">Same Time</option>
                <option value="Next Time">Next Time</option>
              </select>
            </div>
          </div>

          <div
            style={{
              marginTop: 20,
              display: 'flex',
              justifyContent: 'flex-end',
              gap: 10,
            }}
          >
            <button
              onClick={() => {
                onDeleteConnection?.();
              }}
              style={{
                height: 40,
                padding: '8px 16px',
                color: 'white',
                background: '#ef4444',
                border: 'none',
                cursor: 'pointer',
                borderRadius: 4,
                transition: 'opacity 0.3s ease',
                fontSize: 14,
                fontWeight: 500,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '0.9';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '1';
              }}
              title="Remove this connection"
            >
              Remove connection
            </button>
            <button
              className="modal-confirm-button"
              onClick={onClose}
              style={{
                height: 40,
                padding: '8px 16px',
                color: 'white',
                background: '#53ab8b',
                border: 'none',
                cursor: 'pointer',
                borderRadius: 4,
                transition: 'opacity 0.3s ease',
                fontSize: 14,
                fontWeight: 500,
              }}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default ConnectionDetailsModal;

