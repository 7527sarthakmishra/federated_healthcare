from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class FederatedRound(Base):
    __tablename__ = "federated_rounds"

    id = Column(Integer, primary_key=True, index=True)
    round_number = Column(Integer, unique=True, nullable=False, index=True)
    global_accuracy = Column(Float, nullable=True)
    global_loss = Column(Float, nullable=True)
    participating_hospitals = Column(Integer, default=0)
    privacy_budget_spent = Column(Float, default=0.0)
    status = Column(String(50), default="pending")  # pending, training, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    local_updates = relationship("LocalModelUpdate", back_populates="round", cascade="all, delete-orphan")

class LocalModelUpdate(Base):
    __tablename__ = "local_model_updates"

    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("federated_rounds.id"), nullable=False, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    local_accuracy = Column(Float, nullable=False)
    local_loss = Column(Float, nullable=False)
    samples_used = Column(Integer, nullable=False)
    noise_added = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    round = relationship("FederatedRound", back_populates="local_updates")
    hospital = relationship("Hospital", back_populates="model_updates")
