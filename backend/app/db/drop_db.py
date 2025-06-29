import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.core.config_service import config_service
from app.core.logging_service import get_logger

# Get logger for this module
logger = get_logger(__name__)

def drop_database():
    """
    Drop the database if it exists.
    WARNING: This will permanently delete all data in the database!
    """
    # Get database connection parameters from config
    db_url = config_service.get_database_url()

    # Skip dropping for SQLite (just log a warning)
    if db_url.startswith("sqlite"):
        logger.warning("Cannot drop SQLite database - please delete the file manually if needed", 
                      operation="drop_database", status="skipped")
        return True

    # Parse the database URL to get connection parameters
    # Format: postgresql://username:password@host:port/database
    db_url_parts = db_url.replace("postgresql://", "").split("/")
    connection_string = db_url_parts[0]
    db_name = db_url_parts[1] if len(db_url_parts) > 1 else "mydatabase"

    # Parse connection string to get user, password, host, port
    user_pass, host_port = connection_string.split("@")
    user, password = user_pass.split(":") if ":" in user_pass else (user_pass, "")
    host, port = host_port.split(":") if ":" in host_port else (host_port, 5432)

    db_params = {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
    }

    logger.warning("About to drop database", database_name=db_name, host=host, port=port)

    try:
        # Connect to PostgreSQL server (to postgres database)
        logger.info("Connecting to PostgreSQL server", host=db_params["host"], port=db_params["port"])
        conn = psycopg2.connect(**db_params, database="postgres")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()

        if exists:
            logger.warning("Dropping database", database_name=db_name)
            
            # Terminate all connections to the database before dropping
            cursor.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
            """, (db_name,))
            
            # Drop the database
            cursor.execute(f'DROP DATABASE "{db_name}"')
            logger.info("Database dropped successfully", database_name=db_name, status="dropped")
        else:
            logger.info("Database does not exist, nothing to drop", database_name=db_name, status="not_exists")

        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        logger.error("PostgreSQL error during database drop", error=str(e), error_code=e.pgcode if hasattr(e, "pgcode") else None)
        return False
    except Exception as e:
        logger.error("Unexpected error during database drop", error=str(e))
        return False

if __name__ == "__main__":
    # This allows the script to be run directly
    success = drop_database()
    sys.exit(0 if success else 1)
