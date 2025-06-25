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
# Import all models to ensure they are registered with Base
# Import app components to create test app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router as api_router
from app.core.config_service import settings
from app.middlewaremiddleware.logging_middleware import RequestLoggingMiddleware
from app.dependencies import get_db
from app.crud.user import UserDAO
from app.services.user_service import UserService
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
def candidate_dao():
    """Create a CandidateDAO instance."""
    from app.crud.candidate import CandidateDAO
    return CandidateDAO()


@pytest.fixture
def interview_dao():
    """Create an InterviewDAO instance."""
    from app.crud.interview import InterviewDAO
    return InterviewDAO()


@pytest.fixture
def question_dao():
    """Create a QuestionDAO instance."""
    from app.crud.question import QuestionDAO
    return QuestionDAO()

@pytest.fixture
def interview_question_dao():
    """Create an InterviewQuestionDAO instance."""
    from app.crud.interview_question import InterviewQuestionDAO
    return InterviewQuestionDAO()


@pytest.fixture
def user_service(user_dao):
    """Create a UserService instance with injected UserDAO."""
    return UserService(user_dao)


@pytest.fixture
def candidate_service(candidate_dao):
    """Create a CandidateService instance with injected CandidateDAO."""
    from app.services.candidate_service import CandidateService
    return CandidateService(candidate_dao)


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
def authenticated_client(client, test_user, mock_cognito):
    """Create an authenticated test client with a valid token."""
    # Sign in to get token
    signin_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }

    signin_response = client.post("/api/v1/auth/signin", json=signin_data)
    assert signin_response.status_code == 200

    token = signin_response.json()["access_token"]

    # Create a client wrapper that automatically includes the auth header
    class AuthenticatedClient:
        def __init__(self, client, token):
            self.client = client
            self.token = token
            self.headers = {"Authorization": f"Bearer {token}"}

        def get(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.get(url, **kwargs)

        def post(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.post(url, **kwargs)

        def put(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.put(url, **kwargs)

        def delete(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.delete(url, **kwargs)

        def patch(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.patch(url, **kwargs)

    return AuthenticatedClient(client, token)


@pytest.fixture
def sample_data(db, test_user):
    """Create sample data for testing reports."""
    from app.models.candidate import Candidate
    from app.models.interview import Interview, InterviewStatus, RiskLevel
    from datetime import datetime, timedelta

       # Create sample candidates
    candidate1 = Candidate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="123-456-7890",
        created_by_user_id=test_user["db_user"].id
    )
    candidate2 = Candidate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone="098-765-4321",
        created_by_user_id=test_user["db_user"].id
    )

    db.add_all([candidate1, candidate2])
    db.commit()
    db.refresh(candidate1)
    db.refresh(candidate2)

    # Create sample interviews
    base_date = datetime.now() - timedelta(days=30)

    from app.schemas.interview import generate_pass_key

    interview1 = Interview(
        candidate_id=candidate1.id,
        interview_date=base_date + timedelta(days=1),
        status=InterviewStatus.COMPLETED,
        score=85.5,
        risk_level=RiskLevel.LOW,
        completed_at=base_date + timedelta(days=1, hours=1),
        created_by_user_id=test_user["db_user"].id,
        pass_key=generate_pass_key()
    )

    interview2 = Interview(
        candidate_id=candidate2.id,
        interview_date=base_date + timedelta(days=5),
        status=InterviewStatus.COMPLETED,
        score=72.0,
        risk_level=RiskLevel.MEDIUM,
        completed_at=base_date + timedelta(days=5, hours=1),
        created_by_user_id=test_user["db_user"].id,
        pass_key=generate_pass_key()
    )

    interview3 = Interview(
        candidate_id=candidate1.id,
        interview_date=base_date + timedelta(days=10),
        status=InterviewStatus.IN_PROGRESS,
        score=None,
        risk_level=None,
        created_by_user_id=test_user["db_user"].id,
        pass_key=generate_pass_key()
    )

    db.add_all([interview1, interview2, interview3])
    db.commit()

    return {
        "candidates": [candidate1, candidate2],
        "interviews": [interview1, interview2, interview3]
    }


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
