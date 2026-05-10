from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional


class SignupRequest(BaseModel):
    """Schema for user signup request."""
    email: EmailStr
    password: str
    name: str

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v: str) -> str:
        """Validate password has minimum 8 characters."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    @field_validator('name')
    @classmethod
    def name_length(cls, v: str) -> str:
        """Validate name is between 2 and 100 characters."""
        if len(v) < 2 or len(v) > 100:
            raise ValueError('Name must be between 2 and 100 characters')
        return v.strip()


class LoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for returning user data after authentication."""
    id: int
    email: EmailStr
    name: str
    profile_picture: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
