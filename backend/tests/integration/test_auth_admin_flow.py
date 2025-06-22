"""
Integration tests for authentication flow with admin role assignment.
Tests the complete flow from user registration to admin role assignment.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.main import app
from app.dependencies import get_db
from app.db import Base
from app.models.user import UserRole
from app.crud.user import UserDAO
from app.services.user_service import UserService


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create a test client."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


class TestAuthAdminFlow:
    """Test authentication flow with admin role assignment."""

    def test_first_user_becomes_admin_via_dao(self, db):
        """Test that first user created via DAO becomes admin."""
        user_dao = UserDAO()
        
        # Create first user
        from app.schemas.user import UserCreate
        user_create = UserCreate(
            username="admin@example.com",
            email="admin@example.com",
            full_name="Admin User",
            cognito_sub="cognito_sub_123"
        )
        
        first_user = user_dao.create(db, obj_in=user_create)
        
        # First user should be admin
        assert first_user.role == UserRole.ADMIN
        assert first_user.username == "admin@example.com"
        assert first_user.email == "admin@example.com"

    def test_second_user_becomes_regular_user_via_dao(self, db):
        """Test that second user created via DAO becomes regular user."""
        user_dao = UserDAO()
        
        # Create first user (admin)
        from app.schemas.user import UserCreate
        first_user_create = UserCreate(
            username="admin@example.com",
            email="admin@example.com",
            full_name="Admin User",
            cognito_sub="cognito_sub_123"
        )
        user_dao.create(db, obj_in=first_user_create)
        
        # Create second user
        second_user_create = UserCreate(
            username="user@example.com",
            email="user@example.com",
            full_name="Regular User",
            cognito_sub="cognito_sub_456"
        )
        
        second_user = user_dao.create(db, obj_in=second_user_create)
        
        # Second user should be regular user
        assert second_user.role == UserRole.USER
        assert second_user.username == "user@example.com"

    def test_first_user_becomes_admin_via_service(self, db):
        """Test that first user created via UserService becomes admin."""
        user_dao = UserDAO()
        user_service = UserService(user_dao)
        
        # Create first user using service
        first_user = user_service.create_user_from_params(
            db=db,
            username="admin@example.com",
            email="admin@example.com",
            full_name="Admin User",
            cognito_sub="cognito_sub_123"
        )
        
        # First user should be admin
        assert first_user.role == UserRole.ADMIN
        assert first_user.username == "admin@example.com"



    def test_user_count_affects_admin_assignment(self, db):
        """Test that user count correctly affects admin role assignment."""
        user_dao = UserDAO()
        
        # Initially no users
        assert user_dao.get_count(db) == 0
        
        # Create first user
        from app.schemas.user import UserCreate
        first_user_create = UserCreate(
            username="first@example.com",
            email="first@example.com",
            full_name="First User",
            cognito_sub="sub_1"
        )
        first_user = user_dao.create(db, obj_in=first_user_create)
        
        # Should be admin and count should be 1
        assert first_user.role == UserRole.ADMIN
        assert user_dao.get_count(db) == 1
        
        # Create second user
        second_user_create = UserCreate(
            username="second@example.com",
            email="second@example.com",
            full_name="Second User",
            cognito_sub="sub_2"
        )
        second_user = user_dao.create(db, obj_in=second_user_create)
        
        # Should be regular user and count should be 2
        assert second_user.role == UserRole.USER
        assert user_dao.get_count(db) == 2

    def test_admin_role_persists_in_database(self, db):
        """Test that admin role is properly persisted in database."""
        user_dao = UserDAO()
        
        # Create admin user
        from app.schemas.user import UserCreate
        user_create = UserCreate(
            username="admin@example.com",
            email="admin@example.com",
            full_name="Admin User",
            cognito_sub="cognito_sub_123"
        )
        created_user = user_dao.create(db, obj_in=user_create)
        
        # Verify admin role
        assert created_user.role == UserRole.ADMIN
        
        # Retrieve user from database
        retrieved_user = user_dao.get(db, created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.role == UserRole.ADMIN
        
        # Retrieve by email
        user_by_email = user_dao.get_by_email(db, "admin@example.com")
        assert user_by_email is not None
        assert user_by_email.role == UserRole.ADMIN
