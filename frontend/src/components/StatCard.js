import React from 'react';
import { FiTrendingUp, FiTrendingDown } from 'react-icons/fi';

const StatCard = ({ title, value, icon: Icon, change, changeType = 'positive', color = '#1a73e8', subtitle }) => {
  return (
    <div className="stat-card" style={{ borderTop: `4px solid ${color}` }}>
      <div className="stat-card-header">
        <div className="stat-card-info">
          <span className="stat-card-title">{title}</span>
          <h3 className="stat-card-value">{value}</h3>
        </div>
        {Icon && (
          <div className="stat-card-icon-wrapper" style={{ backgroundColor: `${color}18`, color: color }}>
            <Icon className="stat-card-icon" />
          </div>
        )}
      </div>
      
      {(change !== undefined || subtitle) && (
        <div className="stat-card-footer">
          {change !== undefined && (
            <span className={`stat-card-change ${changeType === 'positive' ? 'positive' : 'negative'}`}>
              {changeType === 'positive' ? <FiTrendingUp /> : <FiTrendingDown />}
              {change}
            </span>
          )}
          {subtitle && <span className="stat-card-subtitle">{subtitle}</span>}
        </div>
      )}
    </div>
  );
};

export default StatCard;
