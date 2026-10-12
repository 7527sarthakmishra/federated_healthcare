from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    disease_type = Column(String(50), nullable=False)  # diabetes, heart_disease, kidney_disease
    input_features = Column(JSON, nullable=False)
    prediction_result = Column(String(50), nullable=False)  # positive, negative, high_risk, low_risk
    confidence_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="predictions")
