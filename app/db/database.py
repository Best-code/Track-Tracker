"""
Database connection and session management.

This module provides the core SQLAlchemy configuration for the Track Tracker
application, including engine creation, session management, and the declarative
base for ORM models.

Usage:
    from app.db.database import SessionLocal, Base, get_db

    # For dependency injection (FastAPI)
    def my_endpoint(db: Session = Depends(get_db)):
        ...

    # For manual session management
    with SessionLocal() as db:
        ...
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session


DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise EnvironmentError(
        "DATABASE_URL environment variable is required. "
        "Expected format: postgresql://user:pass@host:5432/dbname"
    )

# Configure engine with connection pooling for scale
engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # Number of connections to keep open
    max_overflow=10,       # Additional connections allowed beyond pool_size
    pool_timeout=30,       # Seconds to wait for available connection
    pool_recycle=1800,     # Recycle connections after 30 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection generator for database sessions.

    Yields a database session and ensures proper cleanup after use.
    Designed for use with FastAPI's Depends() system.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/tracks")
        def get_tracks(db: Session = Depends(get_db)):
            return db.query(Track).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI.

    Provides a database session with automatic commit on success
    and rollback on exception.

    Yields:
        Session: SQLAlchemy database session

    Example:
        with get_db_context() as db:
            db.add(new_track)
            # Commits automatically on exit
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()