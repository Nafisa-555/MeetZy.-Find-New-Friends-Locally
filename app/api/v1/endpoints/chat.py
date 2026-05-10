from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func

from app.core.database import get_db
from app.models.user import User
from app.models.message import Message
from app.schemas.chat import (
    SendMessageRequest, MessageResponse, ConversationResponse, MarkMessagesReadRequest
)
from app.services.chat_service import ChatService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/messages/{receiver_id}", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    receiver_id: int = Path(..., gt=0),
    message_data: SendMessageRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Send a message to a friend.
    
    Both sender and receiver must be friends to send messages.
    """
    message = ChatService.send_message(
        db,
        current_user.id,
        receiver_id,
        message_data.content
    )
    
    # Get sender name
    sender = db.query(User).filter(User.id == message.sender_id).first()
    
    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        sender_name=sender.name,
        content=message.content,
        is_read=message.is_read,
        created_at=message.created_at
    )


@router.get("/messages/{friend_id}", response_model=ConversationResponse)
def get_conversation(
    friend_id: int = Path(..., gt=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ConversationResponse:
    """
    Get conversation history with a friend.
    
    Returns messages in chronological order with unread count.
    """
    messages_list = ChatService.get_conversation(
        db,
        current_user.id,
        friend_id,
        limit
    )
    
    message_responses = []
    for msg in messages_list:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        message_responses.append(
            MessageResponse(
                id=msg.id,
                sender_id=msg.sender_id,
                receiver_id=msg.receiver_id,
                sender_name=sender.name,
                content=msg.content,
                is_read=msg.is_read,
                created_at=msg.created_at
            )
        )
    
    # Get unread count for this specific conversation
    unread_count = db.query(func.count(Message.id)).filter(
        Message.sender_id == friend_id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).scalar() or 0
    
    return ConversationResponse(
        messages=message_responses,
        total_count=len(message_responses),
        unread_count=unread_count
    )


@router.put("/messages/read")
def mark_messages_read(
    mark_data: MarkMessagesReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark specified messages as read.
    """
    ChatService.mark_messages_as_read(
        db,
        mark_data.message_ids,
        current_user.id
    )
    
    return {"message": "Messages marked as read"}


@router.get("/conversations")
def get_conversations_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all conversations with last message and unread count.
    """
    conversations = ChatService.get_conversations_list(db, current_user.id)
    return {"conversations": conversations}


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get total count of unread messages for current user.
    """
    unread_count = ChatService.get_unread_count(db, current_user.id)
    return {"unread_count": unread_count}