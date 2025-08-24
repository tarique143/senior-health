# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Import the settings instance from our config file.
from app.config import settings

# Create the SQLAlchemy engine. The engine is the starting point for any
# SQLAlchemy application. It's the 'home base' for the actual database.
# We connect it using the DATABASE_URL from our settings.
engine = create_engine(settings.DATABASE_URL)

# Create a SessionLocal class. Each instance of SessionLocal will be a
# database session. The session is the primary interface for all database
# operations like adding, updating, and deleting records.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class. Our ORM models (like User, Medication, etc.) will
# inherit from this class. This is how SQLAlchemy connects our Python objects
# to the database tables.
Base = declarative_base()


def get_db() -> Session:
    """
    FastAPI dependency to get a database session for each request.

    This function creates a new SessionLocal, yields it to the path operation,
    and then ensures the session is closed after the request is finished,
    even if an error occurred. This prevents database connections from being
    left open.

    Yields:
        An active SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
