"""Comprehensive backend API integration and validation test suite."""

import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(backend_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=" * 60)
print("RUNNING FULL FEDHEALTH BACKEND TEST SUITE")
print("=" * 60)

# 1. Health check
res = client.get("/health")
assert res.status_code == 200, f"Health check failed: {res.text}"
print(f"1. Health Check: PASSED (Status: {res.status_code}, Project: {res.json().get('project')})")

# 2. Login as Admin
login_res = client.post("/api/auth/login", json={"email": "admin@fedhealth.com", "password": "admin123"})
assert login_res.status_code == 200, f"Login failed: {login_res.text}"
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"2. Admin Authentication: PASSED (Token received, length: {len(token)})")

# 3. User Profile
me_res = client.get("/api/auth/me", headers=headers)
assert me_res.status_code == 200, f"Profile fetch failed: {me_res.text}"
me_data = me_res.json()
print(f"3. User Profile: PASSED (Email: {me_data['email']}, Role: {me_data['role']})")

# 4. Hospitals listing
hosp_res = client.get("/api/hospitals/", headers=headers)
assert hosp_res.status_code == 200, f"Hospitals fetch failed: {hosp_res.text}"
hospitals = hosp_res.json()
print(f"4. Hospitals Listing: PASSED ({len(hospitals)} hospitals registered)")
for h in hospitals:
    print(f"   - {h['name']} ({h['location']}) - Score: {h['data_contribution_score']}")

# 5. Patient records
pat_res = client.get("/api/patients/", headers=headers)
assert pat_res.status_code == 200, f"Patients fetch failed: {pat_res.text}"
patients = pat_res.json()
print(f"5. Anonymized Patients: PASSED ({len(patients)} records retrieved)")

# 6. Patient statistics
pat_stats = client.get("/api/patients/stats", headers=headers)
assert pat_stats.status_code == 200, f"Patient stats failed: {pat_stats.text}"
stats_data = pat_stats.json()
print(f"6. Patient Statistics: PASSED (Total: {stats_data['total_records']}, Avg Age: {stats_data['avg_age']})")

# 7. Disease Prediction
pred_payload = {
    "age": 58,
    "gender": "male",
    "bmi": 32.1,
    "blood_pressure_systolic": 148,
    "blood_pressure_diastolic": 94,
    "cholesterol": 248,
    "glucose": 165,
    "smoking_status": "current",
    "heart_rate": 84
}
pred_res = client.post("/api/predictions/predict", headers=headers, json=pred_payload)
assert pred_res.status_code == 200, f"Prediction failed: {pred_res.text}"
pred_data = pred_res.json()
print("7. Multi-Disease Risk Prediction: PASSED")
for disease_name, d_res in pred_data["results"].items():
    print(f"   - {disease_name.upper()}: Risk={d_res['risk_level']}, Prob={d_res['probability']}, Conf={d_res['confidence']}")

# 8. Prediction History
hist_res = client.get("/api/predictions/history", headers=headers)
assert hist_res.status_code == 200, f"Prediction history failed: {hist_res.text}"
history = hist_res.json()
print(f"8. Prediction History: PASSED ({len(history)} logs retrieved)")

# 9. Analytics Dashboard
dash_res = client.get("/api/analytics/dashboard", headers=headers)
assert dash_res.status_code == 200, f"Dashboard analytics failed: {dash_res.text}"
dash_data = dash_res.json()
kpis = dash_data["kpis"]
print(f"9. Analytics Dashboard: PASSED (Total Patients: {kpis['total_patients']}, Global Accuracy: {kpis['global_accuracy']}%)")

# 10. Disease Distribution Analytics
dist_res = client.get("/api/analytics/disease-distribution", headers=headers)
assert dist_res.status_code == 200, f"Disease distribution failed: {dist_res.text}"
print(f"10. Disease Distribution Analytics: PASSED ({len(dist_res.json())} hospitals analyzed)")

# 11. Federated Training Status
fed_status = client.get("/api/federated/status", headers=headers)
assert fed_status.status_code == 200, f"Federated status failed: {fed_status.text}"
print(f"11. Federated Training Status: PASSED (Status: {fed_status.json()['status']}, Round: {fed_status.json()['current_round']})")

# 12. Federated Rounds
rounds_res = client.get("/api/federated/rounds", headers=headers)
assert rounds_res.status_code == 200, f"Federated rounds failed: {rounds_res.text}"
rounds = rounds_res.json()
print(f"12. Federated Rounds History: PASSED ({len(rounds)} training rounds on record)")

# 13. Privacy Budget Metrics
privacy_res = client.get("/api/federated/privacy-budget", headers=headers)
assert privacy_res.status_code == 200, f"Privacy budget failed: {privacy_res.text}"
pb = privacy_res.json()
print(f"13. Differential Privacy Accounting: PASSED (Budget spent: {pb['budget_spent']} / {pb['total_budget_limit']}, Delta: {pb['delta']})")

# 14. Audit Logs (Admin only)
audit_res = client.get("/api/audit/logs", headers=headers)
assert audit_res.status_code == 200, f"Audit logs failed: {audit_res.text}"
print(f"14. Audit Trail: PASSED ({len(audit_res.json())} immutable audit events logged)")

print("=" * 60)
print("SUCCESS: ALL 14 TEST SUITE SPECIFICATIONS PASSED PERFECTLY!")
print("=" * 60)
