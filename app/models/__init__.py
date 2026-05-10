"""
Models package - Database models for the Friends Finder application.

This file imports all database models to make them easily accessible
and ensures they are registered with SQLAlchemy's Base metadata.

Usage:
    from app.models import User, Interest, FriendRequest, Message
    
    # Or import all at once
    from app.models import *
"""

from app.models.user import User
from app.models.interest import Interest
from app.models.user_interest import UserInterest
from app.models.friend_request import FriendRequest, RequestStatus
from app.models.message import Message

# Define what gets exported when using "from app.models import *"
__all__ = [
    "User",
    "Interest", 
    "UserInterest",
    "FriendRequest",
    "RequestStatus",
    "Message"
]