"""
Integration tests for authentication flow with mock services
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAuthFlow:
    """Integration tests for authentication endpoints"""



    def test_signin_flow(self, client: TestClient, test_user, mock_cognito):
        """Test complete signin flow"""
        signin_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }

        response = client.post("/api/v1/auth/signin", json=signin_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["user"]["email"] == test_user["email"]

    def test_signin_invalid_credentials(self, client: TestClient, mock_cognito):
        """Test signin with invalid credentials"""
        signin_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword!"
        }

        response = client.post("/api/v1/auth/signin", json=signin_data)

        # Should return 500 for user not found (database-backed mock Cognito)
        assert response.status_code == 500

    def test_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/auth/me")

        # FastAPI HTTPBearer returns 403 for missing Authorization header
        assert response.status_code == 403

    def test_protected_endpoint_with_valid_token(self, client: TestClient, test_user, mock_cognito):
        """Test accessing protected endpoint with valid token"""
        # First sign in to get token
        signin_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }

        signin_response = client.post("/api/v1/auth/signin", json=signin_data)
        assert signin_response.status_code == 200
        
        token = signin_response.json()["access_token"]
        
        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]

    def test_protected_endpoint_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401

    def test_refresh_token_flow(self, client: TestClient, test_user, mock_cognito):
        """Test token refresh flow"""
        # First sign in to get tokens
        signin_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }

        signin_response = client.post("/api/v1/auth/signin", json=signin_data)
        assert signin_response.status_code == 200
        
        signin_data_response = signin_response.json()
        refresh_token = signin_data_response["refresh_token"]
        
        # Use refresh token to get new access token
        refresh_data = {
            "refresh_token": refresh_token,
            "email": test_user["email"]
        }
        
        response = client.post("/api/v1/auth/refresh-token", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"




