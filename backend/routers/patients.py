from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from ..database import get_db
from ..models.patient import PatientRecord
from ..models.hospital import Hospital
from ..models.user import User
from ..schemas.patient import (
    PatientRecordCreate,
    PatientRecordResponse,
    PatientStats,
    PatientBulkUploadResponse
)
from ..utils.security import get_current_user, require_roles

router = APIRouter(prefix="/patients", tags=["Patients (Anonymized)"])

@router.post("/", response_model=PatientRecordResponse, status_code=status.HTTP_201_CREATED)
def add_patient_record(
    patient_in: PatientRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hospital_admin", "researcher"]))
):
    """Add a new anonymized patient record."""
    hospital = db.query(Hospital).filter(Hospital.id == patient_in.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    if current_user.role == "hospital_admin" and current_user.hospital_id != patient_in.hospital_id:
        raise HTTPException(status_code=403, detail="Hospital admins can only add records for their hospital")

    record = PatientRecord(**patient_in.model_dump())
    db.add(record)
    
    # Update hospital patient count
    hospital.total_patients += 1
    # Simple score update based on volume
    hospital.data_contribution_score = round(min(10.0, hospital.total_patients * 0.1), 2)
    
    db.commit()
    db.refresh(record)
    return record

@router.get("/", response_model=List[PatientRecordResponse])
def list_patient_records(
    hospital_id: Optional[int] = None,
    disease: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List anonymized patient records with pagination and filters."""
    query = db.query(PatientRecord)
    
    if current_user.role == "hospital_admin" and current_user.hospital_id:
        query = query.filter(PatientRecord.hospital_id == current_user.hospital_id)
    elif hospital_id:
        query = query.filter(PatientRecord.hospital_id == hospital_id)

    if disease == "diabetes":
        query = query.filter(PatientRecord.has_diabetes == True)
    elif disease == "heart_disease":
        query = query.filter(PatientRecord.has_heart_disease == True)
    elif disease == "kidney_disease":
        query = query.filter(PatientRecord.has_kidney_disease == True)

    return query.offset(skip).limit(limit).all()

@router.get("/stats", response_model=PatientStats)
def get_patient_statistics(
    hospital_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated cohort statistics across anonymized patient records."""
    query = db.query(PatientRecord)
    if hospital_id:
        query = query.filter(PatientRecord.hospital_id == hospital_id)
    elif current_user.role == "hospital_admin" and current_user.hospital_id:
        query = query.filter(PatientRecord.hospital_id == current_user.hospital_id)

    records = query.all()
    count = len(records)
    if count == 0:
        return PatientStats(
            total_records=0,
            avg_age=0.0,
            avg_bmi=0.0,
            avg_glucose=0.0,
            avg_cholesterol=0.0,
            diabetes_rate=0.0,
            heart_disease_rate=0.0,
            kidney_disease_rate=0.0,
            gender_distribution={"Male": 0, "Female": 0, "Other": 0},
            smoking_distribution={"never": 0, "former": 0, "current": 0}
        )

    avg_age = sum(r.age for r in records) / count
    avg_bmi = sum(r.bmi for r in records) / count
    avg_glucose = sum(r.glucose for r in records) / count
    avg_cholesterol = sum(r.cholesterol for r in records) / count

    diabetes_rate = (sum(1 for r in records if r.has_diabetes) / count) * 100
    heart_rate = (sum(1 for r in records if r.has_heart_disease) / count) * 100
    kidney_rate = (sum(1 for r in records if r.has_kidney_disease) / count) * 100

    gender_dist = {"Male": 0, "Female": 0, "Other": 0}
    smoking_dist = {"never": 0, "former": 0, "current": 0}

    for r in records:
        gender_dist[r.gender] = gender_dist.get(r.gender, 0) + 1
        smoking_dist[r.smoking_status] = smoking_dist.get(r.smoking_status, 0) + 1

    return PatientStats(
        total_records=count,
        avg_age=round(avg_age, 1),
        avg_bmi=round(avg_bmi, 1),
        avg_glucose=round(avg_glucose, 1),
        avg_cholesterol=round(avg_cholesterol, 1),
        diabetes_rate=round(diabetes_rate, 2),
        heart_disease_rate=round(heart_rate, 2),
        kidney_disease_rate=round(kidney_rate, 2),
        gender_distribution=gender_dist,
        smoking_distribution=smoking_dist
    )

@router.post("/bulk-upload", response_model=PatientBulkUploadResponse)
def bulk_upload_patient_data(
    records: List[PatientRecordCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "hospital_admin"]))
):
    """Bulk upload an array of anonymized patient records."""
    if not records:
        raise HTTPException(status_code=400, detail="No records provided")

    hospital_id = records[0].hospital_id
    if current_user.role == "hospital_admin" and current_user.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="Hospital admins can only upload records for their hospital")

    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Target hospital not found")

    new_entities = []
    for r in records:
        new_entities.append(PatientRecord(**r.model_dump()))

    db.add_all(new_entities)
    hospital.total_patients += len(new_entities)
    hospital.data_contribution_score = round(min(10.0, hospital.total_patients * 0.1), 2)
    db.commit()

    return PatientBulkUploadResponse(
        message="Bulk patient records uploaded successfully",
        records_processed=len(new_entities),
        hospital_id=hospital_id
    )

@router.get("/export")
def export_anonymized_data(
    hospital_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "researcher"]))
):
    """Export anonymized dataset for federated training or verification."""
    query = db.query(PatientRecord)
    if hospital_id:
        query = query.filter(PatientRecord.hospital_id == hospital_id)
    records = query.all()

    export_list = []
    for r in records:
        export_list.append({
            "id": r.id,
            "hospital_id": r.hospital_id,
            "age": r.age,
            "gender": r.gender,
            "bmi": r.bmi,
            "blood_pressure_systolic": r.blood_pressure_systolic,
            "blood_pressure_diastolic": r.blood_pressure_diastolic,
            "cholesterol": r.cholesterol,
            "glucose": r.glucose,
            "smoking_status": r.smoking_status,
            "heart_rate": r.heart_rate,
            "has_diabetes": r.has_diabetes,
            "has_heart_disease": r.has_heart_disease,
            "has_kidney_disease": r.has_kidney_disease
        })
    return {"total_records": len(export_list), "data": export_list}
