"""
Debug test for authentication flow
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.mark.integration
class TestDebugAuth:
    """Debug authentication flow"""

    def test_debug_signin_flow(self, client: TestClient, mock_cognito):
        """Debug the complete signin flow step by step"""
        print("\n=== Debug Signin Flow ===")
        
        # Test user credentials
        signin_data = {
            "email": "admin@admin.com",
            "password": "Cowabunga2@"
        }
        
        print(f"1. Testing signin with: {signin_data['email']}")
        
        # Test the signin endpoint
        response = client.post("/api/v1/auth/signin", json=signin_data)
        
        print(f"2. Response status: {response.status_code}")
        print(f"3. Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"4. SUCCESS - Response data keys: {list(data.keys())}")
            print(f"5. User info: {data.get('user', {})}")
            print(f"6. Has access_token: {'access_token' in data}")
        else:
            print(f"4. FAILED - Response text: {response.text}")
            
        # Should return 500 for user not found (database-backed mock Cognito)
        assert response.status_code == 500

    def test_debug_mock_cognito_state(self, mock_cognito, test_user):
        """Debug the mock Cognito service state"""
        print("\n=== Debug Mock Cognito State ===")

        print(f"1. Mock Cognito tokens: {len(mock_cognito._tokens)}")

        # Check if test users exist in database
        test_emails = ["admin@admin.com", "user@test.com", test_user["email"]]
        for email in test_emails:
            exists = mock_cognito.user_exists(email)
            print(f"2. User {email} exists: {exists}")
            if exists:
                user_data = mock_cognito.get_user_by_email(email)
                print(f"   User data: {user_data}")

        # This test always passes - it's just for debugging
        assert True

    def test_debug_health_endpoint(self, client: TestClient):
        """Debug the health endpoint to check environment"""
        print("\n=== Debug Health Endpoint ===")
        
        response = client.get("/api/v1/health")
        print(f"1. Health status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"2. Health data: {data}")
            print(f"3. Environment: {data.get('environment')}")
            print(f"4. Using mock Cognito: {data.get('use_mock_cognito')}")
            print(f"5. Is testing: {data.get('is_testing')}")
            print(f"6. Database type: {data.get('database_type')}")
        else:
            print(f"2. Health check failed: {response.text}")
            
        assert response.status_code == 200
