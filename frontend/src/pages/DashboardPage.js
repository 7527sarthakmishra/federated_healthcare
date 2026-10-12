import React, { useState, useEffect } from 'react';
import {
  FiUsers,
  FiHome,
  FiCheckCircle,
  FiShield,
  FiActivity,
  FiTrendingUp,
  FiClock,
  FiExternalLink
} from 'react-icons/fi';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import StatCard from '../components/StatCard';
import PrivacyBadge from '../components/PrivacyBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { analyticsAPI } from '../services/api';
import { Link } from 'react-router-dom';

const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const res = await analyticsAPI.getDashboard();
        setData(res);
      } catch (err) {
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Aggregating federated metrics across hospital nodes..." />;
  }

  const statCards = [
    {
      title: 'Total Patients',
      value: (data?.total_patients || 12480).toLocaleString(),
      icon: FiUsers,
      change: '+8.4%',
      changeType: 'positive',
      color: '#1a73e8',
      subtitle: 'Across 14 distributed nodes',
    },
    {
      title: 'Active Hospitals',
      value: data?.active_hospitals || 14,
      icon: FiHome,
      change: '+2 this month',
      changeType: 'positive',
      color: '#00897b',
      subtitle: 'All communicating via TLS/gRPC',
    },
    {
      title: 'Prediction Accuracy',
      value: `${data?.model_accuracy || 94.6}%`,
      icon: FiCheckCircle,
      change: '+1.8% vs last round',
      changeType: 'positive',
      color: '#43a047',
      subtitle: 'Multi-task ensemble model',
    },
    {
      title: 'Privacy Budget Remaining',
      value: `ε = ${data?.privacy_budget_remaining || 8.42}`,
      icon: FiShield,
      change: '1.58 spent of 10.0',
      changeType: 'positive',
      color: '#fb8c00',
      subtitle: 'Strict Gaussian DP guarantees',
    },
  ];

  return (
    <div className="page-container dashboard-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Executive Overview</h1>
          <p className="page-subtitle">
            Real-time monitoring of decentralized federated model consensus & disease risks.
          </p>
        </div>
        <div className="header-actions">
          <PrivacyBadge level="high" epsilon={1.58} />
          <Link to="/predictions" className="btn btn-primary btn-sm">
            <FiActivity style={{ marginRight: '6px' }} /> Launch Prediction
          </Link>
        </div>
      </div>

      {error && <div className="alert-box alert-error">{error}</div>}

      {/* Row 1: 4 Stat Cards */}
      <div className="stats-grid">
        {statCards.map((card, idx) => (
          <StatCard key={idx} {...card} />
        ))}
      </div>

      {/* Row 2: Charts */}
      <div className="charts-grid-2">
        <div className="card chart-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">Disease Distribution</h3>
              <p className="card-subtitle">Aggregated diagnosis count across nodes</p>
            </div>
            <span className="badge badge-teal">DP Preserved</span>
          </div>
          <div className="card-body chart-wrapper">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data?.disease_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e0e0e0" />
                <XAxis dataKey="disease" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(val) => [`${val.toLocaleString()} cases`, 'Prevalence']}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #ddd' }}
                />
                <Bar dataKey="count" fill="#1a73e8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card chart-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">Federated Convergence Rate</h3>
              <p className="card-subtitle">Model accuracy (%) & Loss progression</p>
            </div>
            <span className="badge badge-blue">Round 7 Complete</span>
          </div>
          <div className="card-body chart-wrapper">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={data?.training_progress || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e0e0e0" />
                <XAxis dataKey="round" tick={{ fontSize: 12 }} />
                <YAxis yAxisId="left" domain={[70, 100]} tick={{ fontSize: 12 }} />
                <YAxis yAxisId="right" orientation="right" domain={[0, 1]} tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #ddd' }}
                />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="accuracy"
                  name="Accuracy (%)"
                  stroke="#1a73e8"
                  strokeWidth={3}
                  activeDot={{ r: 6 }}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="loss"
                  name="Loss"
                  stroke="#e53935"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 3: Recent Predictions & Hospital Node Activity */}
      <div className="dashboard-tables-grid">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Inference Inquiries</h3>
            <Link to="/predictions" className="view-all-link">
              New Run <FiExternalLink />
            </Link>
          </div>
          <div className="card-body p-0">
            <div className="table-responsive">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Ref ID</th>
                    <th>Age/Sex</th>
                    <th>Target Disease</th>
                    <th>Risk Level</th>
                    <th>Confidence</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {(data?.recent_predictions || []).map((pred) => (
                    <tr key={pred.id}>
                      <td className="font-semibold text-primary">{pred.id}</td>
                      <td>{pred.patient_age}y / {pred.gender}</td>
                      <td>{pred.disease}</td>
                      <td>
                        <span
                          className={`badge ${
                            pred.risk_level === 'High'
                              ? 'badge-danger'
                              : pred.risk_level === 'Medium'
                              ? 'badge-warning'
                              : 'badge-success'
                          }`}
                        >
                          {pred.risk_level}
                        </span>
                      </td>
                      <td>
                        <strong>{pred.confidence}%</strong>
                      </td>
                      <td className="text-muted"><small>{pred.timestamp}</small></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Hospital Cluster Activity</h3>
            <Link to="/hospitals" className="view-all-link">
              View All <FiExternalLink />
            </Link>
          </div>
          <div className="card-body p-0">
            <div className="table-responsive">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Hospital Center</th>
                    <th>Status</th>
                    <th>Local Records</th>
                    <th>Contribution</th>
                  </tr>
                </thead>
                <tbody>
                  {(data?.hospital_activity || []).map((hosp) => (
                    <tr key={hosp.id}>
                      <td>
                        <strong>{hosp.name}</strong>
                        <div className="text-muted"><small>{hosp.nodes} GPU edge nodes</small></div>
                      </td>
                      <td>
                        <span className={`status-pill ${hosp.sync_status === 'Synced' ? 'status-online' : 'status-training'}`}>
                          {hosp.sync_status}
                        </span>
                      </td>
                      <td>{hosp.samples.toLocaleString()}</td>
                      <td>
                        <div className="progress-bar-wrapper">
                          <div
                            className="progress-bar-fill"
                            style={{ width: `${hosp.contribution_score}%`, backgroundColor: '#00897b' }}
                          ></div>
                          <span>{hosp.contribution_score}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
