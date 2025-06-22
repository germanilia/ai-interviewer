import typer
import logging
from app.db.init_db import init_db
from app.db.populate_db import populate_db
from app.db.run_migrations import run_migrations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Typer app
app = typer.Typer(help="Database management commands")


@app.command()
def init():
    """
    Initialize the database by creating all tables.
    """
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully!")


@app.command()
def migrate():
    """
    Run database migrations using Alembic.
    """
    logger.info("Running database migrations...")
    success = run_migrations()
    if success:
        logger.info("Database migrations completed successfully!")
    else:
        logger.error("Database migrations failed!")
        raise typer.Exit(code=1)


@app.command()
def populate():
    """
    Populate the database with sample data.
    """
    logger.info("Populating database...")
    # Initialize the database first to ensure tables exist
    init_db()
    # Then populate it
    populate_db()
    logger.info("Database populated successfully!")


@app.command()
def setup():
    """
    Complete database setup: run migrations and populate with sample data.
    """
    logger.info("Setting up database...")
    # Run migrations first
    success = run_migrations()
    if not success:
        logger.error("Database migrations failed!")
        raise typer.Exit(code=1)

    # Then populate with sample data
    populate_db()
    logger.info("Database setup completed successfully!")


if __name__ == "__main__":
    app()
