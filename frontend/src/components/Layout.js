import React from 'react';
import Navbar from './Navbar';

const Layout = ({ children }) => {
  return (
    <div className="app-layout">
      <Navbar />
      <main className="main-content">
        <header className="top-banner">
          <div className="system-health-indicator">
            <span className="node-status-indicator active"></span>
            <span className="network-status-text">Federated Network: <strong>Online</strong> (14 Hospital Nodes Connected)</span>
          </div>
          <div className="encryption-pill">
            <span className="shield-icon">🛡️</span> End-to-End Homomorphic & DP Aggregation
          </div>
        </header>
        <div className="content-container">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
