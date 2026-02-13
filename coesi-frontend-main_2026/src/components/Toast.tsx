import React, { useEffect, useState } from 'react';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ 
  message, 
  type = 'success', 
  duration = 1000, 
  onClose 
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);

  useEffect(() => {
    // Show toast immediately
    setIsVisible(true);
    
    // Start leaving animation after duration
    const leaveTimer = setTimeout(() => {
      setIsLeaving(true);
    }, duration);

    // Remove from DOM after animation
    const removeTimer = setTimeout(() => {
      onClose();
    }, duration + 300); // 300ms for animation

    return () => {
      clearTimeout(leaveTimer);
      clearTimeout(removeTimer);
    };
  }, [duration, onClose]);

  const getToastStyles = () => {
    const baseStyles = {
      position: 'fixed' as const,
      top: '20px',
      right: '20px',
      zIndex: 9999,
      padding: '16px 20px',
      borderRadius: '8px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      color: 'white',
      fontWeight: '500',
      fontSize: '14px',
      maxWidth: '300px',
      wordWrap: 'break-word' as const,
      transform: isVisible && !isLeaving ? 'translateX(0)' : 'translateX(100%)',
      opacity: isVisible && !isLeaving ? 1 : 0,
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
    };

    switch (type) {
      case 'success':
        return {
          ...baseStyles,
          background: 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)',
        };
      case 'error':
        return {
          ...baseStyles,
          background: 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)',
        };
      case 'info':
        return {
          ...baseStyles,
          background: 'linear-gradient(135deg, #2196F3 0%, #1976D2 100%)',
        };
      case 'warning':
        return {
          ...baseStyles,
          background: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
        };
      default:
        return baseStyles;
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return (
          <div style={{
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
          }}>
            ✓
          </div>
        );
      case 'error':
        return (
          <div style={{
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
          }}>
            ✕
          </div>
        );
      case 'info':
        return (
          <div style={{
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
          }}>
            i
          </div>
        );
      case 'warning':
        return (
          <div style={{
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
          }}>
            !
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div style={getToastStyles()}>
      {getIcon()}
      <span>{message}</span>
    </div>
  );
};

export default Toast;













