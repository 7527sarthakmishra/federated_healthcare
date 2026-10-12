from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PatientRecordBase(BaseModel):
    hospital_id: int
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., description="Male, Female, or Other")
    bmi: float = Field(..., ge=10.0, le=70.0)
    blood_pressure_systolic: int = Field(..., ge=50, le=250)
    blood_pressure_diastolic: int = Field(..., ge=30, le=160)
    cholesterol: float = Field(..., ge=50.0, le=500.0)
    glucose: float = Field(..., ge=30.0, le=500.0)
    smoking_status: str = Field(..., description="never, former, or current")
    heart_rate: int = Field(..., ge=30, le=220)
    has_diabetes: bool = False
    has_heart_disease: bool = False
    has_kidney_disease: bool = False

class PatientRecordCreate(PatientRecordBase):
    pass

class PatientRecordResponse(PatientRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PatientStats(BaseModel):
    total_records: int
    avg_age: float
    avg_bmi: float
    avg_glucose: float
    avg_cholesterol: float
    diabetes_rate: float
    heart_disease_rate: float
    kidney_disease_rate: float
    gender_distribution: dict
    smoking_distribution: dict

class PatientBulkUploadResponse(BaseModel):
    message: str
    records_processed: int
    hospital_id: int
