"""Synthetic patient clinical data generator with realistic physiological distributions

and correlated multi-disease risk modeling.
"""

from typing import Any, Dict, List, Optional
import numpy as np


class SyntheticDataGenerator:
    """Generates realistic synthetic patient health records with clinical correlations."""

    def __init__(self, random_state: Optional[int] = None):
        """Initialize the synthetic generator with an optional random seed.

        Args:
            random_state: Seed for reproducible synthetic generation.
        """
        self.rng = np.random.RandomState(random_state)

    def _generate_disease_labels(
        self,
        age: np.ndarray,
        bmi: np.ndarray,
        bp_sys: np.ndarray,
        bp_dia: np.ndarray,
        chol: np.ndarray,
        glucose: np.ndarray,
        smoking: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        """Compute physiologically grounded multi-label probabilities and binary labels.

        Clinically motivated logistic risk factors:
        - Diabetes: driven by elevated glucose (>100 fasting, >126 diabetic), BMI (>25 overweight, >30 obese), and age.
        - Heart disease: driven by systolic/diastolic hypertension, elevated cholesterol, smoking, and age.
        - Kidney disease: driven by combined chronic hypertension, high glucose (diabetic nephropathy), and age.
        """
        n = len(age)

        # 1. Diabetes risk logit
        # Baseline centered around normal values: Glucose ~ 100, BMI ~ 25, Age ~ 50
        z_diabetes = (
            -4.5
            + 0.040 * (glucose - 100.0)
            + 0.120 * (bmi - 25.0)
            + 0.025 * (age - 50.0)
            + 0.250 * (smoking > 0)
        )
        prob_diabetes = 1.0 / (1.0 + np.exp(-z_diabetes))
        diabetes = (self.rng.uniform(0.0, 1.0, size=n) < prob_diabetes).astype(int)

        # 2. Heart disease risk logit
        # High BP (>130 systolic, >85 diastolic), cholesterol (>200), smoking (0, 1, 2), age
        z_heart = (
            -4.8
            + 0.030 * (bp_sys - 120.0)
            + 0.025 * (bp_dia - 80.0)
            + 0.015 * (chol - 200.0)
            + 0.040 * (age - 50.0)
            + 0.500 * (smoking == 1)
            + 0.900 * (smoking == 2)
        )
        prob_heart = 1.0 / (1.0 + np.exp(-z_heart))
        heart_disease = (self.rng.uniform(0.0, 1.0, size=n) < prob_heart).astype(int)

        # 3. Kidney disease risk logit
        # Driven by chronic hypertension, high glucose, older age, elevated BMI
        z_kidney = (
            -5.2
            + 0.025 * (bp_sys - 120.0)
            + 0.018 * (glucose - 100.0)
            + 0.035 * (age - 50.0)
            + 0.050 * (bmi - 25.0)
            + 0.300 * diabetes
            + 0.200 * heart_disease
        )
        prob_kidney = 1.0 / (1.0 + np.exp(-z_kidney))
        kidney_disease = (self.rng.uniform(0.0, 1.0, size=n) < prob_kidney).astype(int)

        return {
            "diabetes": diabetes,
            "heart_disease": heart_disease,
            "kidney_disease": kidney_disease,
        }

    def generate_patient_records(
        self,
        n_records: int,
        hospital_id: Optional[str] = "hospital_1",
        age_bias: float = 0.0,
        bmi_bias: float = 0.0,
        bp_bias: float = 0.0,
        glucose_bias: float = 0.0,
        chol_bias: float = 0.0,
        seed: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Generate realistic synthetic patient records.

        Args:
            n_records: Number of synthetic patient samples.
            hospital_id: Unique hospital identifier tag.
            age_bias: Demographic shift for simulating heterogeneous hospital cohorts.
            bmi_bias: BMI shift for cohort heterogeneity.
            bp_bias: Blood pressure shift for cohort heterogeneity.
            glucose_bias: Glucose shift for cohort heterogeneity.
            chol_bias: Cholesterol shift for cohort heterogeneity.
            seed: Optional local random seed.

        Returns:
            List of patient dictionaries with health features and disease labels.
        """
        if seed is not None:
            self.rng = np.random.RandomState(seed)

        # 1. Age: 25-85 (normal dist around 55 + bias)
        age = self.rng.normal(loc=55.0 + age_bias, scale=12.0, size=n_records)
        age = np.clip(np.round(age), 25.0, 85.0)

        # 2. Gender: 0 (female) or 1 (male)
        gender = self.rng.binomial(n=1, p=0.5, size=n_records).astype(float)

        # 3. BMI: 18-45 (normal dist around 27 + bias)
        bmi = self.rng.normal(loc=27.0 + bmi_bias, scale=5.0, size=n_records)
        bmi = np.clip(np.round(bmi, 1), 18.0, 45.0)

        # 4. Blood pressure systolic: 90-200
        bp_sys = self.rng.normal(loc=125.0 + bp_bias, scale=18.0, size=n_records)
        bp_sys = np.clip(np.round(bp_sys), 90.0, 200.0)

        # 5. Blood pressure diastolic: 60-130 (physiologically correlated with systolic)
        bp_dia_base = 0.55 * bp_sys + 12.0
        bp_dia = bp_dia_base + self.rng.normal(loc=0.0, scale=6.0, size=n_records)
        bp_dia = np.clip(np.round(bp_dia), 60.0, 130.0)

        # 6. Cholesterol: 120-350
        chol = self.rng.normal(loc=200.0 + chol_bias, scale=38.0, size=n_records)
        chol = np.clip(np.round(chol), 120.0, 350.0)

        # 7. Glucose: 60-300
        glucose = self.rng.normal(loc=105.0 + glucose_bias, scale=36.0, size=n_records)
        glucose = np.clip(np.round(glucose), 60.0, 300.0)

        # 8. Smoking status: 0 (never), 1 (former), 2 (current)
        smoking = self.rng.choice([0, 1, 2], p=[0.55, 0.25, 0.20], size=n_records).astype(float)

        # 9. Heart rate: 50-120
        hr = self.rng.normal(loc=72.0, scale=11.0, size=n_records)
        hr = np.clip(np.round(hr), 50.0, 120.0)

        # Correlated disease labels
        labels = self._generate_disease_labels(
            age=age,
            bmi=bmi,
            bp_sys=bp_sys,
            bp_dia=bp_dia,
            chol=chol,
            glucose=glucose,
            smoking=smoking,
        )

        records: List[Dict[str, Any]] = []
        for i in range(n_records):
            records.append(
                {
                    "patient_id": f"{hospital_id}_p_{i:04d}",
                    "hospital_id": hospital_id,
                    "age": float(age[i]),
                    "gender": float(gender[i]),
                    "bmi": float(bmi[i]),
                    "blood_pressure_systolic": float(bp_sys[i]),
                    "blood_pressure_diastolic": float(bp_dia[i]),
                    "cholesterol": float(chol[i]),
                    "glucose": float(glucose[i]),
                    "smoking_status": float(smoking[i]),
                    "heart_rate": float(hr[i]),
                    "diabetes": int(labels["diabetes"][i]),
                    "heart_disease": int(labels["heart_disease"][i]),
                    "kidney_disease": int(labels["kidney_disease"][i]),
                }
            )

        return records

    def generate_hospital_datasets(
        self,
        n_hospitals: int = 3,
        records_per_hospital: int = 100,
        seed: Optional[int] = 42,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate partitioned datasets simulating real-world non-IID hospital heterogeneity.

        Args:
            n_hospitals: Number of participating hospitals.
            records_per_hospital: Number of patient records per hospital.
            seed: Master random seed.

        Returns:
            Dictionary mapping hospital ID to list of patient records.
        """
        master_rng = np.random.RandomState(seed)
        datasets: Dict[str, List[Dict[str, Any]]] = {}

        # Heterogeneous population profiles (simulating urban, cardiac-focused, endocrine-focused, etc.)
        profiles = [
            # Hospital 1: General community hospital (balanced)
            {"age_bias": 0.0, "bmi_bias": 0.0, "bp_bias": 0.0, "glucose_bias": 0.0, "chol_bias": 0.0},
            # Hospital 2: Geriatric & Cardiology specialized center (older, higher BP, higher chol)
            {"age_bias": 8.0, "bmi_bias": 1.5, "bp_bias": 12.0, "glucose_bias": 5.0, "chol_bias": 22.0},
            # Hospital 3: Metabolic & Bariatric center (higher BMI, higher glucose)
            {"age_bias": -3.0, "bmi_bias": 6.0, "bp_bias": 4.0, "glucose_bias": 25.0, "chol_bias": 10.0},
            # Hospital 4: Regional suburban clinic (slightly younger, lower BP)
            {"age_bias": -5.0, "bmi_bias": -1.0, "bp_bias": -6.0, "glucose_bias": -5.0, "chol_bias": -8.0},
        ]

        for idx in range(n_hospitals):
            hid = f"hospital_{idx + 1}"
            prof = profiles[idx % len(profiles)]
            h_seed = int(master_rng.randint(0, 1_000_000))
            records = self.generate_patient_records(
                n_records=records_per_hospital,
                hospital_id=hid,
                age_bias=prof["age_bias"],
                bmi_bias=prof["bmi_bias"],
                bp_bias=prof["bp_bias"],
                glucose_bias=prof["glucose_bias"],
                chol_bias=prof["chol_bias"],
                seed=h_seed,
            )
            datasets[hid] = records

        return datasets
