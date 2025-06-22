"""
Development-only router for testing and debugging.
Only available in development mode.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.dependencies import get_db, get_user_service
from app.core.config_service import config_service
from app.core.jwt_utils import create_access_token
from app.services.user_service import UserService

from app.models.user import UserRole
from app.core.logging_service import get_logger

logger = get_logger(__name__)

# Only create router if in development mode
if config_service.is_development():
    dev_router = APIRouter()
else:
    dev_router = None


class DevTokenRequest(BaseModel):
    """Request schema for creating development tokens"""
    username: str
    email: Optional[str] = None
    user_sub: Optional[str] = None
    expires_in: Optional[int] = 3600  # 1 hour default


class DevTokenResponse(BaseModel):
    """Response schema for development tokens"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def check_development_mode():
    """Dependency to ensure endpoint is only available in development"""
    if not config_service.is_development():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Development endpoints not available in production"
        )


if dev_router is not None:
    @dev_router.post("/create-token", response_model=DevTokenResponse)
    async def create_dev_token(
        request: DevTokenRequest,
        db: Session = Depends(get_db),
        user_service: UserService = Depends(get_user_service),
        _: None = Depends(check_development_mode)
    ):
        """
        Create a local development token for testing API endpoints.
        Only available in development mode.
        """
        try:
            # Check if user exists in database
            user = user_service.get_user_by_username(db, username=request.username)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User '{request.username}' not found in database"
                )

            # Create token data
            token_data = {
                "username": request.username,
                "email": request.email or user.email,
                "user_sub": request.user_sub
            }

            # Create the token
            access_token = create_access_token(
                data=token_data,
                expires_delta=request.expires_in
            )

            logger.info(f"Created development token for user: {request.username}")

            return DevTokenResponse(
                access_token=access_token,
                expires_in=request.expires_in or 30
            )

        except Exception as e:
            logger.error(f"Failed to create development token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create token: {str(e)}"
            )

    @dev_router.get("/users")
    async def list_dev_users(
        db: Session = Depends(get_db),
        user_service: UserService = Depends(get_user_service),
        _: None = Depends(check_development_mode)
    ):
        """
        List all users for development token creation.
        Only available in development mode.
        """
        try:
            users = user_service.get_users(db, skip=0, limit=100)
            return [
                {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active
                }
                for user in users
            ]
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list users: {str(e)}"
            )

    @dev_router.post("/create-test-user")
    async def create_test_user(
        db: Session = Depends(get_db),
        user_service: UserService = Depends(get_user_service),
        _: None = Depends(check_development_mode)
    ):
        """
        Create a test user for development.
        Only available in development mode.
        """
        try:
            # Check if test user already exists
            existing_user = user_service.get_user_by_username(db, username="testuser")
            if existing_user:
                return {
                    "message": "Test user already exists",
                    "username": existing_user.username,
                    "email": existing_user.email
                }

            # Create test user using UserService
            test_user = user_service.create_user_from_params(
                db=db,
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                role=UserRole.USER
            )

            logger.info("Created test user for development")

            return {
                "message": "Test user created successfully",
                "username": test_user.username,
                "email": test_user.email,
                "role": test_user.role
            }

        except Exception as e:
            logger.error(f"Failed to create test user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create test user: {str(e)}"
            )

else:
    # Create empty router for production
    dev_router = APIRouter()

    @dev_router.get("/")
    async def dev_not_available():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Development endpoints not available in production"
        )
