"""
Admin Panel Schemas

Pydantic schemas for admin API request/response validation.

"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ─── Dashboard Stats ────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    """Overall app statistics for the admin dashboard."""
    total_users: int
    active_users: int
    inactive_users: int
    total_messages: int
    total_friend_requests: int
    accepted_friendships: int
    total_interests: int
    new_users_today: int


# ─── User Schemas ────────────────────────────────────────────────────────────

class AdminUserListItem(BaseModel):
    """Compact user info for listing in admin panel."""
    id: int
    name: str
    email: str
    is_active: bool
    is_admin: bool
    is_verified: bool
    created_at: datetime
    friend_count: int
    message_count: int

    class Config:
        from_attributes = True


class AdminUserDetail(AdminUserListItem):
    """Detailed user info for admin user detail view."""
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    interests: List[str] = []

    class Config:
        from_attributes = True


# ─── Interest Schemas ────────────────────────────────────────────────────────

class AdminInterestCreate(BaseModel):
    """Schema for creating a new interest."""
    category: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


class AdminInterestResponse(BaseModel):
    """Interest info for admin panel."""
    id: int
    category: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    user_count: int = 0

    class Config:
        from_attributes = True


# ─── Message Schemas ─────────────────────────────────────────────────────────

class AdminMessageResponse(BaseModel):
    """Message info for admin panel."""
    id: int
    sender_id: int
    sender_name: str
    receiver_id: int
    receiver_name: str
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Friend Request Schemas ───────────────────────────────────────────────────

class AdminFriendRequestResponse(BaseModel):
    """Friend request info for admin panel."""
    id: int
    sender_id: int
    sender_name: str
    receiver_id: int
    receiver_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Generic Responses ───────────────────────────────────────────────────────

class AdminActionResponse(BaseModel):
    """Generic success response for admin actions."""
    success: bool
    message: str
