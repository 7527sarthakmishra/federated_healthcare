from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.auth import UserCreate, UserLogin, UserResponse, Token, UserUpdate
from ..services.auth_service import AuthService
from ..utils.security import get_current_user, get_password_hash

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Register a new user (admin, researcher, or hospital_admin)."""
    client_ip = request.client.host if request.client else None
    return AuthService.register_user(db, user_in, ip_address=client_ip)

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticate a user and return JWT bearer token."""
    client_ip = request.client.host if request.client else None
    return AuthService.authenticate_user(db, login_data, ip_address=client_ip)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get profile of current authenticated user."""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update profile of current authenticated user."""
    if profile_data.email and profile_data.email != current_user.email:
        existing = db.query(User).filter(User.email == profile_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
        current_user.email = profile_data.email

    if profile_data.username and profile_data.username != current_user.username:
        existing = db.query(User).filter(User.username == profile_data.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = profile_data.username

    if profile_data.password:
        current_user.hashed_password = get_password_hash(profile_data.password)

    if profile_data.hospital_id is not None:
        current_user.hospital_id = profile_data.hospital_id

    db.commit()
    db.refresh(current_user)
    return current_user
