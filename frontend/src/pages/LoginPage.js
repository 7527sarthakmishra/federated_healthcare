import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiShield, FiLock, FiMail, FiAlertCircle } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(email, password);
      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.error || 'Failed to authenticate. Please check your credentials.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoFill = (role) => {
    if (role === 'admin') {
      setEmail('admin@fedhealth.com');
      setPassword('admin123');
    } else {
      setEmail('researcher@fedhealth.com');
      setPassword('researcher123');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo-badge">
            <FiShield size={36} color="#1a73e8" />
          </div>
          <h1 className="auth-title">FedHealth</h1>
          <p className="auth-tagline">
            Privacy-Preserving Federated Learning Platform for Multi-Hospital Disease Prediction
          </p>
        </div>

        {error && (
          <div className="alert-box alert-error">
            <FiAlertCircle className="alert-icon" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Hospital / Medical Email</label>
            <div className="input-with-icon">
              <FiMail className="input-icon" />
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@hospital.org"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Secure Password</label>
            <div className="input-with-icon">
              <FiLock className="input-icon" />
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                required
              />
            </div>
          </div>

          <div className="demo-credentials-helper">
            <span>Quick Fill Demo: </span>
            <button
              type="button"
              className="badge-button"
              onClick={() => handleDemoFill('admin')}
            >
              Admin Mode
            </button>
            <button
              type="button"
              className="badge-button"
              onClick={() => handleDemoFill('researcher')}
            >
              Researcher Mode
            </button>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={loading}
          >
            {loading ? 'Authenticating & Verifying DP Node...' : 'Sign In to Secure Node'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Need access to a hospital node?{' '}
            <Link to="/register" className="auth-link">
              Register New Hospital
            </Link>
          </p>
        </div>

        <div className="auth-security-disclaimer">
          <small>
            🔒 All communications are secured using Differential Privacy and zero-knowledge model aggregation. Local raw patient data never leaves your institution.
          </small>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
