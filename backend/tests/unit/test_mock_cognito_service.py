"""
Unit tests for MockCognitoService
"""
import pytest
from app.services.mock_cognito_service import MockCognitoService


@pytest.mark.asyncio
class TestMockCognitoService:
    """Test cases for MockCognitoService"""

    @pytest.fixture
    def mock_cognito(self):
        """Create a fresh MockCognitoService instance for each test"""
        service = MockCognitoService()
        yield service
        # Clear tokens only, users are in database
        service._tokens.clear()





    def test_validate_invalid_token(self, mock_cognito):
        """Test validation of invalid token"""
        with pytest.raises(Exception, match="Invalid token"):
            mock_cognito.validate_token("invalid-token")

    def test_clear_all_tokens(self, mock_cognito):
        """Test clearing all tokens"""
        # Create some tokens
        mock_cognito._tokens["test-token"] = {"test": "data"}

        # Clear all tokens
        mock_cognito._tokens.clear()

        assert len(mock_cognito._tokens) == 0
