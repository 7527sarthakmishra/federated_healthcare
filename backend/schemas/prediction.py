from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

class PredictionRequest(BaseModel):
    disease_type: Optional[str] = Field("all", description="Target disease: diabetes, heart_disease, kidney_disease, or all")
    age: int = Field(50, ge=0, le=120)
    gender: str = Field("Male", description="Male, Female, or Other")
    bmi: float = Field(25.0, ge=10.0, le=70.0)
    blood_pressure_systolic: Optional[int] = Field(None, ge=50, le=250)
    bp_systolic: Optional[int] = Field(None, ge=50, le=250)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=30, le=160)
    bp_diastolic: Optional[int] = Field(None, ge=30, le=160)
    cholesterol: float = Field(200.0, ge=50.0, le=500.0)
    glucose: float = Field(100.0, ge=30.0, le=500.0)
    smoking_status: Optional[str] = Field(None, description="never, former, or current")
    smoking: Optional[str] = Field(None, description="Never, Former, or Current")
    heart_rate: int = Field(75, ge=30, le=220)

    @property
    def systolic_bp(self) -> int:
        if self.blood_pressure_systolic is not None:
            return self.blood_pressure_systolic
        if self.bp_systolic is not None:
            return self.bp_systolic
        return 120

    @property
    def diastolic_bp(self) -> int:
        if self.blood_pressure_diastolic is not None:
            return self.blood_pressure_diastolic
        if self.bp_diastolic is not None:
            return self.bp_diastolic
        return 80

    @property
    def clean_smoking(self) -> str:
        s = self.smoking_status or self.smoking or "never"
        return str(s).lower()

class DiseaseDetail(BaseModel):
    prediction: bool = False
    prediction_result: str = "negative"
    probability: float = 0.0
    confidence_score: float = 0.0
    confidence: float = 0.0
    risk_level: str = "Low"
    key_contributors: List[str] = []
    contributing_factors: List[str] = []

class PredictionResponse(BaseModel):
    prediction_id: str
    disease_type: str
    prediction_result: str  # positive, negative, high_risk, low_risk
    probability: float
    confidence_score: float
    risk_level: str  # Low, Moderate, High
    contributing_factors: List[str] = []
    diseases: Dict[str, Any] = {}
    results: Dict[str, Any] = {}
    feature_importance: List[Dict[str, Any]] = []
    privacy_guarantee: Dict[str, Any] = {}
    model_version: str
    timestamp: datetime

class PredictionHistory(BaseModel):
    id: int
    user_id: Optional[int]
    disease_type: str
    input_features: Dict[str, Any]
    prediction_result: str
    confidence_score: float
    created_at: datetime

    class Config:
        from_attributes = True

class ModelInfoResponse(BaseModel):
    disease_types: List[str]
    supported_features: List[str]
    current_global_round: int
    latest_accuracy: float
    differential_privacy_enabled: bool
    epsilon: float
