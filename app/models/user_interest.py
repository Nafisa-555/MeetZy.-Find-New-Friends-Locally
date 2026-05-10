from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class UserInterest(Base):
    """
    UserInterest model - Junction table for many-to-many relationship.
    
    This table connects users with their selected interests.
    One user can have multiple interests, and one interest can belong to multiple users.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        interest_id: Foreign key to interests table
        added_at: Timestamp when user selected this interest
    
    Example:
        If User #1 selects "Football", "Rock Music", and "PUBG":
        - user_id=1, interest_id=5 (Football)
        - user_id=1, interest_id=12 (Rock Music)
        - user_id=1, interest_id=18 (PUBG)
    """
    __tablename__ = "user_interests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    interest_id = Column(Integer, ForeignKey("interests.id", ondelete="CASCADE"), nullable=False, index=True)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Ensure a user can't select the same interest twice
    __table_args__ = (
        UniqueConstraint('user_id', 'interest_id', name='unique_user_interest'),
    )
    
    # Relationships
    user = relationship("User", back_populates="interests")
    interest = relationship("Interest", back_populates="users")
    
    def __repr__(self):
        return f"<UserInterest(user_id={self.user_id}, interest_id={self.interest_id})>"