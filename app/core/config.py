"""
Configuration management for the Friends Finder API.

This module handles all application settings using Pydantic Settings.
Environment variables are loaded from .env file.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables.
    Example: DATABASE_URL=postgresql://user:pass@localhost/db
    """
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./friends_finder.db"
    
    # Security Settings
    SECRET_KEY: str  # Must be set in .env - used for JWT signing
    ALGORITHM: str = "HS256"  # JWT algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token expiration time
    
    # Application Info
    PROJECT_NAME: str = "MeetZy"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for finding friends based on shared interests and location"
    
    # CORS Settings (for frontend)
    CORS_ORIGINS: list = ["*"]  # In production, specify your frontend URL
    
    # Pagination Defaults
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Matching Algorithm Settings
    DEFAULT_MAX_DISTANCE_KM: float = 50.0
    DEFAULT_MIN_MATCH_PERCENTAGE: int = 30
    MAX_INTERESTS_PER_USER: int = 10
    
    class Config:
        """Pydantic config for loading from .env file"""
        env_file = ".env"
        case_sensitive = True


# Create a single settings instance to be imported throughout the app
settings = Settings()