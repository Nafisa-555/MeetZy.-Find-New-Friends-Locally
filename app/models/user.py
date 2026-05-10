from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """
    User model representing registered users in the application.
    
    Attributes:
        id: Primary key
        email: Unique email address for login
        password_hash: Hashed password (never store plain passwords!)
        name: User's full name
        bio: Optional user biography/description
        profile_picture: URL or path to profile picture
        latitude: Geographic latitude for location-based matching
        longitude: Geographic longitude for location-based matching
        is_active: Whether the user account is active
        is_verified: Whether email is verified
        created_at: Timestamp when user registered
        updated_at: Timestamp of last profile update
    """
    __tablename__ = "users"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    bio = Column(String(500), nullable=True)
    profile_picture = Column(String(255), nullable=True, default=None)
    
    # Location for nearby feature (GPS coordinates)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # User's selected interests
    interests = relationship(
        "UserInterest", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    
    # Friend requests sent by this user
    sent_requests = relationship(
        "FriendRequest", 
        foreign_keys="FriendRequest.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    
    # Friend requests received by this user
    received_requests = relationship(
        "FriendRequest", 
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan"
    )
    
    # Messages sent by this user
    sent_messages = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    
    # Messages received by this user
    received_messages = relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
