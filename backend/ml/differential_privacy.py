"""Differential Privacy mechanisms for Federated Learning in Healthcare.

Implements gradient clipping, calibrated Gaussian mechanism noise injection,
parameter privatizing, and cumulative privacy accounting (Moments Accountant / Renyi DP).
"""

from typing import Dict, List, Optional, Tuple, Union
import math
import numpy as np
import torch


class PrivacyAccountant:
    """Tracks cumulative privacy expenditure (epsilon, delta) across federated rounds.

    Uses the Moments Accountant / Renyi Differential Privacy (RDP) approximation
    for Gaussian mechanism under subsampled/federated SGD.
    """

    def __init__(
        self,
        target_epsilon: float = 5.0,
        target_delta: float = 1e-5,
    ):
        """Initialize the Privacy Accountant.

        Args:
            target_epsilon: Maximum privacy loss budget (epsilon).
            target_delta: Privacy failure probability parameter (delta).
        """
        self.target_epsilon = float(target_epsilon)
        self.target_delta = float(target_delta)
        self.current_epsilon = 0.0
        self.steps = 0
        self.history: List[Dict[str, float]] = []

    def step(
        self,
        noise_multiplier: float,
        sample_rate: float = 1.0,
        steps: int = 1,
    ) -> float:
        """Advance the accountant by a number of steps and compute cumulative epsilon.

        Under Gaussian mechanism composition:
        Using RDP-to-DP conversion approximation for subsampled Gaussian mechanism:
        epsilon ~ sample_rate * sqrt(2 * steps * ln(1/delta)) / noise_multiplier + ...
        or standard strong composition:
        eps_step = sample_rate * (math.sqrt(2 * math.log(1.25 / delta)) / noise_multiplier)
        cumulative_eps = math.sqrt(2 * total_steps * math.log(1.0 / delta)) * eps_single + ...

        Args:
            noise_multiplier: Ratio of Gaussian noise standard deviation to clipping threshold (sigma / C).
            sample_rate: Subsampling ratio q (fraction of hospital clients or samples per round).
            steps: Number of rounds/steps executed in this batch.

        Returns:
            Current cumulative epsilon.
        """
        if noise_multiplier <= 0:
            # Infinite privacy loss if no noise is added
            self.current_epsilon = float("inf")
            self.steps += steps
            return self.current_epsilon

        self.steps += steps
        q = min(1.0, max(1e-4, sample_rate))
        sigma = max(1e-4, noise_multiplier)

        # RDP approximation for orders alpha in [2, 64]
        # For Gaussian mechanism with sampling ratio q:
        # Renyi divergence of order alpha: D_alpha ~ (alpha * q^2) / (2 * sigma^2)
        alphas = np.linspace(1.5, 64.0, 100)
        rdp_totals = []
        for alpha in alphas:
            # Effective RDP for subsampled Gaussian
            rdp_per_step = (alpha * (q ** 2)) / (2.0 * (sigma ** 2))
            total_rdp = rdp_per_step * self.steps
            # Convert RDP at order alpha to (eps, delta):
            # eps = total_rdp + log(1 / delta) / (alpha - 1)
            eps_alpha = total_rdp + (math.log(1.0 / self.target_delta) / (alpha - 1.0))
            rdp_totals.append(eps_alpha)

        best_epsilon = float(np.min(rdp_totals))
        self.current_epsilon = best_epsilon

        self.history.append(
            {
                "step": self.steps,
                "noise_multiplier": sigma,
                "sample_rate": q,
                "current_epsilon": self.current_epsilon,
                "target_epsilon": self.target_epsilon,
                "target_delta": self.target_delta,
            }
        )
        return self.current_epsilon

    def get_epsilon(self) -> float:
        """Return the current cumulative epsilon."""
        return self.current_epsilon

    def is_budget_exhausted(self) -> bool:
        """Check if the cumulative privacy spending has exceeded target epsilon."""
        return self.current_epsilon >= self.target_epsilon


