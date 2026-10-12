from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from ..models.user import User
from ..models.hospital import Hospital
from ..models.audit import AuditLog
from ..schemas.auth import UserCreate, UserLogin, Token, UserResponse
from ..utils.security import get_password_hash, verify_password, create_access_token

class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate, ip_address: Optional[str] = None) -> User:
        # Check if email exists
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        # Check if username exists
        if db.query(User).filter(User.username == user_in.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Verify hospital if specified
        if user_in.hospital_id:
            hospital = db.query(Hospital).filter(Hospital.id == user_in.hospital_id).first()
            if not hospital:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Hospital with id {user_in.hospital_id} does not exist"
                )

        new_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            hospital_id=user_in.hospital_id,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Log audit
        audit = AuditLog(
            user_id=new_user.id,
            action="USER_REGISTERED",
            resource_type="User",
            resource_id=str(new_user.id),
            details=f"Registered user {new_user.username} with role {new_user.role}",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()

        return new_user

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin, ip_address: Optional[str] = None) -> Token:
        identifier = login_data.identifier
        user = db.query(User).filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "user_id": user.id, "username": user.username, "role": user.role}
        )

        # Log audit
        audit = AuditLog(
            user_id=user.id,
            action="USER_LOGIN",
            resource_type="User",
            resource_id=str(user.id),
            details=f"User {user.username} logged in successfully",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
