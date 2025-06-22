"""
Configuration service for the backend application.
Loads configuration from environment variables, AWS Secrets Manager, and secrets file.
"""
import os
import yaml
from typing import Dict, Any, List
from pathlib import Path
import logging
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


logger = logging.getLogger(__name__)

class ConfigService:
    """
    Service for loading and accessing application configuration.
    Combines environment variables, AWS Secrets Manager, and secrets from YAML file.
    """

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._secrets: Dict[str, Any] = {}
        self._aws_secrets: Dict[str, Any] = {}

        # Determine environment
        self._env = os.getenv("APP_ENV", "development")

        # Load configuration
        self._load_env_file()
        self._load_env_vars()
        self._load_aws_secrets()
        self._load_secrets()

    def _load_env_file(self) -> None:
        """Load the appropriate .env file based on environment"""
        base_dir = Path(__file__).resolve().parent.parent.parent

        # Try to load environment-specific .env file
        env_file = base_dir / f".env.{self._env}"

        # If environment-specific file doesn't exist, fall back to development
        if not env_file.exists() and self._env != "development":
            logger.warning(f"Environment file {env_file} not found. Falling back to development.")
            self._env = "development"
            env_file = base_dir / ".env.development"

        # If still no file, try generic .env
        if not env_file.exists():
            env_file = base_dir / ".env"

        # Load the environment file if it exists
        if env_file.exists():
            logger.info(f"Loading environment from {env_file}")
            load_dotenv(env_file)
        else:
            logger.warning("No environment file found. Using default values.")

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables"""
        self._config = {
            "app_env": self._env,
            "debug": os.getenv("DEBUG", "True").lower() in ("true", "1", "t"),
            "api_prefix": os.getenv("API_PREFIX", "/api/v1"),
            "project_name": os.getenv("PROJECT_NAME", "My Boilerplate App"),
            "allowed_hosts": os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(","),
            "cors_origins": os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(","),
            "port": int(os.getenv("PORT", "9000")),
            "host": os.getenv("HOST", "0.0.0.0"),

            # Logging configuration
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_json_format": os.getenv("LOG_JSON_FORMAT", "True").lower() in ("true", "1", "t"),
            "log_console_output": os.getenv("LOG_CONSOLE_OUTPUT", "True").lower() in ("true", "1", "t"),
            "log_file_output": os.getenv("LOG_FILE_OUTPUT", "False").lower() in ("true", "1", "t"),
            "log_file_path": os.getenv("LOG_FILE_PATH", "logs/app.log"),
            "log_rotation": os.getenv("LOG_ROTATION", "20 MB"),
            "log_retention": os.getenv("LOG_RETENTION", "1 week"),
            "log_compression": os.getenv("LOG_COMPRESSION", "zip"),
        }

    def _load_aws_secrets(self) -> None:
        """Load secrets from AWS Secrets Manager if configured"""
        # Check if AWS Secrets Manager is configured
        secret_name = os.getenv("AWS_SECRETS_MANAGER_SECRET_NAME")
        if not secret_name:
            logger.info("AWS Secrets Manager not configured. Skipping AWS secrets loading.")
            return

        try:
            # Get AWS region from environment or use default
            region_name = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

            # Create a Secrets Manager client
            session = boto3.Session()
            client = session.client(
                service_name="secretsmanager",
                region_name=region_name
            )

            logger.info(f"Loading secrets from AWS Secrets Manager: {secret_name}")

            # Get the secret value
            response = client.get_secret_value(SecretId=secret_name)
            secret_string = response["SecretString"]

            # Parse the secret as YAML (same format as local secrets.yaml)
            self._aws_secrets = yaml.safe_load(secret_string)
            logger.info("Successfully loaded secrets from AWS Secrets Manager")

        except NoCredentialsError:
            logger.error("AWS credentials not found. Cannot load secrets from AWS Secrets Manager.")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "DecryptionFailureException":
                logger.error("Secrets Manager can't decrypt the protected secret text using the provided KMS key.")
            elif error_code == "InternalServiceErrorException":
                logger.error("An error occurred on the server side.")
            elif error_code == "InvalidParameterException":
                logger.error("You provided an invalid value for a parameter.")
            elif error_code == "InvalidRequestException":
                logger.error("You provided a parameter value that is not valid for the current state of the resource.")
            elif error_code == "ResourceNotFoundException":
                logger.error(f"The requested secret {secret_name} was not found.")
            else:
                logger.error(f"Error loading secrets from AWS Secrets Manager: {e}")
        except yaml.YAMLError:
            logger.error("Failed to parse secrets from AWS Secrets Manager. Expected YAML format.")
        except Exception as e:
            logger.error(f"Unexpected error loading secrets from AWS Secrets Manager: {e}")

    def _load_secrets(self) -> None:
        """Load secrets from YAML file"""
        # Determine the secrets file path based on environment
        base_dir = Path(__file__).resolve().parent.parent.parent
        secrets_file = base_dir / "secrets.yaml"

        # If secrets file doesn't exist, try to use example file
        if not secrets_file.exists():
            logger.warning(f"Secrets file not found at {secrets_file}. Using example file.")
            secrets_file = base_dir / "secrets.example.yaml"

        # Load secrets from file
        if secrets_file.exists():
            try:
                with open(secrets_file, "r") as f:
                    self._secrets = yaml.safe_load(f)
                logger.info(f"Loaded secrets from {secrets_file}")
            except Exception as e:
                logger.error(f"Error loading secrets file: {e}")
                self._secrets = {}
        else:
            logger.warning("No secrets file found. Using default values.")
            self._secrets = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        Priority order:
        1. Environment variables
        2. AWS Secrets Manager
        3. Local secrets file
        4. Default value
        """
        # Check if key exists in environment variables
        if key in self._config:
            return self._config[key]

        # Check if key exists in AWS Secrets Manager (supports nested keys with dot notation)
        if self._aws_secrets and "." in key:
            parts = key.split(".")
            value = self._aws_secrets
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    break
            else:
                return value

        # Check if key exists at top level of AWS secrets
        if self._aws_secrets and key in self._aws_secrets:
            return self._aws_secrets[key]

        # Check if key exists in local secrets file (supports nested keys with dot notation)
        if "." in key:
            parts = key.split(".")
            value = self._secrets
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value

        # Check if key exists at top level of local secrets
        if key in self._secrets:
            return self._secrets[key]

        return default

    def get_database_url(self) -> str:
        """
        Get database URL from secrets or construct it from components.
        Priority:
        1. Full URL from environment (prioritized in test mode)
        2. Full URL from secrets
        3. Constructed from components
        """
        # In test mode, prioritize environment variable over secrets
        if self.is_testing():
            db_url = os.getenv("DATABASE_URL")
            if db_url:
                return db_url

        # Check if a full URL is provided in secrets
        if self._secrets and "database" in self._secrets and "url" in self._secrets["database"]:
            return self._secrets["database"]["url"]

        # Check if a full URL is provided in environment
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            return db_url

        # Construct from components
        username = self.get("database.username", "postgres")
        password = self.get("database.password", "postgres")
        host = self.get("database.host", "localhost")
        port = self.get("database.port", 5432)
        name = self.get("database.name", "mydatabase")

        return f"postgresql://{username}:{password}@{host}:{port}/{name}"

    def get_secret_key(self) -> str:
        """Get the secret key for JWT tokens and other security features"""
        return self.get("security.secret_key", "your_secret_key_here")

    def get_aws_credentials(self) -> Dict[str, str]:
        """Get AWS credentials from secrets"""
        return {
            "access_key_id": self.get("aws.access_key_id", ""),
            "secret_access_key": self.get("aws.secret_access_key", ""),
            "region": self.get("aws.region", "us-east-1")
        }

    def get_cognito_config(self) -> Dict[str, str]:
        """Get Cognito configuration from environment variables"""
        return {
            "user_pool_id": os.getenv("COGNITO_USER_POOL_ID", ""),
            "client_id": os.getenv("COGNITO_CLIENT_ID", ""),
            "client_secret": os.getenv("COGNITO_CLIENT_SECRET", ""),
            "endpoint_url": os.getenv("COGNITO_ENDPOINT_URL", ""),
            "region": os.getenv("COGNITO_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
        }

    def is_localstack_enabled(self) -> bool:
        """Check if LocalStack is enabled for development"""
        return self.get("use_localstack", False)

    def is_development(self) -> bool:
        """Check if the application is running in development mode"""
        return self._env.lower() == "development"

    def is_production(self) -> bool:
        """Check if the application is running in production mode"""
        return self._env.lower() == "production"

    def is_testing(self) -> bool:
        """Check if the application is running in test mode"""
        return self._env.lower() in ("test", "testing")

    def use_mock_cognito(self) -> bool:
        """Check if mock Cognito service should be used"""
        return os.getenv("USE_MOCK_COGNITO", "false").lower() == "true"


# Create a singleton instance
config_service = ConfigService()


# Determine the environment file path for Settings
def get_env_file_path() -> str:
    # Get the base directory for the backend
    base_dir = Path(__file__).resolve().parent.parent.parent

    # Determine the environment
    env = os.getenv("APP_ENV", "development")

    # Set the environment file path
    env_file = base_dir / f".env.{env}"

    # If environment-specific file doesn't exist, fall back to development
    if not env_file.exists() and env != "development":
        logger.warning(f"Environment file {env_file} not found. Falling back to development.")
        env_file = base_dir / ".env.development"

    # If still no file, try generic .env
    if not env_file.exists():
        env_file = base_dir / ".env"

    # If no environment file exists, log a warning
    if not env_file.exists():
        logger.warning("No environment file found. Using default values.")
        return ""
    else:
        logger.info(f"Using environment file: {env_file}")
        return str(env_file)


class Settings(BaseSettings):
    """
    Application settings that loads from environment variables and secrets file
    """
    # API settings
    API_V1_STR: str = config_service.get("api_prefix", "/api/v1")
    PROJECT_NAME: str = config_service.get("project_name", "My Boilerplate App")

    # CORS settings
    CORS_ORIGINS: str = ",".join(config_service.get("cors_origins", ["http://localhost:3000", "http://localhost:5173"]))

    # Database settings
    DATABASE_URL: str = config_service.get_database_url()
    DB_NAME: str = config_service.get("database.name", "mydatabase")

    # Security settings
    SECRET_KEY: str = config_service.get_secret_key()

    # Application settings
    DEBUG: bool = config_service.get("debug", True)
    LOG_LEVEL: str = config_service.get("log_level", "info")
    ALLOWED_HOSTS: str = ",".join(config_service.get("allowed_hosts", ["localhost", "127.0.0.1"]))

    # AWS settings
    AWS_ACCESS_KEY_ID: str = config_service.get("aws.access_key_id", "")
    AWS_SECRET_ACCESS_KEY: str = config_service.get("aws.secret_access_key", "")

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """Returns the CORS origins as a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def ALLOWED_HOSTS_LIST(self) -> List[str]:
        """Returns the allowed hosts as a list"""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    class Config:
        env_file = get_env_file_path()
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'  # Ignore extra fields from environment


# Create a singleton instance of Settings
settings = Settings()
