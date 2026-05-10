from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List

from app.models.user import User
from app.models.friend_request import FriendRequest


class FriendService:
    """Service for managing friend requests."""

    @staticmethod
    def send_friend_request(db: Session, sender_id: int, receiver_id: int) -> FriendRequest:
        """
        Send a friend request from sender to receiver.
        
        Args:
            db: Database session
            sender_id: ID of user sending request
            receiver_id: ID of user receiving request
        
        Returns:
            Created FriendRequest object
        
        Raises:
            HTTPException: 400 for various validation errors, 404 if receiver not found
        """
        # Validate receiver exists
        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver user not found"
            )
        
        # Can't befriend yourself
        if sender_id == receiver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot send a friend request to yourself"
            )
        
        # Check if request already exists
        existing_request = db.query(FriendRequest).filter(
            or_(
                and_(
                    FriendRequest.sender_id == sender_id,
                    FriendRequest.receiver_id == receiver_id
                ),
                and_(
                    FriendRequest.sender_id == receiver_id,
                    FriendRequest.receiver_id == sender_id
                )
            )
        ).first()
        
        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Friend request already exists between these users"
            )
        
        # Check if already friends
        existing_friend = db.query(FriendRequest).filter(
            or_(
                and_(
                    FriendRequest.sender_id == sender_id,
                    FriendRequest.receiver_id == receiver_id,
                    FriendRequest.status == "accepted"
                ),
                and_(
                    FriendRequest.sender_id == receiver_id,
                    FriendRequest.receiver_id == sender_id,
                    FriendRequest.status == "accepted"
                )
            )
        ).first()
        
        if existing_friend:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends with this user"
            )
        
        # Create new friend request
        friend_request = FriendRequest(
            sender_id=sender_id,
            receiver_id=receiver_id,
            status="pending"
        )
        
        db.add(friend_request)
        db.commit()
        db.refresh(friend_request)
        
        return friend_request

    @staticmethod
    def accept_friend_request(db: Session, request_id: int, current_user_id: int) -> FriendRequest:
        """
        Accept a pending friend request.
        
        Args:
            db: Database session
            request_id: ID of friend request to accept
            current_user_id: ID of current user (must be receiver)
        
        Returns:
            Updated FriendRequest object
        
        Raises:
            HTTPException: 404 if request not found, 400 for various validation errors
        """
        friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
        
        if not friend_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend request not found"
            )
        
        # Verify current user is the receiver
        if friend_request.receiver_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not the receiver of this request"
            )
        
        # Check status is pending
        if friend_request.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request status is {friend_request.status}, cannot accept"
            )
        
        # Update status
        friend_request.status = "accepted"
        db.commit()
        db.refresh(friend_request)
        
        return friend_request

    @staticmethod
    def reject_friend_request(db: Session, request_id: int, current_user_id: int) -> FriendRequest:
        """
        Reject a pending friend request.
        
        Args:
            db: Database session
            request_id: ID of friend request to reject
            current_user_id: ID of current user (must be receiver)
        
        Returns:
            Updated FriendRequest object
        
        Raises:
            HTTPException: 404 if request not found, 400 for various validation errors
        """
        friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
        
        if not friend_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend request not found"
            )
        
        # Verify current user is the receiver
        if friend_request.receiver_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not the receiver of this request"
            )
        
        # Check status is pending
        if friend_request.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request status is {friend_request.status}, cannot reject"
            )
        
        # Update status
        friend_request.status = "rejected"
        db.commit()
        db.refresh(friend_request)
        
        return friend_request

    @staticmethod
    def get_pending_requests(db: Session, user_id: int) -> List[FriendRequest]:
        """
        Get all pending friend requests received by user.
        
        Args:
            db: Database session
            user_id: ID of user
        
        Returns:
            List of pending FriendRequest objects
        """
        requests = db.query(FriendRequest).filter(
            FriendRequest.receiver_id == user_id,
            FriendRequest.status == "pending"
        ).all()
        
        return requests

    @staticmethod
    def get_friends_list(db: Session, user_id: int) -> List[User]:
        """
        Get list of all accepted friends for user.
        
        Args:
            db: Database session
            user_id: ID of user
        
        Returns:
            List of User objects who are friends
        """
        # Query accepted friend requests
        friend_requests = db.query(FriendRequest).filter(
            FriendRequest.status == "accepted",
            or_(
                FriendRequest.sender_id == user_id,
                FriendRequest.receiver_id == user_id
            )
        ).all()
        
        friends = []
        for req in friend_requests:
            # If user is sender, get receiver; if user is receiver, get sender
            friend_id = req.receiver_id if req.sender_id == user_id else req.sender_id
            friend = db.query(User).filter(User.id == friend_id).first()
            if friend:
                friends.append(friend)
        
        return friends

    @staticmethod
    def unfriend(db: Session, user_id: int, friend_id: int) -> None:
        """
        Remove a friend (delete accepted friend request).
        
        Args:
            db: Database session
            user_id: ID of user
            friend_id: ID of friend to remove
        
        Raises:
            HTTPException: 404 if friendship not found
        """
        # Find accepted friend request between them
        friend_request = db.query(FriendRequest).filter(
            FriendRequest.status == "accepted",
            or_(
                and_(
                    FriendRequest.sender_id == user_id,
                    FriendRequest.receiver_id == friend_id
                ),
                and_(
                    FriendRequest.sender_id == friend_id,
                    FriendRequest.receiver_id == user_id
                )
            )
        ).first()
        
        if not friend_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friendship not found"
            )
        
        # Delete the record
        db.delete(friend_request)
        db.commit()
