from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.database import get_db
from app.models.user import User
from app.models.interest import Interest
from app.schemas.user import (
    UserProfileResponse, UpdateProfileRequest, UpdateInterestsRequest,
    UpdateLocationRequest, InterestResponse
)
from app.services.user_service import UserService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserProfileResponse:
    """
    Get current user's profile with interests and friend count.
    """
    user = UserService.get_user_profile(db, current_user.id)
    
    interests = [
        InterestResponse(
            id=interest.interest.id,
            category=interest.interest.category,
            name=interest.interest.name,
            icon=interest.interest.icon
        )
        for interest in user.interests
    ]
    
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        bio=user.bio,
        profile_picture=user.profile_picture,
        latitude=user.latitude,
        longitude=user.longitude,
        interests=interests,
        friend_count=user.friend_count,
        created_at=user.created_at
    )


@router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserProfileResponse:
    """
    Update current user's profile (name, bio, location).
    """
    user = UserService.update_profile(db, current_user.id, profile_data)
    
    interests = [
        InterestResponse(
            id=interest.interest.id,
            category=interest.interest.category,
            name=interest.interest.name,
            icon=interest.interest.icon
        )
        for interest in user.interests
    ]
    
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        bio=user.bio,
        profile_picture=user.profile_picture,
        latitude=user.latitude,
        longitude=user.longitude,
        interests=interests,
        friend_count=0,
        created_at=user.created_at
    )


@router.put("/interests", response_model=UserProfileResponse)
def update_interests(
    interests_data: UpdateInterestsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserProfileResponse:
    """
    Update current user's interests.
    """
    user = UserService.update_interests(db, current_user.id, interests_data.interest_ids)
    
    interests = [
        InterestResponse(
            id=interest.interest.id,
            category=interest.interest.category,
            name=interest.interest.name,
            icon=interest.interest.icon
        )
        for interest in user.interests
    ]
    
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        bio=user.bio,
        profile_picture=user.profile_picture,
        latitude=user.latitude,
        longitude=user.longitude,
        interests=interests,
        friend_count=0,
        created_at=user.created_at
    )


@router.get("/interests/available", response_model=Dict[str, List[InterestResponse]])
def get_available_interests(db: Session = Depends(get_db)) -> Dict[str, List[InterestResponse]]:
    """
    Get all available interests grouped by category.
    """
    interests = db.query(Interest).all()
    
    # Group by category
    grouped = {}
    for interest in interests:
        if interest.category not in grouped:
            grouped[interest.category] = []
        
        grouped[interest.category].append(
            InterestResponse(
                id=interest.id,
                category=interest.category,
                name=interest.name,
                icon=interest.icon
            )
        )
    
    return grouped


@router.put("/location")
def update_location(
    location_data: UpdateLocationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Update current user's location coordinates.
    """
    profile_request = UpdateProfileRequest(
        latitude=location_data.latitude,
        longitude=location_data.longitude
    )
    UserService.update_profile(db, current_user.id, profile_request)
    
    return {"message": "Location updated successfully"}
