"""
Pytest configuration and shared fixtures for backend tests.
"""
import os
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
# Import app components to create test app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router as api_router
from app.core.config_service import settings
from app.middlewaremiddleware.logging_middleware import RequestLoggingMiddleware
from app.dependencies import get_db
from app.crud.user import UserDAO
from app.services.user_service import UserService
from app.core.service_factory import get_cognito_service, get_jwt_validator
from app.services.mock_cognito_service import mock_cognito_service
from app.core.mock_jwt_utils import mock_jwt_validator

# Set test environment - must be done before importing app modules
os.environ["APP_ENV"] = "test"
os.environ["USE_MOCK_COGNITO"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Force reload of config service with test environment
import importlib
import sys
if 'app.core.config_service' in sys.modules:
    importlib.reload(sys.modules['app.core.config_service'])

# Create test app without lifespan (no database initialization)
test_app = FastAPI(
    title=f"{settings.PROJECT_NAME} - Test",
    description="Test FastAPI backend",
    version="1.0.0-test",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
test_app.add_middleware(RequestLoggingMiddleware)
test_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
test_app.include_router(api_router)

# Add basic endpoints
@test_app.get("/")
async def read_root():
    return {"message": "Welcome to the test FastAPI application!"}

@test_app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

test_app.dependency_overrides[get_db] = override_get_db


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


@pytest.fixture
def user_dao():
    """Create a UserDAO instance."""
    return UserDAO()


@pytest.fixture
def user_service(user_dao):
    """Create a UserService instance with injected UserDAO."""
    return UserService(user_dao)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    Base.metadata.create_all(bind=engine)
    with TestClient(test_app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_cognito():
    """Create a clean mock Cognito service for testing."""
    # Clear tokens only, users are in database
    mock_cognito_service._tokens.clear()

    # Patch the SessionLocal to use the test database session
    import app.services.mock_cognito_service as mock_cognito_module
    import app.db as db_module

    original_cognito_session_local = mock_cognito_module.SessionLocal
    original_db_session_local = db_module.SessionLocal

    mock_cognito_module.SessionLocal = TestingSessionLocal
    db_module.SessionLocal = TestingSessionLocal

    yield mock_cognito_service

    # Restore original SessionLocal
    mock_cognito_module.SessionLocal = original_cognito_session_local
    db_module.SessionLocal = original_db_session_local
    mock_cognito_service._tokens.clear()


@pytest.fixture
def mock_jwt():
    """Create a clean mock JWT validator for testing."""
    mock_jwt_validator.clear_all_tokens()
    yield mock_jwt_validator
    mock_jwt_validator.clear_all_tokens()


@pytest.fixture
def test_user(db):
    """Create a test user in the database."""
    from app.models.user import User, UserRole
    import hashlib

    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }

    # Generate deterministic user_sub
    email_hash = hashlib.md5(user_data["email"].encode()).hexdigest()[:8]
    user_sub = f"mock-user-{email_hash}"

    # Create user in database
    db_user = User(
        username=user_data["email"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        cognito_sub=user_sub,
        role=UserRole.USER,
        is_active=True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "email": user_data["email"],
        "password": user_data["password"],
        "full_name": user_data["full_name"],
        "user_sub": user_sub,
        "db_user": db_user
    }


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
