import logging
import sys
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User
from app.db import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample users to populate the database
SAMPLE_USERS = [
    {
        "username": "johndoe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "is_active": True
    },
    {
        "username": "janedoe",
        "email": "jane@example.com",
        "full_name": "Jane Doe",
        "is_active": True
    },
    {
        "username": "bobsmith",
        "email": "bob@example.com",
        "full_name": "Bob Smith",
        "is_active": True
    },
    {
        "username": "alicejones",
        "email": "alice@example.com",
        "full_name": "Alice Jones",
        "is_active": True
    },
    {
        "username": "mikebrown",
        "email": "mike@example.com",
        "full_name": "Mike Brown",
        "is_active": True
    }
]


def populate_db():
    """
    Populate the database with sample users.
    """
    db = SessionLocal()
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            logger.info(f"Database already contains {existing_users} users. Skipping population.")
            return

        logger.info("Populating database with sample users")
        for user_data in SAMPLE_USERS:
            user = User(**user_data)
            db.add(user)

        db.commit()
        logger.info(f"Successfully added {len(SAMPLE_USERS)} users to the database")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error populating database: {e}")
        return False
    finally:
        db.close()

    return True


if __name__ == "__main__":
    # This allows the script to be run directly
    from app.db.init_db import init_db

    # Initialize the database first
    if not init_db():
        logger.error("Failed to initialize database")
        sys.exit(1)

    # Then populate it
    if not populate_db():
        logger.error("Failed to populate database")
        sys.exit(1)

    logger.info("Database populated successfully!")
    sys.exit(0)
