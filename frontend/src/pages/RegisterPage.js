import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiShield, FiUser, FiMail, FiLock, FiHome, FiAlertCircle } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    hospital: '',
    role: 'researcher',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);

    try {
      const result = await register({
        username: formData.username,
        email: formData.email,
        hospital: formData.hospital,
        role: formData.role,
        password: formData.password,
      });

      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.error || 'Registration failed');
      }
    } catch (err) {
      setError('An unexpected error occurred during node provisioning.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card auth-card-wide">
        <div className="auth-header">
          <div className="auth-logo-badge">
            <FiShield size={36} color="#1a73e8" />
          </div>
          <h1 className="auth-title">FedHealth Registration</h1>
          <p className="auth-tagline">
            Connect your clinical hospital node to the collaborative predictive network
          </p>
        </div>

        {error && (
          <div className="alert-box alert-error">
            <FiAlertCircle className="alert-icon" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-row-2">
            <div className="form-group">
              <label htmlFor="username">Full Name / Clinical ID</label>
              <div className="input-with-icon">
                <FiUser className="input-icon" />
                <input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Dr. Gregory House"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="email">Hospital Email</label>
              <div className="input-with-icon">
                <FiMail className="input-icon" />
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="ghouse@princeton-plainsboro.org"
                  required
                />
              </div>
            </div>
          </div>

          <div className="form-row-2">
            <div className="form-group">
              <label htmlFor="hospital">Hospital Node Affiliation</label>
              <div className="input-with-icon">
                <FiHome className="input-icon" />
                <input
                  id="hospital"
                  name="hospital"
                  type="text"
                  value={formData.hospital}
                  onChange={handleChange}
                  placeholder="Memorial Hospital Center"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="role">Platform Role</label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="select-input"
              >
                <option value="researcher">Clinical Researcher / Doctor</option>
                <option value="admin">Federated Node Administrator</option>
                <option value="auditor">Healthcare Compliance Auditor</option>
              </select>
            </div>
          </div>

          <div className="form-row-2">
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="input-with-icon">
                <FiLock className="input-icon" />
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••••••"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <div className="input-with-icon">
                <FiLock className="input-icon" />
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="••••••••••••"
                  required
                />
              </div>
            </div>
          </div>

          <div className="dp-compliance-checkbox">
            <label className="checkbox-label">
              <input type="checkbox" required defaultChecked />
              <span>
                I verify that this node operates under HIPAA/GDPR compliance with differential privacy enabled.
              </span>
            </label>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={loading}
          >
            {loading ? 'Provisioning Federated Node...' : 'Register Hospital & Join Network'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an active node?{' '}
            <Link to="/" className="auth-link">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
