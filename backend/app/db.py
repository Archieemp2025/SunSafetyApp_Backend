from pathlib import Path
import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Load local environment variables only if a .env file exists.
# This supports local development while still allowing deployment platforms to provide DATABASE_URL through real environment variables.
env_path = Path(".env")
if env_path.exists():
    load_dotenv(env_path)


# Read the database connection string from the environment. This must be set either in a local .env file or in deployment config.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. Define it in environment variables or in a local .env file."
    )


# Basic logger for database-related errors. Logging minimal and avoid printing secrets.
logger = logging.getLogger(__name__)


# Create the SQLAlchemy engine.
# pool_pre_ping=True helps detect stale or dropped DB connections before the application tries to use them.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# Create a session factory. Each request will use its own database session created from this.
# autocommit=False means changes are not committed automatically. autoflush=False prevents automatic flushes before explicit actions.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for SQLAlchemy ORM models. All table-mapped model classes will inherit from this later.
Base = declarative_base()

# FastAPI dependency for getting a database session. # A new session is opened for each request and always closed safely.
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # Log unexpected DB session errors without exposing secrets.
        logger.exception("Database session error occurred.")
        raise
    finally:
        # Always close the session to avoid connection leaks.
        db.close()