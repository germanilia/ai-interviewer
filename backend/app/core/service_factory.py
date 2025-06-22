"""
Service factory for choosing between real and mock services based on configuration.
"""
import logging
from app.core.config_service import config_service

logger = logging.getLogger(__name__)


def get_cognito_service():
    """Factory function to get appropriate Cognito service"""
    if config_service.use_mock_cognito():
        logger.info("Using Mock Cognito Service for testing")
        from app.services.mock_cognito_service import mock_cognito_service
        return mock_cognito_service
    else:
        logger.info("Using Real Cognito Service")
        from app.services.cognito_service import cognito_service
        return cognito_service


def get_jwt_validator():
    """Factory function to get appropriate JWT validator"""
    if config_service.use_mock_cognito():
        logger.info("Using Mock JWT Validator for testing")
        from app.core.mock_jwt_utils import mock_jwt_validator
        return mock_jwt_validator
    else:
        logger.info("Using Real JWT Validator")
        from app.core.jwt_utils import jwt_validator
        return jwt_validator
