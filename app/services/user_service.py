from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List

from app.models.user import User
from app.models.interest import Interest
from app.models.user_interest import UserInterest
from app.models.friend_request import FriendRequest
from app.schemas.user import UpdateProfileRequest


class UserService:
    """Service for managing user profiles and interests."""

    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> User:
        """
        Get user profile with interests and friend count.
        
        Args:
            db: Database session
            user_id: ID of user to retrieve
        
        Returns:
            User object with interests loaded
        
        Raises:
            HTTPException: 404 if user not found
        """
        # Query user with relationships
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Count accepted friends
        friend_count = db.query(func.count(FriendRequest.id)).filter(
            FriendRequest.status == "accepted",
            ((FriendRequest.sender_id == user_id) | (FriendRequest.receiver_id == user_id))
        ).scalar()
        
        user.friend_count = friend_count or 0
        
        return user

    @staticmethod
    def update_profile(db: Session, user_id: int, profile_data: UpdateProfileRequest) -> User:
        """
        Update user profile information.
        
        Args:
            db: Database session
            user_id: ID of user to update
            profile_data: UpdateProfileRequest schema with optional fields
        
        Returns:
            Updated User object
        
        Raises:
            HTTPException: 404 if user not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update only provided fields
        update_dict = profile_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            if value is not None:
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user

    @staticmethod
    def update_interests(db: Session, user_id: int, interest_ids: List[int]) -> User:
        """
        Update user interests.
        
        Args:
            db: Database session
            user_id: ID of user to update
            interest_ids: List of interest IDs to set
        
        Returns:
            Updated User object with interests
        
        Raises:
            HTTPException: 404 if user not found, 400 if invalid interests
        """
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate all interest IDs exist
        existing_interests = db.query(Interest).filter(
            Interest.id.in_(interest_ids)
        ).count()
        
        if existing_interests != len(set(interest_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more interests do not exist"
            )
        
        # Delete existing user interests
        db.query(UserInterest).filter(UserInterest.user_id == user_id).delete()
        
        # Create new user interests
        for interest_id in interest_ids:
            user_interest = UserInterest(
                user_id=user_id,
                interest_id=interest_id
            )
            db.add(user_interest)
        
        db.commit()
        db.refresh(user)
        
        return user

    @staticmethod
    def get_user_interests(db: Session, user_id: int) -> List[Interest]:
        """
        Get all interests for a user.
        
        Args:
            db: Database session
            user_id: ID of user
        
        Returns:
            List of Interest objects for user
        """
        interests = db.query(Interest).join(
            UserInterest,
            Interest.id == UserInterest.interest_id
        ).filter(UserInterest.user_id == user_id).all()
        
        return interests
