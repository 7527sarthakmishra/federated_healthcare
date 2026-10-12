"""Federated Learning engine implementing Federated Averaging (FedAvg)

with Differential Privacy and multi-hospital client simulation.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import copy
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

logger = logging.getLogger("federated_engine")

try:
    from .models import DiseasePredictor
    from .differential_privacy import DifferentialPrivacy
    from .data_preprocessing import DataPreprocessor, DISEASE_NAMES
except ImportError:
    try:
        from backend.ml.models import DiseasePredictor
        from backend.ml.differential_privacy import DifferentialPrivacy
        from backend.ml.data_preprocessing import DataPreprocessor, DISEASE_NAMES
    except ImportError:
        from ml.models import DiseasePredictor
        from ml.differential_privacy import DifferentialPrivacy
        from ml.data_preprocessing import DataPreprocessor, DISEASE_NAMES


class FederatedClient:
    """Simulates a hospital node in the federated network with private local data."""

    def __init__(
        self,
        hospital_id: str,
        local_data: np.ndarray,
        local_labels: np.ndarray,
    ):
        """Initialize the hospital federated client.

        Args:
            hospital_id: Unique hospital identifier.
            local_data: Local patient feature matrix X (normalized, shape N x 9).
            local_labels: Local binary disease labels y (shape N x 3).
        """
        self.hospital_id = str(hospital_id)
        self.local_data = torch.from_numpy(np.asarray(local_data, dtype=np.float32))
        self.local_labels = torch.from_numpy(np.asarray(local_labels, dtype=np.float32))
        self.sample_count = len(local_data)

    def train_local(
        self,
        global_params: Dict[str, torch.Tensor],
        epochs: int = 5,
        lr: float = 0.01,
        batch_size: int = 16,
    ) -> Tuple[Dict[str, torch.Tensor], int, Dict[str, float]]:
        """Train a local copy of the model initialized with global parameters.

        Args:
            global_params: State dict parameters distributed by the central server.
            epochs: Number of local SGD epochs.
            lr: Local optimizer learning rate.
            batch_size: Batch size for mini-batch SGD.

        Returns:
            Tuple of (updated_model_params, sample_count, local_metrics_dict).
        """
        local_model = DiseasePredictor()
        local_model.set_model_params(global_params)
        local_model.train()

        criterion = nn.BCEWithLogitsLoss()
        optimizer = optim.Adam(local_model.parameters(), lr=lr, weight_decay=1e-4)

        n_samples = self.sample_count
        if n_samples == 0:
            return global_params, 0, {"loss": 0.0, "accuracy": 0.0}

        dataset = torch.utils.data.TensorDataset(self.local_data, self.local_labels)
        # Avoid drop_last unless very small batch
        use_shuffle = n_samples > 1
        loader = torch.utils.data.DataLoader(
            dataset,
            batch_size=min(batch_size, n_samples),
            shuffle=use_shuffle,
        )

        total_loss = 0.0
        batches_processed = 0

        for epoch in range(epochs):
            epoch_loss = 0.0
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                logits = local_model(batch_x)
                loss = criterion(logits, batch_y)
                loss.backward()

                # Local gradient clipping for training stability
                torch.nn.utils.clip_grad_norm_(local_model.parameters(), max_norm=2.0)

                optimizer.step()
                epoch_loss += loss.item()
                batches_processed += 1
            total_loss += epoch_loss / max(1, len(loader))

        avg_loss = total_loss / max(1, epochs)

        # Evaluate local model performance
        local_model.eval()
        with torch.no_grad():
            eval_logits = local_model(self.local_data)
            eval_probs = torch.sigmoid(eval_logits).cpu().numpy()
            eval_preds = (eval_probs >= 0.5).astype(int)
            y_true = self.local_labels.cpu().numpy().astype(int)

            # Overall accuracy across all labels
            acc = float(np.mean(eval_preds == y_true))

            # Per disease accuracies
            disease_accs = {}
            for i, d in enumerate(DISEASE_NAMES):
                disease_accs[f"{d}_acc"] = float(np.mean(eval_preds[:, i] == y_true[:, i]))

        local_metrics = {
            "loss": float(avg_loss),
            "accuracy": acc,
            **disease_accs,
        }

        updated_params = local_model.get_model_params()
        return updated_params, n_samples, local_metrics


class FederatedServer:
    """Central Federated Learning Server managing rounds, aggregation,

    and differential privacy budget.
    """

    def __init__(
        self,
        num_hospitals: int = 3,
        privacy_budget: float = 5.0,
        noise_multiplier: float = 0.8,
        delta: float = 1e-5,
    ):
        """Initialize the Federated Server.

        Args:
            num_hospitals: Expected number of participating hospital nodes.
            privacy_budget: Total cumulative epsilon privacy budget.
            noise_multiplier: Calibrated noise scale sigma for DP Gaussian mechanism.
            delta: Privacy failure probability delta.
        """
        self.num_hospitals = num_hospitals
        self.privacy_budget = privacy_budget
        self.noise_multiplier = noise_multiplier

        # Global model instance
        self.global_model = DiseasePredictor()
        self.hospital_models: Dict[str, Dict[str, torch.Tensor]] = {}
        self.round_history: List[Dict[str, Any]] = []

        # Differential privacy engine
        self.dp = DifferentialPrivacy(
            epsilon=privacy_budget,
            delta=delta,
            noise_multiplier=noise_multiplier,
            max_grad_norm=1.0,
        )

        # Active round tracking
        self.current_round: int = 0
        self.pending_updates: List[Tuple[str, Dict[str, torch.Tensor], int, Dict[str, float]]] = []

    def start_round(self) -> int:
        """Initialize a new federated training round.

        Returns:
            The current active round index.
        """
        self.current_round += 1
        self.pending_updates = []
        logger.info(f"--- Starting Federated Round {self.current_round} ---")
        return self.current_round

    def receive_update(
        self,
        hospital_id: str,
        model_params: Dict[str, torch.Tensor],
        sample_count: int,
        metrics: Optional[Dict[str, float]] = None,
    ) -> None:
        """Receive local model updates and metadata from a hospital client.

        Args:
            hospital_id: Hospital node identifier.
            model_params: State dict of local parameters.
            sample_count: Number of patient samples trained on.
            metrics: Optional local performance metrics.
        """
        self.hospital_models[hospital_id] = model_params
        self.pending_updates.append(
            (hospital_id, model_params, sample_count, metrics or {})
        )
        logger.info(
            f"Received update from {hospital_id} ({sample_count} samples)"
        )

    def federated_averaging(
        self,
        local_updates: List[Tuple[Dict[str, torch.Tensor], int]],
    ) -> Dict[str, torch.Tensor]:
        """Implement the standard Federated Averaging (FedAvg) algorithm.

        Computes the weighted parameter average:
        theta_global = sum_{k=1}^K (n_k / N) * theta_k

        Args:
            local_updates: List of (model_params, sample_count) tuples.

        Returns:
            Weighted average parameter dictionary.
        """
        if not local_updates:
            return self.global_model.get_model_params()

        total_samples = sum(sample_count for _, sample_count in local_updates)
        if total_samples == 0:
            return self.global_model.get_model_params()

        base_params = local_updates[0][0]
        aggregated_params: Dict[str, torch.Tensor] = {}

        for key, tensor in base_params.items():
            # For floating point weights and biases, perform weighted average
            if tensor.dtype in (torch.float32, torch.float64):
                weighted_sum = torch.zeros_like(tensor, dtype=torch.float32)
                for params, sample_count in local_updates:
                    weight = float(sample_count) / float(total_samples)
                    weighted_sum += params[key].float() * weight
                aggregated_params[key] = weighted_sum
            else:
                # Integer tensors like num_batches_tracked take first or max
                aggregated_params[key] = tensor.clone()

        return aggregated_params

    def aggregate(self) -> Dict[str, Any]:
        """Aggregate all pending hospital model updates using FedAvg and inject DP noise.

        Returns:
            Summary dictionary containing aggregated metrics for the round.
        """
        if not self.pending_updates:
            logger.warning("Aggregate called with no pending hospital updates.")
            return {}

        total_samples = sum(s for _, _, s, _ in self.pending_updates)
        updates_for_fedavg = [(p, s) for _, p, s, _ in self.pending_updates]

        # 1. Standard FedAvg weighted aggregation
        raw_aggregated_params = self.federated_averaging(updates_for_fedavg)

        # 2. Add Differential Privacy calibrated Gaussian noise to parameter updates
        # Sensitivity is inversely proportional to sqrt(total_samples)
        dp_sensitivity = 1.0 / max(1.0, np.sqrt(float(total_samples)))
        privatized_params = self.dp.privatize_model_update(
            raw_aggregated_params, sensitivity=dp_sensitivity
        )

        # 3. Update global model with privatized aggregated parameters
        self.global_model.set_model_params(privatized_params)

        # 4. Advance privacy accountant
        spent_epsilon = self.dp.compute_privacy_spent(num_steps=1, sample_rate=1.0)
        remaining_budget = self.dp.get_privacy_budget_remaining()

        # 5. Compile round metrics
        per_hospital_accuracy = {
            hid: m.get("accuracy", 0.0) for hid, _, _, m in self.pending_updates
        }
        per_hospital_loss = {
            hid: m.get("loss", 0.0) for hid, _, _, m in self.pending_updates
        }

        avg_loss = float(
            sum(m.get("loss", 0.0) * s for _, _, s, m in self.pending_updates)
            / max(1, total_samples)
        )
        avg_acc = float(
            sum(m.get("accuracy", 0.0) * s for _, _, s, m in self.pending_updates)
            / max(1, total_samples)
        )

        round_summary = {
            "round": self.current_round,
            "participating_hospitals": len(self.pending_updates),
            "total_samples": total_samples,
            "global_loss": avg_loss,
            "global_accuracy": avg_acc,
            "per_hospital_accuracy": per_hospital_accuracy,
            "per_hospital_loss": per_hospital_loss,
            "privacy_budget_spent": float(spent_epsilon),
            "privacy_budget_remaining": float(remaining_budget),
            "privacy_exhausted": self.dp.accountant.is_budget_exhausted(),
        }

        self.round_history.append(round_summary)
        self.pending_updates = []
        return round_summary

    def get_global_model(self) -> DiseasePredictor:
        """Return the current global model instance."""
        return self.global_model

    def get_round_history(self) -> List[Dict[str, Any]]:
        """Return the training history across all federated rounds."""
        return copy.deepcopy(self.round_history)

    def simulate_federated_training(
        self,
        hospital_data_dict: Dict[str, List[Dict[str, Any]]],
        num_rounds: int = 5,
        epochs_per_round: int = 3,
        lr: float = 0.01,
        batch_size: int = 16,
    ) -> List[Dict[str, Any]]:
        """Simulate an end-to-end multi-round federated training session.

        Distributes global model -> each hospital trains locally -> collects updates ->
        aggregates with DP noise -> updates global model -> tracks metrics per round.

        Args:
            hospital_data_dict: Dictionary mapping hospital ID to list of patient records.
            num_rounds: Number of federated synchronization rounds.
            epochs_per_round: Local training epochs per client per round.
            lr: Client SGD learning rate.
            batch_size: Local batch size.

        Returns:
            List of metrics dictionaries for all completed rounds.
        """
        preprocessor = DataPreprocessor()
        clients: Dict[str, FederatedClient] = {}

        # Prepare clients with local data
        for hid, records in hospital_data_dict.items():
            X_norm, y = preprocessor.prepare_training_data(records)
            clients[hid] = FederatedClient(
                hospital_id=hid,
                local_data=X_norm,
                local_labels=y,
            )

        logger.info(
            f"Starting federated simulation across {len(clients)} hospitals for {num_rounds} rounds."
        )

        for r in range(num_rounds):
            self.start_round()
            global_params = self.global_model.get_model_params()

            # Local hospital client training
            for hid, client in clients.items():
                updated_params, sample_count, local_metrics = client.train_local(
                    global_params=global_params,
                    epochs=epochs_per_round,
                    lr=lr,
                    batch_size=batch_size,
                )
                self.receive_update(
                    hospital_id=hid,
                    model_params=updated_params,
                    sample_count=sample_count,
                    metrics=local_metrics,
                )

            # Central DP-FedAvg aggregation
            round_summary = self.aggregate()
            logger.info(
                f"Round {r + 1}/{num_rounds} complete: Acc={round_summary.get('global_accuracy', 0.0):.4f}, "
                f"Loss={round_summary.get('global_loss', 0.0):.4f}, "
                f"Epsilon spent={round_summary.get('privacy_budget_spent', 0.0):.3f}"
            )

        return self.get_round_history()
