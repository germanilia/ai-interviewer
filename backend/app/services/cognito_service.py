"""
Cognito service for handling authentication operations.
Supports both LocalStack (development) and AWS Cognito (production).
"""
import boto3
import hmac
import hashlib
import base64
from typing import Dict, Optional, Any
from botocore.exceptions import ClientError
from app.core.config_service import config_service
from app.core.logging_service import get_logger
from app.core.exceptions import CognitoError, get_user_friendly_error_message


logger = get_logger(__name__)


class CognitoService:
    """Service for handling Cognito authentication operations"""

    def __init__(self):
        self.config = config_service.get_cognito_config()
        self.aws_config = config_service.get_aws_credentials()
        self.is_localstack = config_service.is_localstack_enabled()
        
        # Initialize Cognito client
        self._init_client()

    def _init_client(self):
        """Initialize the Cognito client"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_config["access_key_id"] or None,
                aws_secret_access_key=self.aws_config["secret_access_key"] or None,
                region_name=self.config["region"]
            )
            
            # Use LocalStack endpoint if enabled
            if self.is_localstack and self.config["endpoint_url"]:
                self.client = session.client(
                    "cognito-idp",
                    endpoint_url=self.config["endpoint_url"]
                )
                logger.info("Initialized Cognito client with LocalStack endpoint")
            else:
                self.client = session.client("cognito-idp")
                logger.info("Initialized Cognito client with AWS endpoint")
                
        except Exception as e:
            logger.error(f"Failed to initialize Cognito client: {e}")
            raise

    def _calculate_secret_hash(self, username: str) -> str:
        """Calculate the secret hash for Cognito client"""
        if not self.config["client_secret"]:
            return ""
            
        message = username + self.config["client_id"]
        dig = hmac.new(
            self.config["client_secret"].encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()

    async def sign_up(self, email: str, password: str, full_name: str = "") -> Dict[str, Any]:
        """Sign up a new user using email as username"""
        try:
            # Use email directly as username since Cognito is configured with username-attributes email
            cognito_username = email

            user_attributes = [
                {"Name": "email", "Value": email}
            ]

            if full_name:
                user_attributes.append({"Name": "name", "Value": full_name})

            params = {
                "ClientId": self.config["client_id"],
                "Username": cognito_username,
                "Password": password,
                "UserAttributes": user_attributes
            }

            # Add secret hash if client secret is configured
            if self.config["client_secret"]:
                params["SecretHash"] = self._calculate_secret_hash(cognito_username)

            response = self.client.sign_up(**params)

            # In development mode, auto-confirm the user
            user_confirmed = response.get("UserConfirmed", False)
            if not user_confirmed and config_service.is_development():
                try:
                    # Auto-confirm user in development
                    await self._admin_confirm_sign_up(email)
                    user_confirmed = True
                    logger.info(f"User {email} auto-confirmed in development mode")
                except Exception as e:
                    logger.warning(f"Failed to auto-confirm user {email}: {e}")

            logger.info(f"User {email} signed up successfully")
            return {
                "user_sub": response["UserSub"],
                "user_confirmed": user_confirmed,
                "email": email,
                "cognito_username": cognito_username
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Sign up failed for {email}: {error_code} - {error_message}")
            user_friendly_message = get_user_friendly_error_message(error_code, error_message)
            raise CognitoError(user_friendly_message, error_code=error_code)

    async def _admin_confirm_sign_up(self, email: str) -> None:
        """Admin confirm sign up for development mode"""
        try:
            self.client.admin_confirm_sign_up(
                UserPoolId=self.config["user_pool_id"],
                Username=email
            )
            logger.info(f"Admin confirmed user {email}")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Admin confirm failed for {email}: {error_code} - {error_message}")
            user_friendly_message = get_user_friendly_error_message(error_code, error_message)
            raise CognitoError(user_friendly_message, error_code=error_code)

    async def confirm_sign_up(self, email: str, confirmation_code: str) -> bool:
        """Confirm user sign up with confirmation code"""
        try:
            # Use email directly as username since Cognito is configured with username-attributes email
            cognito_username = email

            params = {
                "ClientId": self.config["client_id"],
                "Username": cognito_username,
                "ConfirmationCode": confirmation_code
            }

            if self.config["client_secret"]:
                params["SecretHash"] = self._calculate_secret_hash(cognito_username)

            self.client.confirm_sign_up(**params)
            logger.info(f"User {email} confirmed successfully")
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Confirmation failed for {email}: {error_code} - {error_message}")
            user_friendly_message = get_user_friendly_error_message(error_code, error_message)
            raise CognitoError(user_friendly_message, error_code=error_code)

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user and return tokens"""
        try:
            # Use email directly as username since Cognito is configured with username-attributes email
            cognito_username = email

            params = {
                "ClientId": self.config["client_id"],
                "AuthFlow": "USER_PASSWORD_AUTH",
                "AuthParameters": {
                    "USERNAME": cognito_username,
                    "PASSWORD": password
                }
            }

            if self.config["client_secret"]:
                params["AuthParameters"]["SECRET_HASH"] = self._calculate_secret_hash(cognito_username)

            response = self.client.initiate_auth(**params)

            auth_result = response["AuthenticationResult"]
            logger.info(f"User {email} signed in successfully")

            return {
                "access_token": auth_result["AccessToken"],
                "id_token": auth_result["IdToken"],
                "refresh_token": auth_result.get("RefreshToken"),
                "expires_in": auth_result.get("ExpiresIn", 3600),
                "email": email,
                "cognito_username": cognito_username
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Sign in failed for {email}: {error_code} - {error_message}")
            user_friendly_message = get_user_friendly_error_message(error_code, error_message)
            raise CognitoError(user_friendly_message, error_code=error_code)

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from access token"""
        try:
            response = self.client.get_user(AccessToken=access_token)
            
            user_attributes = {}
            for attr in response["UserAttributes"]:
                user_attributes[attr["Name"]] = attr["Value"]
            
            return {
                "username": response["Username"],
                "user_sub": user_attributes.get("sub"),
                "email": user_attributes.get("email"),
                "name": user_attributes.get("name", ""),
                "email_verified": user_attributes.get("email_verified") == "true"
            }
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Get user info failed: {error_code} - {error_message}")
            user_friendly_message = get_user_friendly_error_message(error_code, error_message)
            raise CognitoError(user_friendly_message, error_code=error_code)

    async def refresh_token(self, refresh_token: str, email: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Use email directly as username since Cognito is configured with username-attributes email
            cognito_username = email

            params = {
                "ClientId": self.config["client_id"],
                "AuthFlow": "REFRESH_TOKEN_AUTH",
                "AuthParameters": {
                    "REFRESH_TOKEN": refresh_token
                }
            }

            if self.config["client_secret"]:
                params["AuthParameters"]["SECRET_HASH"] = self._calculate_secret_hash(cognito_username)

            response = self.client.initiate_auth(**params)

            auth_result = response["AuthenticationResult"]
            logger.info(f"Token refreshed successfully for {email}")

            return {
                "access_token": auth_result["AccessToken"],
                "id_token": auth_result["IdToken"],
                "expires_in": auth_result.get("ExpiresIn", 3600)
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Token refresh failed: {error_code} - {error_message}")
            user_friendly_message = get_user_friendly_error_message(error_code, error_message)
            raise CognitoError(user_friendly_message, error_code=error_code)


# Global instance
cognito_service = CognitoService()
