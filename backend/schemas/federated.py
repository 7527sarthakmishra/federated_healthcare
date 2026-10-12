from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TrainingConfig(BaseModel):
    num_rounds: int = Field(default=1, ge=1, le=50)
    epochs_per_round: int = Field(default=5, ge=1, le=50)
    learning_rate: float = Field(default=0.01, ge=0.0001, le=1.0)
    batch_size: int = Field(default=32, ge=8, le=256)
    noise_multiplier: float = Field(default=0.5, ge=0.0, le=5.0)
    clipping_norm: float = Field(default=1.0, ge=0.1, le=10.0)
    target_epsilon: float = Field(default=1.0, ge=0.1, le=10.0)
    disease_type: str = Field(default="all", description="all, diabetes, heart_disease, kidney_disease")

class LocalUpdateResponse(BaseModel):
    id: int
    round_id: int
    hospital_id: int
    hospital_name: Optional[str] = None
    local_accuracy: float
    local_loss: float
    samples_used: int
    noise_added: float
    created_at: datetime

    class Config:
        from_attributes = True

class RoundStatus(BaseModel):
    id: int
    round_number: int
    global_accuracy: Optional[float] = None
    global_loss: Optional[float] = None
    participating_hospitals: int
    privacy_budget_spent: float
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    local_updates: List[LocalUpdateResponse] = []

    class Config:
        from_attributes = True

class FederatedStatus(BaseModel):
    is_training: bool
    current_round: int
    total_rounds_completed: int
    latest_global_accuracy: float
    latest_global_loss: float
    participating_hospitals_count: int
    privacy_budget_spent: float
    privacy_budget_remaining: float
    status: str
