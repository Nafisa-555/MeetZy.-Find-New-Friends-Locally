"""
Security utilities for password hashing and JWT token management.

This module provides functions for:
- Password hashing and verification using bcrypt
- JWT token creation and validation
- User authentication helpers
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context using bcrypt
# bcrypt is a secure algorithm designed for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password from database
    
    Returns:
        bool: True if password matches, False otherwise
    
    Example:
        >>> hashed = get_password_hash("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    
    This function should be called when:
    - Creating a new user account
    - User changes their password
    
    Args:
        password: Plain text password to hash
    
    Returns:
        str: Hashed password (safe to store in database)
    
    Example:
        >>> hashed = get_password_hash("mypassword123")
        >>> print(hashed)
        $2b$12$KIXxFz... (60 character bcrypt hash)
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    The token contains:
    - User data (typically user_id in 'sub' field)
    - Expiration timestamp
    - Any additional claims you want to include
    
    Args:
        data: Dictionary of data to encode in token (usually {"sub": user_id})
        expires_delta: Optional custom expiration time
    
    Returns:
        str: Encoded JWT token
    
    Example:
        >>> token = create_access_token({"sub": "123"})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = data.copy()
    
    # Calculate expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration to token payload
    to_encode.update({"exp": expire})
    
    # Encode JWT token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token.
    
    This verifies:
    - Token signature is valid
    - Token has not expired
    - Token was created with our SECRET_KEY
    
    Args:
        token: The JWT token string to decode
    
    Returns:
        dict: Token payload if valid, None if invalid or expired
    
    Example:
        >>> token = create_access_token({"sub": "123"})
        >>> payload = decode_access_token(token)
        >>> print(payload)
        {'sub': '123', 'exp': 1234567890}
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # Token is invalid, expired, or tampered with
        return None


def create_token_for_user(user_id: int) -> str:
    """
    Helper function to create a token for a specific user.
    
    This is a convenience wrapper around create_access_token
    that follows the standard convention of putting user_id in 'sub' field.
    
    Args:
        user_id: The user's database ID
    
    Returns:
        str: JWT token for this user
    
    Example:
        >>> token = create_token_for_user(123)
        >>> # User can now use this token to authenticate requests
    """
    return create_access_token(data={"sub": str(user_id)})


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Extract user ID from a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        int: User ID if token is valid, None otherwise
    
    Example:
        >>> token = create_token_for_user(123)
        >>> user_id = get_user_id_from_token(token)
        >>> print(user_id)
        123
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    try:
        return int(user_id)
    except (ValueError, TypeError):
        return None