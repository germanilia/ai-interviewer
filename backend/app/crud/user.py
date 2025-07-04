from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.crud.base import BaseDAO


class UserDAO(BaseDAO[User, UserResponse, UserCreate, UserUpdate]):
    """
    Data Access Object for User operations.
    Returns Pydantic objects instead of SQLAlchemy models.
    """

    def __init__(self):
        super().__init__(User, UserResponse)

    def get(self, db: Session, id: int) -> Optional[UserResponse]:
        """Get a user by ID."""
        user = db.query(User).filter(User.id == id).first()
        return self._to_schema(user) if user else None

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get multiple users with pagination."""
        users = db.query(User).offset(skip).limit(limit).all()
        return self._to_schema_list(users)

    def get_by_email(self, db: Session, email: str) -> Optional[UserResponse]:
        """Get a user by email."""
        user = db.query(User).filter(User.email == email).first()
        return self._to_schema(user) if user else None

    def get_by_username(self, db: Session, username: str) -> Optional[UserResponse]:
        """Get a user by username."""
        user = db.query(User).filter(User.username == username).first()
        return self._to_schema(user) if user else None

    def get_by_cognito_sub(self, db: Session, cognito_sub: str) -> Optional[UserResponse]:
        """Get a user by Cognito sub (user ID)."""
        user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
        return self._to_schema(user) if user else None

    def create(self, db: Session, *, obj_in: UserCreate) -> UserResponse:
        """Create a new user."""
        # Check if this is the first user (make them admin)
        user_count = db.query(User).count()
        role = UserRole.ADMIN if user_count == 0 else obj_in.role

        user = User(
            username=obj_in.username,
            email=obj_in.email,
            full_name=obj_in.full_name,
            role=role,
            cognito_sub=obj_in.cognito_sub
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return self._to_schema(user)

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> UserResponse:
        """Update an existing user."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return self._to_schema(db_obj)

    def update_by_id(self, db: Session, user_id: int, obj_in: UserUpdate) -> Optional[UserResponse]:
        """Update a user by ID."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return self.update(db, db_obj=user, obj_in=obj_in)

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete a user by ID."""
        user = db.query(User).filter(User.id == id).first()
        if not user:
            return False

        db.delete(user)
        db.commit()
        return True

    def get_count(self, db: Session) -> int:
        """Get the total number of users."""
        return db.query(User).count()

    def create_user_legacy(
        self,
        db: Session,
        username: str,
        email: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER,
        cognito_sub: Optional[str] = None
    ) -> UserResponse:
        """
        Legacy method for creating a user with individual parameters.
        Use create() with UserCreate schema instead.
        """
        user_create = UserCreate(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            cognito_sub=cognito_sub
        )
        return self.create(db, obj_in=user_create)
