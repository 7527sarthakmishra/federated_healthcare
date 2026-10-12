import os
import sys
import random
from datetime import datetime, timedelta

# Support running directly via `python main.py` or `uvicorn main:app` or as package `backend.main:app`
if not __package__:
    _backend_dir = os.path.dirname(os.path.abspath(__file__))
    _parent_dir = os.path.dirname(_backend_dir)
    if _parent_dir not in sys.path:
        sys.path.insert(0, _parent_dir)
    __package__ = "backend"

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .database import engine, Base, SessionLocal, get_db
from .models.hospital import Hospital
from .models.user import User
from .models.patient import PatientRecord
from .models.training import FederatedRound, LocalModelUpdate
from .models.prediction import PredictionLog
from .models.audit import AuditLog
from .utils.security import get_password_hash

# Routers
from .routers.auth import router as auth_router
from .routers.hospitals import router as hospitals_router
from .routers.patients import router as patients_router
from .routers.predictions import router as predictions_router
from .routers.federated import router as federated_router
from .routers.analytics import router as analytics_router
from .routers.audit import router as audit_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Privacy-Preserving Federated Learning Platform for Multi-Hospital Disease Prediction (FastAPI Backend)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(hospitals_router, prefix=settings.API_V1_STR)
app.include_router(patients_router, prefix=settings.API_V1_STR)
app.include_router(predictions_router, prefix=settings.API_V1_STR)
app.include_router(federated_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)

# Ensure tables are created immediately and seeded
Base.metadata.create_all(bind=engine)
_init_db = SessionLocal()
try:
    # Seed data will be defined below or execute safely
    pass
finally:
    _init_db.close()

