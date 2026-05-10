from pydantic import BaseModel, field_validator
from typing import List, Optional


class MatchedUserResponse(BaseModel):
    """Schema for matched user response."""
    id: int
    name: str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    common_interests: List[str] = []
    match_percentage: int
    distance_km: Optional[float] = None

    @field_validator('match_percentage')
    @classmethod
    def validate_match_percentage(cls, v: int) -> int:
        """Validate match percentage is between 0 and 100."""
        if v < 0 or v > 100:
            raise ValueError('Match percentage must be between 0 and 100')
        return v

    class Config:
        from_attributes = True


class FindMatchesRequest(BaseModel):
    """Schema for finding matches query parameters."""
    max_distance_km: Optional[float] = 50.0
    min_match_percentage: Optional[int] = 30
    limit: Optional[int] = 20

    @field_validator('min_match_percentage')
    @classmethod
    def validate_min_match_percentage(cls, v: Optional[int]) -> Optional[int]:
        """Validate min match percentage is between 0 and 100."""
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError('Minimum match percentage must be between 0 and 100')
        return v

    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: Optional[int]) -> Optional[int]:
        """Validate limit is between 1 and 100."""
        if v is not None:
            if v < 1 or v > 100:
                raise ValueError('Limit must be between 1 and 100')
        return v


class MatchListResponse(BaseModel):
    """Schema for match list response."""
    matches: List[MatchedUserResponse]
    total_count: int
