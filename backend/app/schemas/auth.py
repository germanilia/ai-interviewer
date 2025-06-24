"""
Authentication schemas for API requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


class SignUpRequest(BaseModel):
    """Request schema for user sign up"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=100)


class SignUpResponse(BaseModel):
    """Response schema for user sign up"""
    message: str
    user_sub: str
    user_confirmed: bool


class ConfirmSignUpRequest(BaseModel):
    """Request schema for confirming user sign up"""
    email: EmailStr
    confirmation_code: str = Field(..., min_length=6, max_length=6)


class ConfirmSignUpResponse(BaseModel):
    """Response schema for confirming user sign up"""
    message: str


class SignInRequest(BaseModel):
    """Request schema for user sign in"""
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    """Response schema for user sign in"""
    access_token: str
    id_token: str
    refresh_token: Optional[str]
    expires_in: int
    token_type: str = "Bearer"
    user: "UserInfo"


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token"""
    refresh_token: str
    email: EmailStr


class RefreshTokenResponse(BaseModel):
    """Response schema for refreshing access token"""
    access_token: str
    id_token: str
    expires_in: int
    token_type: str = "Bearer"


class UserInfo(BaseModel):
    """User information schema"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    user_sub: Optional[str] = None


class TokenData(BaseModel):
    """Token data schema for JWT validation"""
    username: Optional[str] = None
    user_sub: Optional[str] = None
    email: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """Request schema for changing password"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordResetRequest(BaseModel):
    """Request schema for password reset"""
    username: str


class PasswordResetConfirmRequest(BaseModel):
    """Request schema for confirming password reset"""
    username: str
    confirmation_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)


class MessageResponse(BaseModel):
    """Generic message response schema"""
    message: str
