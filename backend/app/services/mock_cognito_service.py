"""
Mock Cognito service for testing purposes.
Provides the same interface as the real Cognito service but checks the database for users.
"""
import hashlib
import time
from typing import Dict, Any
import logging
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)


class MockCognitoService:
    """
    Mock implementation of Cognito service for testing.
    Checks database for users and generates deterministic user_sub values.
    """

    def __init__(self):
        # Only store tokens in memory, users are in database
        self._tokens: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized Mock Cognito Service")

    def _generate_user_sub(self, email: str) -> str:
        """Generate deterministic user_sub based on email"""
        email_hash = hashlib.md5(email.encode()).hexdigest()[:8]
        return f"mock-user-{email_hash}"

    async def sign_up(self, email: str, password: str, full_name: str = "") -> Dict[str, Any]:
        """Sign up a new user using email as username"""
        try:
            # Generate deterministic user_sub
            user_sub = self._generate_user_sub(email)

            # For mock service, we'll just return success
            # In real implementation, this would create the user in Cognito
            # The actual user creation in database is handled by the signup endpoint

            logger.info(f"Mock Cognito: Created user {email} with sub {user_sub}")

            return {
                "user_sub": user_sub,
                "user_confirmed": True,
                "email": email,
                "cognito_username": email
            }

        except Exception as e:
            logger.error(f"Mock Cognito sign up failed for {email}: {e}")
            raise Exception(f"Sign up failed: {str(e)}")

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user and return mock tokens"""
        try:
            # Check database for user
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.email == email).first()
                if not user:
                    logger.error(f"Mock Cognito: User {email} not found in database")
                    raise Exception("User not found")

                # For mock service, we'll use a simple password check
                # In real implementation, passwords would be hashed
                # For testing, we'll check against the test user passwords
                test_passwords = {
                    "admin@admin.com": "Cowabunga2@",
                    "user@test.com": "TestPassword123!",
                    "test@example.com": "TestPassword123!"  # Add test user
                }

                expected_password = test_passwords.get(email)
                if not expected_password or password != expected_password:
                    logger.error(f"Mock Cognito: Invalid password for {email}")
                    raise Exception("Invalid credentials")

                # Generate mock tokens
                timestamp = int(time.time())
                access_token = f"mock-access-{user.cognito_sub}-{timestamp}"
                id_token = f"mock-id-{user.cognito_sub}-{timestamp}"
                refresh_token = f"mock-refresh-{user.cognito_sub}"

                # Store tokens for validation
                self._tokens[access_token] = {
                    "user_sub": user.cognito_sub,
                    "email": email,
                    "token_type": "access",
                    "expires_at": timestamp + 3600
                }
                self._tokens[id_token] = {
                    "user_sub": user.cognito_sub,
                    "email": email,
                    "token_type": "id",
                    "expires_at": timestamp + 3600
                }

                logger.info(f"Mock Cognito: User {email} signed in successfully")

                return {
                    "access_token": access_token,
                    "id_token": id_token,
                    "refresh_token": refresh_token,
                    "expires_in": 3600,
                    "token_type": "Bearer",
                    "email": email,
                    "cognito_username": email
                }
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Mock Cognito sign in failed for {email}: {e}")
            raise Exception(f"Sign in failed: {str(e)}")

    async def refresh_token(self, refresh_token: str, email: str) -> Dict[str, Any]:
        """Refresh tokens for a user"""
        try:
            # Find user in database
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.email == email).first()
                if not user:
                    raise Exception("User not found")

                # Generate new tokens
                timestamp = int(time.time())
                access_token = f"mock-access-{user.cognito_sub}-{timestamp}"
                id_token = f"mock-id-{user.cognito_sub}-{timestamp}"

                # Store new tokens
                self._tokens[access_token] = {
                    "user_sub": user.cognito_sub,
                    "email": email,
                    "token_type": "access",
                    "expires_at": timestamp + 3600
                }
                self._tokens[id_token] = {
                    "user_sub": user.cognito_sub,
                    "email": email,
                    "token_type": "id",
                    "expires_at": timestamp + 3600
                }

                logger.info(f"Mock Cognito: Token refreshed for {email}")

                return {
                    "access_token": access_token,
                    "id_token": id_token,
                    "expires_in": 3600
                }
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Mock Cognito token refresh failed for {email}: {e}")
            raise Exception(f"Token refresh failed: {str(e)}")

    def user_exists(self, email: str) -> bool:
        """Check if user exists"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            return user is not None
        finally:
            db.close()

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user data by email"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                return {
                    "user_sub": user.cognito_sub,
                    "email": user.email,
                    "full_name": user.full_name,
                    "cognito_username": user.email
                }
            return {}
        finally:
            db.close()

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate a token and return token data"""
        if token in self._tokens:
            token_data = self._tokens[token]
            # Check if token is expired
            if token_data["expires_at"] > int(time.time()):
                return token_data
            else:
                logger.warning(f"Mock Cognito: Token {token[:20]}... has expired")
                raise Exception("Token expired")
        else:
            logger.warning(f"Mock Cognito: Invalid token {token[:20]}...")
            raise Exception("Invalid token")

    async def confirm_sign_up(self, email: str, confirmation_code: str):
        """Confirm user sign up (mock implementation - always succeeds)"""
        # For mock service, we just log the confirmation
        # In real implementation, this would confirm the user in Cognito
        logger.info(f"Mock Cognito: Confirmed user {email} with code {confirmation_code}")

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from access token"""
        try:
            token_data = self.validate_token(access_token)
            email = token_data["email"]

            db = SessionLocal()
            try:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    return {
                        "user_sub": user.cognito_sub,
                        "email": user.email,
                        "name": user.full_name,  # Use 'name' to match real Cognito response
                        "full_name": user.full_name,  # Keep both for compatibility
                        "cognito_username": user.email
                    }
                else:
                    raise Exception("User not found")
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Mock Cognito: Failed to get user info: {e}")
            raise Exception("Failed to get user info")

    def clear_all_users(self):
        """Clear all users and tokens (for testing)"""
        # Only clear tokens, users are in database
        self._tokens.clear()
        logger.info("Mock Cognito: Cleared all tokens")




# Global instance
mock_cognito_service = MockCognitoService()
