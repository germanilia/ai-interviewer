"""
Unit tests for MockCognitoJWTValidator
"""
import pytest
from app.core.mock_jwt_utils import MockCognitoJWTValidator
from app.schemas.auth import TokenData


class TestMockCognitoJWTValidator:
    """Test cases for MockCognitoJWTValidator"""

    @pytest.fixture
    def mock_jwt_validator(self):
        """Create a fresh MockCognitoJWTValidator instance for each test"""
        validator = MockCognitoJWTValidator()
        yield validator
        validator.clear_all_tokens()

    def test_validate_registered_token(self, mock_jwt_validator):
        """Test validation of a registered token"""
        token = "test-token-123"
        username = "test@example.com"
        user_sub = "test-user-sub"
        email = "test@example.com"

        # Register token
        mock_jwt_validator.add_valid_token(token, username, user_sub, email)

        # Validate token
        token_data = mock_jwt_validator.validate_token(token)

        assert isinstance(token_data, TokenData)
        assert token_data.username == username
        assert token_data.user_sub == user_sub
        assert token_data.email == email

    def test_validate_default_admin_token(self, mock_jwt_validator):
        """Test validation of default admin mock token"""
        token = "mock-admin-token"

        token_data = mock_jwt_validator.validate_token(token)

        assert isinstance(token_data, TokenData)
        assert token_data.username == "admin@admin.com"
        assert token_data.user_sub == "mock-user-admin123"
        assert token_data.email == "admin@admin.com"

    def test_validate_default_user_token(self, mock_jwt_validator):
        """Test validation of default user mock token"""
        token = "mock-user-token"

        token_data = mock_jwt_validator.validate_token(token)

        assert isinstance(token_data, TokenData)
        assert token_data.username == "user@test.com"
        assert token_data.user_sub == "mock-user-test456"
        assert token_data.email == "user@test.com"

    def test_validate_mock_access_token_format(self, mock_jwt_validator):
        """Test validation of mock access token with proper format"""
        # Mock token format: mock-access-{user_sub}-{timestamp}
        token = "mock-access-mock-user-abc123-1234567890"

        # This test now relies on the fallback mechanism since we don't have _users
        token_data = mock_jwt_validator.validate_token(token)

        assert isinstance(token_data, TokenData)
        assert token_data.username == "test@example.com"
        assert token_data.user_sub == "mock-user-default"
        assert token_data.email == "test@example.com"

    def test_validate_fallback_mock_token(self, mock_jwt_validator):
        """Test validation of unrecognized mock token (fallback)"""
        token = "mock-unknown-token"

        token_data = mock_jwt_validator.validate_token(token)

        assert isinstance(token_data, TokenData)
        assert token_data.username == "test@example.com"
        assert token_data.user_sub == "mock-user-default"
        assert token_data.email == "test@example.com"

    def test_validate_invalid_token(self, mock_jwt_validator):
        """Test validation of invalid token"""
        token = "invalid-token"

        with pytest.raises(Exception, match="Invalid authentication token"):
            mock_jwt_validator.validate_token(token)

    def test_add_valid_token(self, mock_jwt_validator):
        """Test adding a valid token"""
        token = "test-token"
        username = "test@example.com"
        user_sub = "test-sub"
        email = "test@example.com"

        mock_jwt_validator.add_valid_token(token, username, user_sub, email)

        # Verify token was added
        assert token in mock_jwt_validator._valid_tokens
        assert mock_jwt_validator._valid_tokens[token]["username"] == username
        assert mock_jwt_validator._valid_tokens[token]["user_sub"] == user_sub
        assert mock_jwt_validator._valid_tokens[token]["email"] == email

    def test_remove_token(self, mock_jwt_validator):
        """Test removing a token"""
        token = "test-token"
        username = "test@example.com"
        user_sub = "test-sub"
        email = "test@example.com"

        # Add token first
        mock_jwt_validator.add_valid_token(token, username, user_sub, email)
        assert token in mock_jwt_validator._valid_tokens

        # Remove token
        mock_jwt_validator.remove_token(token)
        assert token not in mock_jwt_validator._valid_tokens

    def test_clear_all_tokens(self, mock_jwt_validator):
        """Test clearing all tokens"""
        # Add some tokens
        mock_jwt_validator.add_valid_token("token1", "user1", "sub1", "email1")
        mock_jwt_validator.add_valid_token("token2", "user2", "sub2", "email2")

        assert len(mock_jwt_validator._valid_tokens) == 2

        # Clear all tokens
        mock_jwt_validator.clear_all_tokens()
        assert len(mock_jwt_validator._valid_tokens) == 0

    def test_is_token_valid(self, mock_jwt_validator):
        """Test is_token_valid method"""
        valid_token = "mock-admin-token"
        invalid_token = "invalid-token"

        assert mock_jwt_validator.is_token_valid(valid_token) is True
        assert mock_jwt_validator.is_token_valid(invalid_token) is False
