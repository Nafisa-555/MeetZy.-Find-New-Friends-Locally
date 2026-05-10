from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest


class AuthService:
    """Authentication service for signup and login operations."""

    @staticmethod
    def signup(db: Session, signup_data: SignupRequest) -> dict:
        """
        Register a new user.
        
        Args:
            db: Database session
            signup_data: SignupRequest schema with email, password, name
        
        Returns:
            Dictionary with access_token, token_type, and user data
        
        Raises:
            HTTPException: 400 if email already exists
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == signup_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(signup_data.password)
        
        # Create new user
        new_user = User(
            email=signup_data.email,
            password_hash=hashed_password,
            name=signup_data.name
        )
        
        # Save to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": str(new_user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "profile_picture": new_user.profile_picture,
                "created_at": new_user.created_at
            }
        }

    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> dict:
        """
        Authenticate user and generate JWT token.
        
        Args:
            db: Database session
            login_data: LoginRequest schema with email and password
        
        Returns:
            Dictionary with access_token, token_type, and user data
        
        Raises:
            HTTPException: 401 if credentials invalid or 400 if user inactive
        """
        # Query user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        # Check if user exists and password is correct
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive"
            )
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "profile_picture": user.profile_picture,
                "created_at": user.created_at
            }
        }
