from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Message(Base):
    """
    Message model for chat functionality.
    
    Stores all messages exchanged between users.
    Messages are one-to-one (direct messages between two users).
    
    Attributes:
        id: Primary key
        sender_id: User who sent the message
        receiver_id: User who received the message
        content: The actual message text
        is_read: Whether receiver has read the message
        created_at: When message was sent
        updated_at: When message was last modified (for edit feature, optional)
    
    Usage:
        - User A sends message to User B
        - User B opens chat → all unread messages marked as read
        - Messages are sorted by created_at (newest last)
    
    Features:
        - Mark as read/unread
        - Delete messages (optional)
        - Edit messages (optional - would use updated_at)
        - Message notifications for unread messages
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite index for efficient queries
    # Example: "Get all messages between User A and User B, sorted by date"
    __table_args__ = (
        Index('idx_conversation', 'sender_id', 'receiver_id', 'created_at'),
        Index('idx_unread_messages', 'receiver_id', 'is_read', 'created_at'),
    )
    
    # Relationships
    sender = relationship(
        "User", 
        foreign_keys=[sender_id], 
        back_populates="sent_messages"
    )
    receiver = relationship(
        "User", 
        foreign_keys=[receiver_id], 
        back_populates="received_messages"
    )
    
    def __repr__(self):
        preview = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"<Message(id={self.id}, from={self.sender_id}, to={self.receiver_id}, preview='{preview}')>"