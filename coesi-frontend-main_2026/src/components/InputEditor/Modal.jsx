import React from 'react';
import './Modal.css';

const Modal = ({ visible, onCancel, onConfirm, children, title, confirmLoading, footer=true, maxWidth="800px", maxHeight="700px" }) => {
  if (!visible) return null;

  const handleOutsideClick = (e) => {
    if (e.target.className === 'modal-overlay') {
      onCancel();
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: maxWidth, maxHeight: maxHeight }}>
      <button className="modal-close" onClick={onCancel}>X</button>

        <h1>{title}</h1>
        <div className="modal-body">
          {children}
        </div>

        {footer && (
          <div className="modal-buttons">
          <button 
            className="modal-cancel-button" 
            onClick={onCancel} 
          >
            Cancel
          </button>
          <button 
          className="modal-confirm-button" 
          onClick={onConfirm} 
          disabled={confirmLoading} 
          >
          Confirm
        </button>
        </div>
        )}
      </div>
    </div>
  );
};

export default Modal;