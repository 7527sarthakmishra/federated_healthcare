from .auth import router as auth_router
from .hospitals import router as hospitals_router
from .patients import router as patients_router
from .predictions import router as predictions_router
from .federated import router as federated_router
from .analytics import router as analytics_router
from .audit import router as audit_router

__all__ = [
    "auth_router",
    "hospitals_router",
    "patients_router",
    "predictions_router",
    "federated_router",
    "analytics_router",
    "audit_router"
]
