import React from 'react';

const LoadingSpinner = ({ size = 'medium', message = 'Loading federated data...' }) => {
  return (
    <div className="spinner-container">
      <div className={`spinner spinner-${size}`}></div>
      {message && <p className="spinner-message">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;
