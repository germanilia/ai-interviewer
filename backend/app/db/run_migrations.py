import sys
import subprocess
from pathlib import Path

from app.core.logging_service import get_logger

# Get logger for this module
logger = get_logger(__name__)

def run_migrations():
    """
    Run database migrations using Alembic.
    This function uses the database URL from the config service via alembic/env.py.
    """
    try:
        # Get the path to the backend directory
        backend_dir = Path(__file__).resolve().parent.parent.parent

        logger.info("Starting database migrations", operation="run_migrations")

        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
            check=True
        )

        if result.stdout.strip():
            logger.info("Migration output", output=result.stdout.strip())
        if result.stderr.strip():
            logger.warning("Migration warnings", warnings=result.stderr.strip())

        logger.info("Database migrations completed successfully", operation="run_migrations", status="success")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(
            "Migration failed",
            operation="run_migrations",
            status="failed",
            error_code=e.returncode,
            error_output=e.stderr if e.stderr else "No error output"
        )
        return False
    except Exception as e:
        logger.error("Unexpected error running migrations", operation="run_migrations", status="error", error=str(e))
        return False

if __name__ == "__main__":
    # This allows the script to be run directly
    success = run_migrations()
    sys.exit(0 if success else 1)
