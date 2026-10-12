"""Machine Learning and Federated Learning package for privacy-preserving disease prediction."""

from .data_preprocessing import (
    DataPreprocessor,
    FEATURE_NAMES,
    DISEASE_NAMES,
    DEFAULT_FEATURE_RANGES,
)
from .synthetic_data import SyntheticDataGenerator
from .models import DiseasePredictor, SklearnPredictor
from .differential_privacy import DifferentialPrivacy, PrivacyAccountant
from .federated_engine import FederatedServer, FederatedClient
from .prediction_service import PredictionService

__all__ = [
    "FEATURE_NAMES",
    "DISEASE_NAMES",
    "DEFAULT_FEATURE_RANGES",
    "DataPreprocessor",
    "SyntheticDataGenerator",
    "DiseasePredictor",
    "SklearnPredictor",
    "DifferentialPrivacy",
    "PrivacyAccountant",
    "FederatedServer",
    "FederatedClient",
    "PredictionService",
]
