"""
Admin Panel API Endpoints

All routes here require admin authentication.
Prefix: /api/v1/admin
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.models.user import User
from app.models.interest import Interest
from app.models.user_interest import UserInterest
from app.models.friend_request import FriendRequest, RequestStatus
from app.models.message import Message
from app.schemas.admin import (
    DashboardStats,
    AdminUserListItem,
    AdminUserDetail,
    AdminInterestCreate,
    AdminInterestResponse,
    AdminMessageResponse,
    AdminFriendRequestResponse,
    AdminActionResponse,
)
from app.utils.dependencies import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["Admin Panel"])


# ─── Dashboard ───────────────────────────────────────────────────────────────

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    """
    Get overall platform statistics for the admin dashboard.
    """
    today_start = datetime.combine(date.today(), datetime.min.time())

    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    inactive_users = db.query(func.count(User.id)).filter(User.is_active == False).scalar()
    total_messages = db.query(func.count(Message.id)).scalar()
    total_friend_requests = db.query(func.count(FriendRequest.id)).scalar()
    accepted_friendships = (
        db.query(func.count(FriendRequest.id))
        .filter(FriendRequest.status == RequestStatus.ACCEPTED)
        .scalar()
    )
    total_interests = db.query(func.count(Interest.id)).scalar()
    new_users_today = (
        db.query(func.count(User.id))
        .filter(User.created_at >= today_start)
        .scalar()
    )

    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        total_messages=total_messages,
        total_friend_requests=total_friend_requests,
        accepted_friendships=accepted_friendships,
        total_interests=total_interests,
        new_users_today=new_users_today,
    )


# ─── User Management ─────────────────────────────────────────────────────────

@router.get("/users", response_model=List[AdminUserListItem])
def list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    """
    List all users. Supports search by name/email and filtering by active status.
    """
    query = db.query(User)

    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for user in users:
        friend_count = (
            db.query(func.count(FriendRequest.id))
            .filter(
                ((FriendRequest.sender_id == user.id) | (FriendRequest.receiver_id == user.id)),
                FriendRequest.status == RequestStatus.ACCEPTED,
            )
            .scalar()
        )
        message_count = (
            db.query(func.count(Message.id))
            .filter(Message.sender_id == user.id)
            .scalar()
        )
        result.append(
            AdminUserListItem(
                id=user.id,
                name=user.name,
                email=user.email,
                is_active=user.is_active,
                is_admin=user.is_admin,
                is_verified=user.is_verified,
                created_at=user.created_at,
                friend_count=friend_count,
                message_count=message_count,
            )
        )
    return result


@router.get("/users/{user_id}", response_model=AdminUserDetail)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    """
    Get detailed info about a specific user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    friend_count = (
        db.query(func.count(FriendRequest.id))
        .filter(
            ((FriendRequest.sender_id == user.id) | (FriendRequest.receiver_id == user.id)),
            FriendRequest.status == RequestStatus.ACCEPTED,
        )
        .scalar()
    )
    message_count = (
        db.query(func.count(Message.id))
        .filter(Message.sender_id == user.id)
        .scalar()
    )

    interests = [ui.interest.name for ui in user.interests if ui.interest]

    return AdminUserDetail(
        id=user.id,
        name=user.name,
        email=user.email,
        bio=user.bio,
        profile_picture=user.profile_picture,
        latitude=user.latitude,
        longitude=user.longitude,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_verified=user.is_verified,
        created_at=user.created_at,
        friend_count=friend_count,
        message_count=message_count,
        interests=interests,
    )


@router.put("/users/{user_id}/toggle-active", response_model=AdminActionResponse)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Ban or unban a user by toggling their is_active status.
    Cannot ban yourself or another admin.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="You cannot ban yourself")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot ban another admin")

    user.is_active = not user.is_active
    db.commit()

    action = "unbanned" if user.is_active else "banned"
    return AdminActionResponse(success=True, message=f"User '{user.name}' has been {action}.")


