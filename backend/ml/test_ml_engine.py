"""Test script for ML and Federated Learning components."""

import sys
import os

# Add paths to test both import styles
backend_dir = r"C:\Users\harsh\.gemini\antigravity\scratch\federated-healthcare-platform\backend"
parent_dir = r"C:\Users\harsh\.gemini\antigravity\scratch\federated-healthcare-platform"

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print(f"Python version: {sys.version}")

# Test 1: Direct imports from backend.ml
try:
    from backend.ml import (
        DataPreprocessor,
        SyntheticDataGenerator,
        DiseasePredictor,
        SklearnPredictor,
        DifferentialPrivacy,
        PrivacyAccountant,
        FederatedServer,
        FederatedClient,
        PredictionService,
        FEATURE_NAMES,
        DISEASE_NAMES,
    )
    print("SUCCESS: Imported all modules from backend.ml")
except Exception as e:
    print(f"FAILED backend.ml import: {e}")
    sys.exit(1)

# Test 2: Imports from ml (for running inside backend directory)
try:
    from ml import (
        DataPreprocessor as DP2,
        PredictionService as PS2,
    )
    print("SUCCESS: Imported from ml directly")
except Exception as e:
    print(f"FAILED ml direct import: {e}")
    sys.exit(1)

# Test 3: Synthetic Data Generator
print("\n--- Testing SyntheticDataGenerator ---")
gen = SyntheticDataGenerator(random_state=42)
records = gen.generate_patient_records(n_records=50, hospital_id="test_hosp")
assert len(records) == 50, "Record count mismatch"
assert "glucose" in records[0] and "diabetes" in records[0]
datasets = gen.generate_hospital_datasets(n_hospitals=3, records_per_hospital=50)
assert len(datasets) == 3
print("SUCCESS: Synthetic data generation validated")

# Test 4: DataPreprocessor
print("\n--- Testing DataPreprocessor ---")
prep = DataPreprocessor()
X_norm, y = prep.prepare_training_data(records)
assert X_norm.shape == (50, 9), f"X shape mismatch: {X_norm.shape}"
assert y.shape == (50, 3), f"y shape mismatch: {y.shape}"
sample_input = {
    "age": 62,
    "gender": "male",
    "bmi": 31.5,
    "blood_pressure_systolic": 145,
    "blood_pressure_diastolic": 92,
    "cholesterol": 240,
    "glucose": 160,
    "smoking_status": "current",
    "heart_rate": 84,
}
is_valid, errors, sanitized = prep.validate_input(sample_input)
assert is_valid, f"Validation failed: {errors}"
norm_input = prep.prepare_prediction_input(sanitized)
assert norm_input.shape == (1, 9)
print("SUCCESS: DataPreprocessor validated")

# Test 5: PyTorch DiseasePredictor
print("\n--- Testing DiseasePredictor ---")
model = DiseasePredictor()
preds = model.predict(norm_input)
assert "probabilities" in preds and "predictions" in preds
params = model.get_model_params()
assert "fc1.weight" in params
model.set_model_params(params)
print("SUCCESS: PyTorch DiseasePredictor validated")

# Test 6: SklearnPredictor
print("\n--- Testing SklearnPredictor ---")
sk_model = SklearnPredictor(n_estimators=10)
accs = sk_model.train(X_norm, y)
assert len(accs) == 3
sk_preds = sk_model.predict(norm_input)
assert len(sk_preds) == 3
imp = sk_model.get_feature_importance()
assert len(imp) == 3
print("SUCCESS: SklearnPredictor validated")

# Test 7: Differential Privacy
print("\n--- Testing DifferentialPrivacy & PrivacyAccountant ---")
dp = DifferentialPrivacy(epsilon=5.0, delta=1e-5, noise_multiplier=0.8)
priv_params = dp.privatize_model_update(params)
spent = dp.compute_privacy_spent(num_steps=3, sample_rate=1.0)
rem = dp.get_privacy_budget_remaining()
assert spent > 0.0
assert rem <= 5.0
print(f"Privacy spent: {spent:.4f}, remaining: {rem:.4f}")
print("SUCCESS: DifferentialPrivacy validated")

# Test 8: Federated Engine Simulation
print("\n--- Testing FederatedServer & FederatedClient ---")
fed_server = FederatedServer(num_hospitals=3, privacy_budget=5.0, noise_multiplier=0.8)
history = fed_server.simulate_federated_training(
    hospital_data_dict=datasets,
    num_rounds=2,
    epochs_per_round=2,
    lr=0.01,
)
assert len(history) == 2
print(f"Federated rounds completed: {len(history)}")
print(f"Round 2 global accuracy: {history[-1]['global_accuracy']:.4f}")
print("SUCCESS: Federated engine validated")

# Test 9: PredictionService
print("\n--- Testing PredictionService ---")
svc = PredictionService(auto_initialize_weights=True)
res = svc.predict(sample_input)
print("Prediction output:", res)
assert "diabetes" in res and "heart_disease" in res and "kidney_disease" in res
assert "prediction" in res["diabetes"] and "confidence" in res["diabetes"]

risk = svc.get_risk_factors(sample_input)
assert "diabetes" in risk
print("Top diabetes risk factors:", risk["diabetes"]["top_risk_factors"])

info = svc.get_model_info()
assert info["framework"] == "PyTorch"
print("Model info validated:", info["model_name"])
print("\nALL TESTS PASSED SUCCESSFULLY!")
