"""
Generate Alembic migration for Cognito authentication fields.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command
from app.core.logging_service import get_logger

logger = get_logger(__name__)


def generate_cognito_migration():
    """Generate migration for Cognito authentication fields"""
    try:
        # Get the alembic.ini file path
        alembic_cfg_path = backend_dir / "alembic.ini"
        
        if not alembic_cfg_path.exists():
            raise FileNotFoundError(f"Alembic config file not found: {alembic_cfg_path}")
        
        # Create Alembic config
        alembic_cfg = Config(str(alembic_cfg_path))
        
        # Generate migration
        message = "Add role and cognito_sub fields to users table"
        command.revision(alembic_cfg, autogenerate=True, message=message)
        
        logger.info(f"Migration generated successfully: {message}")
        
    except Exception as e:
        logger.error(f"Failed to generate migration: {e}")
        raise


if __name__ == "__main__":
    generate_cognito_migration()
