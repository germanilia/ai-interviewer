from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    role: UserRole = UserRole.USER
    cognito_sub: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    cognito_sub: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user responses."""
    id: int
    is_active: bool
    role: UserRole
    cognito_sub: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Schema for user data as stored in database."""
    pass