from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class PatientRecord(Base):
    __tablename__ = "patient_records"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    
    # Anonymized health features (No PII)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)  # Male, Female, Other
    bmi = Column(Float, nullable=False)
    blood_pressure_systolic = Column(Integer, nullable=False)
    blood_pressure_diastolic = Column(Integer, nullable=False)
    cholesterol = Column(Float, nullable=False)
    glucose = Column(Float, nullable=False)
    smoking_status = Column(String(50), nullable=False)  # never, former, current
    heart_rate = Column(Integer, nullable=False)
    
    # Target disease labels
    has_diabetes = Column(Boolean, nullable=False, default=False)
    has_heart_disease = Column(Boolean, nullable=False, default=False)
    has_kidney_disease = Column(Boolean, nullable=False, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hospital = relationship("Hospital", back_populates="patients")
