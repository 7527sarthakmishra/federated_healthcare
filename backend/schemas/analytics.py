from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class DiseaseStat(BaseModel):
    disease: str
    positive_count: int
    negative_count: int
    prevalence_percentage: float

class DashboardStats(BaseModel):
    total_hospitals: int
    active_hospitals: int
    total_patients: int
    total_predictions: int
    completed_rounds: int
    global_model_accuracy: float
    model_accuracy: Optional[float] = None
    total_privacy_budget_spent: float
    total_privacy_budget_limit: float
    privacy_budget_remaining: Optional[float] = None
    disease_prevalence: Dict[str, float]
    kpis: Optional[Dict[str, Any]] = None

class TrainingProgressPoint(BaseModel):
    round_number: int
    global_accuracy: float
    global_loss: float
    privacy_budget_spent: float
    participating_hospitals: int
    completed_at: Optional[datetime]

class TrainingProgress(BaseModel):
    rounds: List[TrainingProgressPoint]
    current_accuracy: float
    improvement_rate: float

class PrivacyMetrics(BaseModel):
    total_budget_limit: float
    budget_spent: float
    budget_remaining: float
    epsilon_per_round: float
    delta: float
    noise_mechanism: str
    noise_scale: float
    dp_guarantee_level: str  # Strong, Moderate, Relaxed

class HospitalComparisonItem(BaseModel):
    hospital_id: int
    name: str
    location: str
    total_patients: int
    data_contribution_score: float
    local_accuracy: float
    local_loss: float
    diabetes_cases: int
    heart_disease_cases: int
    kidney_disease_cases: int

class HospitalComparison(BaseModel):
    hospitals: List[HospitalComparisonItem]

class RiskFactorAnalysis(BaseModel):
    factor: str
    correlation_diabetes: float
    correlation_heart_disease: float
    correlation_kidney_disease: float
    high_risk_threshold: str