@router.delete("/users/{user_id}", response_model=AdminActionResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Permanently delete a user and all their data.
    Cannot delete yourself or another admin.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot delete an admin account")

    name = user.name
    db.delete(user)
    db.commit()
    return AdminActionResponse(success=True, message=f"User '{name}' has been permanently deleted.")


@router.put("/users/{user_id}/make-admin", response_model=AdminActionResponse)
def make_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    """
    Promote a regular user to admin role.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin:
        return AdminActionResponse(success=True, message=f"'{user.name}' is already an admin.")

    user.is_admin = True
    db.commit()
    return AdminActionResponse(success=True, message=f"'{user.name}' has been promoted to admin.")


# ─── Interest Management ──────────────────────────────────────────────────────

@router.get("/interests", response_model=List[AdminInterestResponse])
def list_interests(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    """
    List all interests with how many users have selected each one.
    """
    interests = db.query(Interest).order_by(Interest.category, Interest.name).all()
    result = []
    for interest in interests:
        user_count = (
            db.query(func.count(UserInterest.user_id))
            .filter(UserInterest.interest_id == interest.id)
            .scalar()
        )
        result.append(
            AdminInterestResponse(
                id=interest.id,
                category=interest.category,
                name=interest.name,
                description=interest.description,
                icon=interest.icon,
                user_count=user_count,
            )
        )
    return result


@router.post("/interests", response_model=AdminInterestResponse, status_code=201)
def create_interest(
    payload: AdminInterestCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    """
    Create a new interest option for users to select.
    """
    existing = (
        db.query(Interest)
        .filter(
            Interest.category == payload.category,
            Interest.name == payload.name,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="This interest already exists in that category.")

    interest = Interest(
        category=payload.category,
        name=payload.name,
        description=payload.description,
        icon=payload.icon,
    )
    db.add(interest)
    db.commit()
    db.refresh(interest)
    return AdminInterestResponse(
        id=interest.id,
        category=interest.category,
        name=interest.name,
        description=interest.description,
        icon=interest.icon,
        user_count=0,
    )


@router.delete("/interests/{interest_id}", response_model=AdminActionResponse)
def delete_interest(
    interest_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    """
    Delete an interest. Also removes it from all users who had selected it.
    """
    interest = db.query(Interest).filter(Interest.id == interest_id).first()
    if not interest:
        raise HTTPException(status_code=404, detail="Interest not found")

    name = f"{interest.category} / {interest.name}"
    db.delete(interest)
    db.commit()
    return AdminActionResponse(success=True, message=f"Interest '{name}' has been deleted.")


# ─── Messages ────────────────────────────────────────────────────────────────

@router.get("/messages", response_model=List[AdminMessageResponse])
def list_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    """
    List recent messages across all users.
    """
    messages = (
        db.query(Message)
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = []
    for msg in messages:
        result.append(
            AdminMessageResponse(
                id=msg.id,
                sender_id=msg.sender_id,
                sender_name=msg.sender.name if msg.sender else "Deleted",
                receiver_id=msg.receiver_id,
                receiver_name=msg.receiver.name if msg.receiver else "Deleted",
                content=msg.content,
                is_read=msg.is_read,
                created_at=msg.created_at,
            )
        )
    return result


# ─── Friend Requests ─────────────────────────────────────────────────────────

@router.get("/friend-requests", response_model=List[AdminFriendRequestResponse])
def list_friend_requests(
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, accepted, rejected"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    """
    List all friend requests with optional status filter.
    """
    query = db.query(FriendRequest)

    if status_filter:
        try:
            status_enum = RequestStatus(status_filter.lower())
            query = query.filter(FriendRequest.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status. Use: pending, accepted, rejected")

    requests = query.order_by(FriendRequest.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for req in requests:
        result.append(
            AdminFriendRequestResponse(
                id=req.id,
                sender_id=req.sender_id,
                sender_name=req.sender.name if req.sender else "Deleted",
                receiver_id=req.receiver_id,
                receiver_name=req.receiver.name if req.receiver else "Deleted",
                status=req.status.value,
                created_at=req.created_at,
            )
        )
    return result
