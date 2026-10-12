import React from 'react';
import { FiShield, FiLock, FiCheckCircle } from 'react-icons/fi';

const PrivacyBadge = ({ level = 'high', epsilon, delta = '1e-5', showDetails = true }) => {
  const normLevel = level.toLowerCase();

  const configs = {
    high: {
      label: 'Strict DP (High Privacy)',
      color: '#00897b',
      bgColor: '#e0f2f1',
      icon: FiShield,
      description: 'Zero raw patient records leave premises. Gaussian differential privacy mathematically guarantees individual data unlearnability.',
    },
    medium: {
      label: 'Standard DP (Balanced)',
      color: '#1a73e8',
      bgColor: '#e8f0fe',
      icon: FiLock,
      description: 'Differential privacy enabled with relaxed epsilon for higher predictive convergence speed.',
    },
    low: {
      label: 'Relaxed DP (High Accuracy Focus)',
      color: '#fb8c00',
      bgColor: '#fff3e0',
      icon: FiCheckCircle,
      description: 'Aggregated gradients with minimal perturbation noise.',
    },
  };

  const current = configs[normLevel] || configs.high;
  const Icon = current.icon;

  return (
    <div className="privacy-badge-container" title={current.description}>
      <span
        className="privacy-badge"
        style={{ color: current.color, backgroundColor: current.bgColor, borderColor: current.color }}
      >
        <Icon className="privacy-badge-icon" />
        <span className="privacy-badge-text">{current.label}</span>
        {epsilon !== undefined && (
          <span className="privacy-badge-epsilon">ε = {epsilon}</span>
        )}
      </span>
      {showDetails && (
        <span className="privacy-guarantee-note">
          <small>Protected via (ε={epsilon || 0.85}, δ={delta})</small>
        </span>
      )}
    </div>
  );
};

export default PrivacyBadge;
