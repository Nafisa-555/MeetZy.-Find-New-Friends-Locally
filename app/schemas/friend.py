from pydantic import BaseModel, field_validator
from typing import List, Literal, Optional
from datetime import datetime


class SendFriendRequestRequest(BaseModel):
    """Schema for sending friend request."""
    receiver_id: int

    @field_validator('receiver_id')
    @classmethod
    def validate_receiver_id(cls, v: int) -> int:
        """Validate receiver_id is positive."""
        if v <= 0:
            raise ValueError('Receiver ID must be a positive integer')
        return v


class FriendRequestResponse(BaseModel):
    """Schema for friend request response."""
    id: int
    sender_id: int
    receiver_id: int
    sender_name: str
    receiver_name: str
    status: Literal["pending", "accepted", "rejected"]
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateFriendRequestRequest(BaseModel):
    """Schema for updating friend request status."""
    action: Literal["accept", "reject"]


class FriendResponse(BaseModel):
    """Schema for friend response."""
    id: int
    name: str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    common_interests_count: int
    became_friends_at: datetime

    class Config:
        from_attributes = True


class FriendListResponse(BaseModel):
    """Schema for friend list response."""
    friends: List[FriendResponse]
    total_count: int
