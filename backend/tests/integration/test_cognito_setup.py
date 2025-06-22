"""
Integration tests for Cognito service setup with LocalStack.
"""
import pytest
from app.services.cognito_service import cognito_service
from app.core.logging_service import get_logger

logger = get_logger(__name__)


class TestCognitoIntegration:
    """Integration tests for Cognito service."""

    def test_cognito_configuration(self):
        """Test that Cognito service is properly configured."""
        config = cognito_service.config

        # Verify required configuration exists
        assert config["user_pool_id"] is not None
        assert config["client_id"] is not None
        assert config["region"] is not None

        logger.info(f"User Pool ID: {config['user_pool_id']}")
        logger.info(f"Client ID: {config['client_id']}")
        logger.info(f"Endpoint URL: {config['endpoint_url']}")
        logger.info(f"Is LocalStack: {cognito_service.is_localstack}")

    @pytest.mark.asyncio
    async def test_cognito_service_initialization(self):
        """Test that Cognito service initializes without errors."""
        # This should not raise an exception
        assert cognito_service.client is not None
        assert cognito_service.config is not None
        assert cognito_service.is_localstack is not None
