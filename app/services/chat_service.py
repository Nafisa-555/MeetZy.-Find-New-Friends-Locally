from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, case
from fastapi import HTTPException, status
from typing import List

from app.models.message import Message
from app.models.user import User
from app.models.friend_request import FriendRequest


class ChatService:
    """Service for managing messaging and conversations."""

    @staticmethod
    def send_message(
        db: Session,
        sender_id: int,
        receiver_id: int,
        content: str
    ) -> Message:
        """
        Send a message from sender to receiver.
        
        Args:
            db: Database session
            sender_id: ID of message sender
            receiver_id: ID of message receiver
            content: Message content
        
        Returns:
            Created Message object
        
        Raises:
            HTTPException: 404 if receiver not found, 400 if not friends
        """
        # Verify receiver exists
        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver user not found"
            )
        
        # Verify sender and receiver are friends
        friendship = db.query(FriendRequest).filter(
            FriendRequest.status == "accepted",
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
        
        if not friendship:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must be friends to send messages"
            )
        
        # Create message
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            is_read=False
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return message

    @staticmethod
    def get_conversation(
        db: Session,
        user1_id: int,
        user2_id: int,
        limit: int = 50
    ) -> List[Message]:
        """
        Get conversation between two users.
        
        Args:
            db: Database session
            user1_id: ID of first user
            user2_id: ID of second user
            limit: Maximum number of messages to retrieve (default 50)
        
        Returns:
            List of Message objects in chronological order
        """
        # Query messages between two users
        messages = db.query(Message).filter(
            or_(
                and_(
                    Message.sender_id == user1_id,
                    Message.receiver_id == user2_id
                ),
                and_(
                    Message.sender_id == user2_id,
                    Message.receiver_id == user1_id
                )
            )
        ).order_by(desc(Message.created_at)).limit(limit).all()
        
        # Return in chronological order (reverse)
        return list(reversed(messages))

    @staticmethod
    def mark_messages_as_read(
        db: Session,
        message_ids: List[int],
        current_user_id: int
    ) -> int:
        """
        Mark messages as read for current user.
        
        Args:
            db: Database session
            message_ids: List of message IDs to mark as read
            current_user_id: ID of current user (security check)
        
        Returns:
            Number of messages updated
        """
        # Update messages (only messages where current user is receiver)
        updated_count = db.query(Message).filter(
            Message.id.in_(message_ids),
            Message.receiver_id == current_user_id
        ).update({"is_read": True})
        
        db.commit()
        
        return updated_count

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """
        Get count of unread messages for user.
        
        Args:
            db: Database session
            user_id: ID of user
        
        Returns:
            Number of unread messages
        """
        unread_count = db.query(func.count(Message.id)).filter(
            Message.receiver_id == user_id,
            Message.is_read == False
        ).scalar()
        
        return unread_count or 0

    @staticmethod
    def get_conversations_list(db: Session, user_id: int) -> List[dict]:
        """
        Get list of all conversations for user with unread counts.
        
        Args:
            db: Database session
            user_id: ID of user
        
        Returns:
            List of dicts with conversation info and unread count
        """
        # Get all users current user has exchanged messages with
        # Query distinct users from messages
        conversation_users = db.query(
            case(
                (Message.sender_id == user_id, Message.receiver_id),
                else_=Message.sender_id
            ).label("other_user_id")
        ).filter(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
        ).distinct().all()
        
        conversations = []
        
        for (other_user_id,) in conversation_users:
            if other_user_id is None:
                continue
            
            # Get other user
            other_user = db.query(User).filter(User.id == other_user_id).first()
            if not other_user:
                continue
            
            # Get last message timestamp
            last_message = db.query(Message).filter(
                or_(
                    and_(
                        Message.sender_id == user_id,
                        Message.receiver_id == other_user_id
                    ),
                    and_(
                        Message.sender_id == other_user_id,
                        Message.receiver_id == user_id
                    )
                )
            ).order_by(desc(Message.created_at)).first()
            
            # Get unread count for this conversation
            unread_count = db.query(func.count(Message.id)).filter(
                Message.sender_id == other_user_id,
                Message.receiver_id == user_id,
                Message.is_read == False
            ).scalar() or 0
            
            conversation = {
                "user_id": other_user.id,
                "user_name": other_user.name,
                "user_profile_picture": other_user.profile_picture,
                "last_message_timestamp": last_message.created_at if last_message else None,
                "last_message_preview": last_message.content[:100] if last_message else None,
                "unread_count": unread_count
            }
            
            conversations.append(conversation)
        
        # Sort by last message timestamp descending
        conversations.sort(
            key=lambda x: x["last_message_timestamp"] or x["last_message_timestamp"],
            reverse=True
        )
        
        return conversations
