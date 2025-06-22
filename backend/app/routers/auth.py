"""
Authentication router for user registration, login, and token management.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_active_user, get_user_service
from app.schemas.auth import (
    SignUpRequest, SignUpResponse, ConfirmSignUpRequest, ConfirmSignUpResponse,
    SignInRequest, SignInResponse, RefreshTokenRequest, RefreshTokenResponse,
    UserInfo, MessageResponse
)
from app.schemas.user import UserResponse, UserUpdate
from app.core.service_factory import get_cognito_service
from app.services.user_service import UserService
from app.core.logging_service import get_logger
from app.utils.username_utils import validate_and_normalize_email
from app.core.exceptions import CognitoError, ValidationError

logger = get_logger(__name__)

auth_router = APIRouter()


@auth_router.post("/signup", response_model=SignUpResponse)
async def sign_up(
    request: SignUpRequest,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """
    Register a new user with Cognito and create user record in database.
    """
    try:
        # Validate and normalize email
        try:
            normalized_email = validate_and_normalize_email(request.email)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Check if user already exists in database
        existing_email = user_service.get_user_by_email(db, normalized_email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Sign up user with Cognito
        cognito_service = get_cognito_service()
        cognito_response = await cognito_service.sign_up(
            email=normalized_email,
            password=request.password,
            full_name=request.full_name or ""
        )

        # Create user record in database
        user_service.create_user_from_params(
            db=db,
            username=normalized_email,  # Use email as username
            email=normalized_email,
            full_name=request.full_name,
            cognito_sub=cognito_response["user_sub"]
        )

        logger.info(f"User {normalized_email} signed up successfully")

        # Determine the message based on whether user is confirmed
        if cognito_response["user_confirmed"]:
            message = "User registered and confirmed successfully. You can now sign in."
        else:
            message = "User registered successfully. Please check your email for confirmation code."

        return SignUpResponse(
            message=message,
            user_sub=cognito_response["user_sub"],
            user_confirmed=cognito_response["user_confirmed"]
        )

    except HTTPException:
        raise
    except CognitoError as e:
        logger.error(f"Cognito error during sign up for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Unexpected error during sign up for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


@auth_router.post("/confirm-signup", response_model=ConfirmSignUpResponse)
async def confirm_sign_up(request: ConfirmSignUpRequest):
    """
    Confirm user sign up with confirmation code.
    """
    try:
        cognito_service = get_cognito_service()
        await cognito_service.confirm_sign_up(
            email=request.email,
            confirmation_code=request.confirmation_code
        )

        logger.info(f"User {request.email} confirmed successfully")

        return ConfirmSignUpResponse(
            message="User confirmed successfully. You can now sign in."
        )

    except CognitoError as e:
        logger.error(f"Cognito error during confirmation for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Unexpected error during confirmation for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


@auth_router.post("/signin", response_model=SignInResponse)
async def sign_in(
    request: SignInRequest,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """
    Sign in user and return access tokens.
    """
    try:
        # Authenticate with Cognito
        cognito_service = get_cognito_service()
        tokens = await cognito_service.sign_in(
            email=request.email,
            password=request.password
        )

        # Get user info from Cognito
        user_info = await cognito_service.get_user_info(tokens["access_token"])

        # Get or update user in database
        user = user_service.get_user_by_cognito_sub(db, user_info["user_sub"])
        if not user:
            # User might exist with email but no cognito_sub
            user = user_service.get_user_by_email(db, request.email)
            if user:
                # Update user with cognito_sub
                user_update = UserUpdate(cognito_sub=user_info["user_sub"])
                user = user_service.update_user(db, user.id, user_update)
            else:
                # Create new user record
                user = user_service.create_user_from_params(
                    db=db,
                    username=request.email,  # Use email as username
                    email=user_info["email"],
                    full_name=user_info["name"],
                    cognito_sub=user_info["user_sub"]
                )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create or retrieve user"
            )

        logger.info(f"User {request.email} signed in successfully")

        return SignInResponse(
            access_token=tokens["access_token"],
            id_token=tokens["id_token"],
            refresh_token=tokens.get("refresh_token"),
            expires_in=tokens["expires_in"],
            user=UserInfo(
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                user_sub=user.cognito_sub
            )
        )

    except CognitoError as e:
        logger.error(f"Cognito error during sign in for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Unexpected error during sign in for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


@auth_router.post("/refresh-token", response_model=RefreshTokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    """
    try:
        cognito_service = get_cognito_service()
        tokens = await cognito_service.refresh_token(
            refresh_token=request.refresh_token,
            email=request.email
        )

        logger.info(f"Token refreshed successfully for {request.email}")

        return RefreshTokenResponse(
            access_token=tokens["access_token"],
            id_token=tokens["id_token"],
            expires_in=tokens["expires_in"]
        )

    except Exception as e:
        logger.error(f"Token refresh failed for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@auth_router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_active_user)):
    """
    Get current user information.
    """
    return UserInfo(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        user_sub=current_user.cognito_sub
    )


@auth_router.post("/signout", response_model=MessageResponse)
async def sign_out():
    """
    Sign out user (client should discard tokens).
    """
    return MessageResponse(
        message="Signed out successfully. Please discard your tokens."
    )