class DifferentialPrivacy:
    """Differential Privacy engine supporting gradient clipping, noise injection,

    and model parameter privatization for federated learning rounds.
    """

    def __init__(
        self,
        epsilon: float = 5.0,
        delta: float = 1e-5,
        noise_multiplier: float = 1.0,
        max_grad_norm: float = 1.0,
    ):
        """Initialize the Differential Privacy engine.

        Args:
            epsilon: Total privacy budget limit.
            delta: Privacy loss relaxation parameter (e.g. 1e-5 for healthcare).
            noise_multiplier: Noise scale sigma = noise_multiplier * max_grad_norm.
            max_grad_norm: Maximum L2 gradient or update norm threshold (C).
        """
        self.epsilon = float(epsilon)
        self.delta = float(delta)
        self.noise_multiplier = float(noise_multiplier)
        self.max_grad_norm = float(max_grad_norm)
        self.accountant = PrivacyAccountant(target_epsilon=epsilon, target_delta=delta)

    def clip_gradients(
        self,
        gradients: Union[List[torch.Tensor], Dict[str, torch.Tensor]],
        max_norm: Optional[float] = None,
    ) -> Tuple[Union[List[torch.Tensor], Dict[str, torch.Tensor]], float]:
        """Clip gradients by global L2 norm to ensure bounded sensitivity C.

        Args:
            gradients: List or Dict of gradient tensors.
            max_norm: Optional clipping norm threshold (defaults to self.max_grad_norm).

        Returns:
            Tuple of (clipped_gradients, total_norm).
        """
        threshold = max_norm if max_norm is not None else self.max_grad_norm

        if isinstance(gradients, dict):
            grad_list = [g for g in gradients.values() if g is not None]
        else:
            grad_list = [g for g in gradients if g is not None]

        if not grad_list:
            return gradients, 0.0

        total_norm_sq = sum(torch.sum(g ** 2).item() for g in grad_list)
        total_norm = math.sqrt(total_norm_sq)
        clip_coef = min(1.0, threshold / (total_norm + 1e-7))

        if isinstance(gradients, dict):
            clipped = {k: (v * clip_coef if v is not None else None) for k, v in gradients.items()}
            return clipped, total_norm
        else:
            clipped = [(g * clip_coef if g is not None else None) for g in gradients]
            return clipped, total_norm

    def add_noise_to_gradients(
        self,
        gradients: Union[List[torch.Tensor], Dict[str, torch.Tensor]],
        sensitivity: Optional[float] = None,
    ) -> Union[List[torch.Tensor], Dict[str, torch.Tensor]]:
        """Add calibrated Gaussian noise N(0, (sigma * sensitivity)^2) to gradients.

        Args:
            gradients: List or dict of gradient tensors.
            sensitivity: L2 sensitivity (defaults to self.max_grad_norm).

        Returns:
            Noisy gradients with same structure.
        """
        sens = sensitivity if sensitivity is not None else self.max_grad_norm
        sigma = self.noise_multiplier * sens

        if sigma <= 0.0:
            return gradients

        if isinstance(gradients, dict):
            noisy = {}
            for k, g in gradients.items():
                if g is not None:
                    noise = torch.randn_like(g) * sigma
                    noisy[k] = g + noise
                else:
                    noisy[k] = None
            return noisy
        else:
            noisy_list = []
            for g in gradients:
                if g is not None:
                    noise = torch.randn_like(g) * sigma
                    noisy_list.append(g + noise)
                else:
                    noisy_list.append(None)
            return noisy_list

    def privatize_model_update(
        self,
        model_params: Dict[str, torch.Tensor],
        sensitivity: Optional[float] = None,
    ) -> Dict[str, torch.Tensor]:
        """Add calibrated Gaussian noise to model parameter updates before transmission.

        Args:
            model_params: Dictionary of weight/bias tensors.
            sensitivity: Sensitivity bound (defaults to self.max_grad_norm / num_samples).

        Returns:
            Dictionary of privatized parameter tensors.
        """
        sens = sensitivity if sensitivity is not None else (self.max_grad_norm * 0.1)
        sigma = self.noise_multiplier * sens

        privatized: Dict[str, torch.Tensor] = {}
        for key, tensor in model_params.items():
            # Never add noise to non-trainable buffers like batchnorm running mean/var or step counters
            if any(buf in key for buf in ["running_mean", "running_var", "num_batches_tracked"]):
                cloned = tensor.clone()
                if "running_var" in key:
                    cloned = torch.clamp(cloned, min=1e-4)
                privatized[key] = cloned
                continue

            # Only add calibrated noise to trainable floating point parameters (weights and biases)
            if tensor.dtype in (torch.float32, torch.float64) and ("weight" in key or "bias" in key):
                if sigma > 0.0:
                    noise = torch.randn_like(tensor) * sigma
                    noisy_param = tensor + noise
                    # Sanitize any potential NaNs/Infs
                    privatized[key] = torch.nan_to_num(noisy_param, nan=0.0)
                else:
                    privatized[key] = tensor.clone()
            else:
                privatized[key] = tensor.clone()

        return privatized

    def compute_privacy_spent(
        self,
        num_steps: int,
        sample_rate: float = 1.0,
    ) -> float:
        """Update and compute cumulative privacy spent.

        Args:
            num_steps: Number of federated rounds / SGD steps.
            sample_rate: Fraction of sampled clients/records.

        Returns:
            Updated epsilon value.
        """
        return self.accountant.step(
            noise_multiplier=self.noise_multiplier,
            sample_rate=sample_rate,
            steps=num_steps,
        )

    def get_privacy_budget_remaining(self) -> float:
        """Return remaining privacy budget (target_epsilon - current_epsilon)."""
        remaining = self.epsilon - self.accountant.get_epsilon()
        return max(0.0, float(remaining))
