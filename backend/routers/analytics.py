from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..database import get_db
from ..models.user import User
from ..schemas.analytics import (
    DashboardStats,
    TrainingProgress,
    PrivacyMetrics,
    HospitalComparison,
    RiskFactorAnalysis
)
from ..services.analytics_service import AnalyticsService
from ..utils.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics & Insights"])

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve high-level operational and ML dashboard KPIs."""
    return AnalyticsService.get_dashboard_stats(db)

@router.get("/disease-distribution")
def get_disease_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve disease distribution across all hospital nodes."""
    return AnalyticsService.get_disease_distribution(db)

@router.get("/training-progress", response_model=TrainingProgress)
def get_training_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve training convergence curves and progress history."""
    return AnalyticsService.get_training_progress(db)

@router.get("/hospital-comparison", response_model=HospitalComparison)
def get_hospital_comparison(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare hospitals by patient counts, contribution scores, and local model accuracies."""
    return AnalyticsService.get_hospital_comparison(db)

@router.get("/privacy-metrics", response_model=PrivacyMetrics)
def get_privacy_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get differential privacy parameters and epsilon consumption stats."""
    return AnalyticsService.get_privacy_metrics(db)

@router.get("/risk-factors", response_model=List[RiskFactorAnalysis])
def get_risk_factors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get epidemiological risk factor correlations for diabetes, heart disease, and kidney disease."""
    return AnalyticsService.get_risk_factors(db)
