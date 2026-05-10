from pydantic import BaseModel, field_validator
from typing import List
from datetime import datetime


class SendMessageRequest(BaseModel):
    """Schema for sending message request."""
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty and within max length."""
        v = v.strip()
        if len(v) < 1:
            raise ValueError('Message content cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message content cannot exceed 5000 characters')
        return v


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    sender_id: int
    receiver_id: int
    sender_name: str
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    messages: List[MessageResponse]
    total_count: int
    unread_count: int


class MarkMessagesReadRequest(BaseModel):
    """Schema for marking messages as read."""
    message_ids: List[int]

    @field_validator('message_ids')
    @classmethod
    def validate_message_ids(cls, v: List[int]) -> List[int]:
        """Validate message_ids list is not empty."""
        if len(v) < 1:
            raise ValueError('Message IDs list cannot be empty')
        return v
