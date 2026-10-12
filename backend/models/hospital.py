from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    location = Column(String(255), nullable=False)
    total_patients = Column(Integer, default=0)
    data_contribution_score = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="hospital")
    patients = relationship("PatientRecord", back_populates="hospital")
    model_updates = relationship("LocalModelUpdate", back_populates="hospital")
