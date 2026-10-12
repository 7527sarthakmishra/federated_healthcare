import React, { useState, useEffect } from 'react';
import {
  FiActivity,
  FiShield,
  FiAlertTriangle,
  FiCheckCircle,
  FiHelpCircle,
  FiInfo,
  FiRotateCcw,
  FiClock,
  FiZap
} from 'react-icons/fi';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from 'recharts';
import PrivacyBadge from '../components/PrivacyBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { predictionAPI } from '../services/api';

const PredictionPage = () => {
  // Input features state
  const [features, setFeatures] = useState({
    age: 58,
    gender: 'Male',
    bmi: 29.5,
    bp_systolic: 142,
    bp_diastolic: 88,
    cholesterol: 242,
    glucose: 168,
    smoking: 'Former',
    heart_rate: 76
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const hist = await predictionAPI.getHistory();
      setHistory(hist);
    } catch (e) {
      console.error(e);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFeatures(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await predictionAPI.predict(features);
      setResult(res);
      fetchHistory();
    } catch (err) {
      setError('Error communicating with federated inference pipeline.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFeatures({
      age: 45,
      gender: 'Female',
      bmi: 24.5,
      bp_systolic: 120,
      bp_diastolic: 80,
      cholesterol: 190,
      glucose: 98,
      smoking: 'Never',
      heart_rate: 72
    });
    setResult(null);
  };

  const handleLoadSample = (sampleType) => {
    if (sampleType === 'high_risk') {
      setFeatures({
        age: 67,
        gender: 'Male',
        bmi: 34.2,
        bp_systolic: 164,
        bp_diastolic: 98,
        cholesterol: 285,
        glucose: 215,
        smoking: 'Current',
        heart_rate: 88
      });
    } else if (sampleType === 'moderate_risk') {
      setFeatures({
        age: 54,
        gender: 'Female',
        bmi: 28.1,
        bp_systolic: 138,
        bp_diastolic: 86,
        cholesterol: 228,
        glucose: 132,
        smoking: 'Former',
        heart_rate: 76
      });
    } else {
      setFeatures({
        age: 32,
        gender: 'Female',
        bmi: 21.8,
        bp_systolic: 114,
        bp_diastolic: 74,
        cholesterol: 165,
        glucose: 86,
        smoking: 'Never',
        heart_rate: 68
      });
    }
  };

  return (
    <div className="page-container prediction-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Federated Clinical Risk Prediction</h1>
          <p className="page-subtitle">
            Evaluate multidimensional patient risk across federated models trained collaboratively without centralizing raw data.
          </p>
        </div>
        <div className="header-actions">
          <PrivacyBadge level="high" epsilon={0.85} />
        </div>
      </div>

      {error && <div className="alert-box alert-error mb-4">{error}</div>}

      <div className="prediction-grid">
        {/* Left Column: Input Form */}
        <div className="card input-section-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">Patient Biometric Indicators</h3>
              <p className="card-subtitle">Values are evaluated locally using global federated weights</p>
            </div>
            <div className="sample-presets">
              <span className="text-muted small">Load Preset: </span>
              <button
                type="button"
                className="btn-link-action text-danger"
                onClick={() => handleLoadSample('high_risk')}
              >
                High Risk
              </button>
              <button
                type="button"
                className="btn-link-action text-warning"
                onClick={() => handleLoadSample('moderate_risk')}
              >
                Moderate
              </button>
              <button
                type="button"
                className="btn-link-action text-success"
                onClick={() => handleLoadSample('healthy')}
              >
                Healthy
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="card-body">
            <div className="form-row-2">
              <div className="form-group">
                <label>Age (years)</label>
                <input
                  type="number"
                  name="age"
                  min="18"
                  max="100"
                  value={features.age}
                  onChange={handleInputChange}
                  required
                />
                <span className="form-hint">Adult cohorts (18 - 100)</span>
              </div>
              <div className="form-group">
                <label>Gender</label>
                <select
                  name="gender"
                  value={features.gender}
                  onChange={handleInputChange}
                  className="select-input"
                  required
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </select>
                <span className="form-hint">Biological sex profile</span>
              </div>
            </div>

            <div className="form-row-2">
              <div className="form-group">
                <label>BMI (Body Mass Index)</label>
                <input
                  type="number"
                  step="0.1"
                  name="bmi"
                  min="15"
                  max="50"
                  value={features.bmi}
                  onChange={handleInputChange}
                  required
                />
                <span className="form-hint">Normal: 18.5 - 24.9 kg/m²</span>
              </div>
              <div className="form-group">
                <label>Smoking Status</label>
                <select
                  name="smoking"
                  value={features.smoking}
                  onChange={handleInputChange}
                  className="select-input"
                  required
                >
                  <option value="Never">Never Smoked</option>
                  <option value="Former">Former Smoker</option>
                  <option value="Current">Current Active Smoker</option>
                </select>
                <span className="form-hint">Cardiovascular risk indicator</span>
              </div>
            </div>

            <div className="form-row-2">
              <div className="form-group">
                <label>Systolic BP (mmHg)</label>
                <input
                  type="number"
                  name="bp_systolic"
                  min="80"
                  max="220"
                  value={features.bp_systolic}
                  onChange={handleInputChange}
                  required
                />
                <span className="form-hint">Target: &lt; 120 mmHg</span>
              </div>
              <div className="form-group">
                <label>Diastolic BP (mmHg)</label>
                <input
                  type="number"
                  name="bp_diastolic"
                  min="50"
                  max="140"
                  value={features.bp_diastolic}
                  onChange={handleInputChange}
                  required
                />
                <span className="form-hint">Target: &lt; 80 mmHg</span>
              </div>
            </div>

            <div className="form-row-3">
              <div className="form-group">
                <label>Cholesterol (mg/dL)</label>
                <input
                  type="number"
                  name="cholesterol"
                  min="100"
                  max="400"
                  value={features.cholesterol}
                  onChange={handleInputChange}
                  required
                />
                <span className="form-hint">Desirable: &lt; 200</span>
              </div>
              <div className="form-group">
                <label>Fasting Glucose (mg/dL)</label>
                <input
                  type="number"
                  name="glucose"
                  min="50"
                  max="350"
                  value={features.glucose}
                  onChange={handleInputChange}
                  required
                />
                <span className="form-hint">Fasting: 70 - 99</span>
              </div>
              <div className="form-group">
                <label>Resting HR (bpm)</label>
                <input
                  type="number"
                  name="heart_rate"
                  min="40"
                  max="150"
                  value={features.heart_rate}
                  onChange={handleInputChange}
                  required
                />
                <span className="form-hint">Resting: 60 - 100</span>
              </div>
            </div>

            <div className="form-actions-split">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleReset}
              >
                <FiRotateCcw style={{ marginRight: '6px' }} /> Reset
              </button>
              <button
                type="submit"
                className="btn btn-primary btn-lg"
                disabled={loading}
              >
                <FiZap style={{ marginRight: '6px' }} />
                {loading ? 'Evaluating via Federated Consensus...' : 'Analyze Disease Risk'}
              </button>
            </div>
          </form>
        </div>

        {/* Right Column: Prediction Outcomes */}
        <div className="results-section">
          {loading ? (
            <div className="card loading-card">
              <LoadingSpinner message="Calculating non-parametric risk estimates using federated ensemble..." />
            </div>
          ) : result ? (
            <div className="results-container">
              <div className="results-header-banner">
                <div>
                  <h3 className="text-white">Multi-Disease Risk Assessment</h3>
                  <p className="text-white-subtle">
                    Ref ID: {result.prediction_id} • Federated Differential Privacy (ε=0.85)
                  </p>
                </div>
                <span className="badge badge-light-outline">Validated Model v4.2</span>
              </div>

              {/* 3 Disease Cards */}
              <div className="disease-cards-row">
                {/* Diabetes */}
                <div
                  className={`card disease-risk-card ${
                    result.diseases.diabetes.risk_level.toLowerCase()
                  }`}
                >
                  <div className="disease-card-header">
                    <h4>Type 2 Diabetes</h4>
                    <span
                      className={`badge ${
                        result.diseases.diabetes.risk_level === 'High'
                          ? 'badge-danger'
                          : result.diseases.diabetes.risk_level === 'Medium'
                          ? 'badge-warning'
                          : 'badge-success'
                      }`}
                    >
                      {result.diseases.diabetes.risk_level} Risk
                    </span>
                  </div>
                  <div className="disease-probability">
                    <span className="prob-value">
                      {result.diseases.diabetes.probability}%
                    </span>
                    <span className="prob-label">Estimated Risk Probability</span>
                  </div>
                  <div className="disease-card-contributors">
                    <small>Key Contributors:</small>
                    <div className="contributor-tags">
                      {result.diseases.diabetes.key_contributors.map((c, i) => (
                        <span key={i} className="tag-pill">{c}</span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Heart Disease */}
                <div
                  className={`card disease-risk-card ${
                    result.diseases.heart_disease.risk_level.toLowerCase()
                  }`}
                >
                  <div className="disease-card-header">
                    <h4>Cardiovascular Disease</h4>
                    <span
                      className={`badge ${
                        result.diseases.heart_disease.risk_level === 'High'
                          ? 'badge-danger'
                          : result.diseases.heart_disease.risk_level === 'Medium'
                          ? 'badge-warning'
                          : 'badge-success'
                      }`}
                    >
                      {result.diseases.heart_disease.risk_level} Risk
                    </span>
                  </div>
                  <div className="disease-probability">
                    <span className="prob-value">
                      {result.diseases.heart_disease.probability}%
                    </span>
                    <span className="prob-label">Estimated Risk Probability</span>
                  </div>
                  <div className="disease-card-contributors">
                    <small>Key Contributors:</small>
                    <div className="contributor-tags">
                      {result.diseases.heart_disease.key_contributors.map((c, i) => (
                        <span key={i} className="tag-pill">{c}</span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Chronic Kidney Disease */}
                <div
                  className={`card disease-risk-card ${
                    result.diseases.kidney_disease.risk_level.toLowerCase()
                  }`}
                >
                  <div className="disease-card-header">
                    <h4>Chronic Kidney Disease</h4>
                    <span
                      className={`badge ${
                        result.diseases.kidney_disease.risk_level === 'High'
                          ? 'badge-danger'
                          : result.diseases.kidney_disease.risk_level === 'Medium'
                          ? 'badge-warning'
                          : 'badge-success'
                      }`}
                    >
                      {result.diseases.kidney_disease.risk_level} Risk
                    </span>
                  </div>
                  <div className="disease-probability">
                    <span className="prob-value">
                      {result.diseases.kidney_disease.probability}%
                    </span>
                    <span className="prob-label">Estimated Risk Probability</span>
                  </div>
                  <div className="disease-card-contributors">
                    <small>Key Contributors:</small>
                    <div className="contributor-tags">
                      {result.diseases.kidney_disease.key_contributors.map((c, i) => (
                        <span key={i} className="tag-pill">{c}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Feature Impact Chart */}
              <div className="card mt-3">
                <div className="card-header">
                  <h4 className="card-title">Biomarker Feature Contribution Breakdown</h4>
                  <span className="text-muted small">SHAP-inspired federated feature attribution</span>
                </div>
                <div className="card-body">
                  <ResponsiveContainer width="100%" height={230}>
                    <BarChart
                      layout="vertical"
                      data={result.feature_importance || []}
                      margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" domain={[0, 100]} />
                      <YAxis dataKey="feature" type="category" tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Bar dataKey="impact" fill="#00897b" radius={[0, 4, 4, 0]} name="Impact Factor" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          ) : (
            <div className="card empty-results-placeholder">
              <div className="placeholder-icon">
                <FiActivity size={48} color="#1a73e8" />
              </div>
              <h3>Ready for Risk Analysis</h3>
              <p className="text-muted">
                Adjust clinical parameters on the left and click "Analyze Disease Risk" to run privacy-preserving federated inference.
              </p>
              <div className="privacy-callout">
                <FiShield color="#00897b" size={20} />
                <span>Zero patient data is stored or transferred outside this session.</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Prediction History Table */}
      <div className="card mt-4">
        <div className="card-header">
          <div className="header-title-with-icon">
            <FiClock className="mr-2 text-primary" />
            <h3 className="card-title">Recent Inference History</h3>
          </div>
          <span className="badge badge-subtle">{history.length} Runs Logged</span>
        </div>
        <div className="card-body p-0">
          <div className="table-responsive">
            <table className="custom-table striped-table">
              <thead>
                <tr>
                  <th>Prediction ID</th>
                  <th>Patient Profile</th>
                  <th>Primary Risk</th>
                  <th>Level</th>
                  <th>Confidence Score</th>
                  <th>Time Executed</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item, idx) => (
                  <tr key={idx}>
                    <td className="font-semibold text-primary">{item.id}</td>
                    <td>{item.patient_age} yrs, {item.gender}</td>
                    <td>{item.disease}</td>
                    <td>
                      <span
                        className={`badge ${
                          item.risk_level === 'High'
                            ? 'badge-danger'
                            : item.risk_level === 'Medium'
                            ? 'badge-warning'
                            : 'badge-success'
                        }`}
                      >
                        {item.risk_level}
                      </span>
                    </td>
                    <td>
                      <div className="confidence-pill">
                        <strong>{item.confidence}%</strong>
                      </div>
                    </td>
                    <td className="text-muted"><small>{item.timestamp}</small></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionPage;
