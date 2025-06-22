"""
User service layer for business logic operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.user import UserDAO
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.models.user import UserRole
from app.core.logging_service import get_logger

logger = get_logger(__name__)


class UserService:
    """
    Service layer for user operations.
    Handles business logic and coordinates between routers and DAOs.
    """

    def __init__(self, user_dao: UserDAO):
        """
        Initialize UserService with UserDAO dependency.
        
        Args:
            user_dao: UserDAO instance for database operations
        """
        self.user_dao = user_dao

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[UserResponse]:
        """
        Get a user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            UserResponse if found, None otherwise
        """
        logger.info(f"Getting user by ID: {user_id}")
        return self.user_dao.get(db, user_id)

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """
        Get multiple users with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of UserResponse objects
        """
        logger.info(f"Getting users with skip={skip}, limit={limit}")
        return self.user_dao.get_multi(db, skip=skip, limit=limit)

    def get_user_by_email(self, db: Session, email: str) -> Optional[UserResponse]:
        """
        Get a user by email address.
        
        Args:
            db: Database session
            email: User email address
            
        Returns:
            UserResponse if found, None otherwise
        """
        logger.info(f"Getting user by email: {email}")
        return self.user_dao.get_by_email(db, email)

    def get_user_by_username(self, db: Session, username: str) -> Optional[UserResponse]:
        """
        Get a user by username.
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            UserResponse if found, None otherwise
        """
        logger.info(f"Getting user by username: {username}")
        return self.user_dao.get_by_username(db, username)

    def get_user_by_cognito_sub(self, db: Session, cognito_sub: str) -> Optional[UserResponse]:
        """
        Get a user by Cognito sub (user ID).
        
        Args:
            db: Database session
            cognito_sub: Cognito user ID
            
        Returns:
            UserResponse if found, None otherwise
        """
        logger.info(f"Getting user by Cognito sub: {cognito_sub}")
        return self.user_dao.get_by_cognito_sub(db, cognito_sub)

    def create_user(self, db: Session, user_create: UserCreate) -> UserResponse:
        """
        Create a new user.
        
        Args:
            db: Database session
            user_create: User creation data
            
        Returns:
            Created UserResponse
        """
        logger.info(f"Creating user: {user_create.username}")
        return self.user_dao.create(db, obj_in=user_create)

    def create_user_from_params(
        self,
        db: Session,
        username: str,
        email: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER,
        cognito_sub: Optional[str] = None
    ) -> UserResponse:
        """
        Create a user from individual parameters (legacy support).
        
        Args:
            db: Database session
            username: Username
            email: Email address
            full_name: Full name (optional)
            role: User role
            cognito_sub: Cognito user ID (optional)
            
        Returns:
            Created UserResponse
        """
        logger.info(f"Creating user from params: {username}")
        return self.user_dao.create_user_legacy(
            db, username, email, full_name, role, cognito_sub
        )

    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        """
        Update a user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            user_update: User update data
            
        Returns:
            Updated UserResponse if found, None otherwise
        """
        logger.info(f"Updating user: {user_id}")
        return self.user_dao.update_by_id(db, user_id, user_update)

    def delete_user(self, db: Session, user_id: int) -> bool:
        """
        Delete a user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting user: {user_id}")
        return self.user_dao.delete(db, id=user_id)

    def get_user_count(self, db: Session) -> int:
        """
        Get the total number of users.
        
        Args:
            db: Database session
            
        Returns:
            Total number of users
        """
        logger.info("Getting user count")
        return self.user_dao.get_count(db)

    def is_first_user(self, db: Session) -> bool:
        """
        Check if this would be the first user in the system.
        
        Args:
            db: Database session
            
        Returns:
            True if no users exist, False otherwise
        """
        return self.get_user_count(db) == 0
