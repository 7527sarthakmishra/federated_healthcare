"""Data preprocessing pipelines and feature definitions for healthcare disease prediction.

Supports multi-hospital federated datasets with categorical encoding,
normalization, input validation, and dataset splitting.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


FEATURE_NAMES: List[str] = [
    "age",
    "gender",
    "bmi",
    "blood_pressure_systolic",
    "blood_pressure_diastolic",
    "cholesterol",
    "glucose",
    "smoking_status",
    "heart_rate",
]

DISEASE_NAMES: List[str] = [
    "diabetes",
    "heart_disease",
    "kidney_disease",
]

# Baseline feature ranges and default normalization statistics
DEFAULT_FEATURE_RANGES: Dict[str, Tuple[float, float]] = {
    "age": (18.0, 100.0),
    "gender": (0.0, 1.0),
    "bmi": (15.0, 50.0),
    "blood_pressure_systolic": (80.0, 220.0),
    "blood_pressure_diastolic": (50.0, 140.0),
    "cholesterol": (100.0, 400.0),
    "glucose": (50.0, 350.0),
    "smoking_status": (0.0, 2.0),
    "heart_rate": (40.0, 150.0),
}


class DataPreprocessor:
    """Preprocesses clinical tabular features for multi-label disease prediction models."""

    def __init__(self, feature_ranges: Optional[Dict[str, Tuple[float, float]]] = None):
        """Initialize the DataPreprocessor with feature ranges.

        Args:
            feature_ranges: Optional custom dictionary mapping feature names to (min, max).
        """
        self.feature_names = FEATURE_NAMES
        self.disease_names = DISEASE_NAMES
        self.feature_ranges = feature_ranges or DEFAULT_FEATURE_RANGES.copy()
        self.min_vals = np.array([self.feature_ranges[f][0] for f in self.feature_names], dtype=np.float32)
        self.max_vals = np.array([self.feature_ranges[f][1] for f in self.feature_names], dtype=np.float32)

    @staticmethod
    def encode_gender(val: Union[str, int, float]) -> float:
        """Encode gender representation to 0.0 (female) or 1.0 (male)."""
        if isinstance(val, (int, float)):
            return 1.0 if float(val) >= 0.5 else 0.0
        val_str = str(val).strip().lower()
        if val_str in ("m", "male", "1", "man"):
            return 1.0
        return 0.0

    @staticmethod
    def encode_smoking(val: Union[str, int, float]) -> float:
        """Encode smoking status to 0.0 (never), 1.0 (former), 2.0 (current)."""
        if isinstance(val, (int, float)):
            clamped = max(0.0, min(2.0, float(val)))
            return float(round(clamped))
        val_str = str(val).strip().lower()
        if "never" in val_str or val_str in ("0", "non-smoker", "no"):
            return 0.0
        if "former" in val_str or val_str in ("1", "ex-smoker", "past"):
            return 1.0
        if "current" in val_str or val_str in ("2", "smoker", "yes", "active"):
            return 2.0
        return 0.0

    def encode_categorical(self, record: Dict[str, Any]) -> Dict[str, float]:
        """Encode categorical attributes in a patient record dict.

        Args:
            record: Patient record dictionary.

        Returns:
            Dictionary with categorical features mapped to numeric values.
        """
        encoded = record.copy()
        if "gender" in encoded:
            encoded["gender"] = self.encode_gender(encoded["gender"])
        if "smoking_status" in encoded:
            encoded["smoking_status"] = self.encode_smoking(encoded["smoking_status"])
        return encoded

    def normalize_features(self, X: np.ndarray) -> np.ndarray:
        """Min-max normalize feature array to [0, 1] range.

        Args:
            X: Input array of shape (N, 9) or (9,).

        Returns:
            Normalized array in [0, 1].
        """
        X_arr = np.asarray(X, dtype=np.float32)
        denom = np.where(self.max_vals == self.min_vals, 1e-6, self.max_vals - self.min_vals)
        normalized = (X_arr - self.min_vals) / denom
        return np.clip(normalized, 0.0, 1.0).astype(np.float32)

    def denormalize_features(self, X_norm: np.ndarray) -> np.ndarray:
        """Denormalize scaled features back to original scale.

        Args:
            X_norm: Normalized array in [0, 1].

        Returns:
            Denormalized array in real clinical units.
        """
        denom = self.max_vals - self.min_vals
        return (np.asarray(X_norm, dtype=np.float32) * denom) + self.min_vals

    def validate_input(self, input_dict: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, float]]:
        """Validate single patient prediction inputs against clinical ranges.

        Args:
            input_dict: Dictionary containing health features.

        Returns:
            Tuple of (is_valid, error_messages, sanitized_features).
        """
        errors = []
        sanitized = {}

        encoded = self.encode_categorical(input_dict)

        for feature in self.feature_names:
            if feature not in encoded:
                errors.append(f"Missing required feature: '{feature}'")
                continue

            try:
                val = float(encoded[feature])
            except (ValueError, TypeError):
                errors.append(f"Feature '{feature}' must be numeric, got: {encoded[feature]}")
                continue

            min_bound, max_bound = self.feature_ranges[feature]
            # Permissive warning / clipping margin
            if val < (min_bound * 0.5) or val > (max_bound * 1.5):
                errors.append(
                    f"Feature '{feature}' value {val} is outside clinical boundary [{min_bound}, {max_bound}]"
                )
            sanitized[feature] = val

        is_valid = len(errors) == 0
        return is_valid, errors, sanitized

    def prepare_prediction_input(self, raw_input_dict: Dict[str, Any]) -> np.ndarray:
        """Prepare and normalize a single record for model inference.

        Args:
            raw_input_dict: Raw input dictionary.

        Returns:
            Normalized numpy array of shape (1, 9).
        """
        encoded = self.encode_categorical(raw_input_dict)
        feature_vals = []
        for feat in self.feature_names:
            val = float(encoded.get(feat, self.feature_ranges[feat][0]))
            feature_vals.append(val)
        raw_arr = np.array([feature_vals], dtype=np.float32)
        return self.normalize_features(raw_arr)

    def prepare_training_data(
        self, patient_records: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert a list of patient records into normalized X and binary multi-label y.

        Args:
            patient_records: List of dictionaries with features and disease targets.

        Returns:
            Tuple (X, y) as float32 numpy arrays.
            X shape: (N, 9), y shape: (N, 3).
        """
        if not patient_records:
            return np.empty((0, len(self.feature_names)), dtype=np.float32), np.empty(
                (0, len(self.disease_names)), dtype=np.float32
            )

        X_rows = []
        y_rows = []

        for record in patient_records:
            encoded = self.encode_categorical(record)
            x_vec = [float(encoded.get(f, self.feature_ranges[f][0])) for f in self.feature_names]
            y_vec = [float(encoded.get(d, 0.0)) for d in self.disease_names]
            X_rows.append(x_vec)
            y_rows.append(y_vec)

        X_raw = np.array(X_rows, dtype=np.float32)
        y_arr = np.array(y_rows, dtype=np.float32)
        X_norm = self.normalize_features(X_raw)

        return X_norm, y_arr

    def split_by_hospital(
        self,
        data: List[Dict[str, Any]],
        hospital_ids: Optional[List[str]] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group patient records by hospital identifier.

        Args:
            data: List of patient records with 'hospital_id' key.
            hospital_ids: Optional list of known hospital IDs.

        Returns:
            Dictionary mapping hospital ID to list of patient records.
        """
        result: Dict[str, List[Dict[str, Any]]] = {}
        if hospital_ids:
            for hid in hospital_ids:
                result[hid] = []

        for record in data:
            hid = str(record.get("hospital_id", "default_hospital"))
            if hid not in result:
                result[hid] = []
            result[hid].append(record)

        return result
