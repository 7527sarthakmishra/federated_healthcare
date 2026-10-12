import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  FiGrid,
  FiHome,
  FiUsers,
  FiActivity,
  FiShare2,
  FiBarChart2,
  FiFileText,
  FiSettings,
  FiLogOut,
  FiShield,
  FiMenu,
  FiX
} from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: FiGrid },
    { name: 'Hospitals', path: '/hospitals', icon: FiHome },
    { name: 'Patient Records', path: '/patients', icon: FiUsers },
    { name: 'Disease Prediction', path: '/predictions', icon: FiActivity },
    { name: 'Federated Training', path: '/federated', icon: FiShare2 },
    { name: 'Analytics', path: '/analytics', icon: FiBarChart2 },
    // Only show Audit Logs for admin role
    ...(user?.role === 'admin'
      ? [{ name: 'Audit Logs', path: '/audit', icon: FiFileText }]
      : []),
    { name: 'Settings', path: '/settings', icon: FiSettings },
  ];

  return (
    <>
      {/* Mobile Toggle Button */}
      <button 
        className="mobile-menu-toggle"
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label="Toggle navigation"
      >
        {mobileOpen ? <FiX size={24} /> : <FiMenu size={24} />}
      </button>

      {/* Backdrop */}
      {mobileOpen && (
        <div 
          className="sidebar-backdrop" 
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Main Sidebar */}
      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-icon-wrapper">
            <FiShield className="brand-icon" />
          </div>
          <div className="brand-text">
            <h2>FedHealth</h2>
            <span>Privacy Learning</span>
          </div>
        </div>

        <div className="sidebar-security-badge">
          <span className="dot-pulse"></span>
          <span>DP Guard Active (ε=0.85)</span>
        </div>

        <nav className="sidebar-nav">
          <ul>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      isActive ? 'nav-link active' : 'nav-link'
                    }
                    onClick={() => setMobileOpen(false)}
                  >
                    <Icon className="nav-icon" />
                    <span>{item.name}</span>
                  </NavLink>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar">
              {(user?.username || 'User').slice(0, 2).toUpperCase()}
            </div>
            <div className="user-details">
              <span className="user-name">{user?.username || 'Dr. Researcher'}</span>
              <span className="user-role">{user?.role || 'Clinician'}</span>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="logout-button"
            title="Log out of platform"
          >
            <FiLogOut className="logout-icon" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Navbar;
