from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List


class InterestResponse(BaseModel):
    """Schema for interest response."""
    id: int
    category: str
    name: str
    icon: Optional[str] = None

    class Config:
        from_attributes = True


class UpdateInterestsRequest(BaseModel):
    """Schema for updating user interests."""
    interest_ids: List[int]

    @field_validator('interest_ids')
    @classmethod
    def validate_interests_count(cls, v: List[int]) -> List[int]:
        """Validate that user selects between 1 and 10 interests."""
        if len(v) < 1 or len(v) > 10:
            raise ValueError('You must select between 1 and 10 interests')
        return v


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    email: EmailStr
    name: str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    interests: List[InterestResponse] = []
    friend_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = None
    bio: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name is between 2 and 100 characters if provided."""
        if v is not None:
            if len(v) < 2 or len(v) > 100:
                raise ValueError('Name must be between 2 and 100 characters')
            return v.strip()
        return v

    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v: Optional[str]) -> Optional[str]:
        """Validate bio is max 500 characters if provided."""
        if v is not None:
            if len(v) > 500:
                raise ValueError('Bio must not exceed 500 characters')
            return v.strip()
        return v

    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        """Validate latitude is between -90 and 90 if provided."""
        if v is not None:
            if v < -90 or v > 90:
                raise ValueError('Latitude must be between -90 and 90')
        return v

    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        """Validate longitude is between -180 and 180 if provided."""
        if v is not None:
            if v < -180 or v > 180:
                raise ValueError('Longitude must be between -180 and 180')
        return v


class UpdateLocationRequest(BaseModel):
    """Schema for updating user location."""
    latitude: float
    longitude: float

    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate latitude is between -90 and 90."""
        if v < -90 or v > 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate longitude is between -180 and 180."""
        if v < -180 or v > 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v
