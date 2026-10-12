"""PyTorch and Scikit-Learn multi-label disease prediction models.

Includes DiseasePredictor (Deep MLP with parameter serialization for federated learning)
and SklearnPredictor (ensemble Random Forests with feature importance analysis).
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestClassifier

from .data_preprocessing import FEATURE_NAMES, DISEASE_NAMES


class DiseasePredictor(nn.Module):
    """3-layer deep MLP model for multi-label disease prediction (PyTorch).

    Architecture: 9 -> 64 -> 32 -> 3
    Supports Batch Normalization, ReLU activations, Dropout, and direct
    parameter serialization / deserialization for Federated Averaging.
    """

    def __init__(
        self,
        input_dim: int = 9,
        hidden_dim1: int = 64,
        hidden_dim2: int = 32,
        output_dim: int = 3,
        dropout_rate: float = 0.2,
    ):
        """Initialize the multi-label disease predictor.

        Args:
            input_dim: Number of input clinical features (default 9).
            hidden_dim1: First hidden layer dimensionality (default 64).
            hidden_dim2: Second hidden layer dimensionality (default 32).
            output_dim: Number of target diseases (default 3).
            dropout_rate: Dropout probability for regularization.
        """
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim

        self.fc1 = nn.Linear(input_dim, hidden_dim1)
        self.bn1 = nn.BatchNorm1d(hidden_dim1)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout_rate)

        self.fc2 = nn.Linear(hidden_dim1, hidden_dim2)
        self.bn2 = nn.BatchNorm1d(hidden_dim2)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout_rate)

        self.fc3 = nn.Linear(hidden_dim2, output_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass computing raw logits for multi-label binary cross entropy.

        Args:
            x: Input tensor of shape (batch_size, input_dim).

        Returns:
            Logits tensor of shape (batch_size, output_dim).
        """
        # If batch size is 1 during evaluation or BatchNorm evaluation mode:
        # Note: BatchNorm1d requires >1 sample during training, but handles 1 during eval
        x = self.fc1(x)
        if x.size(0) > 1 or not self.training:
            x = self.bn1(x)
        x = self.relu1(x)
        x = self.dropout1(x)

        x = self.fc2(x)
        if x.size(0) > 1 or not self.training:
            x = self.bn2(x)
        x = self.relu2(x)
        x = self.dropout2(x)

        logits = self.fc3(x)
        return logits

    def predict(
        self,
        x: Union[np.ndarray, torch.Tensor],
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """Predict disease probabilities and binary classifications.

        Args:
            x: Feature input as numpy array (N, 9) or torch Tensor.
            threshold: Decision boundary probability threshold (default 0.5).

        Returns:
            Dictionary containing:
                - 'probabilities': np.ndarray of shape (N, 3)
                - 'predictions': np.ndarray of shape (N, 3) with binary 0/1
                - 'diseases': list of disease names
        """
        self.eval()
        with torch.no_grad():
            if isinstance(x, np.ndarray):
                tensor_x = torch.from_numpy(x).float()
            else:
                tensor_x = x.float()

            logits = self.forward(tensor_x)
            probs = torch.sigmoid(logits).cpu().numpy()
            preds = (probs >= threshold).astype(int)

        return {
            "probabilities": probs,
            "predictions": preds,
            "diseases": DISEASE_NAMES,
        }

    def get_model_params(self) -> Dict[str, torch.Tensor]:
        """Extract a detached, cloned dictionary of all model state tensors (weights/biases).

        Returns:
            Dictionary mapping layer parameter names to cloned CPU tensors.
        """
        return {k: v.detach().cpu().clone() for k, v in self.state_dict().items()}

    def set_model_params(self, params: Dict[str, torch.Tensor]) -> None:
        """Load external model parameters (e.g. from aggregated FedAvg).

        Args:
            params: Dictionary mapping parameter names to tensors.
        """
        new_state_dict = {}
        for k, v in params.items():
            if isinstance(v, np.ndarray):
                t = torch.from_numpy(v)
            else:
                t = v.clone()
            if "running_var" in k:
                t = torch.clamp(t, min=1e-4)
            t = torch.nan_to_num(t, nan=0.0)
            new_state_dict[k] = t
        self.load_state_dict(new_state_dict, strict=False)


class SklearnPredictor:
    """Multi-disease predictor using Random Forest ensembles with feature importances."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = 6,
        random_state: int = 42,
    ):
        """Initialize independent Random Forest classifiers for each target disease.

        Args:
            n_estimators: Number of trees in each forest.
            max_depth: Maximum tree depth.
            random_state: Random seed for reproducibility.
        """
        self.disease_names = DISEASE_NAMES
        self.feature_names = FEATURE_NAMES
        self.models: Dict[str, RandomForestClassifier] = {
            d: RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=random_state,
                class_weight="balanced",
            )
            for d in self.disease_names
        }
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train separate Random Forest models for each disease target.

        Args:
            X: Input features array of shape (N, 9).
            y: Binary target array of shape (N, 3).

        Returns:
            Dictionary mapping disease to training accuracy.
        """
        accuracies = {}
        for idx, disease in enumerate(self.disease_names):
            y_disease = y[:, idx].astype(int)
            # Handle edge case where a disease only has single class in small batch
            if len(np.unique(y_disease)) < 2:
                # Add a dummy sample if single class
                y_disease = y_disease.copy()
                y_disease[0] = 1 - y_disease[0]

            self.models[disease].fit(X, y_disease)
            train_preds = self.models[disease].predict(X)
            accuracies[disease] = float(np.mean(train_preds == y[:, idx]))

        self.is_trained = True
        return accuracies

    def predict(
        self,
        X: np.ndarray,
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """Predict disease presence and probability scores.

        Args:
            X: Feature array of shape (N, 9).
            threshold: Decision probability threshold.

        Returns:
            Dictionary mapping disease names to prediction arrays and probabilities.
        """
        results: Dict[str, Any] = {}
        for disease in self.disease_names:
            model = self.models[disease]
            if hasattr(model, "classes_") and len(model.classes_) > 1:
                prob = model.predict_proba(X)[:, 1]
            else:
                prob = np.full(shape=(X.shape[0],), fill_value=0.5)

            pred = (prob >= threshold).astype(int)
            results[disease] = {
                "probability": prob,
                "prediction": pred,
            }

        return results

    def get_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """Extract normalized feature importance scores per disease.

        Returns:
            Dictionary mapping disease to a dictionary of {feature_name: importance_score}.
        """
        importances: Dict[str, Dict[str, float]] = {}
        for disease in self.disease_names:
            model = self.models[disease]
            if hasattr(model, "feature_importances_"):
                imp = model.feature_importances_
                importances[disease] = {
                    feat: float(imp[i]) for i, feat in enumerate(self.feature_names)
                }
            else:
                # Default baseline uniform importance if untrained
                importances[disease] = {
                    feat: 1.0 / len(self.feature_names) for feat in self.feature_names
                }

        return importances
