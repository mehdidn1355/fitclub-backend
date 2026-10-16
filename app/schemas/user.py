from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    avatar: str
    is_active: bool
    plan: str
    created_at: datetime

    class Config:
        from_attributes = True


class TrainerResponse(UserResponse):
    specialty: Optional[str] = None
    bio: Optional[str] = None
    rating: int = 0
    sessions_count: int = 0