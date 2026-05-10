from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional

from app.models.user import User
from app.models.interest import Interest
from app.models.user_interest import UserInterest
from app.models.friend_request import FriendRequest
from app.schemas.match import MatchedUserResponse
from app.utils.match_calculator import calculate_match_percentage, calculate_distance, get_common_interests


class MatchingService:
    """Service for finding matches between users based on interests and location."""

    @staticmethod
    def find_matches(
        db: Session,
        current_user_id: int,
        max_distance_km: float = 50.0,
        min_match_percentage: int = 30,
        limit: int = 20
    ) -> tuple[List[MatchedUserResponse], int]:
        """
        Find potential friend matches for current user.
        
        Algorithm:
        a) Get current user's interest IDs
        b) Query potential candidates:
           - Users who share at least 1 interest
           - Exclude: current user, already friends, pending requests
           - Use SQLAlchemy joins on user_interests
        c) For each candidate:
           - Get their interest IDs
           - Calculate match percentage
           - Calculate distance if both have location
           - Filter by min_match_percentage and max_distance_km
        d) Create MatchedUserResponse objects
        e) Sort by match_percentage descending
        f) Return top 'limit' matches
        
        Args:
            db: Database session
            current_user_id: ID of user searching for matches
            max_distance_km: Maximum distance in km (default 50.0)
            min_match_percentage: Minimum match percentage (default 30)
            limit: Maximum number of matches to return (default 20)
        
        Returns:
            Tuple of (List of MatchedUserResponse, total_count)
        """
        # Get current user
        current_user = db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            return [], 0
        
        # Get current user's interest IDs
        current_user_interests = db.query(UserInterest.interest_id).filter(
            UserInterest.user_id == current_user_id
        ).all()
        current_user_interest_ids = [ui[0] for ui in current_user_interests]
        
        # Handle case where user has no interests
        if not current_user_interest_ids:
            return [], 0
        
        # Query users with shared interests
        potential_candidates = db.query(User.id).distinct().join(
            UserInterest,
            User.id == UserInterest.user_id
        ).filter(
            UserInterest.interest_id.in_(current_user_interest_ids),
            User.id != current_user_id
        ).all()
        
        candidate_ids = [c[0] for c in potential_candidates]
        
        # Filter out already connected users
        connected_user_ids = []
        for candidate_id in candidate_ids:
            if MatchingService.is_already_connected(db, current_user_id, candidate_id):
                connected_user_ids.append(candidate_id)
        
        # Remove connected users from candidates
        final_candidates = [c for c in candidate_ids if c not in connected_user_ids]
        
        # Calculate matches for each candidate
        matches = []
        
        for candidate_id in final_candidates:
            candidate = db.query(User).filter(User.id == candidate_id).first()
            if not candidate:
                continue
            
            # Get candidate's interest IDs
            candidate_interests = db.query(UserInterest.interest_id).filter(
                UserInterest.user_id == candidate_id
            ).all()
            candidate_interest_ids = [ci[0] for ci in candidate_interests]
            
            # Calculate match percentage
            match_percentage = calculate_match_percentage(
                current_user_interest_ids,
                candidate_interest_ids
            )
            
            # Filter by minimum match percentage
            if match_percentage < min_match_percentage:
                continue
            
            # Calculate distance if both have location
            distance_km = None
            if (current_user.latitude and current_user.longitude and
                candidate.latitude and candidate.longitude):
                distance_km = calculate_distance(
                    current_user.latitude,
                    current_user.longitude,
                    candidate.latitude,
                    candidate.longitude
                )
                
                # Filter by maximum distance
                if distance_km and distance_km > max_distance_km:
                    continue
            
            # Get common interests names
            common_interest_ids = get_common_interests(
                current_user_interest_ids,
                candidate_interest_ids
            )
            common_interest_names = MatchingService.get_common_interests_names(
                db,
                current_user_interest_ids,
                candidate_interest_ids
            )
            
            # Create match response
            match = MatchedUserResponse(
                id=candidate.id,
                name=candidate.name,
                bio=candidate.bio,
                profile_picture=candidate.profile_picture,
                common_interests=common_interest_names,
                match_percentage=match_percentage,
                distance_km=distance_km
            )
            
            matches.append(match)
        
        # Sort by match percentage descending
        matches.sort(key=lambda x: x.match_percentage, reverse=True)
        
        # Return top 'limit' matches
        total_count = len(matches)
        limited_matches = matches[:limit]
        
        return limited_matches, total_count

    @staticmethod
    def get_common_interests_names(
        db: Session,
        user_interest_ids: List[int],
        candidate_interest_ids: List[int]
    ) -> List[str]:
        """
        Get names of common interests between two users.
        
        Args:
            db: Database session
            user_interest_ids: List of user's interest IDs
            candidate_interest_ids: List of candidate's interest IDs
        
        Returns:
            List of interest names
        """
        # Find intersection
        user_set = set(user_interest_ids)
        candidate_set = set(candidate_interest_ids)
        common_ids = user_set.intersection(candidate_set)
        
        if not common_ids:
            return []
        
        # Query interest names
        interests = db.query(Interest.name).filter(
            Interest.id.in_(common_ids)
        ).all()
        
        return [interest[0] for interest in interests]

    @staticmethod
    def is_already_connected(db: Session, user_id: int, candidate_id: int) -> bool:
        """
        Check if two users are already friends or have a pending request.
        
        Args:
            db: Database session
            user_id: ID of first user
            candidate_id: ID of second user
        
        Returns:
            True if connected (accepted or pending), False otherwise
        """
        # Check for friend request in either direction with accepted or pending status
        existing_request = db.query(FriendRequest).filter(
            or_(
                and_(
                    FriendRequest.sender_id == user_id,
                    FriendRequest.receiver_id == candidate_id
                ),
                and_(
                    FriendRequest.sender_id == candidate_id,
                    FriendRequest.receiver_id == user_id
                )
            ),
            FriendRequest.status.in_(["accepted", "pending"])
        ).first()
        
        return existing_request is not None
