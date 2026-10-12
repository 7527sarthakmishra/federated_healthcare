from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: str = "researcher"  # admin, researcher, hospital_admin
    hospital_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username_or_email: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

    @property
    def identifier(self) -> str:
        return self.username_or_email or self.email or self.username or ""

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    hospital_id: Optional[int] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str
    hospital_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
