"""
Database connection and session management.

This module sets up SQLAlchemy engine, session factory, and base model class.
It also provides the get_db dependency for FastAPI endpoints.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
# For SQLite, we need check_same_thread=False to work with FastAPI
# For PostgreSQL, this parameter is ignored
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False  # Set to True for SQL query logging during development
)

# Create SessionLocal class - each instance is a database session
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit - we want explicit control
    autoflush=False,   # Don't auto-flush - we want explicit control
    bind=engine
)

# Base class for all database models
# All models will inherit from this
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    
    This is used with FastAPI's Depends() to inject database session
    into endpoint functions. The session is automatically closed after
    the request is complete.
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    
    This creates all tables defined in models if they don't exist.
    Should be called on application startup.
    """
    # Import all models here to ensure they are registered with Base
    from app.models import (
        User, 
        Interest, 
        UserInterest, 
        FriendRequest, 
        Message
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)