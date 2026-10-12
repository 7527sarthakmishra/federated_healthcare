from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HospitalBase(BaseModel):
    name: str
    location: str

class HospitalCreate(HospitalBase):
    pass

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None

class HospitalResponse(HospitalBase):
    id: int
    total_patients: int
    data_contribution_score: float
    is_active: bool
    joined_at: datetime

    class Config:
        from_attributes = True

class HospitalStats(BaseModel):
    hospital_id: int
    hospital_name: str
    patient_count: int
    data_contribution_score: float
    diabetes_prevalence: float
    heart_disease_prevalence: float
    kidney_disease_prevalence: float
    avg_patient_age: float
