from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.core.database import Base


class RequestStatus(str, Enum):
    """
    Enum for friend request status.
    
    PENDING: Request sent, waiting for response
    ACCEPTED: Request accepted, users are now friends
    REJECTED: Request rejected by receiver
    """
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class FriendRequest(Base):
    """
    FriendRequest model for managing friend connections.
    
    Represents friend requests between users. When a request is accepted,
    both users become friends.
    
    Attributes:
        id: Primary key
        sender_id: User who sent the friend request
        receiver_id: User who received the friend request
        status: Current status (pending/accepted/rejected)
        created_at: When request was sent
        updated_at: When status was last changed
    
    Flow:
        1. User A sends request to User B → status = PENDING
        2. User B accepts → status = ACCEPTED (they're friends now!)
        3. OR User B rejects → status = REJECTED
    
    Business Rules:
        - Can't send request to yourself
        - Can't send duplicate requests to the same person
        - Once accepted, both users are friends
        - Rejected requests can be re-sent (optional implementation)
    """
    __tablename__ = "friend_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(
        SQLEnum(RequestStatus), 
        default=RequestStatus.PENDING, 
        nullable=False,
        index=True
    )
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure no duplicate requests between same two users
    __table_args__ = (
        UniqueConstraint('sender_id', 'receiver_id', name='unique_friend_request'),
    )
    
    # Relationships
    sender = relationship(
        "User", 
        foreign_keys=[sender_id], 
        back_populates="sent_requests"
    )
    receiver = relationship(
        "User", 
        foreign_keys=[receiver_id], 
        back_populates="received_requests"
    )
    
    def __repr__(self):
        return f"<FriendRequest(id={self.id}, sender={self.sender_id}, receiver={self.receiver_id}, status='{self.status}')>"