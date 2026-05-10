"""
Core module for Friends Finder API.

This module contains essential configuration, database, and security utilities
that are used throughout the application.

Modules:
    - config: Application settings and configuration
    - database: Database connection and session management
    - security: Password hashing and JWT token utilities
"""

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal, get_db, init_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    create_token_for_user,
    get_user_id_from_token
)

__all__ = [
    # Config
    "settings",
    
    # Database
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    
    # Security
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "create_token_for_user",
    "get_user_id_from_token",
]