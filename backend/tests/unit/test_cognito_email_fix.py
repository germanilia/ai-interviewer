"""
Test for Cognito email username fix.
Verifies that email addresses are used directly as usernames in Cognito operations.
"""
import pytest
from unittest.mock import Mock
from app.services.cognito_service import CognitoService
from app.utils.username_utils import validate_and_normalize_email, normalize_email, is_valid_email


class TestCognitoEmailFix:
    """Test that Cognito service uses email directly as username."""

    @pytest.fixture
    def mock_cognito_service(self):
        """Create a mock Cognito service for testing."""
        service = CognitoService()
        service.client = Mock()
        service.config = {
            "user_pool_id": "test_pool_id",
            "client_id": "test_client_id",
            "client_secret": "",
            "region": "us-east-1"
        }
        return service

    @pytest.mark.asyncio
    async def test_sign_up_uses_email_as_username(self, mock_cognito_service):
        """Test that sign_up uses email directly as username."""
        # Mock the Cognito client response
        mock_cognito_service.client.sign_up.return_value = {
            "UserSub": "test_user_sub",
            "UserConfirmed": True
        }

        test_email = "iliag@sela.co.il"
        test_password = "TestPass123!"
        test_full_name = "Test User"

        # Call sign_up
        result = await mock_cognito_service.sign_up(
            email=test_email,
            password=test_password,
            full_name=test_full_name
        )

        # Verify the client was called with email as username
        mock_cognito_service.client.sign_up.assert_called_once()
        call_args = mock_cognito_service.client.sign_up.call_args[1]
        
        assert call_args["Username"] == test_email  # Email used directly as username
        assert call_args["Password"] == test_password
        assert call_args["ClientId"] == "test_client_id"
        
        # Verify user attributes
        user_attributes = call_args["UserAttributes"]
        email_attr = next(attr for attr in user_attributes if attr["Name"] == "email")
        assert email_attr["Value"] == test_email
        
        # Verify result
        assert result["user_sub"] == "test_user_sub"
        assert result["user_confirmed"] is True
        assert result["email"] == test_email
        assert result["cognito_username"] == test_email

    @pytest.mark.asyncio
    async def test_sign_in_uses_email_as_username(self, mock_cognito_service):
        """Test that sign_in uses email directly as username."""
        # Mock the Cognito client response
        mock_cognito_service.client.initiate_auth.return_value = {
            "AuthenticationResult": {
                "AccessToken": "test_access_token",
                "IdToken": "test_id_token",
                "RefreshToken": "test_refresh_token",
                "ExpiresIn": 3600
            }
        }

        test_email = "iliag@sela.co.il"
        test_password = "TestPass123!"

        # Call sign_in
        result = await mock_cognito_service.sign_in(
            email=test_email,
            password=test_password
        )

        # Verify the client was called with email as username
        mock_cognito_service.client.initiate_auth.assert_called_once()
        call_args = mock_cognito_service.client.initiate_auth.call_args[1]
        
        assert call_args["AuthParameters"]["USERNAME"] == test_email
        assert call_args["AuthParameters"]["PASSWORD"] == test_password
        
        # Verify result
        assert result["access_token"] == "test_access_token"
        assert result["email"] == test_email
        assert result["cognito_username"] == test_email

    @pytest.mark.asyncio
    async def test_confirm_sign_up_uses_email_as_username(self, mock_cognito_service):
        """Test that confirm_sign_up uses email directly as username."""
        # Mock the Cognito client response
        mock_cognito_service.client.confirm_sign_up.return_value = {}

        test_email = "iliag@sela.co.il"
        test_code = "123456"

        # Call confirm_sign_up
        result = await mock_cognito_service.confirm_sign_up(
            email=test_email,
            confirmation_code=test_code
        )

        # Verify the client was called with email as username
        mock_cognito_service.client.confirm_sign_up.assert_called_once()
        call_args = mock_cognito_service.client.confirm_sign_up.call_args[1]
        
        assert call_args["Username"] == test_email
        assert call_args["ConfirmationCode"] == test_code
        assert result is True

    def test_validate_and_normalize_email(self):
        """Test that validate_and_normalize_email works correctly."""
        test_email = "Test.User@Example.COM"

        normalized_email = validate_and_normalize_email(test_email)

        # Should be normalized to lowercase
        assert normalized_email == "test.user@example.com"

    def test_email_validation_functions(self):
        """Test email validation and normalization functions."""
        # Test valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "iliag@sela.co.il",
            "test+tag@example.com"
        ]
        
        for email in valid_emails:
            assert is_valid_email(email), f"Email {email} should be valid"
            normalized = normalize_email(email)
            assert normalized == email.lower().strip()

        # Test invalid emails
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            ""
        ]
        
        for email in invalid_emails:
            assert not is_valid_email(email), f"Email {email} should be invalid"

    def test_special_characters_in_email(self):
        """Test that emails with special characters work correctly."""
        test_emails = [
            "iliag@sela.co.il",
            "user+tag@example.com",
            "user.name@sub.domain.com",
            "test_user@example-domain.org"
        ]

        for email in test_emails:
            assert is_valid_email(email), f"Email {email} should be valid"
            normalized_email = validate_and_normalize_email(email)
            assert normalized_email == email.lower()
