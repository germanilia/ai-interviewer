"""
Unit tests for authentication endpoints focusing on admin role assignment.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.dependencies import get_db
from app.db import Base
from app.models.user import UserRole


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth_endpoints.db"
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


class TestAuthEndpoints:
    """Test authentication endpoints with focus on admin role assignment."""











    def test_signin_endpoint_validation(self, client):
        """Test signin endpoint input validation."""
        # Test missing email
        response = client.post("/api/v1/auth/signin", json={
            "password": "TestPass123!"
        })
        assert response.status_code == 422
        
        # Test missing password
        response = client.post("/api/v1/auth/signin", json={
            "email": "test@example.com"
        })
        assert response.status_code == 422
        
        # Test invalid email format
        response = client.post("/api/v1/auth/signin", json={
            "email": "invalid-email",
            "password": "TestPass123!"
        })
        assert response.status_code == 422

    def test_signin_handles_cognito_errors(self, client, mock_cognito):
        """Test that signin endpoint handles Cognito errors gracefully."""
        # Test with non-existent user (will cause error in database-backed mock Cognito)
        response = client.post("/api/v1/auth/signin", json={
            "email": "nonexistent@example.com",
            "password": "TestPass123!"
        })

        # Should return 500 for user not found (database-backed mock Cognito)
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
