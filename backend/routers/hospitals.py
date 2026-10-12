from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.hospital import Hospital
from ..models.patient import PatientRecord
from ..models.user import User
from ..schemas.hospital import HospitalCreate, HospitalUpdate, HospitalResponse, HospitalStats
from ..utils.security import get_current_user, require_roles

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])

@router.get("/", response_model=List[HospitalResponse])
def list_hospitals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all participating hospitals."""
    return db.query(Hospital).offset(skip).limit(limit).all()

@router.post("/", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
def create_hospital(
    hospital_in: HospitalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """Register a new hospital institution (Admin only)."""
    existing = db.query(Hospital).filter(Hospital.name == hospital_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital with this name already exists"
        )
    
    hospital = Hospital(
        name=hospital_in.name,
        location=hospital_in.location,
        total_patients=0,
        data_contribution_score=0.0,
        is_active=True
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital

@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital_details(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific hospital."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return hospital

@router.get("/{hospital_id}/stats", response_model=HospitalStats)
def get_hospital_stats(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a specific hospital."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")

    patients = db.query(PatientRecord).filter(PatientRecord.hospital_id == hospital_id).all()
    count = len(patients)

    if count == 0:
        return HospitalStats(
            hospital_id=hospital.id,
            hospital_name=hospital.name,
            patient_count=0,
            data_contribution_score=hospital.data_contribution_score,
            diabetes_prevalence=0.0,
            heart_disease_prevalence=0.0,
            kidney_disease_prevalence=0.0,
            avg_patient_age=0.0
        )

    diabetes_count = sum(1 for p in patients if p.has_diabetes)
    heart_count = sum(1 for p in patients if p.has_heart_disease)
    kidney_count = sum(1 for p in patients if p.has_kidney_disease)
    avg_age = sum(p.age for p in patients) / count

    return HospitalStats(
        hospital_id=hospital.id,
        hospital_name=hospital.name,
        patient_count=count,
        data_contribution_score=hospital.data_contribution_score,
        diabetes_prevalence=round((diabetes_count / count) * 100, 2),
        heart_disease_prevalence=round((heart_count / count) * 100, 2),
        kidney_disease_prevalence=round((kidney_count / count) * 100, 2),
        avg_patient_age=round(avg_age, 1)
    )

@router.put("/{hospital_id}", response_model=HospitalResponse)
def update_hospital(
    hospital_id: int,
    hospital_update: HospitalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hospital_admin"]))
):
    """Update hospital details."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")

    if current_user.role == "hospital_admin" and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital admins can only update their own hospital"
        )

    if hospital_update.name is not None:
        hospital.name = hospital_update.name
    if hospital_update.location is not None:
        hospital.location = hospital_update.location
    if hospital_update.is_active is not None and current_user.role == "admin":
        hospital.is_active = hospital_update.is_active

    db.commit()
    db.refresh(hospital)
    return hospital
