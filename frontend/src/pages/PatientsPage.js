import React, { useState, useEffect } from 'react';
import {
  FiUsers,
  FiPlus,
  FiDownload,
  FiSearch,
  FiFilter,
  FiX,
  FiCheck,
  FiShield
} from 'react-icons/fi';
import LoadingSpinner from '../components/LoadingSpinner';
import { patientAPI } from '../services/api';

const PatientsPage = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterHospital, setFilterHospital] = useState('All');
  const [showAddModal, setShowAddModal] = useState(false);
  const [page, setPage] = useState(1);
  const itemsPerPage = 6;

  // New patient form state
  const [formData, setFormData] = useState({
    hospital: 'Metro Health General',
    age: 45,
    gender: 'Female',
    bmi: 26.2,
    bp_systolic: 120,
    bp_diastolic: 80,
    cholesterol: 195,
    glucose: 105,
    smoking: 'Never',
    diseases: 'None'
  });

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      const data = await patientAPI.getPatients();
      setPatients(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleAddPatient = async (e) => {
    e.preventDefault();
    try {
      await patientAPI.addPatient(formData);
      setShowAddModal(false);
      fetchPatients();
    } catch (err) {
      console.error(err);
    }
  };

  const handleExport = () => {
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(patients, null, 2)
    )}`;
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', jsonString);
    downloadAnchor.setAttribute('download', 'anonymized_patients_export.json');
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  if (loading) {
    return <LoadingSpinner message="Decentralized decrypting of anonymized patient records..." />;
  }

  // Filter logic
  const filtered = (patients || []).filter((p) => {
    if (!p) return false;
    const pId = String(p.id || '');
    const pHosp = String(p.hospital || '');
    const matchSearch =
      pId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      pHosp.toLowerCase().includes(searchTerm.toLowerCase());
    const matchHosp = filterHospital === 'All' || pHosp.includes(filterHospital);
    return matchSearch && matchHosp;
  });

  const totalPages = Math.ceil(filtered.length / itemsPerPage) || 1;
  const currentRecords = filtered.slice((page - 1) * itemsPerPage, page * itemsPerPage);

  const avgAge = patients && patients.length > 0 
    ? (patients.reduce((sum, p) => sum + (Number(p.age) || 0), 0) / patients.length).toFixed(1)
    : '0.0';
  const avgBMI = patients && patients.length > 0
    ? (patients.reduce((sum, p) => sum + (Number(p.bmi) || 0), 0) / patients.length).toFixed(1)
    : '0.0';

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Patient Records (De-Identified)</h1>
          <p className="page-subtitle">
            Local healthcare databases indexed with k-anonymity and zero direct identifier exposure.
          </p>
        </div>
        <div className="header-actions">
          <button className="btn btn-outline" onClick={handleExport}>
            <FiDownload style={{ marginRight: '6px' }} /> Export Anonymized
          </button>
          <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
            <FiPlus style={{ marginRight: '6px' }} /> Enroll Patient Record
          </button>
        </div>
      </div>

      {/* Patient Stats Bar */}
      <div className="stats-grid mb-4">
        <div className="stat-card">
          <span className="stat-card-title">Indexed Records</span>
          <h3 className="stat-card-value">{patients.length}</h3>
          <span className="stat-card-subtitle">Local + federated sync</span>
        </div>
        <div className="stat-card">
          <span className="stat-card-title">Average Cohort Age</span>
          <h3 className="stat-card-value">{avgAge} yrs</h3>
          <span className="stat-card-subtitle">Range: 18 - 85</span>
        </div>
        <div className="stat-card">
          <span className="stat-card-title">Average BMI</span>
          <h3 className="stat-card-value">{avgBMI}</h3>
          <span className="stat-card-subtitle">Normal: 18.5 - 24.9</span>
        </div>
        <div className="stat-card">
          <span className="stat-card-title">Privacy Level</span>
          <h3 className="stat-card-value text-teal">k-Anonymity 5</h3>
          <span className="stat-card-subtitle">HIPAA Safe Harbor compliant</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="card mb-4 filter-bar-card">
        <div className="filter-bar">
          <div className="search-input-wrapper">
            <FiSearch className="search-icon" />
            <input
              type="text"
              placeholder="Search by Patient Hash ID or Hospital..."
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
              value={filterHospital}
              onChange={(e) => {
                setFilterHospital(e.target.value);
                setPage(1);
              }}
              className="filter-select"
            >
              <option value="All">All Hospital Nodes</option>
              <option value="Metro">Metro Health General</option>
              <option value="St. Jude">St. Jude Memorial</option>
              <option value="University">University Medical Center</option>
              <option value="Pacific">Pacific Coast Health</option>
            </select>
          </div>
        </div>
      </div>

      {/* Records Table */}
      <div className="card">
        <div className="card-body p-0">
          <div className="table-responsive">
            <table className="custom-table striped-table">
              <thead>
                <tr>
                  <th>Anon ID</th>
                  <th>Hospital Origin</th>
                  <th>Age</th>
                  <th>Gender</th>
                  <th>BMI</th>
                  <th>Blood Pressure</th>
                  <th>Cholesterol</th>
                  <th>Glucose</th>
                  <th>Smoking</th>
                  <th>Diagnosed Co-morbidities</th>
                </tr>
              </thead>
              <tbody>
                {currentRecords.map((p) => (
                  <tr key={p.id}>
                    <td className="font-semibold text-primary">{p.id}</td>
                    <td>{p.hospital}</td>
                    <td>{p.age}</td>
                    <td>{p.gender}</td>
                    <td>
                      <span className={p.bmi > 30 ? 'text-danger font-semibold' : ''}>
                        {p.bmi}
                      </span>
                    </td>
                    <td>
                      {p.bp_systolic}/{p.bp_diastolic} mmHg
                    </td>
                    <td>
                      <span className={p.cholesterol > 240 ? 'text-danger font-semibold' : ''}>
                        {p.cholesterol} mg/dL
                      </span>
                    </td>
                    <td>
                      <span className={p.glucose > 140 ? 'text-danger font-semibold' : ''}>
                        {p.glucose} mg/dL
                      </span>
                    </td>
                    <td>{p.smoking}</td>
                    <td>
                      {Array.isArray(p.diseases)
                        ? p.diseases.map((d, i) => (
                            <span key={i} className="badge badge-subtle mr-1">
                              {d}
                            </span>
                          ))
                        : <span className="badge badge-subtle">{p.diseases}</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="table-pagination">
            <span>
              Showing {(page - 1) * itemsPerPage + 1} to{' '}
              {Math.min(page * itemsPerPage, filtered.length)} of {filtered.length} entries
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

      {/* Add Patient Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2>Enroll Anonymized Patient Record</h2>
                <p className="text-muted">Data remains on this local node with differential privacy.</p>
              </div>
              <button className="modal-close-btn" onClick={() => setShowAddModal(false)}>
                <FiX size={20} />
              </button>
            </div>

            <form onSubmit={handleAddPatient}>
              <div className="modal-body">
                <div className="form-row-2">
                  <div className="form-group">
                    <label>Hospital Node</label>
                    <select
                      name="hospital"
                      value={formData.hospital}
                      onChange={handleInputChange}
                      className="select-input"
                    >
                      <option value="Metro Health General">Metro Health General</option>
                      <option value="St. Jude Memorial Hospital">St. Jude Memorial Hospital</option>
                      <option value="University Medical Center">University Medical Center</option>
                      <option value="Pacific Coast Health">Pacific Coast Health</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Gender</label>
                    <select
                      name="gender"
                      value={formData.gender}
                      onChange={handleInputChange}
                      className="select-input"
                    >
                      <option value="Female">Female</option>
                      <option value="Male">Male</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>

                <div className="form-row-3">
                  <div className="form-group">
                    <label>Age (years)</label>
                    <input
                      type="number"
                      name="age"
                      min="18"
                      max="110"
                      value={formData.age}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>BMI (kg/m²)</label>
                    <input
                      type="number"
                      step="0.1"
                      name="bmi"
                      min="15"
                      max="55"
                      value={formData.bmi}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Smoking Status</label>
                    <select
                      name="smoking"
                      value={formData.smoking}
                      onChange={handleInputChange}
                      className="select-input"
                    >
                      <option value="Never">Never</option>
                      <option value="Former">Former</option>
                      <option value="Current">Current</option>
                    </select>
                  </div>
                </div>

                <div className="form-row-2">
                  <div className="form-group">
                    <label>Systolic BP (mmHg)</label>
                    <input
                      type="number"
                      name="bp_systolic"
                      value={formData.bp_systolic}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Diastolic BP (mmHg)</label>
                    <input
                      type="number"
                      name="bp_diastolic"
                      value={formData.bp_diastolic}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="form-row-2">
                  <div className="form-group">
                    <label>Total Cholesterol (mg/dL)</label>
                    <input
                      type="number"
                      name="cholesterol"
                      value={formData.cholesterol}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Fasting Blood Glucose (mg/dL)</label>
                    <input
                      type="number"
                      name="glucose"
                      value={formData.glucose}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Existing Diagnoses</label>
                  <input
                    type="text"
                    name="diseases"
                    value={formData.diseases}
                    onChange={handleInputChange}
                    placeholder="e.g. Hypertension, None"
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save to Local Node
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientsPage;
