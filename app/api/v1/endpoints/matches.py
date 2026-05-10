from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.match import MatchListResponse, MatchedUserResponse
from app.services.matching_service import MatchingService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/matches", tags=["Matching"])


@router.get("/find-friends", response_model=MatchListResponse)
def find_friends(
    max_distance_km: float = Query(50.0, ge=0),
    min_match_percentage: int = Query(30, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MatchListResponse:
    """
    Find friend matches based on shared interests and location.
    
    The core feature of MeetZy! Returns users with matching interests,
    sorted by match percentage in descending order.
    
    Query Parameters:
    - max_distance_km: Maximum distance in kilometers (default: 50.0)
    - min_match_percentage: Minimum match percentage to include (default: 30)
    - limit: Maximum number of matches to return (default: 20)
    """
    matches, total_count = MatchingService.find_matches(
        db=db,
        current_user_id=current_user.id,
        max_distance_km=max_distance_km,
        min_match_percentage=min_match_percentage,
        limit=limit
    )
    
    return MatchListResponse(
        matches=matches,
        total_count=total_count
    )


@router.get("/preview/{user_id}", response_model=MatchedUserResponse)
def get_match_preview(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MatchedUserResponse:
    """
    Get preview of a specific user before sending friend request.
    
    Calculates match percentage and distance with current user.
    """
    # Get user to preview
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get interests for both users
    from app.models.user import UserInterest
    current_interests = db.query(UserInterest.interest_id).filter(
        UserInterest.user_id == current_user.id
    ).all()
    target_interests = db.query(UserInterest.interest_id).filter(
        UserInterest.user_id == user_id
    ).all()
    
    current_interest_ids = [ui[0] for ui in current_interests]
    target_interest_ids = [ui[0] for ui in target_interests]
    
    # Calculate match percentage and distance
    from app.utils.match_calculator import (
        calculate_match_percentage,
        calculate_distance,
        get_common_interests
    )
    
    match_percentage = calculate_match_percentage(
        current_interest_ids,
        target_interest_ids
    )
    
    distance_km = None
    if (current_user.latitude and current_user.longitude and
        target_user.latitude and target_user.longitude):
        distance_km = calculate_distance(
            current_user.latitude,
            current_user.longitude,
            target_user.latitude,
            target_user.longitude
        )
    
    # Get common interest names
    common_interest_ids = get_common_interests(
        current_interest_ids,
        target_interest_ids
    )
    
    from app.models.interest import Interest
    common_interests = db.query(Interest.name).filter(
        Interest.id.in_(common_interest_ids)
    ).all()
    common_interest_names = [interest[0] for interest in common_interests]
    
    return MatchedUserResponse(
        id=target_user.id,
        name=target_user.name,
        bio=target_user.bio,
        profile_picture=target_user.profile_picture,
        common_interests=common_interest_names,
        match_percentage=match_percentage,
        distance_km=distance_km
    )
