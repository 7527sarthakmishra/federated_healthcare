import React, { useState, useEffect } from 'react';
import {
  FiFileText,
  FiSearch,
  FiFilter,
  FiShield,
  FiDownload,
  FiUser,
  FiActivity
} from 'react-icons/fi';
import LoadingSpinner from '../components/LoadingSpinner';
import { auditAPI } from '../services/api';

const AuditPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState('ALL');
  const [page, setPage] = useState(1);
  const itemsPerPage = 8;

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await auditAPI.getLogs();
      setLogs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(logs, null, 2)
    )}`;
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', jsonString);
    downloadAnchor.setAttribute('download', `fedhealth_audit_logs_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  if (loading) {
    return <LoadingSpinner message="Retrieving tamper-evident cryptographic audit logs..." />;
  }

  // Filter logic
  const filtered = logs.filter(log => {
    const matchesSearch =
      log.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.resource.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesAction = actionFilter === 'ALL' || log.action === actionFilter;

    return matchesSearch && matchesAction;
  });

  const totalPages = Math.ceil(filtered.length / itemsPerPage) || 1;
  const currentLogs = filtered.slice((page - 1) * itemsPerPage, page * itemsPerPage);

  const getActionBadgeClass = (action) => {
    if (action.includes('PREDICTION')) return 'badge-primary';
    if (action.includes('AGGREGATION') || action.includes('MODEL')) return 'badge-teal';
    if (action.includes('NOISE') || action.includes('PRIVACY')) return 'badge-warning';
    return 'badge-subtle';
  };

  return (
    <div className="page-container audit-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Immutable Audit Trail</h1>
          <p className="page-subtitle">
            Cryptographic ledger tracking all federated training rounds, model weights synchronization, and inference requests.
          </p>
        </div>
        <div className="header-actions">
          <button className="btn btn-outline" onClick={handleExport}>
            <FiDownload style={{ marginRight: '6px' }} /> Export Audit Ledger
          </button>
        </div>
      </div>

      {/* Filter and Search Controls */}
      <div className="card mb-4 filter-bar-card">
        <div className="filter-bar">
          <div className="search-input-wrapper">
            <FiSearch className="search-icon" />
            <input
              type="text"
              placeholder="Search audit trail by User, Resource, Hash or Details..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPage(1);
              }}
              className="table-search-input"
            />
          </div>

          <div className="filter-select-wrapper">
            <FiFilter className="filter-icon" />
            <select
              value={actionFilter}
              onChange={(e) => {
                setActionFilter(e.target.value);
                setPage(1);
              }}
              className="filter-select"
            >
              <option value="ALL">All Action Events</option>
              <option value="RUN_PREDICTION">Inference Requests</option>
              <option value="FED_AGGREGATION">Federated Aggregations</option>
              <option value="NOISE_INJECTION">Differential Privacy Noise</option>
              <option value="BATCH_UPLOAD">Batch Uploads</option>
              <option value="MODEL_CHECKPOINT">Model Checkpoints</option>
            </select>
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="card">
        <div className="card-body p-0">
          <div className="table-responsive">
            <table className="custom-table striped-table">
              <thead>
                <tr>
                  <th>Log Entry ID</th>
                  <th>Timestamp (UTC)</th>
                  <th>Actor / Identity</th>
                  <th>Event Action</th>
                  <th>Resource Target</th>
                  <th>Details & Cryptographic Signature</th>
                  <th>Origin IP</th>
                </tr>
              </thead>
              <tbody>
                {currentLogs.map((log) => (
                  <tr key={log.id}>
                    <td className="font-semibold text-primary">{log.id}</td>
                    <td className="text-muted"><small>{log.timestamp}</small></td>
                    <td>
                      <div className="actor-cell">
                        <FiUser className="mr-1 text-muted" />
                        <span>{log.user}</span>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${getActionBadgeClass(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td>{log.resource}</td>
                    <td>{log.details}</td>
                    <td><code>{log.ip}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="table-pagination">
            <span>
              Showing {(page - 1) * itemsPerPage + 1} to{' '}
              {Math.min(page * itemsPerPage, filtered.length)} of {filtered.length} logs
            </span>
            <div className="pagination-buttons">
              <button
                className="btn btn-outline btn-sm"
                disabled={page === 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
              >
                Previous
              </button>
              <span className="pagination-page-indicator">
                Page {page} of {totalPages}
              </span>
              <button
                className="btn btn-outline btn-sm"
                disabled={page === totalPages}
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuditPage;
