from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(
    signup_data: SignupRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Register a new user with email, password, and name.
    
    Returns JWT token for authentication and user information.
    """
    result = AuthService.signup(db, signup_data)
    return TokenResponse(
        access_token=result["access_token"],
        token_type=result["token_type"]
    )


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user with email and password.
    
    Returns JWT token for authentication.
    
    Raises:
        401: Invalid email or password
    """
    result = AuthService.login(db, login_data)
    return TokenResponse(
        access_token=result["access_token"],
        token_type=result["token_type"]
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user's profile information.
    
    Requires valid JWT token in Authorization header.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        profile_picture=current_user.profile_picture,
        created_at=current_user.created_at
    )
