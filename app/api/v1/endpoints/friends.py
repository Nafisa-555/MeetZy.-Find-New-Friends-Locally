from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.user_interest import UserInterest
from app.schemas.friend import (
    SendFriendRequestRequest, FriendRequestResponse, UpdateFriendRequestRequest,
    FriendResponse, FriendListResponse
)
from app.services.friend_service import FriendService
from app.utils.dependencies import get_current_user
from sqlalchemy import func

router = APIRouter(prefix="/friends", tags=["Friends"])


@router.post("/request", response_model=FriendRequestResponse, status_code=status.HTTP_201_CREATED)
def send_friend_request(
    request_data: SendFriendRequestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FriendRequestResponse:
    """
    Send a friend request to another user.
    """
    friend_request = FriendService.send_friend_request(
        db,
        current_user.id,
        request_data.receiver_id
    )
    
    # Get names
    sender = db.query(User).filter(User.id == friend_request.sender_id).first()
    receiver = db.query(User).filter(User.id == friend_request.receiver_id).first()
    
    return FriendRequestResponse(
        id=friend_request.id,
        sender_id=friend_request.sender_id,
        receiver_id=friend_request.receiver_id,
        sender_name=sender.name,
        receiver_name=receiver.name,
        status=friend_request.status,
        created_at=friend_request.created_at
    )


@router.get("/requests/pending", response_model=List[FriendRequestResponse])
def get_pending_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[FriendRequestResponse]:
    """
    Get all pending friend requests received by current user.
    """
    requests = FriendService.get_pending_requests(db, current_user.id)
    
    result = []
    for req in requests:
        sender = db.query(User).filter(User.id == req.sender_id).first()
        receiver = db.query(User).filter(User.id == req.receiver_id).first()
        
        result.append(
            FriendRequestResponse(
                id=req.id,
                sender_id=req.sender_id,
                receiver_id=req.receiver_id,
                sender_name=sender.name,
                receiver_name=receiver.name,
                status=req.status,
                created_at=req.created_at
            )
        )
    
    return result


@router.put("/request/{request_id}/accept", response_model=FriendRequestResponse)
def accept_friend_request(
    request_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FriendRequestResponse:
    """
    Accept a pending friend request.
    """
    friend_request = FriendService.accept_friend_request(
        db,
        request_id,
        current_user.id
    )
    
    sender = db.query(User).filter(User.id == friend_request.sender_id).first()
    receiver = db.query(User).filter(User.id == friend_request.receiver_id).first()
    
    return FriendRequestResponse(
        id=friend_request.id,
        sender_id=friend_request.sender_id,
        receiver_id=friend_request.receiver_id,
        sender_name=sender.name,
        receiver_name=receiver.name,
        status=friend_request.status,
        created_at=friend_request.created_at
    )


@router.put("/request/{request_id}/reject", response_model=FriendRequestResponse)
def reject_friend_request(
    request_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FriendRequestResponse:
    """
    Reject a pending friend request.
    """
    friend_request = FriendService.reject_friend_request(
        db,
        request_id,
        current_user.id
    )
    
    sender = db.query(User).filter(User.id == friend_request.sender_id).first()
    receiver = db.query(User).filter(User.id == friend_request.receiver_id).first()
    
    return FriendRequestResponse(
        id=friend_request.id,
        sender_id=friend_request.sender_id,
        receiver_id=friend_request.receiver_id,
        sender_name=sender.name,
        receiver_name=receiver.name,
        status=friend_request.status,
        created_at=friend_request.created_at
    )


@router.get("/", response_model=FriendListResponse)
def get_friends_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FriendListResponse:
    """
    Get list of all friends (accepted friend requests).
    """
    friends = FriendService.get_friends_list(db, current_user.id)
    
    friend_responses = []
    for friend in friends:
        # Count common interests
        common_interests_count = db.query(func.count()).select_from(UserInterest).filter(
            UserInterest.interest_id.in_(
                db.query(UserInterest.interest_id).filter(
                    UserInterest.user_id == current_user.id
                )
            ),
            UserInterest.user_id == friend.id
        ).scalar() or 0
        
        friend_responses.append(
            FriendResponse(
                id=friend.id,
                name=friend.name,
                bio=friend.bio,
                profile_picture=friend.profile_picture,
                common_interests_count=common_interests_count,
                became_friends_at=friend.created_at
            )
        )
    
    return FriendListResponse(
        friends=friend_responses,
        total_count=len(friend_responses)
    )


@router.delete("/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
def unfriend(
    friend_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a friend (unfriend).
    """
    FriendService.unfriend(db, current_user.id, friend_id)
    return None
