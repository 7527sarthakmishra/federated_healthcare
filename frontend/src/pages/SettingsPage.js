import React, { useState } from 'react';
import {
  FiSettings,
  FiUser,
  FiShield,
  FiBell,
  FiInfo,
  FiSave,
  FiCheck,
  FiLock,
  FiServer
} from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

const SettingsPage = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState({
    username: user?.username || 'Dr. Evelyn Reed',
    email: user?.email || 'evelyn@fedhealth.org',
    hospital: user?.hospital || 'Metro Health General Node'
  });

  const [privacySettings, setPrivacySettings] = useState({
    epsilon_budget: 1.0,
    noise_level: 'Gaussian (σ=1.25)',
    clipping_norm: 1.0,
    enforce_local_dp: true,
    homomorphic_encryption: true
  });

  const [notifications, setNotifications] = useState({
    round_completion: true,
    privacy_budget_warning: true,
    inference_alert: false,
    hospital_sync_fail: true
  });

  const [savedMessage, setSavedMessage] = useState('');

  const handleProfileSubmit = (e) => {
    e.preventDefault();
    setSavedMessage('Profile information updated successfully.');
    setTimeout(() => setSavedMessage(''), 3000);
  };

  const handlePrivacySubmit = (e) => {
    e.preventDefault();
    setSavedMessage('Differential privacy parameters re-calibrated on local node.');
    setTimeout(() => setSavedMessage(''), 3000);
  };

  return (
    <div className="page-container settings-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Platform & Node Settings</h1>
          <p className="page-subtitle">
            Configure institutional identities, differential privacy boundaries, and secure communication preferences.
          </p>
        </div>
      </div>

      {savedMessage && (
        <div className="alert-box alert-success mb-4">
          <FiCheck className="alert-icon" />
          <span>{savedMessage}</span>
        </div>
      )}

      <div className="settings-grid">
        {/* Profile Settings */}
        <div className="card">
          <div className="card-header">
            <div className="header-title-with-icon">
              <FiUser className="mr-2 text-primary" />
              <h3 className="card-title">Hospital Node Profile</h3>
            </div>
            <span className="badge badge-teal">Authenticated</span>
          </div>

          <form onSubmit={handleProfileSubmit} className="card-body">
            <div className="form-group">
              <label>Clinical Investigator / Username</label>
              <input
                type="text"
                value={profile.username}
                onChange={(e) => setProfile({ ...profile, username: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Official Institutional Email</label>
              <input
                type="email"
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Registered Hospital Affiliate</label>
              <input
                type="text"
                value={profile.hospital}
                onChange={(e) => setProfile({ ...profile, hospital: e.target.value })}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary">
              <FiSave style={{ marginRight: '6px' }} /> Update Profile
            </button>
          </form>
        </div>

        {/* Privacy & Cryptography Settings */}
        <div className="card">
          <div className="card-header">
            <div className="header-title-with-icon">
              <FiShield className="mr-2 text-teal" />
              <h3 className="card-title">Differential Privacy Thresholds</h3>
            </div>
            <span className="badge badge-teal">DP-SGD</span>
          </div>

          <form onSubmit={handlePrivacySubmit} className="card-body">
            <div className="form-group">
              <label>Max Epsilon Per Round (ε)</label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="5.0"
                value={privacySettings.epsilon_budget}
                onChange={(e) =>
                  setPrivacySettings({ ...privacySettings, epsilon_budget: Number(e.target.value) })
                }
              />
              <span className="form-hint">Lower values yield stronger mathematical privacy.</span>
            </div>

            <div className="form-group">
              <label>Differential Noise Distribution</label>
              <select
                value={privacySettings.noise_level}
                onChange={(e) => setPrivacySettings({ ...privacySettings, noise_level: e.target.value })}
                className="select-input"
              >
                <option value="Gaussian (σ=1.25)">Gaussian DP (σ=1.25, Recommended)</option>
                <option value="Laplace (b=0.8)">Laplace Mechanism (Pure ε-DP)</option>
                <option value="Gaussian Strict (σ=2.0)">Gaussian Strict (σ=2.0, High Noise)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Gradient L2 Clipping Norm (C)</label>
              <input
                type="number"
                step="0.1"
                min="0.5"
                max="5.0"
                value={privacySettings.clipping_norm}
                onChange={(e) =>
                  setPrivacySettings({ ...privacySettings, clipping_norm: Number(e.target.value) })
                }
              />
            </div>

            <div className="toggle-group mb-3">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={privacySettings.enforce_local_dp}
                  onChange={(e) =>
                    setPrivacySettings({ ...privacySettings, enforce_local_dp: e.target.checked })
                  }
                />
                <span>Enforce Local DP clipping prior to edge weight transmission</span>
              </label>
            </div>

            <button type="submit" className="btn btn-secondary">
              <FiSave style={{ marginRight: '6px' }} /> Save Privacy Policy
            </button>
          </form>
        </div>

        {/* Notification Alerts */}
        <div className="card">
          <div className="card-header">
            <div className="header-title-with-icon">
              <FiBell className="mr-2 text-warning" />
              <h3 className="card-title">Real-Time Health Notifications</h3>
            </div>
          </div>

          <div className="card-body">
            <div className="toggle-list">
              <label className="toggle-item">
                <div>
                  <strong>Federated Round Completion</strong>
                  <p className="text-muted small">Notify when central aggregator finishes merging weights</p>
                </div>
                <input
                  type="checkbox"
                  checked={notifications.round_completion}
                  onChange={(e) =>
                    setNotifications({ ...notifications, round_completion: e.target.checked })
                  }
                />
              </label>

              <label className="toggle-item">
                <div>
                  <strong>Privacy Budget Depletion Warning</strong>
                  <p className="text-muted small">Alert when node consumes &gt; 80% of allocated epsilon</p>
                </div>
                <input
                  type="checkbox"
                  checked={notifications.privacy_budget_warning}
                  onChange={(e) =>
                    setNotifications({ ...notifications, privacy_budget_warning: e.target.checked })
                  }
                />
              </label>

              <label className="toggle-item">
                <div>
                  <strong>Hospital Node Disconnect Alert</strong>
                  <p className="text-muted small">Alert if any peer hospital node drops gRPC heartbeat</p>
                </div>
                <input
                  type="checkbox"
                  checked={notifications.hospital_sync_fail}
                  onChange={(e) =>
                    setNotifications({ ...notifications, hospital_sync_fail: e.target.checked })
                  }
                />
              </label>
            </div>
          </div>
        </div>

        {/* Platform Architecture & About */}
        <div className="card">
          <div className="card-header">
            <div className="header-title-with-icon">
              <FiInfo className="mr-2 text-primary" />
              <h3 className="card-title">About FedHealth Framework</h3>
            </div>
          </div>

          <div className="card-body">
            <div className="about-platform-content">
              <p>
                <strong>FedHealth</strong> is a privacy-preserving federated machine learning architecture designed to enable multi-hospital collaborative disease risk stratification without sharing or exposing patient health information.
              </p>
              <ul className="info-list mt-3">
                <li><strong>Federated Protocol:</strong> FedAvg with Differential Privacy SGD</li>
                <li><strong>Privacy Metric:</strong> Rényi Differential Privacy (RDP)</li>
                <li><strong>Compliance Standard:</strong> HIPAA Safe Harbor & GDPR Recital 26</li>
                <li><strong>Client Node SDK:</strong> PyTorch Distributed RPC & WebAssembly</li>
                <li><strong>Platform Version:</strong> 4.2.1-Enterprise</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