@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    """Health status endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "project": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

def seed_demo_data(db: Session):
    """Seed initial demo hospitals, admin user, ~100 anonymized patients, and 3 federated rounds."""
    # 1. Seed Hospitals if not exists
    if db.query(Hospital).count() == 0:
        hospitals = [
            Hospital(
                name="City General Hospital",
                location="Metropolitan District, Building A",
                total_patients=0,
                data_contribution_score=9.5,
                is_active=True,
                joined_at=datetime.utcnow() - timedelta(days=90)
            ),
            Hospital(
                name="Regional Medical Center",
                location="Eastern Valley, Health Campus",
                total_patients=0,
                data_contribution_score=8.7,
                is_active=True,
                joined_at=datetime.utcnow() - timedelta(days=75)
            ),
            Hospital(
                name="University Health System",
                location="Academic Quad, Pavilion 4",
                total_patients=0,
                data_contribution_score=9.1,
                is_active=True,
                joined_at=datetime.utcnow() - timedelta(days=60)
            )
        ]
        db.add_all(hospitals)
        db.commit()

    hospitals = db.query(Hospital).all()
    h_map = {h.name: h.id for h in hospitals}

    # 2. Seed Admin User
    admin_user = db.query(User).filter(User.email == "admin@fedhealth.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@fedhealth.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            hospital_id=hospitals[0].id if hospitals else None,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=90)
        )
        db.add(admin_user)

        # Also add a sample researcher and hospital admin
        researcher_user = User(
            email="researcher@fedhealth.com",
            username="dr_curie",
            hashed_password=get_password_hash("researcher123"),
            role="researcher",
            hospital_id=hospitals[1].id if len(hospitals) > 1 else None,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=60)
        )
        hospital_admin = User(
            email="hospital_admin@fedhealth.com",
            username="hosp_admin",
            hashed_password=get_password_hash("hospital123"),
            role="hospital_admin",
            hospital_id=hospitals[0].id if hospitals else None,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=45)
        )
        db.add_all([researcher_user, hospital_admin])
        db.commit()

    # 3. Seed ~100 Sample Patient Records (anonymized clinical cohort)
    patient_count = db.query(PatientRecord).count()
    if patient_count == 0:
        random.seed(42)  # Deterministic seed for repeatable test data
        genders = ["Male", "Female"]
        smoking_choices = ["never", "never", "former", "current"]

        patient_records = []
        for i in range(105):
            hosp = hospitals[i % len(hospitals)]
            age = random.randint(22, 78)
            gender = random.choice(genders)
            
            # Correlated clinical features
            has_diabetes = False
            has_heart = False
            has_kidney = False

            # Randomize base metrics
            bmi = round(random.uniform(19.0, 38.0), 1)
            glucose = round(random.uniform(75.0, 220.0), 1)
            cholesterol = round(random.uniform(150.0, 290.0), 1)
            systolic = random.randint(105, 175)
            diastolic = random.randint(65, 105)
            heart_rate = random.randint(58, 98)
            smoking = random.choice(smoking_choices)

            # Assign logical label correlation
            if glucose > 135 or (bmi > 31 and random.random() < 0.65):
                has_diabetes = True
            if systolic > 140 or cholesterol > 230 or (smoking == "current" and age > 50 and random.random() < 0.6):
                has_heart = True
            if (systolic > 145 and glucose > 140) or (age > 65 and random.random() < 0.4):
                has_kidney = True

            record = PatientRecord(
                hospital_id=hosp.id,
                age=age,
                gender=gender,
                bmi=bmi,
                blood_pressure_systolic=systolic,
                blood_pressure_diastolic=diastolic,
                cholesterol=cholesterol,
                glucose=glucose,
                smoking_status=smoking,
                heart_rate=heart_rate,
                has_diabetes=has_diabetes,
                has_heart_disease=has_heart,
                has_kidney_disease=has_kidney,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 80))
            )
            patient_records.append(record)

        db.add_all(patient_records)
        db.commit()

        # Update hospital total patient counts
        for h in hospitals:
            count = db.query(PatientRecord).filter(PatientRecord.hospital_id == h.id).count()
            h.total_patients = count
            h.data_contribution_score = round(min(10.0, 7.5 + (count * 0.05)), 2)
        db.commit()

    # 4. Seed 3 Completed Federated Rounds
    rounds_count = db.query(FederatedRound).count()
    if rounds_count == 0:
        round1_time = datetime.utcnow() - timedelta(days=14)
        round2_time = datetime.utcnow() - timedelta(days=7)
        round3_time = datetime.utcnow() - timedelta(days=1)

        r1 = FederatedRound(
            round_number=1,
            global_accuracy=0.812,
            global_loss=0.485,
            participating_hospitals=len(hospitals),
            privacy_budget_spent=1.0,
            status="completed",
            started_at=round1_time - timedelta(minutes=45),
            completed_at=round1_time
        )
        r2 = FederatedRound(
            round_number=2,
            global_accuracy=0.854,
            global_loss=0.362,
            participating_hospitals=len(hospitals),
            privacy_budget_spent=1.0,
            status="completed",
            started_at=round2_time - timedelta(minutes=50),
            completed_at=round2_time
        )
        r3 = FederatedRound(
            round_number=3,
            global_accuracy=0.892,
            global_loss=0.258,
            participating_hospitals=len(hospitals),
            privacy_budget_spent=1.0,
            status="completed",
            started_at=round3_time - timedelta(minutes=55),
            completed_at=round3_time
        )
        db.add_all([r1, r2, r3])
        db.commit()

        # Local model updates for round 1, 2, 3
        local_updates = [
            # Round 1
            LocalModelUpdate(round_id=r1.id, hospital_id=hospitals[0].id, local_accuracy=0.805, local_loss=0.492, samples_used=35, noise_added=0.035, created_at=round1_time),
            LocalModelUpdate(round_id=r1.id, hospital_id=hospitals[1].id, local_accuracy=0.818, local_loss=0.478, samples_used=35, noise_added=0.032, created_at=round1_time),
            LocalModelUpdate(round_id=r1.id, hospital_id=hospitals[2].id, local_accuracy=0.812, local_loss=0.486, samples_used=35, noise_added=0.034, created_at=round1_time),
            # Round 2
            LocalModelUpdate(round_id=r2.id, hospital_id=hospitals[0].id, local_accuracy=0.849, local_loss=0.370, samples_used=35, noise_added=0.028, created_at=round2_time),
            LocalModelUpdate(round_id=r2.id, hospital_id=hospitals[1].id, local_accuracy=0.861, local_loss=0.355, samples_used=35, noise_added=0.025, created_at=round2_time),
            LocalModelUpdate(round_id=r2.id, hospital_id=hospitals[2].id, local_accuracy=0.852, local_loss=0.364, samples_used=35, noise_added=0.027, created_at=round2_time),
            # Round 3
            LocalModelUpdate(round_id=r3.id, hospital_id=hospitals[0].id, local_accuracy=0.888, local_loss=0.264, samples_used=35, noise_added=0.021, created_at=round3_time),
            LocalModelUpdate(round_id=r3.id, hospital_id=hospitals[1].id, local_accuracy=0.897, local_loss=0.249, samples_used=35, noise_added=0.019, created_at=round3_time),
            LocalModelUpdate(round_id=r3.id, hospital_id=hospitals[2].id, local_accuracy=0.891, local_loss=0.260, samples_used=35, noise_added=0.020, created_at=round3_time),
        ]
        db.add_all(local_updates)
        db.commit()

    # 5. Seed Initial Audit Log
    if db.query(AuditLog).count() == 0:
        db.add(AuditLog(
            user_id=1,
            action="SYSTEM_INITIALIZE",
            resource_type="Platform",
            resource_id="init",
            details="Federated Healthcare Platform initialized with Differential Privacy and demo hospital silos.",
            ip_address="127.0.0.1",
            created_at=datetime.utcnow() - timedelta(days=90)
        ))
        db.commit()

@app.on_event("startup")
def on_startup():
    """Create database tables and seed baseline demo records."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # Seed data
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()

# Ensure database is prepared immediately upon module import
try:
    on_startup()
except Exception:
    pass
